"""Cross-object resolution for Metheus indexes, symbolic maps, and summaries."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .authorization import evaluate_authorization
from .schema_validation import validate_record_schema, validate_schema_instance


_KIND_RECORD_TYPES = {
    "birth_chart_input": {"birth_chart_input"},
    "symbolic_map": {"symbolic_map"},
    "observation": {"observation", "event", "estimate", "symbolic_feature", "context"},
    "phase_annotation": {"phase_annotation"},
    "rhythm_summary": {"rhythm_summary"},
}
_KIND_DOMAINS = {
    "birth_chart_input": "birth_chart_inputs",
    "symbolic_map": "symbolic",
}


def _resolve_index(
    subject_index: dict[str, Any], resources: list[dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    issues: list[dict[str, str | None]] = []
    seen: set[tuple[str, str | None]] = set()

    def issue(code: str, identifier: str | None = None) -> None:
        key = (code, identifier)
        if key not in seen:
            seen.add(key)
            entry: dict[str, str | None] = {"code": code}
            if identifier is not None:
                entry["id"] = identifier
            issues.append(entry)

    if not isinstance(subject_index, dict):
        return {"valid": False, "issues": [{"code": "invalid_subject_index"}], "resolvedIds": []}, {}

    subject_id = subject_index.get("subjectId")
    if not isinstance(subject_id, str) or not subject_id.strip():
        issue("missing_index_subject")
    if subject_index.get("recordType") != "subject_index":
        issue("invalid_subject_index_type")
    schema_version = subject_index.get("schemaVersion")
    if not isinstance(schema_version, str) or not schema_version.strip():
        issue("missing_subject_index_schema_version")

    refs = subject_index.get("resourceRefs")
    if not isinstance(refs, list):
        refs = []
        issue("invalid_resource_refs")

    by_id: dict[str, dict[str, Any]] = {}
    for resource in resources:
        if not isinstance(resource, dict):
            issue("invalid_candidate_resource")
            continue
        resource_id = resource.get("id")
        if not isinstance(resource_id, str) or not resource_id:
            issue("candidate_resource_missing_id")
            continue
        if resource_id in by_id:
            issue("duplicate_candidate_resource_id", resource_id)
            continue
        by_id[resource_id] = resource

    ref_by_id: dict[str, dict[str, Any]] = {}
    resolved: dict[str, dict[str, Any]] = {}
    for ref in refs:
        if not isinstance(ref, dict):
            issue("invalid_resource_ref")
            continue
        resource_id = ref.get("id")
        kind = ref.get("kind")
        version = ref.get("schemaVersion")
        if not isinstance(resource_id, str) or not resource_id:
            issue("resource_ref_missing_id")
            continue
        if resource_id in ref_by_id:
            issue("duplicate_resource_ref_id", resource_id)
            continue
        ref_by_id[resource_id] = ref
        if not isinstance(kind, str) or kind not in _KIND_RECORD_TYPES:
            issue("unsupported_resource_kind", resource_id)
            continue
        if not isinstance(version, str) or not version.strip():
            issue("resource_ref_missing_schema_version", resource_id)
        resource = by_id.get(resource_id)
        if resource is None:
            issue("unresolved_resource_ref", resource_id)
            continue
        resolved[resource_id] = resource
        if resource.get("subjectId") != subject_id:
            issue("resource_subject_mismatch", resource_id)
        record_type = resource.get("recordType")
        if not isinstance(record_type, str) or record_type not in _KIND_RECORD_TYPES[kind]:
            issue("resource_kind_mismatch", resource_id)
        expected_domain = _KIND_DOMAINS.get(kind)
        if expected_domain is not None and resource.get("domain") != expected_domain:
            issue("resource_domain_mismatch", resource_id)
        if not isinstance(resource.get("schemaVersion"), str):
            issue("resource_missing_schema_version", resource_id)
        elif resource.get("schemaVersion") != version:
            issue("resource_schema_version_mismatch", resource_id)

    for resource_id, resource in resolved.items():
        if resource.get("recordType") == "rhythm_summary":
            measure = resource.get("summaryMeasure")
            expected_summary_shapes = {
                "bleeding_onset_intervals": ("reproductive", "metheus-bleeding-onset-gap/0.2.0"),
                "main_sleep": ("sleep", "metheus-rhythm-summary/0.2.0"),
                "meal_events": ("nutrition", "metheus-feeding-summary/0.3.0"),
                "caregiver_feeding_events": ("feeding", "metheus-feeding-summary/0.3.0"),
                "meal_timing_relative_to_wake": ("nutrition", "metheus-wake-relative-meal/0.2.0"),
            }
            if not isinstance(measure, str) or measure not in expected_summary_shapes:
                issue("rhythm_summary_unknown_measure", resource_id)
                continue
            expected_domain, expected_method = expected_summary_shapes[measure]
            if resource.get("domain") != expected_domain:
                issue("rhythm_summary_measure_domain_mismatch", resource_id)
            if (
                resource.get("id") != resource.get("summaryId")
                or resource.get("schemaVersion") != "0.1"
                or resource.get("summaryType") != "derived_rhythm_summary"
                or resource.get("epistemicClass") != "derived"
                or resource.get("methodVersion") != expected_method
            ):
                issue("rhythm_summary_metadata_mismatch", resource_id)
            input_ids = resource.get("inputRecordIds")
            if not isinstance(input_ids, list) or not all(isinstance(value, str) and value for value in input_ids):
                issue("rhythm_summary_invalid_input_record_ids", resource_id)
                continue
            if len(set(input_ids)) != len(input_ids):
                issue("rhythm_summary_duplicate_input_record_ids", resource_id)
            for input_id in input_ids:
                target = by_id.get(input_id)
                if target is None:
                    issue("rhythm_summary_dependency_unresolved", input_id)
                    continue
                if target.get("subjectId") != subject_id:
                    issue("rhythm_summary_dependency_subject_mismatch", input_id)
                if target.get("recordType") not in {"observation", "event"}:
                    issue("rhythm_summary_dependency_kind_mismatch", input_id)
                if input_id not in ref_by_id or ref_by_id[input_id].get("kind") != "observation":
                    issue("rhythm_summary_dependency_not_indexed", input_id)
                event_type = target.get("eventType")
                domain = target.get("domain")
                expected_sources = {
                    "bleeding_onset_intervals": {("bleeding_start", "reproductive")},
                    "main_sleep": {("main_sleep", "sleep")},
                    "meal_events": {("meal", "feeding"), ("meal", "nutrition")},
                    "caregiver_feeding_events": {("feeding", "feeding")},
                    "meal_timing_relative_to_wake": {
                        ("wake", "sleep"), ("wake", "circadian"),
                        ("meal", "feeding"), ("meal", "nutrition"),
                    },
                }
                if measure in expected_sources and (event_type, domain) not in expected_sources[measure]:
                    issue("rhythm_summary_dependency_measure_mismatch", input_id)
            continue
        if resource.get("recordType") != "symbolic_map":
            continue
        calculation = resource.get("calculation")
        if not isinstance(calculation, dict):
            issue("symbolic_map_missing_calculation", resource_id)
            continue
        status = calculation.get("status")
        if not isinstance(status, str) or status not in {"calculated", "partial", "illustrative"}:
            issue("symbolic_map_invalid_calculation_status", resource_id)
            status = None
        for field, expected_type, expected_kind in (
            ("inputRecordIds", "birth_chart_input", "birth_chart_input"),
            ("featureRecordIds", "symbolic_feature", "observation"),
        ):
            references = calculation.get(field)
            if not isinstance(references, list) or not all(isinstance(value, str) and value for value in references):
                issue(f"symbolic_map_invalid_{field}", resource_id)
                continue
            if len(set(references)) != len(references):
                issue(f"symbolic_map_duplicate_{field}", resource_id)
            if status in {"calculated", "partial"} and not references:
                issue(f"symbolic_map_empty_{field}", resource_id)
            for reference_id in references:
                target = by_id.get(reference_id)
                if target is None:
                    issue("symbolic_map_dependency_unresolved", reference_id)
                    continue
                if target.get("subjectId") != subject_id:
                    issue("symbolic_map_dependency_subject_mismatch", reference_id)
                if target.get("recordType") != expected_type:
                    issue("symbolic_map_dependency_kind_mismatch", reference_id)
                expected_domain = "birth_chart_inputs" if expected_type == "birth_chart_input" else "symbolic"
                if target.get("domain") != expected_domain:
                    issue("symbolic_map_dependency_domain_mismatch", reference_id)
                if reference_id not in ref_by_id or ref_by_id[reference_id].get("kind") != expected_kind:
                    issue("symbolic_map_dependency_not_indexed", reference_id)

    result = {
        "valid": not issues,
        "subjectId": subject_id if isinstance(subject_id, str) else None,
        "issues": issues,
        "resolvedIds": sorted(resolved),
    }
    return result, resolved


def resolve_subject_index(
    subject_index: dict[str, Any], resources: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Resolve index pointers and validate kind, schema version, and ownership.

    Symbolic-map calculation inputs/features and rhythm-summary source events
    must also resolve, belong to the same subject, and appear in the index under
    the expected kind. Summary measure, method, and source event/domain pairings
    receive narrow cross-object checks; this is not complete schema validation.
    The returned object contains identifiers and issue codes, not record bodies.
    Resolution does not imply authorization; use
    :func:`authorize_subject_index_resources` for a separately selected set.
    """
    resource_list = list(resources)
    result, _ = _resolve_index(subject_index, resource_list)
    return result


