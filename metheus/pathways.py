"""Reference-integrity checks for subject-authored experience pathways."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .resources import authorize_subject_index_resources
from .schema_validation import validate_record_schema, validate_schema_instance


def validate_experience_pathway_references(
    pathway: dict[str, Any],
    records: Iterable[dict[str, Any]],
    evidence_claims: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Check pathway schema, source-record ownership, and evidence references.

    This is an in-memory integrity check only. It does not authorize, select,
    render, or analyze records; callers must perform the appropriate consent
    preflight before using any referenced personal record. Candidate evidence
    claims may be resolved here even when they are internal-only; this function
    does not make them eligible for readings or establish their scientific
    quality. The result contains IDs and issue codes, never source record text.
    """
    issues: list[dict[str, str]] = []
    seen_issues: set[tuple[str, str]] = set()

    def issue(code: str, identifier: str | None = None) -> None:
        key = (code, identifier or "")
        if key in seen_issues:
            return
        seen_issues.add(key)
        item = {"code": code}
        if identifier is not None:
            item["id"] = identifier
        issues.append(item)

    if not isinstance(pathway, dict):
        return {"valid": False, "issues": [{"code": "invalid_pathway_shape"}]}

    schema_check = validate_schema_instance(pathway, "experience-pathway.schema.json")
    if not schema_check["valid"]:
        issue("invalid_pathway_schema")

    subject_id = pathway.get("subjectId")
    if not isinstance(subject_id, str) or not subject_id:
        issue("missing_pathway_subject")

    record_index: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            issue("invalid_source_record")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            issue("source_record_missing_id")
            continue
        if record_id in record_index:
            issue("duplicate_source_record_id", record_id)
            continue
        record_index[record_id] = record

    evidence_index: dict[str, dict[str, Any]] = {}
    for claim in evidence_claims:
        if not isinstance(claim, dict):
            issue("invalid_evidence_claim")
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            issue("evidence_claim_missing_id")
            continue
        if claim_id in evidence_index:
            issue("duplicate_evidence_claim_id", claim_id)
            continue
        evidence_index[claim_id] = claim

    resolved_record_ids: set[str] = set()
    resolved_evidence_ids: set[str] = set()

    nodes = pathway.get("nodes", [])
    node_index: dict[str, dict[str, Any]] = {}
    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, dict):
            continue
        node_id = node.get("nodeId")
        if not isinstance(node_id, str) or not node_id:
            issue("pathway_node_missing_id")
            continue
        if node_id in node_index:
            issue("duplicate_pathway_node_id", node_id)
            continue
        node_index[node_id] = node

    relations = pathway.get("relations", [])
    seen_relation_ids: set[str] = set()
    for relation in relations if isinstance(relations, list) else []:
        if not isinstance(relation, dict):
            continue
        relation_id = relation.get("relationId")
        if not isinstance(relation_id, str) or not relation_id:
            issue("pathway_relation_missing_id")
        elif relation_id in seen_relation_ids:
            issue("duplicate_pathway_relation_id", relation_id)
        else:
            seen_relation_ids.add(relation_id)
        for endpoint_name in ("fromNodeId", "toNodeId"):
            endpoint_id = relation.get(endpoint_name)
            if not isinstance(endpoint_id, str) or endpoint_id not in node_index:
                issue("unresolved_pathway_node_reference", endpoint_id if isinstance(endpoint_id, str) else None)

    def resolve_record_reference(record_id: Any) -> None:
        if not isinstance(record_id, str) or not record_id:
            issue("invalid_pathway_source_reference")
            return
        record = record_index.get(record_id)
        if record is None:
            issue("unresolved_pathway_source_reference", record_id)
            return
        if record.get("subjectId") != subject_id:
            issue("pathway_source_subject_mismatch", record_id)
            return
        if not validate_record_schema(record)["valid"]:
            issue("invalid_pathway_source_record", record_id)
            return
        resolved_record_ids.add(record_id)

    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, dict):
            continue
        source_ids = node.get("basisRecordIds", [])
        for record_id in source_ids if isinstance(source_ids, list) else []:
            resolve_record_reference(record_id)

    for relation in relations if isinstance(relations, list) else []:
        if not isinstance(relation, dict):
            continue
        source_ids = relation.get("basisRecordIds", [])
        for record_id in source_ids if isinstance(source_ids, list) else []:
            resolve_record_reference(record_id)
        evidence_ids = relation.get("evidenceClaimIds", [])
        for claim_id in evidence_ids if isinstance(evidence_ids, list) else []:
            if not isinstance(claim_id, str) or not claim_id:
                issue("invalid_pathway_evidence_reference")
                continue
            claim = evidence_index.get(claim_id)
            if claim is None:
                issue("unresolved_pathway_evidence_reference", claim_id)
                continue
            claim_check = validate_schema_instance(claim, "evidence-claim.schema.json")
            if not claim_check["valid"]:
                issue("invalid_pathway_evidence_claim", claim_id)
                continue
            resolved_evidence_ids.add(claim_id)

    return {
        "valid": not issues,
        "pathwayId": pathway.get("id") if isinstance(pathway.get("id"), str) else None,
        "subjectId": subject_id if isinstance(subject_id, str) else None,
        "resolvedRecordIds": sorted(resolved_record_ids),
        "resolvedEvidenceClaimIds": sorted(resolved_evidence_ids),
        "issues": issues,
    }


