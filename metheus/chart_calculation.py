"""Privacy-conscious preflight for a future local chart calculator.

This module does not calculate a chart. It accepts only a schema-valid private
birth input, rejects uncertain or unresolved wall-clock values, and discloses
normalized birth timing only after an explicit scoped consent check.
"""

from __future__ import annotations

from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
import re
from typing import Any, Iterable
import zoneinfo
from zoneinfo import ZoneInfoNotFoundError

from .authorization import evaluate_authorization
from .schema_validation import validate_record_schema, validate_schema_instance


def _validate_preflight_result(result: dict[str, Any]) -> dict[str, Any]:
    validation = validate_schema_instance(result, "chart-calculation-preflight.schema.json")
    if not validation.get("valid"):
        raise RuntimeError("chart calculation preflight result violates its schema")
    return result


def _time_zone_database_metadata(time_zone: str) -> dict[str, str]:
    """Identify the timezone-data source used by ZoneInfo when possible."""
    zone_path = Path(*time_zone.split("/"))
    for root in zoneinfo.TZPATH:
        root_path = Path(root)
        if not (root_path / zone_path).is_file():
            continue
        version_file = root_path / "tzdata.zi"
        try:
            with version_file.open(encoding="utf-8") as stream:
                first_line = stream.readline().strip()
        except OSError:
            first_line = ""
        match = re.fullmatch(r"# version ([A-Za-z0-9._-]+)", first_line)
        return {
            "source": "system_zoneinfo",
            "version": match.group(1) if match else "unavailable",
        }

    try:
        package = import_module("tzdata")
        version = getattr(package, "IANA_VERSION", None)
        if isinstance(version, str) and version.strip():
            return {"source": "python_tzdata", "version": version}
    except ImportError:
        pass
    return {"source": "unresolved", "version": "unavailable"}


def _inspect_chart_calculation_input(
    record: dict[str, Any],
    *, include_calculation_input: bool,
) -> dict[str, Any]:
    """Determine whether a birth input has an exact, unambiguous local instant.

    Results contain issue codes, never copies of rejected input values. The
    default ready result contains no birth details. Only the authorization
    wrapper can return normalized timing after a scoped consent check.
    """
    schema_result = validate_record_schema(record)
    if not schema_result.get("valid"):
        return {
            "ready": False,
            "issues": [{"code": "birth_chart_input_schema_invalid"}],
            "schemaIssues": schema_result.get("issues", []),
        }

    if record.get("recordType") != "birth_chart_input":
        return {"ready": False, "issues": [{"code": "not_a_birth_chart_input"}]}

    issues: list[dict[str, str]] = []
    birth_date = record["birthDate"]
    birth_time = record["birthTime"]
    birth_location = record["birthLocation"]

    if birth_date.get("precision") != "exact" or birth_date.get("uncertaintyDays", 0) > 0:
        issues.append({"code": "birth_date_uncertainty_requires_interval_analysis"})
    if birth_time.get("precision") != "exact" or birth_time.get("uncertaintyMinutes", 0) > 0:
        issues.append({"code": "birth_time_uncertainty_requires_interval_analysis"})
    if birth_time.get("precision") == "unknown" or not birth_time.get("localTime"):
        issues.append({"code": "birth_time_unavailable"})

    time_zone = birth_location.get("timeZone")
    if not isinstance(time_zone, str) or not time_zone.strip():
        issues.append({"code": "birth_time_zone_unavailable"})
    elif birth_location.get("precision") != "exact":
        issues.append({"code": "birth_location_or_time_zone_uncertainty"})

    if issues:
        return {"ready": False, "issues": issues}

    try:
        # Avoid ZoneInfo's process cache so the source metadata below can be
        # matched against the same current search path used for this conversion.
        zone = zoneinfo.ZoneInfo.no_cache(time_zone)
    except (ZoneInfoNotFoundError, ValueError):
        return {"ready": False, "issues": [{"code": "birth_time_zone_invalid"}]}

    wall_time = datetime.fromisoformat(f"{birth_date['date']}T{birth_time['localTime']}")
    candidates: dict[datetime, datetime] = {}
    for fold in (0, 1):
        local = wall_time.replace(tzinfo=zone, fold=fold)
        utc = local.astimezone(timezone.utc)
        round_trip = utc.astimezone(zone).replace(tzinfo=None)
        if round_trip == wall_time:
            candidates[utc] = local

    if not candidates:
        return {"ready": False, "issues": [{"code": "birth_local_time_nonexistent"}]}

    supplied_offset = birth_time.get("utcOffset")
    if isinstance(supplied_offset, str):
        parsed_offset = datetime.fromisoformat(f"2000-01-01T00:00:00{supplied_offset}").utcoffset()
        candidates = {
            utc: local for utc, local in candidates.items()
            if local.utcoffset() == parsed_offset
        }
        if not candidates:
            return {"ready": False, "issues": [{"code": "birth_utc_offset_timezone_mismatch"}]}
    if len(candidates) > 1:
        return {"ready": False, "issues": [{"code": "birth_local_time_ambiguous"}]}

    utc_instant, resolved_local = next(iter(candidates.items()))
    offset = resolved_local.utcoffset()
    assert offset is not None
    offset_seconds = int(offset.total_seconds())
    offset_sign = "+" if offset_seconds >= 0 else "-"
    offset_seconds = abs(offset_seconds)
    offset_hours, remainder = divmod(offset_seconds, 3600)
    offset_minutes, offset_seconds = divmod(remainder, 60)
    resolved_offset = f"{offset_sign}{offset_hours:02d}:{offset_minutes:02d}"
    if offset_seconds:
        resolved_offset += f":{offset_seconds:02d}"
    time_zone_database = _time_zone_database_metadata(time_zone)
    result = {
        "ready": True,
        "precision": "exact_to_supplied_clock_precision",
        "limitations": [
            "This is input normalization only; no chart or gate activation has been calculated.",
            "A local engine adapter must still preserve engine version, calculation method, and activation uncertainty.",
        ],
    }
    if not include_calculation_input:
        result["limitations"].append(
            "Readiness is not authorization; callers must check birth-input consent before using these details."
        )
    if time_zone_database["version"] == "unavailable":
        result["limitations"].append(
            "The active time-zone database version could not be identified, so this UTC normalization may not be reproducible."
        )
    if include_calculation_input:
        result["calculationInput"] = {
            "localDate": birth_date["date"],
            "localTime": birth_time["localTime"],
            "resolvedUtcOffset": resolved_offset,
            "timeZone": time_zone,
            "birthUtc": utc_instant.isoformat().replace("+00:00", "Z"),
            "timeZoneDatabase": time_zone_database,
        }
        result["limitations"].append(
            "The calculationInput contains sensitive birth timing; use it only for the authorized actions and do not reuse it for other processing."
        )
    return result


