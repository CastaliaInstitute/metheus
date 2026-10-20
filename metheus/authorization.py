"""Fail-closed, in-memory evaluation of scoped Metheus consent grants.

This module evaluates policy inputs supplied by a trusted caller. It does not
authenticate subjects or grantors, validate JSON Schemas, persist audit logs,
or enforce access at a storage boundary.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .phase_domains import phase_authorization_domain
from .rhythms import measurement_series_source_matches, measurement_series_summary_valid


POLICY_VERSION = "metheus-consent-policy/0.4.0"

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
}

_DOMAIN_ALIASES = {"relationship": "relationships"}

_RECORD_DOMAINS = {
    "birth_chart_inputs", "circadian", "sleep", "feeding", "nutrition", "hydration",
    "activity", "behavior", "learning", "sensory_exposure", "supplement", "medication",
    "physiology", "hormone_assay", "symptom", "reproductive", "development",
    "relationship", "relationships", "intimacy", "environment", "life_event", "symbolic", "other",
}
_CONSENT_DOMAINS = (_RECORD_DOMAINS - {"relationship"}) | {
    "biometrics", "clinical_results", "nutrition_behavior", "child_development",
}
_OBSERVATION_RECORD_TYPES = {"observation", "event", "estimate", "symbolic_feature", "context"}
_SUMMARY_MEASURES = {
    "bleeding_onset_intervals": ("reproductive", "metheus-bleeding-onset-gap/0.2.0"),
    "main_sleep": ("sleep", "metheus-rhythm-summary/0.2.0"),
    "meal_events": ("nutrition", "metheus-feeding-summary/0.3.0"),
    "caregiver_feeding_events": ("feeding", "metheus-feeding-summary/0.3.0"),
    "meal_timing_relative_to_wake": ("nutrition", "metheus-wake-relative-meal/0.2.0"),
    "measurement_series": (None, "metheus-numeric-measurement-series/0.1.0"),
}
_SUMMARY_SOURCE_TYPES = {
    "bleeding_onset_intervals": {("bleeding_start", "reproductive")},
    "main_sleep": {("main_sleep", "sleep")},
    "meal_events": {("meal", "feeding"), ("meal", "nutrition")},
    "caregiver_feeding_events": {("feeding", "feeding")},
    "meal_timing_relative_to_wake": {
        ("wake", "sleep"), ("wake", "circadian"),
        ("meal", "feeding"), ("meal", "nutrition"),
    },
}

_CHILD_STEWARD_ROLES = {"parent_guardian", "legally_authorized_representative"}
_PURPOSES = {
    "symbolic_calculation", "personal_reflection", "rhythm_summary", "learning_support",
    "health_record_organization", "caregiver_coordination", "clinical_sharing", "other",
}
_PERMITTED_ACTIONS = {"collect", "analyze", "share", "remote_processing"}
_CHILD_ASSENT_STATES = {
    "not_applicable", "not_asked", "asked_agreed", "asked_declined",
    "not_able_to_express", "unknown",
}


def _is_phase_annotation(record: dict[str, Any]) -> bool:
    return record.get("recordType") == "phase_annotation"


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


def _local_date(value: Any, zone_name: Any = None) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass
    instant = _parse_instant(value)
    if instant is None:
        return None
    if isinstance(zone_name, str):
        try:
            return instant.astimezone(ZoneInfo(zone_name)).date()
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return instant.date()


def _record_dates(record: dict[str, Any]) -> tuple[date, date] | None:
    # Do not let an added/malformed `time` field narrow a phase annotation's
    # authorization window; its declared phase window is authoritative.
    if "phaseSystem" in record:
        if not _is_phase_annotation(record) or record_domain(record) is None:
            return None
        window = record.get("window")
        if not isinstance(window, dict):
            return None
        kind = window.get("kind")
        zone_name = window.get("timeZone")
        start_date = _local_date(window.get("start"), zone_name)
        if start_date is None:
            return None
        if kind == "point":
            if "end" in window:
                return None
            return start_date, start_date
        if kind == "ongoing":
            # An open-ended life-stage context cannot be covered by a finite
            # date scope. A specifically record-scoped grant can still match.
            if "end" in window:
                return None
            return None
        if kind != "interval" or "end" not in window:
            return None
        end_date = _local_date(window.get("end"), zone_name)
        if end_date is None or end_date < start_date:
            return None
        return start_date, end_date

    time_data = record.get("time")
    if isinstance(time_data, dict):
        if time_data.get("precision") == "date_only":
            if any(key in time_data for key in ("observedAt", "start", "end")):
                return None
            observed = _local_date(time_data.get("date"))
            return (observed, observed) if observed is not None else None
        zone_name = time_data.get("timeZone")
        if time_data.get("observedAt") is not None:
            if "start" in time_data or "end" in time_data:
                return None
            observed = _local_date(time_data.get("observedAt"), zone_name)
            return (observed, observed) if observed is not None else None
        if time_data.get("start") is not None:
            if "end" not in time_data:
                return None
            start_date = _local_date(time_data.get("start"), zone_name)
            end_date = _local_date(time_data.get("end"), zone_name)
            if start_date is None or end_date is None or end_date < start_date:
                return None
            return start_date, end_date

    return None


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
    record_dates = _record_dates(record)
    return record_dates is not None and start <= record_dates[0] and record_dates[1] <= end


def _record_scope_matches(grant: dict[str, Any], record: dict[str, Any]) -> bool:
    record_ids = grant.get("recordIds")
    if record_ids is not None:
        if not isinstance(record_ids, list) or record.get("id") not in record_ids:
            return False
    return _time_scope_matches(grant, record)


def _covers_domain(grant_domains: Any, record_domain: Any) -> bool:
    if (
        not isinstance(grant_domains, list)
        or not grant_domains
        or not all(isinstance(value, str) and value in _CONSENT_DOMAINS for value in grant_domains)
        or not isinstance(record_domain, str)
    ):
        return False
    required = _DOMAIN_ALIASES.get(record_domain, record_domain)
    return required in grant_domains or bool(_BROAD_SCOPES.get(record_domain, set()) & set(grant_domains))


def record_domain(record: dict[str, Any]) -> str | None:
    if record.get("recordType") == "interaction_event":
        if record.get("eventKind") == "intimacy":
            return "intimacy" if record.get("domain") == "intimacy" else None
        return "relationships" if record.get("domain") == "relationship" else None
    if "phaseSystem" in record:
        if not _is_phase_annotation(record):
            return None
        return phase_authorization_domain(record.get("phaseSystem"), record.get("canonicalPhase"))
    record_type = record.get("recordType")
    domain = record.get("domain")
    if not isinstance(domain, str) or domain not in _RECORD_DOMAINS:
        return None
    if record_type == "birth_chart_input":
        return domain if domain == "birth_chart_inputs" else None
    if record_type == "symbolic_map":
        return domain if domain == "symbolic" else None
    if record_type == "rhythm_summary":
        measure = record.get("summaryMeasure")
        expected = _SUMMARY_MEASURES.get(measure) if isinstance(measure, str) else None
        if (
            expected is None
            or record.get("summaryType") != "derived_rhythm_summary"
            or record.get("epistemicClass") != "derived"
            or record.get("schemaVersion") != "0.1"
            or record.get("summaryId") != record.get("id")
            or (expected[0] is not None and domain != expected[0])
            or record.get("methodVersion") != expected[1]
            or (measure == "measurement_series" and not measurement_series_summary_valid(record))
        ):
            return None
        return domain
    if record_type in _OBSERVATION_RECORD_TYPES:
        if record_type == "symbolic_feature" and domain != "symbolic":
            return None
        if domain == "birth_chart_inputs":
            return None
        return domain
    return None


def _grantor_is_usable(grant: dict[str, Any], record: dict[str, Any]) -> bool:
    grantor = grant.get("grantor")
    if not isinstance(grantor, dict):
        return False
    role = grantor.get("role")
    reference = grantor.get("reference")
    development = record.get("developmentContext", {})
    life_stage = development.get("lifeStage") if isinstance(development, dict) else None
    early_child_stages = {"prenatal", "newborn", "infancy", "early_childhood", "middle_childhood", "adolescence"}
    if _is_phase_annotation(record) and record.get("phaseSystem") == "development":
        adult_stages = {"adulthood", "pregnancy", "postpartum", "menopause_transition", "later_life"}
        if life_stage not in adult_stages:
            return role in _CHILD_STEWARD_ROLES
    if (
        "child_development" in grant.get("domains", [])
        or life_stage in early_child_stages
        or record.get("epistemicClass") == "caregiver_reported"
    ):
        return role in _CHILD_STEWARD_ROLES
    return role == "subject" and reference == record.get("subjectId")


def _recipient_matches(grant: dict[str, Any], requested: dict[str, str] | None) -> bool:
    valid_roles = {"clinician", "educator", "caregiver", "family_member", "service_provider", "other"}
    if (
        not isinstance(requested, dict)
        or not isinstance(requested.get("reference"), str)
        or not requested["reference"].strip()
        or not isinstance(requested.get("role"), str)
        or requested["role"] not in valid_roles
    ):
        return False
    recipient = grant.get("recipient")
    return (
        isinstance(recipient, dict)
        and isinstance(recipient.get("reference"), str)
        and bool(recipient["reference"].strip())
        and isinstance(recipient.get("role"), str)
        and recipient["role"] in valid_roles
        and recipient.get("reference") == requested.get("reference")
        and recipient.get("role") == requested.get("role")
    )


def _inactive_grant_ids(grants: list[dict[str, Any]]) -> set[tuple[str, str]]:
    inactive: set[tuple[str, str]] = set()
    for grant in grants:
        subject_id = grant.get("subjectId")
        if not isinstance(subject_id, str) or not subject_id:
            continue
        status = grant.get("status")
        if status not in {"granted", "withdrawn"}:
            continue
        if status == "granted" and isinstance(grant.get("supersedes"), str):
            inactive.add((subject_id, grant["supersedes"]))
        if status == "withdrawn":
            values = grant.get("revokesGrantIds", [])
            if isinstance(values, list):
                inactive.update((subject_id, value) for value in values if isinstance(value, str))
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
    role. `records` may contain observations/events and phase annotations; for
    derived annotations, callers should include the source records in
    `basisRecordIds` as well. Every supplied item must be authorized. The result
    contains only identifiers and policy reasons, not record data.
    """
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id is required")
    if not isinstance(purpose, str) or not purpose.strip():
        raise ValueError("purpose is required")
    if purpose not in _PURPOSES:
        raise ValueError("unsupported authorization purpose")
    if not isinstance(action, str) or action not in {"collect", "analyze", "share", "remote_processing"}:
        raise ValueError("unsupported authorization action")
    evaluated_at = datetime.now(timezone.utc) if now is None else now
    if not isinstance(evaluated_at, datetime) or evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("now must include a timezone")
    evaluated_at = evaluated_at.astimezone(timezone.utc)

    selected_records = list(records)
    selected_record_id_values = [
        record.get("id") for record in selected_records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    ]
    selected_record_ids = set(selected_record_id_values)
    duplicate_record_ids = {
        record_id for record_id, count in Counter(selected_record_id_values).items() if count > 1
    }
    selected_phase_ids = {
        record.get("id") for record in selected_records
        if isinstance(record, dict) and _is_phase_annotation(record) and isinstance(record.get("id"), str)
    }
    selected_record_index = {
        record.get("id"): record
        for record in selected_records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    grant_list = [grant for grant in grants if isinstance(grant, dict)]
    inactive_ids = _inactive_grant_ids(grant_list)
    grant_identity_counts = Counter(
        (grant.get("subjectId"), grant.get("id"))
        for grant in grant_list
        if isinstance(grant.get("subjectId"), str)
        and isinstance(grant.get("id"), str)
        and grant.get("id")
    )
    ambiguous_grant_ids = {
        identity for identity, count in grant_identity_counts.items() if count > 1
    }
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
        if record_id in duplicate_record_ids:
            decisions.append({"recordId": record_id, "authorized": False, "reason": "duplicate_record_id"})
            continue
        if record.get("subjectId") != subject_id:
            decisions.append({"recordId": record_id, "authorized": False, "reason": "subject_mismatch"})
            continue
        domain = record_domain(record)
        if not isinstance(domain, str):
            decisions.append({"recordId": record_id, "authorized": False, "reason": "missing_record_domain"})
            continue
        if _is_phase_annotation(record):
            basis_ids = record.get("basisRecordIds")
            if not isinstance(basis_ids, list) or not basis_ids or not all(isinstance(value, str) and value for value in basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "missing_phase_basis_records"})
                continue
            if record_id in basis_ids:
                decisions.append({"recordId": record_id, "authorized": False, "reason": "self_referential_phase_basis"})
                continue
            if any(value not in selected_record_ids for value in basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "phase_basis_record_not_selected"})
                continue
            if any(value in selected_phase_ids for value in basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "phase_basis_must_be_source_record"})
                continue
        if record.get("recordType") == "rhythm_summary":
            basis_ids = record.get("inputRecordIds")
            if not isinstance(basis_ids, list) or not basis_ids or not all(isinstance(value, str) and value for value in basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "missing_rhythm_summary_sources"})
                continue
            if len(set(basis_ids)) != len(basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "duplicate_rhythm_summary_sources"})
                continue
            if record_id in basis_ids:
                decisions.append({"recordId": record_id, "authorized": False, "reason": "self_referential_rhythm_summary"})
                continue
            if any(value not in selected_record_ids for value in basis_ids):
                decisions.append({"recordId": record_id, "authorized": False, "reason": "rhythm_summary_source_not_selected"})
                continue
            invalid_source = False
            for value in basis_ids:
                source = selected_record_index.get(value)
                if (
                    source is None
                    or source.get("recordType") not in {"observation", "event"}
                    or source.get("subjectId") != subject_id
                    or (
                        not measurement_series_source_matches(record, source)
                        if record.get("summaryMeasure") == "measurement_series"
                        else (source.get("eventType"), source.get("domain"))
                        not in _SUMMARY_SOURCE_TYPES.get(record.get("summaryMeasure"), set())
                    )
                ):
                    invalid_source = True
                    break
            if invalid_source:
                decisions.append({"recordId": record_id, "authorized": False, "reason": "invalid_rhythm_summary_source"})
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
                or (subject_id, grant_id) in ambiguous_grant_ids
                or (subject_id, grant_id) in inactive_ids
                or grant.get("subjectId") != subject_id
                or grant.get("status") != "granted"
                or not isinstance(permitted_actions, list)
                or not permitted_actions
                or not all(isinstance(value, str) and value in _PERMITTED_ACTIONS for value in permitted_actions)
                or action not in permitted_actions
                or not isinstance(purposes, list)
                or not purposes
                or not all(isinstance(value, str) and value in _PURPOSES for value in purposes)
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
            if "childParticipation" in grant and (
                not isinstance(participation, dict)
                or (
                    "assentState" in participation
                    and participation.get("assentState") not in _CHILD_ASSENT_STATES
                )
            ):
                continue
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
