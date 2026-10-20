"""Reference-integrity checks for subject-authored experience pathways."""

from __future__ import annotations

from typing import Any, Iterable

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
