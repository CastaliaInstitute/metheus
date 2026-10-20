"""Fail-closed, in-memory evaluation of scoped Metheus consent grants.

This module evaluates policy inputs supplied by a trusted caller. It does not
authenticate subjects or grantors, validate JSON Schemas, persist audit logs,
or enforce access at a storage boundary.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


POLICY_VERSION = "metheus-consent-policy/0.1.0"

# A narrow permission may be covered by an explicit broad category for users
# who chose that scope. Reproductive, intimacy, relationship, child, and chart
# data have no broad-category fallback.
_BROAD_SCOPES: dict[str, set[str]] = {
    "circadian": {"biometrics"},
    "sleep": {"biometrics"},
    "feeding": {"nutrition_behavior"},
    "nutrition": {"nutrition_behavior"},
    "hydration": {"biometrics", "nutrition_behavior"},
    "activity": {"biometrics", "nutrition_behavior"},
    "behavior": {"nutrition_behavior"},
    "sensory_exposure": {"nutrition_behavior"},
    "supplement": {"nutrition_behavior"},
    "medication": {"clinical_results"},
    "physiology": {"biometrics"},
    "hormone_assay": {"clinical_results"},
    "symptom": {"clinical_results"},
    "development": {"child_development"},
    "symbolic": {"birth_chart_inputs"},
}

_DOMAIN_ALIASES = {"relationship": "relationships"}

_CHILD_STEWARD_ROLES = {"parent_guardian", "legally_authorized_representative"}


def _parse_instant(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if instant.tzinfo is None or instant.utcoffset() is None:
        return None
    return instant.astimezone(timezone.utc)


def _record_date(record: dict[str, Any]) -> date | None:
    time_data = record.get("time")
    if not isinstance(time_data, dict):
        return None
    if time_data.get("precision") == "date_only":
        try:
            return date.fromisoformat(time_data["date"])
        except (KeyError, TypeError, ValueError):
            return None

    instant = _parse_instant(time_data.get("observedAt") or time_data.get("start"))
    if instant is None:
        return None
    zone_name = time_data.get("timeZone")
    if isinstance(zone_name, str):
        try:
            return instant.astimezone(ZoneInfo(zone_name)).date()
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return instant.date()


def _grant_time_matches(grant: dict[str, Any], now: datetime) -> bool:
    created = _parse_instant(grant.get("createdAt"))
    if created is None or created > now:
        return False
    expires_value = grant.get("expiresAt")
    if expires_value is not None:
        expires = _parse_instant(expires_value)
        if expires is None or now >= expires:
            return False
    return True


def _time_scope_matches(grant: dict[str, Any], record: dict[str, Any]) -> bool:
    scope = grant.get("timeScope")
    if scope is None:
        return True
    if not isinstance(scope, dict):
        return False
    try:
        start = date.fromisoformat(scope["startDate"])
        end = date.fromisoformat(scope["endDate"])
    except (KeyError, TypeError, ValueError):
        return False
    if end < start:
        return False
    observed_day = _record_date(record)
    return observed_day is not None and start <= observed_day <= end


def _record_scope_matches(grant: dict[str, Any], record: dict[str, Any]) -> bool:
    record_ids = grant.get("recordIds")
    if record_ids is not None:
        if not isinstance(record_ids, list) or record.get("id") not in record_ids:
            return False
    return _time_scope_matches(grant, record)


def _covers_domain(grant_domains: Any, record_domain: Any) -> bool:
    if (
        not isinstance(grant_domains, list)
        or not all(isinstance(value, str) for value in grant_domains)
        or not isinstance(record_domain, str)
    ):
        return False
    required = _DOMAIN_ALIASES.get(record_domain, record_domain)
    return required in grant_domains or bool(_BROAD_SCOPES.get(record_domain, set()) & set(grant_domains))


def _grantor_is_usable(grant: dict[str, Any], record: dict[str, Any]) -> bool:
    grantor = grant.get("grantor")
    if not isinstance(grantor, dict):
        return False
    role = grantor.get("role")
    reference = grantor.get("reference")
    development = record.get("developmentContext", {})
    life_stage = development.get("lifeStage") if isinstance(development, dict) else None
    early_child_stages = {"prenatal", "newborn", "infancy", "early_childhood", "middle_childhood"}
    if (
        "child_development" in grant.get("domains", [])
        or life_stage in early_child_stages
        or record.get("epistemicClass") == "caregiver_reported"
    ):
        return role in _CHILD_STEWARD_ROLES
    return role == "subject" and reference == record.get("subjectId")


def _recipient_matches(grant: dict[str, Any], requested: dict[str, str] | None) -> bool:
    if requested is None:
        return False
    recipient = grant.get("recipient")
    return (
        isinstance(recipient, dict)
        and recipient.get("reference") == requested.get("reference")
        and recipient.get("role") == requested.get("role")
    )


def _inactive_grant_ids(grants: list[dict[str, Any]]) -> set[str]:
    inactive: set[str] = set()
    for grant in grants:
        status = grant.get("status")
        if status not in {"granted", "withdrawn"}:
            continue
        if status == "granted" and isinstance(grant.get("supersedes"), str):
            inactive.add(grant["supersedes"])
        if status == "withdrawn":
            values = grant.get("revokesGrantIds", [])
            if isinstance(values, list):
                inactive.update(value for value in values if isinstance(value, str))
    return inactive


def evaluate_authorization(
    records: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    subject_id: str,
    purpose: str,
    action: str,
    now: datetime | None = None,
    recipient: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Evaluate whether every selected record is covered by an active grant.

    Supported actions are `collect`, `analyze`, `share`, and
    `remote_processing`. A share requires an exact recipient reference and
    role. `records` should contain the source records used by the requested
    operation; derived outputs alone are not sufficient authorization inputs.
    The result contains only identifiers and policy reasons, not record data.
    """
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id is required")
    if not isinstance(purpose, str) or not purpose.strip():
        raise ValueError("purpose is required")
    if action not in {"collect", "analyze", "share", "remote_processing"}:
        raise ValueError("unsupported authorization action")
    evaluated_at = now or datetime.now(timezone.utc)
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("now must include a timezone")
    evaluated_at = evaluated_at.astimezone(timezone.utc)

    selected_records = list(records)
    grant_list = [grant for grant in grants if isinstance(grant, dict)]
    inactive_ids = _inactive_grant_ids(grant_list)
    decisions: list[dict[str, Any]] = []

    if not selected_records:
        return {
            "policyVersion": POLICY_VERSION,
            "subjectId": subject_id,
            "purpose": purpose,
            "action": action,
            "authorized": False,
            "decisions": [{"recordId": None, "authorized": False, "reason": "no_records_selected"}],
        }

    for record in selected_records:
        if not isinstance(record, dict):
            decisions.append({"recordId": None, "authorized": False, "reason": "invalid_record"})
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            decisions.append({"recordId": None, "authorized": False, "reason": "missing_record_id"})
            continue
        if record.get("subjectId") != subject_id:
            decisions.append({"recordId": record_id, "authorized": False, "reason": "subject_mismatch"})
            continue
        domain = record.get("domain")
        if not isinstance(domain, str):
            decisions.append({"recordId": record_id, "authorized": False, "reason": "missing_record_domain"})
            continue

        matching_grant: dict[str, Any] | None = None
        declined_grant_applies = False
        for grant in grant_list:
            grant_id = grant.get("id")
            permitted_actions = grant.get("permittedActions")
            purposes = grant.get("purposes")
            if (
                not isinstance(grant_id, str)
                or not grant_id.strip()
                or grant_id in inactive_ids
                or grant.get("subjectId") != subject_id
                or grant.get("status") != "granted"
                or not isinstance(permitted_actions, list)
                or action not in permitted_actions
                or not isinstance(purposes, list)
                or purpose not in purposes
                or not _covers_domain(grant.get("domains"), domain)
                or not _grant_time_matches(grant, evaluated_at)
                or not _grantor_is_usable(grant, record)
                or not _record_scope_matches(grant, record)
            ):
                continue
            if action in {"share", "remote_processing"} and not (grant.get("recordIds") or grant.get("timeScope")):
                continue
            if action == "share" and not _recipient_matches(grant, recipient):
                continue
            if action == "share" and not (isinstance(grant.get("scopeNote"), str) and grant["scopeNote"].strip()):
                continue
            if action == "remote_processing" and not (
                isinstance(grant.get("remoteProcessingDisclosureVersion"), str)
                and grant["remoteProcessingDisclosureVersion"].strip()
            ):
                continue
            participation = grant.get("childParticipation", {})
            if isinstance(participation, dict) and participation.get("assentState") == "asked_declined":
                declined_grant_applies = True
                continue
            matching_grant = grant
            break

        if declined_grant_applies:
            decisions.append({"recordId": record_id, "authorized": False, "reason": "child_declined_in_applicable_grant"})
        elif matching_grant is None:
            decisions.append({"recordId": record_id, "authorized": False, "reason": "no_matching_active_grant"})
        else:
            decisions.append({
                "recordId": record_id,
                "authorized": True,
                "grantId": matching_grant["id"],
                "reason": "covered_by_active_scoped_grant",
            })

    return {
        "policyVersion": POLICY_VERSION,
        "subjectId": subject_id,
        "purpose": purpose,
        "action": action,
        "authorized": all(decision["authorized"] for decision in decisions),
        "decisions": decisions,
    }
