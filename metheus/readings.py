"""Reference-integrity checks for Metheus reflective readings.

This module validates selected contracts and checks their references and
consent before assembling a supplied reading. It does not generate or entailment
check claim text, authenticate a subject, or enforce a storage boundary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .authorization import evaluate_authorization, record_domain
from .resources import resolve_subject_index
from .schema_validation import validate_record_schema, validate_schema_instance


_READING_DOMAINS = {
    "birth_chart_inputs", "circadian", "sleep", "feeding", "nutrition", "hydration",
    "activity", "behavior", "learning", "sensory_exposure", "supplement", "medication",
    "physiology", "hormone_assay", "symptom", "reproductive", "development",
    "relationship", "relationships", "intimacy", "environment", "life_event", "symbolic", "other",
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


def validate_reading_references(
    reading: dict[str, Any],
    records: Iterable[dict[str, Any]],
    phase_annotations: Iterable[dict[str, Any]] = (),
    correspondences: Iterable[dict[str, Any]] = (),
    evidence_claims: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Check that reading citations resolve to selected, same-subject inputs.

    `records` and `phase_annotations` are subject-level candidate inputs.
    `correspondences` and `evidence_claims` are separately selected, non-personal
    reference catalogs. Every `inputId` and `referenceId` must resolve to the
    matching catalog; claim-level references must be selected in the reading.
    Subject-level records must belong to the reading subject. Evidence claims
    and correspondences must be eligible for the claim's permitted use. The
    result contains only issue codes and identifiers.
    """
    issues: list[dict[str, str | None]] = []
    seen_issues: set[tuple[str, str | None]] = set()

    def issue(code: str, identifier: str | None = None) -> None:
        key = (code, identifier)
        if key in seen_issues:
            return
        seen_issues.add(key)
        item = {"code": code}
        if identifier is not None:
            item["id"] = identifier
        issues.append(item)

    if not isinstance(reading, dict):
        return {"valid": False, "issues": [{"code": "invalid_reading"}]}

    subject_id = reading.get("subjectId")
    if not isinstance(subject_id, str) or not subject_id.strip():
        issue("missing_reading_subject")

    selected_value = reading.get("inputIds", [])
    if not isinstance(selected_value, list) or not all(isinstance(x, str) and x for x in selected_value):
        selected_ids: set[str] = set()
        issue("invalid_input_ids")
    else:
        selected_ids = set(selected_value)
        if len(selected_ids) != len(selected_value):
            issue("duplicate_input_id")

    reference_value = reading.get("referenceIds", [])
    if not isinstance(reference_value, list) or not all(isinstance(x, str) and x for x in reference_value):
        selected_reference_ids: set[str] = set()
        issue("invalid_reference_ids")
    else:
        selected_reference_ids = set(reference_value)
        if len(selected_reference_ids) != len(reference_value):
            issue("duplicate_reference_id")

    excluded_value = reading.get("excludedDomains", [])
    if not isinstance(excluded_value, list) or not all(
        isinstance(value, str) and value in _READING_DOMAINS for value in excluded_value
    ):
        excluded_domains: set[str] = set()
        issue("invalid_excluded_domains")
    else:
        excluded_domains = {"relationships" if value == "relationship" else value for value in excluded_value}

    record_index: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            issue("invalid_record")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            issue("missing_record_id")
            continue
        if record.get("recordType") == "phase_annotation":
            issue("phase_annotation_in_source_records", record_id)
            continue
        if record_id in record_index:
            issue("duplicate_record_id", record_id)
            continue
        record_index[record_id] = record

    phase_index: dict[str, dict[str, Any]] = {}
    for annotation in phase_annotations:
        if not isinstance(annotation, dict):
            issue("invalid_phase_annotation")
            continue
        annotation_id = annotation.get("id")
        if not isinstance(annotation_id, str) or not annotation_id:
            issue("missing_phase_annotation_id")
            continue
        if annotation.get("recordType") != "phase_annotation":
            issue("invalid_phase_annotation_type", annotation_id)
            continue
        layer = annotation.get("layer")
        if not isinstance(layer, str) or layer not in {"promethean", "epimethean"}:
            issue("invalid_phase_annotation_layer", annotation_id)
        if annotation_id in phase_index:
            issue("duplicate_phase_annotation_id", annotation_id)
            continue
        phase_index[annotation_id] = annotation

    def index_reference_catalog(
        items: Iterable[dict[str, Any]], label: str
    ) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for item in items:
            if not isinstance(item, dict):
                issue(f"invalid_{label}")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                issue(f"missing_{label}_id")
                continue
            if "subjectId" in item:
                issue(f"subject_owned_{label}_cannot_be_catalog_reference", item_id)
            if item_id in result:
                issue(f"duplicate_{label}_id", item_id)
                continue
            result[item_id] = item
        return result

    correspondence_index = index_reference_catalog(correspondences, "correspondence")
    evidence_index = index_reference_catalog(evidence_claims, "evidence_claim")

    all_catalog_ids = (
        set(record_index) | set(phase_index) |
        set(correspondence_index) | set(evidence_index)
    )
    if len(all_catalog_ids) != len(record_index) + len(phase_index) + len(correspondence_index) + len(evidence_index):
        for catalog in (record_index, phase_index, correspondence_index, evidence_index):
            for item_id in catalog:
                occurrences = sum(item_id in candidate for candidate in (
                    record_index, phase_index, correspondence_index, evidence_index
                ))
                if occurrences > 1:
                    issue("ambiguous_catalog_id", item_id)

    for input_id in selected_ids:
        matches = int(input_id in record_index) + int(input_id in phase_index)
        if matches == 0:
            issue("unresolved_input_id", input_id)
        elif matches > 1:
            issue("ambiguous_input_id", input_id)
        elif input_id in record_index and record_index[input_id].get("subjectId") != subject_id:
            issue("source_subject_mismatch", input_id)
        elif input_id in phase_index and phase_index[input_id].get("subjectId") != subject_id:
            issue("phase_annotation_subject_mismatch", input_id)
        if input_id in correspondence_index or input_id in evidence_index:
            issue("reference_item_in_subject_inputs", input_id)
        selected_resource = record_index.get(input_id) or phase_index.get(input_id)
        if selected_resource is not None:
            domain = record_domain(selected_resource)
            if not isinstance(domain, str):
                issue("selected_input_domain_unresolvable", input_id)
            else:
                canonical_domain = "relationships" if domain == "relationship" else domain
                if canonical_domain in excluded_domains:
                    issue("excluded_domain_selected", input_id)

    for reference_id in selected_reference_ids:
        matches = int(reference_id in correspondence_index) + int(reference_id in evidence_index)
        if matches == 0:
            issue("unresolved_reference_id", reference_id)
        elif matches > 1:
            issue("ambiguous_reference_id", reference_id)
        if reference_id in record_index or reference_id in phase_index:
            issue("subject_item_in_reference_ids", reference_id)

    def check_phase_basis(phase_id: str, annotation: dict[str, Any]) -> None:
        support_ids = annotation.get("basisRecordIds", [])
        if not isinstance(support_ids, list) or not support_ids or not all(isinstance(x, str) and x for x in support_ids):
            issue("invalid_phase_basis_record_ids", phase_id)
            return
        for support_id in support_ids:
            if support_id not in selected_ids:
                issue("phase_basis_record_not_selected", support_id)
            support_record = record_index.get(support_id)
            if support_record is None:
                issue("unresolved_phase_basis_record", support_id)
            elif support_record.get("subjectId") != subject_id:
                issue("phase_basis_subject_mismatch", support_id)

    def check_summary_basis(summary_id: str, summary: dict[str, Any]) -> None:
        support_ids = summary.get("inputRecordIds")
        if not isinstance(support_ids, list) or not support_ids or not all(isinstance(x, str) and x for x in support_ids):
            issue("invalid_rhythm_summary_input_record_ids", summary_id)
            return
        if len(set(support_ids)) != len(support_ids):
            issue("duplicate_rhythm_summary_input_record_ids", summary_id)
        for support_id in support_ids:
            if support_id == summary_id:
                issue("self_referential_rhythm_summary", summary_id)
            if support_id not in selected_ids:
                issue("rhythm_summary_basis_record_not_selected", support_id)
            support_record = record_index.get(support_id)
            if support_record is None:
                issue("unresolved_rhythm_summary_basis_record", support_id)
            elif support_record.get("subjectId") != subject_id:
                issue("rhythm_summary_basis_subject_mismatch", support_id)
            elif support_record.get("recordType") not in {"observation", "event"}:
                issue("invalid_rhythm_summary_basis_type", support_id)
            elif (
                support_record.get("eventType"), support_record.get("domain")
            ) not in _SUMMARY_SOURCE_TYPES.get(summary.get("summaryMeasure"), set()):
                issue("rhythm_summary_basis_measure_mismatch", support_id)

    for phase_id in selected_ids.intersection(phase_index):
        annotation = phase_index[phase_id]
        if annotation.get("subjectId") == subject_id:
            check_phase_basis(phase_id, annotation)

    for summary_id in selected_ids.intersection(record_index):
        summary = record_index[summary_id]
        if summary.get("recordType") == "rhythm_summary" and summary.get("subjectId") == subject_id:
            check_summary_basis(summary_id, summary)

    claims = reading.get("claims", [])
    if not isinstance(claims, list):
        issue("invalid_claims")
        claims = []

    for claim in claims:
        if not isinstance(claim, dict):
            issue("invalid_claim")
            continue

        source_ids = claim.get("sourceIds", [])
        if not isinstance(source_ids, list) or not all(isinstance(x, str) and x for x in source_ids):
            issue("invalid_claim_source_ids")
            source_ids = []
        for source_id in source_ids:
            if source_id not in selected_ids:
                issue("claim_source_not_selected", source_id)
            source_record = record_index.get(source_id)
            if source_record is None:
                issue("unresolved_claim_source", source_id)
            elif source_record.get("subjectId") != subject_id:
                issue("source_subject_mismatch", source_id)

        phase_ids = claim.get("phaseAnnotationIds", [])
        if not isinstance(phase_ids, list) or not all(isinstance(x, str) and x for x in phase_ids):
            issue("invalid_phase_annotation_ids")
            phase_ids = []
        resolved_phases: list[dict[str, Any]] = []
        for phase_id in phase_ids:
            if phase_id not in selected_ids:
                issue("phase_annotation_not_selected", phase_id)
            annotation = phase_index.get(phase_id)
            if annotation is None:
                issue("unresolved_phase_annotation", phase_id)
                continue
            if annotation.get("subjectId") != subject_id:
                issue("phase_annotation_subject_mismatch", phase_id)
            else:
                check_phase_basis(phase_id, annotation)
                resolved_phases.append(annotation)

        if resolved_phases:
            claim_type = claim.get("claimType")
            layers = {
                annotation.get("layer") for annotation in resolved_phases
                if isinstance(annotation.get("layer"), str)
            }
            if claim_type == "symbolic_prompt" and layers != {"promethean"}:
                for phase_id in phase_ids:
                    annotation = phase_index.get(phase_id)
                    if annotation is not None and annotation.get("layer") != "promethean":
                        issue("symbolic_prompt_requires_promethean_phase", phase_id)
            if isinstance(claim_type, str) and claim_type in {"observation", "estimate", "hypothesis"} and "promethean" in layers:
                for phase_id in phase_ids:
                    annotation = phase_index.get(phase_id)
                    if annotation is not None and annotation.get("layer") == "promethean":
                        issue("lived_claim_cannot_use_promethean_phase", phase_id)
            if claim_type == "observation":
                for phase_id in phase_ids:
                    annotation = phase_index.get(phase_id)
                    if annotation is not None and annotation.get("layer") == "epimethean" and annotation.get("basis") == "derived":
                        issue("observation_requires_reported_or_observed_phase", phase_id)
            if claim_type == "estimate":
                for phase_id in phase_ids:
                    annotation = phase_index.get(phase_id)
                    if annotation is not None and annotation.get("layer") == "epimethean" and annotation.get("basis") != "derived":
                        issue("estimate_requires_derived_phase", phase_id)
            if claim_type == "hypothesis":
                if not source_ids:
                    issue("phase_hypothesis_requires_subject_sources")

        correspondence_ids = claim.get("correspondenceIds", [])
        if not isinstance(correspondence_ids, list) or not all(isinstance(x, str) and x for x in correspondence_ids):
            issue("invalid_correspondence_ids")
            correspondence_ids = []
        for correspondence_id in correspondence_ids:
            if correspondence_id not in selected_reference_ids:
                issue("correspondence_not_selected", correspondence_id)
            correspondence = correspondence_index.get(correspondence_id)
            if correspondence is None:
                issue("unresolved_correspondence", correspondence_id)
                continue
            if correspondence.get("permittedUse") != "optional_reflective_prompt":
                issue("correspondence_not_permitted_in_reading", correspondence_id)
            if claim.get("claimType") not in {"symbolic_prompt", "interpretive_question"}:
                issue("correspondence_claim_type_not_permitted", correspondence_id)
            if correspondence.get("relationType") not in {"tradition_attributed", "reflective_association"}:
                issue("invalid_correspondence_relation_type", correspondence_id)
            if not isinstance(correspondence.get("claimText"), str) or not correspondence["claimText"].strip():
                issue("correspondence_missing_claim_text", correspondence_id)
            if not isinstance(correspondence.get("limitations"), list) or not correspondence["limitations"]:
                issue("correspondence_missing_limitations", correspondence_id)
            if correspondence.get("relationType") == "tradition_attributed" and not correspondence.get("sourceCitations"):
                issue("tradition_correspondence_missing_citation", correspondence_id)

        evidence_ids = claim.get("evidenceClaimIds", [])
        if not isinstance(evidence_ids, list) or not all(isinstance(x, str) and x for x in evidence_ids):
            issue("invalid_evidence_claim_ids")
            evidence_ids = []
        for evidence_id in evidence_ids:
            if evidence_id not in selected_reference_ids:
                issue("evidence_claim_not_selected", evidence_id)
            evidence_claim = evidence_index.get(evidence_id)
            if evidence_claim is None:
                issue("unresolved_evidence_claim", evidence_id)
                continue
            status = evidence_claim.get("evidenceStatus")
            permitted_use = evidence_claim.get("permittedUse")
            if status not in {"supported_for_scope", "not_supported", "conflicting"}:
                issue("evidence_claim_not_reviewed", evidence_id)
            if status in {"not_supported", "conflicting"} and claim.get("claimType") != "boundary":
                issue("unsupported_evidence_requires_boundary_claim", evidence_id)
            if permitted_use not in {"educational_context", "reading_boundary"}:
                issue("evidence_claim_not_permitted_in_reading", evidence_id)
            if not isinstance(evidence_claim.get("claimText"), str) or not evidence_claim["claimText"].strip():
                issue("evidence_claim_missing_text", evidence_id)
            scope = evidence_claim.get("scope")
            if not isinstance(scope, dict) or not isinstance(scope.get("description"), str) or not scope["description"].strip():
                issue("evidence_claim_missing_scope", evidence_id)
            if not isinstance(evidence_claim.get("sourceCitations"), list) or not evidence_claim["sourceCitations"]:
                issue("evidence_claim_missing_citations", evidence_id)
            if not isinstance(evidence_claim.get("limitations"), list) or not evidence_claim["limitations"]:
                issue("evidence_claim_missing_limitations", evidence_id)
            if not isinstance(evidence_claim.get("reviewedAt"), str) or not evidence_claim["reviewedAt"].strip():
                issue("evidence_claim_missing_review_date", evidence_id)
            if not isinstance(evidence_claim.get("reviewerRole"), str) or not evidence_claim["reviewerRole"].strip():
                issue("evidence_claim_missing_reviewer_role", evidence_id)
            if claim.get("claimType") not in {"hypothesis", "boundary"}:
                issue("evidence_claim_type_not_permitted", evidence_id)
            if permitted_use == "reading_boundary" and claim.get("claimType") != "boundary":
                issue("evidence_boundary_requires_boundary_claim", evidence_id)
            if claim.get("claimType") == "hypothesis" and not source_ids:
                issue("evidence_hypothesis_requires_subject_sources", evidence_id)

    return {"valid": not issues, "issues": issues}