def preflight_experience_pathway_sources(
    pathway: dict[str, Any],
    subject_index: dict[str, Any],
    resources: Iterable[dict[str, Any]],
    selected_source_ids: Iterable[str],
    grants: Iterable[dict[str, Any]],
    *,
    purpose: str,
    evidence_claims: Iterable[dict[str, Any]] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    """Check that every pathway source is explicitly selected and authorized.

    `resources` must include the subject index's complete indexed resource set
    because index resolution checks every pointer. Pass all evidence claims
    cited by the graph in `evidence_claims`; candidate status remains unchanged
    by validation. When personal source records are referenced, this preflight
    supports local `analyze` authorization for those records. The caller must
    explicitly select exactly the source IDs referenced by the graph. Remote
    processing, sharing, storage, and authorization of the pathway artifact
    itself are outside this helper.
    """
    if not isinstance(pathway, dict):
        return {"sourceRecordsAuthorized": False, "reason": "invalid_pathway_shape"}
    if not isinstance(purpose, str) or not purpose.strip():
        return {"sourceRecordsAuthorized": False, "reason": "invalid_purpose"}

    resource_list = list(resources)
    grant_list = list(grants)
    evidence_list = list(evidence_claims)
    integrity = validate_experience_pathway_references(pathway, resource_list, evidence_list)
    if not integrity["valid"]:
        return {
            "sourceRecordsAuthorized": False,
            "reason": "invalid_pathway_references",
            "integrity": integrity,
        }

    subject_id = pathway.get("subjectId")
    if not isinstance(subject_index, dict):
        return {"sourceRecordsAuthorized": False, "reason": "invalid_subject_index", "integrity": integrity}
    index_schema = validate_schema_instance(subject_index, "subject-index.schema.json")
    if not index_schema["valid"]:
        return {
            "sourceRecordsAuthorized": False,
            "reason": "invalid_subject_index_schema",
            "integrity": integrity,
        }
    if subject_index.get("subjectId") != subject_id:
        return {
            "sourceRecordsAuthorized": False,
            "reason": "pathway_subject_index_mismatch",
            "integrity": integrity,
        }

    selected_values: list[str]
    if isinstance(selected_source_ids, (str, bytes, dict)):
        return {"sourceRecordsAuthorized": False, "reason": "invalid_selected_source_ids", "integrity": integrity}
    try:
        selected_values = list(selected_source_ids)
    except TypeError:
        return {"sourceRecordsAuthorized": False, "reason": "invalid_selected_source_ids", "integrity": integrity}
    if not all(isinstance(value, str) and value for value in selected_values):
        return {"sourceRecordsAuthorized": False, "reason": "invalid_selected_source_ids", "integrity": integrity}
    if len(set(selected_values)) != len(selected_values):
        return {"sourceRecordsAuthorized": False, "reason": "duplicate_selected_source_id", "integrity": integrity}

    referenced_ids = set(integrity["resolvedRecordIds"])
    selected_ids = set(selected_values)
    if selected_ids != referenced_ids:
        return {
            "sourceRecordsAuthorized": False,
            "reason": "selected_source_ids_must_match_pathway_references",
            "unselectedReferenceIds": sorted(referenced_ids - selected_ids),
            "unreferencedSelectedIds": sorted(selected_ids - referenced_ids),
            "integrity": integrity,
        }

    if not referenced_ids:
        return {
            "sourceRecordsAuthorized": None,
            "pathwayId": integrity.get("pathwayId"),
            "subjectId": subject_id,
            "sourceAuthorization": {"authorized": None, "reason": "no_personal_source_records_referenced"},
            "integrity": integrity,
            "limitations": [
                "This preflight does not authorize the pathway artifact itself or authorize storage or remote processing."
            ],
        }

    authorization = authorize_subject_index_resources(
        subject_index,
        resource_list,
        selected_values,
        grant_list,
        purpose=purpose,
        action="analyze",
        now=now,
    )
    return {
        "sourceRecordsAuthorized": bool(authorization.get("authorized")),
        "pathwayId": integrity.get("pathwayId"),
        "subjectId": subject_id,
        "sourceAuthorization": authorization,
        "integrity": integrity,
        "limitations": [
            "This preflight authorizes only the explicitly referenced source records for local analysis.",
            "It does not authorize the pathway artifact itself, remote processing, sharing, storage, or access at a service boundary.",
        ],
    }