def inspect_chart_calculation_input(record: dict[str, Any]) -> dict[str, Any]:
    """Check input readiness without returning any birth date or time."""
    return _validate_preflight_result(
        _inspect_chart_calculation_input(record, include_calculation_input=False)
    )


def authorize_chart_calculation_input(
    record: dict[str, Any],
    grants: Iterable[dict[str, Any]],
    *,
    action: str = "analyze",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return normalized timing only after scoped consent authorizes its use.

    Local calculation requires `analyze`; remote calculation additionally
    requires a separate `remote_processing` grant and disclosure. This remains
    an in-memory consent preflight, not a storage or identity boundary.
    """
    if not isinstance(action, str) or action not in {"analyze", "remote_processing"}:
        raise ValueError("action must be 'analyze' or 'remote_processing'")

    readiness = _inspect_chart_calculation_input(record, include_calculation_input=False)
    if not readiness.get("ready"):
        return _validate_preflight_result({**readiness, "authorized": False, "authorizationIssues": []})

    subject_id = record.get("subjectId") if isinstance(record, dict) else None
    if not isinstance(subject_id, str) or not subject_id.strip():
        return _validate_preflight_result({
            "ready": True,
            "authorized": False,
            "authorizationIssues": [{"code": "missing_birth_input_subject"}],
        })

    grant_list = list(grants)
    if any(not validate_schema_instance(grant, "consent.schema.json").get("valid") for grant in grant_list):
        return _validate_preflight_result({
            "ready": True,
            "authorized": False,
            "authorizationIssues": [{"code": "consent_grant_schema_invalid"}],
        })

    actions = ["analyze", "remote_processing"] if action == "remote_processing" else ["analyze"]
    authorization_issues: list[dict[str, str]] = []
    for required_action in actions:
        decision = evaluate_authorization(
            [record],
            grant_list,
            subject_id=subject_id,
            purpose="symbolic_calculation",
            action=required_action,
            now=now,
        )
        if not decision.get("authorized"):
            reasons = {
                item.get("reason")
                for item in decision.get("decisions", [])
                if isinstance(item, dict) and isinstance(item.get("reason"), str)
            }
            authorization_issues.append({
                "code": f"{required_action}_not_authorized",
                "reason": ",".join(sorted(reasons)) if reasons else "no_covering_grant",
            })

    if authorization_issues:
        return _validate_preflight_result({
            "ready": True,
            "authorized": False,
            "authorizationIssues": authorization_issues,
        })

    authorized_result = _inspect_chart_calculation_input(record, include_calculation_input=True)
    return _validate_preflight_result({
        **authorized_result,
        "authorized": True,
        "authorizedActions": actions,
    })