def authorize_reading_inputs(
    reading: dict[str, Any],
    records: Iterable[dict[str, Any]],
    phase_annotations: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    action: str = "analyze",
    now: datetime | None = None,
    correspondences: Iterable[dict[str, Any]] = (),
    evidence_claims: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Preflight selected reading inputs for reference integrity and consent.

    `action` may be `analyze` or `remote_processing`. Remote processing also
    requires a separate successful `analyze` authorization. Only personal
    objects named by the reading's `inputIds` are sent to the consent evaluator.
    Correspondence and evidence reference catalogs are resolved separately and
    are not treated as subject records requiring the subject's consent. This is
    an in-memory preflight. The reading, selected resources, same-subject
    grants, and selected references are schema-validated before authorization;
    this is not an authentication or storage access boundary.
    """
    if not isinstance(action, str) or action not in {"analyze", "remote_processing"}:
        raise ValueError("action must be 'analyze' or 'remote_processing'")
    if not isinstance(reading, dict):
        return {"authorized": False, "reason": "invalid_reading"}

    reading_schema = validate_schema_instance(reading, "reading.schema.json")
    if not reading_schema["valid"]:
        return {
            "authorized": False,
            "reason": "invalid_reading_schema",
            "schemaIssues": reading_schema["issues"],
            "authorizationChecks": [],
        }

    record_list = list(records)
    phase_list = list(phase_annotations)
    correspondence_list = list(correspondences)
    evidence_list = list(evidence_claims)
    grant_list = list(grants)
    subject_id = reading.get("subjectId")
    selected_ids = set(reading.get("inputIds", []))
    selected_references = set(reading.get("referenceIds", []))

    invalid_objects: list[dict[str, Any]] = []
    selected_resources = [
        item for item in [*record_list, *phase_list]
        if isinstance(item, dict) and item.get("id") in selected_ids
    ]
    for resource in selected_resources:
        validation = validate_record_schema(resource)
        if not validation["valid"]:
            invalid_objects.append({
                "id": resource.get("id"),
                "kind": "subject_input",
                "issues": validation["issues"],
            })
    for grant in grant_list:
        if isinstance(grant, dict) and grant.get("subjectId") == subject_id:
            validation = validate_schema_instance(grant, "consent.schema.json")
            if not validation["valid"]:
                invalid_objects.append({
                    "id": grant.get("id") if isinstance(grant.get("id"), str) else None,
                    "kind": "consent_grant",
                    "issues": validation["issues"],
                })
    for reference_id in selected_references:
        correspondence = next((item for item in correspondence_list if isinstance(item, dict) and item.get("id") == reference_id), None)
        evidence = next((item for item in evidence_list if isinstance(item, dict) and item.get("id") == reference_id), None)
        if correspondence is not None:
            validation = validate_schema_instance(correspondence, "correspondence.schema.json")
            if not validation["valid"]:
                invalid_objects.append({"id": reference_id, "kind": "correspondence", "issues": validation["issues"]})
        if evidence is not None:
            validation = validate_schema_instance(evidence, "evidence-claim.schema.json")
            if not validation["valid"]:
                invalid_objects.append({"id": reference_id, "kind": "evidence_claim", "issues": validation["issues"]})
    if invalid_objects:
        return {
            "authorized": False,
            "reason": "invalid_selected_schema",
            "schemaIssues": invalid_objects,
            "authorizationChecks": [],
        }

    reference_check = validate_reading_references(
        reading,
        record_list,
        phase_list,
        correspondence_list,
        evidence_list,
    )
    if not reference_check["valid"]:
        return {
            "authorized": False,
            "reason": "invalid_reading_references",
            "referenceIssues": reference_check["issues"],
            "authorizationChecks": [],
        }

    purpose = reading.get("purpose")
    if not isinstance(subject_id, str) or not subject_id.strip():
        return {"authorized": False, "reason": "missing_reading_subject", "authorizationChecks": []}
    if not isinstance(purpose, str) or not purpose.strip():
        return {"authorized": False, "reason": "missing_reading_purpose", "authorizationChecks": []}

    selected_items = selected_resources
    required_actions = ["analyze"]
    if action == "remote_processing":
        required_actions.append("remote_processing")

    checks = [
        evaluate_authorization(
            selected_items,
            grant_list,
            subject_id=subject_id,
            purpose=purpose,
            action=required_action,
            now=now,
        )
        for required_action in required_actions
    ]
    return {
        "authorized": all(check["authorized"] for check in checks),
        "subjectId": subject_id,
        "purpose": purpose,
        "requestedAction": action,
        "referenceCheck": {"valid": True, "issues": []},
        "authorizationChecks": checks,
    }


def preflight_subject_reading(
    reading: dict[str, Any],
    subject_index: dict[str, Any],
    resources: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    action: str = "analyze",
    now: datetime | None = None,
    correspondences: Iterable[dict[str, Any]] = (),
    evidence_claims: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Preflight a reading against one subject index and its consent grants.

    Every `inputId` must be both indexed and resolved. The existing reading
    reference/consent checks then enforce citations, exclusions, and grants for
    those selected inputs. Index membership never widens the reading selection.
    This function returns a presentation preflight only: callers must still
    enforce storage authorization at a trusted data boundary.
    """
    if not isinstance(reading, dict):
        return {"authorized": False, "preflightPassed": False, "reason": "invalid_reading"}

    resource_list = list(resources)
    index_schema = validate_schema_instance(subject_index, "subject-index.schema.json")
    if not index_schema["valid"]:
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "invalid_subject_index_schema",
            "schemaIssues": index_schema["issues"],
        }
    resolution = resolve_subject_index(subject_index, resource_list)
    if not resolution["valid"]:
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "invalid_subject_index_references",
            "resolution": resolution,
        }

    resource_index = {
        resource.get("id"): resource
        for resource in resource_list
        if isinstance(resource, dict) and isinstance(resource.get("id"), str)
    }
    invalid_indexed_resources = []
    for resource_id in resolution["resolvedIds"]:
        resource = resource_index.get(resource_id)
        validation = validate_record_schema(resource)
        if not validation["valid"]:
            invalid_indexed_resources.append({
                "id": resource_id,
                "issues": validation["issues"],
            })
    if invalid_indexed_resources:
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "invalid_indexed_resource_schema",
            "schemaIssues": invalid_indexed_resources,
            "resolution": resolution,
        }

    subject_id = reading.get("subjectId")
    if subject_id != subject_index.get("subjectId"):
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "reading_subject_index_mismatch",
            "resolution": resolution,
        }

    input_ids = reading.get("inputIds", [])
    if not isinstance(input_ids, list) or not all(isinstance(value, str) and value for value in input_ids):
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "invalid_reading_input_ids",
            "resolution": resolution,
        }
    unindexed_ids = sorted(set(input_ids) - set(resolution["resolvedIds"]))
    if unindexed_ids:
        return {
            "authorized": False,
            "preflightPassed": False,
            "reason": "reading_input_not_indexed",
            "unindexedIds": unindexed_ids,
            "resolution": resolution,
        }

    records = [
        resource for resource in resource_list
        if isinstance(resource, dict) and resource.get("recordType") != "phase_annotation"
    ]
    phases = [
        resource for resource in resource_list
        if isinstance(resource, dict) and resource.get("recordType") == "phase_annotation"
    ]
    authorization = authorize_reading_inputs(
        reading,
        records,
        phases,
        grants,
        action=action,
        now=now,
        correspondences=correspondences,
        evidence_claims=evidence_claims,
    )
    return {
        "authorized": authorization.get("authorized", False),
        "preflightPassed": authorization.get("authorized", False),
        "readingId": reading.get("id"),
        "subjectId": subject_id,
        "resolution": resolution,
        "authorization": authorization,
    }


