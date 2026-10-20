"""Consent preflight for explicitly selected, separately authored interaction records."""

from __future__ import annotations

from datetime import datetime
from itertools import islice
import re
from typing import Any, Iterable

from .authorization import evaluate_authorization
from .lifecycle import resolve_current_records
from .resources import resolve_subject_index
from .schema_validation import validate_record_schema, validate_schema_instance


def authorize_multi_party_interaction_records(
    records: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    interaction_group_id: str,
    selected_record_ids: Iterable[str],
    subject_indexes: Iterable[dict[str, Any]],
    purpose: str,
    action: str = "analyze",
    now: datetime | None = None,
    recipient: dict[str, str] | None = None,
    max_records: int = 20,
) -> dict[str, Any]:
    """Require separate authorization from every represented record owner.

    This checks explicitly selected, current, indexed interaction-event
    records that share one opaque group token. Each subject's own selected
    records are authorized independently. Remote processing requires separate
    successful analyze and remote_processing decisions for every subject. It
    does not authenticate identities, prove that records describe the same
    real event, establish that all participants are
    represented, or persist, share, or analyze the records.
    """
    denied = {"eligible": False, "reason": "", "participantCount": 0, "authorizations": []}
    if (
        not isinstance(interaction_group_id, str)
        or re.fullmatch(r"[A-Za-z0-9_-]{22,128}", interaction_group_id) is None
    ):
        return {**denied, "reason": "invalid_interaction_group_id"}
    if not isinstance(purpose, str) or not purpose.strip():
        return {**denied, "reason": "invalid_authorization_purpose"}
    if not isinstance(action, str) or action not in {"analyze", "share", "remote_processing"}:
        return {**denied, "reason": "unsupported_multi_party_action"}
    if not isinstance(max_records, int) or isinstance(max_records, bool) or max_records < 2:
        return {**denied, "reason": "invalid_record_limit"}
    if action == "share" and not isinstance(recipient, dict):
        return {**denied, "reason": "recipient_required_for_share"}
    if isinstance(selected_record_ids, (str, bytes, dict)):
        return {**denied, "reason": "invalid_selected_record_ids"}

    try:
        record_ids = list(islice(selected_record_ids, max_records + 1))
        record_list = list(records)
        grant_list = list(grants)
    except TypeError:
        return {**denied, "reason": "invalid_selected_inputs"}
    if (
        len(record_ids) < 2
        or len(record_ids) > max_records
        or any(not isinstance(value, str) or not value.strip() for value in record_ids)
        or len(set(record_ids)) != len(record_ids)
    ):
        return {**denied, "reason": "invalid_selected_record_ids"}

    record_matches: dict[str, list[dict[str, Any]]] = {record_id: [] for record_id in record_ids}
    for record in record_list:
        if isinstance(record, dict) and record.get("id") in record_matches:
            record_matches[record["id"]].append(record)
    if any(len(matches) != 1 for matches in record_matches.values()):
        return {**denied, "reason": "selected_record_id_not_unique"}
    selected = [record_matches[record_id][0] for record_id in record_ids]
    if any(
        record.get("recordType") != "interaction_event"
        or record.get("interactionGroupId") != interaction_group_id
        or not validate_record_schema(record).get("valid")
        for record in selected
    ):
        return {**denied, "reason": "selected_record_not_in_valid_interaction_group"}

    subject_ids = [record.get("subjectId") for record in selected]
    if (
        any(not isinstance(value, str) or not value.strip() for value in subject_ids)
        or len(set(subject_ids)) < 2
        or len(set(subject_ids)) != len(subject_ids)
    ):
        return {**denied, "reason": "one_current_record_per_subject_required"}

    try:
        index_list = list(subject_indexes)
    except TypeError:
        return {**denied, "reason": "invalid_subject_indexes"}
    index_by_subject: dict[str, list[dict[str, Any]]] = {subject_id: [] for subject_id in set(subject_ids)}
    for subject_index in index_list:
        if isinstance(subject_index, dict) and subject_index.get("subjectId") in index_by_subject:
            index_by_subject[subject_index["subjectId"]].append(subject_index)
    for subject_id, indexes in index_by_subject.items():
        if len(indexes) != 1:
            return {**denied, "reason": "one_subject_index_per_subject_required"}
        if not validate_schema_instance(indexes[0], "subject-index.schema.json").get("valid"):
            return {**denied, "reason": "invalid_subject_index_schema"}
        resolution = resolve_subject_index(indexes[0], record_list)
        if not resolution.get("valid"):
            return {**denied, "reason": "invalid_subject_index_references"}
        subject_record_ids = {
            record["id"] for record in selected if record.get("subjectId") == subject_id
        }
        if not subject_record_ids.issubset(set(resolution.get("resolvedIds", []))):
            return {**denied, "reason": "selected_record_not_in_subject_index"}

    if any(
        grant.get("subjectId") in index_by_subject
        and not validate_schema_instance(grant, "consent.schema.json").get("valid")
        for grant in grant_list
        if isinstance(grant, dict)
    ):
        return {**denied, "reason": "invalid_subject_consent_schema"}

    resolutions = {
        subject_id: resolve_current_records(record_list, subject_id=subject_id)
        for subject_id in set(subject_ids)
    }
    if any(not result.get("valid") for result in resolutions.values()):
        return {**denied, "reason": "invalid_subject_revision_history"}
    current_ids = {
        subject_id: {record.get("id") for record in result.get("currentRecords", [])}
        for subject_id, result in resolutions.items()
    }
    if any(record["id"] not in current_ids[record["subjectId"]] for record in selected):
        return {**denied, "reason": "selected_record_not_current"}

    authorizations = []
    required_actions = ["analyze", "remote_processing"] if action == "remote_processing" else [action]
    for subject_id in sorted(set(subject_ids)):
        subject_records = [record for record in selected if record.get("subjectId") == subject_id]
        try:
            checks = [
                evaluate_authorization(
                    subject_records,
                    grant_list,
                    subject_id=subject_id,
                    purpose=purpose,
                    action=required_action,
                    now=now,
                    recipient=recipient,
                )
                for required_action in required_actions
            ]
        except (TypeError, ValueError):
            return {**denied, "reason": "invalid_authorization_context"}
        authorizations.append({
            "subjectId": subject_id,
            "authorized": all(check.get("authorized") is True for check in checks),
            "requestedAction": action,
            "authorizationChecks": checks,
        })

    eligible = all(item.get("authorized") is True for item in authorizations)
    return {
        "eligible": eligible,
        "reason": "" if eligible else "every_represented_subject_must_authorize",
        "interactionGroupId": interaction_group_id,
        "participantCount": len(authorizations),
        "authorizations": authorizations,
        "limitations": [
            "Each authorization covers only that subject's explicitly selected current records, purpose, and requested action; remote processing is separately checked alongside analysis.",
            "The opaque group token links selected accounts by caller assertion; it does not verify identity or prove a shared event.",
            "This preflight cannot establish that every actual participant is represented or that omitted participants consented.",
            "This in-memory decision does not enforce storage access or itself transmit, analyze, or persist records.",
        ],
    }
