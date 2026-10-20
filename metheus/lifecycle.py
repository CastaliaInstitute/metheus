"""Revision-chain helpers for subject-scoped Metheus records."""

from __future__ import annotations

from typing import Any, Iterable


def resolve_current_records(
    records: Iterable[dict[str, Any]], *, subject_id: str
) -> dict[str, Any]:
    """Return unsuperseded records for one subject, validating visible chains.

    Callers should supply the broadest available subject history before applying
    date or domain filters. A missing predecessor is reported as a warning so a
    deliberately pruned history can still be read; duplicate IDs, branching
    revisions, malformed links, and cycles fail closed. IDs are resolved only
    inside the requested subject namespace.
    Superseded objects are not deleted or made inaccessible by this function.
    """
    if not isinstance(subject_id, str) or not subject_id.strip():
        return {"valid": False, "currentRecords": [], "supersededIds": [], "issues": [{"code": "invalid_subject_id"}]}

    supplied_records = [item for item in records if isinstance(item, dict)]
    subject_records = [
        item for item in supplied_records if item.get("subjectId") == subject_id
    ]
    by_id: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    for position, item in enumerate(subject_records):
        record_id = item.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            issues.append({"code": "invalid_record_id", "position": position})
            continue
        if record_id in by_id:
            issues.append({"code": "duplicate_record_id", "recordId": record_id})
            continue
        by_id[record_id] = item

    successors: dict[str, str] = {}
    parents: dict[str, str] = {}
    warnings: list[dict[str, Any]] = []
    for record_id, item in by_id.items():
        if "supersedes" not in item:
            continue
        predecessor_id = item["supersedes"]
        if not isinstance(predecessor_id, str) or not predecessor_id.strip():
            issues.append({"code": "invalid_supersedes_reference", "recordId": record_id})
            continue
        if predecessor_id == record_id:
            issues.append({"code": "revision_cycle", "recordId": record_id})
            continue
        predecessor = by_id.get(predecessor_id)
        if predecessor is None:
            warnings.append({"code": "superseded_record_not_in_supplied_history", "recordId": record_id})
            continue
        current_revision = item.get("revision")
        prior_revision = predecessor.get("revision")
        if (
            isinstance(current_revision, int) and not isinstance(current_revision, bool)
            and isinstance(prior_revision, int) and not isinstance(prior_revision, bool)
            and current_revision != prior_revision + 1
        ):
            issues.append({"code": "nonconsecutive_revision", "recordId": record_id})
            continue
        existing_successor = successors.get(predecessor_id)
        if existing_successor is not None and existing_successor != record_id:
            issues.append({"code": "competing_revision_successors", "recordId": predecessor_id})
            continue
        successors[predecessor_id] = record_id
        parents[record_id] = predecessor_id

    visited: set[str] = set()
    for start_id in parents:
        path: set[str] = set()
        current_id = start_id
        while current_id in parents:
            if current_id in path:
                issues.append({"code": "revision_cycle", "recordId": current_id})
                break
            if current_id in visited:
                break
            path.add(current_id)
            current_id = parents[current_id]
        visited.update(path)

    if issues:
        return {"valid": False, "currentRecords": [], "supersededIds": sorted(successors), "issues": issues, "warnings": warnings}

    superseded_ids = set(successors)
    current = [item for item in subject_records if item.get("id") not in superseded_ids]
    return {
        "valid": True,
        "currentRecords": current,
        "currentIds": [item["id"] for item in current],
        "supersededIds": sorted(superseded_ids),
        "issues": [],
        "warnings": warnings,
    }