def assemble_reading(
    reading: dict[str, Any],
    subject_index: dict[str, Any],
    resources: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    action: str = "analyze",
    now: datetime | None = None,
    correspondences: Iterable[dict[str, Any]] = (),
    evidence_claims: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Assemble an authorized reading into typed, provenance-carrying claims.

    This deterministic renderer preserves supplied claim text; it does not
    generate or verify that text. Input contracts are schema-validated during
    preflight and the assembled package is checked against its output schema.
    The result is still an in-memory prototype, not a storage authorization
    boundary or a text-entailment check.
    """
    resource_list = list(resources)
    correspondence_list = list(correspondences)
    evidence_list = list(evidence_claims)
    preflight = preflight_subject_reading(
        reading,
        subject_index,
        resource_list,
        grants,
        action=action,
        now=now,
        correspondences=correspondence_list,
        evidence_claims=evidence_list,
    )
    if not preflight.get("preflightPassed"):
        return {
            "assembled": False,
            "reason": preflight.get("reason", "reading_preflight_failed"),
            "preflight": preflight,
        }

    if not isinstance(reading.get("id"), str) or not isinstance(reading.get("claims"), list):
        return {
            "assembled": False,
            "reason": "reading_missing_assembly_fields",
            "preflight": preflight,
        }

    selected_ids = set(reading.get("inputIds", []))
    selected_refs = set(reading.get("referenceIds", []))
    record_index = {
        item.get("id"): item for item in resource_list
        if isinstance(item, dict) and isinstance(item.get("id"), str)
        and item.get("recordType") != "phase_annotation"
    }
    source_fields = (
        "id", "recordType", "eventType", "domain", "label", "epistemicClass",
        "time", "source", "methodDetails", "uncertainty", "limitations",
        "schemaVersion", "summaryType", "summaryMeasure", "methodVersion",
        "window", "inputRecordIds", "supersedes",
    )
    phase_index = {
        item.get("id"): item for item in resource_list
        if isinstance(item, dict) and isinstance(item.get("id"), str)
        and item.get("recordType") == "phase_annotation"
    }
    correspondence_index = {
        item.get("id"): item for item in correspondence_list
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    evidence_index = {
        item.get("id"): item for item in evidence_list
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    assembled_claims: list[dict[str, Any]] = []
    for position, claim in enumerate(reading["claims"], start=1):
        if not isinstance(claim, dict):
            return {
                "assembled": False,
                "reason": "invalid_claim_shape",
                "claimPosition": position,
                "preflight": preflight,
            }
        if not isinstance(claim.get("claimType"), str) or not isinstance(claim.get("text"), str):
            return {
                "assembled": False,
                "reason": "claim_missing_type_or_text",
                "claimPosition": position,
                "preflight": preflight,
            }
        source_ids = claim.get("sourceIds", [])
        phase_ids = claim.get("phaseAnnotationIds", [])
        correspondence_ids = claim.get("correspondenceIds", [])
        evidence_ids = claim.get("evidenceClaimIds", [])
        if not all(isinstance(values, list) for values in (
            source_ids, phase_ids, correspondence_ids, evidence_ids
        )):
            return {
                "assembled": False,
                "reason": "invalid_claim_reference_shape",
                "claimPosition": position,
                "preflight": preflight,
            }

        phases = []
        for phase_id in phase_ids:
            annotation = phase_index.get(phase_id)
            if annotation is not None:
                phase_entry = {
                    "id": phase_id,
                    "layer": annotation.get("layer"),
                    "phaseSystem": annotation.get("phaseSystem"),
                    "canonicalPhase": annotation.get("canonicalPhase"),
                    "window": annotation.get("window"),
                    "basis": annotation.get("basis"),
                    "interpretation": annotation.get("interpretation"),
                    "basisRecordIds": annotation.get("basisRecordIds", []),
                    "method": annotation.get("method"),
                    "uncertainty": annotation.get("uncertainty"),
                    "limitations": annotation.get("limitations", []),
                }
                for optional_field in (
                    "evocativeName", "description", "sourceSystem", "nameSource",
                    "methodVersion", "supersedes",
                ):
                    if optional_field in annotation:
                        phase_entry[optional_field] = annotation[optional_field]
                phases.append(phase_entry)

        claim_refs = []
        for reference_id in correspondence_ids:
            correspondence = correspondence_index.get(reference_id)
            if correspondence is not None and reference_id in selected_refs:
                claim_refs.append({
                    "id": reference_id,
                    "kind": "correspondence",
                    "claimText": correspondence.get("claimText"),
                    "sourceCitations": correspondence.get("sourceCitations", []),
                    "limitations": correspondence.get("limitations", []),
                })
        for reference_id in evidence_ids:
            evidence = evidence_index.get(reference_id)
            if evidence is not None and reference_id in selected_refs:
                claim_refs.append({
                    "id": reference_id,
                    "kind": "evidence_claim",
                    "claimText": evidence.get("claimText"),
                    "evidenceStatus": evidence.get("evidenceStatus"),
                    "scope": evidence.get("scope"),
                    "sourceCitations": evidence.get("sourceCitations", []),
                    "limitations": evidence.get("limitations", []),
                })

        sources = []
        for source_id in source_ids:
            source = record_index.get(source_id)
            if source is None:
                continue
            source_entry = {key: source[key] for key in source_fields if key in source}
            if source.get("recordType") == "rhythm_summary":
                summary_metadata = {
                    "id", "summaryId", "subjectId", "recordType", "schemaVersion",
                    "summaryType", "summaryMeasure", "epistemicClass", "domain", "label",
                }
                source_entry["derivedSummary"] = {
                    key: value for key, value in source.items() if key not in summary_metadata
                }
            sources.append(source_entry)

        assembled_claims.append({
            "position": position,
            "claimType": claim.get("claimType"),
            "text": claim.get("text"),
            "sourceIds": [source_id for source_id in source_ids if source_id in selected_ids],
            "sources": sources,
            "phaseAnnotations": phases,
            "references": claim_refs,
            "support": claim.get("support"),
        })

    provenance_issues = []
    for index, (claim, rendered) in enumerate(zip(reading["claims"], assembled_claims), start=1):
        expected_source_ids = [value for value in claim.get("sourceIds", []) if value in selected_ids]
        expected_phase_ids = claim.get("phaseAnnotationIds", [])
        expected_reference_ids = [
            *claim.get("correspondenceIds", []),
            *claim.get("evidenceClaimIds", []),
        ]
        if rendered["sourceIds"] != expected_source_ids or [item["id"] for item in rendered["sources"]] != expected_source_ids:
            provenance_issues.append({"claimPosition": index, "field": "sourceIds"})
        if [item["id"] for item in rendered["phaseAnnotations"]] != expected_phase_ids:
            provenance_issues.append({"claimPosition": index, "field": "phaseAnnotationIds"})
        if [item["id"] for item in rendered["references"]] != expected_reference_ids:
            provenance_issues.append({"claimPosition": index, "field": "referenceIds"})
    if provenance_issues:
        return {
            "assembled": False,
            "reason": "assembly_provenance_mismatch",
            "provenanceIssues": provenance_issues,
            "preflight": preflight,
        }

    assembled_output = {
        "assembled": True,
        "readingId": reading["id"],
        "subjectId": reading.get("subjectId"),
        "version": reading.get("version"),
        "purpose": reading.get("purpose"),
        "question": reading.get("question"),
        "timeWindow": reading.get("timeWindow"),
        "claims": assembled_claims,
        "limitations": reading.get("limitations", []),
        "assembly": {
            "kind": "deterministic_claim_assembly",
            "sourceTextGenerated": False,
            "textEntailmentVerified": False,
            "inputSchemasValidated": True,
            "outputSchemaValidated": True,
            "authorizedAction": action,
        },
    }
    output_validation = validate_schema_instance(assembled_output, "assembled-reading.schema.json")
    if not output_validation["valid"]:
        return {
            "assembled": False,
            "reason": "invalid_assembled_output_schema",
            "schemaIssues": output_validation["issues"],
            "preflight": preflight,
        }
    return assembled_output
