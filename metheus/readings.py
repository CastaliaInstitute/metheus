"""Reference-integrity checks for Metheus reflective readings.

This module checks selected in-memory inputs before a reading is presented. It
does not validate JSON Schema, authorize access, authenticate a subject, or
enforce a storage boundary.
"""

from __future__ import annotations

from typing import Any, Iterable


def validate_reading_references(
    reading: dict[str, Any],
    records: Iterable[dict[str, Any]],
    phase_annotations: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Check that reading citations resolve to selected, same-subject inputs.

    `records` and `phase_annotations` are the candidate input objects supplied
    by a trusted caller. Every reading `inputId` must resolve to exactly one of
    these objects. Claim-level source and phase references, plus phase support
    record references, must be selected by the reading and belong to its
    subject. The result contains only issue codes and identifiers.
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
        if annotation_id in phase_index:
            issue("duplicate_phase_annotation_id", annotation_id)
            continue
        phase_index[annotation_id] = annotation

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

    def check_phase_basis(phase_id: str, annotation: dict[str, Any]) -> None:
        support_ids = annotation.get("basisRecordIds", [])
        if not isinstance(support_ids, list) or not all(isinstance(x, str) and x for x in support_ids):
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

    for phase_id in selected_ids.intersection(phase_index):
        annotation = phase_index[phase_id]
        if annotation.get("subjectId") == subject_id:
            check_phase_basis(phase_id, annotation)

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

    return {"valid": not issues, "issues": issues}