def authorize_subject_index_resources(
    subject_index: dict[str, Any],
    resources: Iterable[dict[str, Any]],
    selected_resource_ids: Iterable[str],
    grants: Iterable[dict[str, Any]],
    *,
    purpose: str,
    action: str = "analyze",
    now: datetime | None = None,
    recipient: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Authorize only explicitly selected index resources after resolution.

    Index membership is navigation metadata, never consent. Each selected ID
    must be listed in the index and resolve to a same-subject object with the
    declared kind and schema version. The index, indexed resources, and
    same-subject grants are checked against their schemas. Remote processing also requires a
    separate successful `analyze` decision. This is an in-memory preflight,
    not authentication or storage-boundary enforcement.
    """
    if not isinstance(purpose, str) or not purpose.strip():
        raise ValueError("purpose is required")
    if not isinstance(action, str) or action not in {"collect", "analyze", "share", "remote_processing"}:
        raise ValueError("unsupported authorization action")

    resource_list = list(resources)
    grant_list = list(grants)
    index_schema = validate_schema_instance(subject_index, "subject-index.schema.json")
    if not index_schema["valid"]:
        return {
            "authorized": False,
            "reason": "invalid_subject_index_schema",
            "schemaIssues": index_schema["issues"],
            "authorizationChecks": [],
        }
    resolution, resolved = _resolve_index(subject_index, resource_list)
    if not resolution["valid"]:
        return {
            "authorized": False,
            "reason": "invalid_subject_index_references",
            "resolution": resolution,
            "authorizationChecks": [],
        }

    invalid_schemas = []
    for resource_id, resource in resolved.items():
        validation = validate_record_schema(resource)
        if not validation["valid"]:
            invalid_schemas.append({"id": resource_id, "kind": "indexed_resource", "issues": validation["issues"]})
    subject_id = subject_index.get("subjectId")
    for grant in grant_list:
        if isinstance(grant, dict) and grant.get("subjectId") == subject_id:
            validation = validate_schema_instance(grant, "consent.schema.json")
            if not validation["valid"]:
                invalid_schemas.append({
                    "id": grant.get("id") if isinstance(grant.get("id"), str) else None,
                    "kind": "consent_grant",
                    "issues": validation["issues"],
                })
    if invalid_schemas:
        return {
            "authorized": False,
            "reason": "invalid_selected_schema",
            "schemaIssues": invalid_schemas,
            "resolution": resolution,
            "authorizationChecks": [],
        }

    if isinstance(selected_resource_ids, (str, bytes, dict)):
        return {"authorized": False, "reason": "invalid_selected_resource_ids", "resolution": resolution}
    try:
        selected_values = list(selected_resource_ids)
    except TypeError:
        return {"authorized": False, "reason": "invalid_selected_resource_ids", "resolution": resolution}
    if not selected_values or not all(isinstance(value, str) and value for value in selected_values):
        return {"authorized": False, "reason": "invalid_selected_resource_ids", "resolution": resolution}
    if len(set(selected_values)) != len(selected_values):
        return {"authorized": False, "reason": "duplicate_selected_resource_id", "resolution": resolution}
    unindexed = sorted(set(selected_values) - set(resolved))
    if unindexed:
        return {
            "authorized": False,
            "reason": "selected_resource_not_in_index",
            "unresolvedIds": unindexed,
            "resolution": resolution,
            "authorizationChecks": [],
        }

    selected_resources = [resolved[resource_id] for resource_id in selected_values]
    required_actions = ["analyze", "remote_processing"] if action == "remote_processing" else [action]
    checks = [
        evaluate_authorization(
            selected_resources,
            grant_list,
            subject_id=subject_id,
            purpose=purpose,
            action=required_action,
            now=now,
            recipient=recipient,
        )
        for required_action in required_actions
    ]
    return {
        "authorized": all(check["authorized"] for check in checks),
        "subjectId": subject_id,
        "purpose": purpose,
        "requestedAction": action,
        "selectedIds": selected_values,
        "resolution": resolution,
        "authorizationChecks": checks,
    }
