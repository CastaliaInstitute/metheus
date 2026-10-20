"""Source-preserving descriptions of one selected environmental-affordance trial."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from itertools import islice
from typing import Any, Iterable

from .authorization import evaluate_authorization
from .lifecycle import resolve_current_records
from .temporal import describe_selected_temporal_relations, describe_temporal_order


AFFORDANCE_TRIAL_SUMMARY_VERSION = "metheus-affordance-trial-summary/0.2.0"
_LIFECYCLE_EVENTS = {
    "made_available", "offered", "chosen", "declined", "unavailable",
    "started", "used", "partial_use", "stopped", "revised",
}


def summarize_affordance_trial(
    records: Iterable[dict[str, Any]],
    *,
    subject_id: str,
    affordance_id: str,
    selected_record_ids: Iterable[str],
    max_records: int = 100,
    max_temporal_pairs: int = 500,
) -> dict[str, Any]:
    """Describe selected trial events and linked experience reports.

    This returns only the explicitly selected current records for one subject
    and one stable affordance ID. It keeps choices/use events separate from
    later reports, carries their source/time/value as recorded, and compares
    event/report timing without estimating effect or cause. The caller must
    authorize every selected input before invoking this helper; the helper is
    in-memory and does not create a stored summary or authorize access.
    """
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id is required")
    if not isinstance(affordance_id, str) or not affordance_id.strip():
        raise ValueError("affordance_id is required")
    if not isinstance(max_records, int) or isinstance(max_records, bool) or max_records < 1:
        raise ValueError("max_records must be a positive integer")
    if not isinstance(max_temporal_pairs, int) or isinstance(max_temporal_pairs, bool) or max_temporal_pairs < 1:
        raise ValueError("max_temporal_pairs must be a positive integer")
    if isinstance(selected_record_ids, (str, bytes, dict)):
        raise ValueError("selected_record_ids must be an explicit sequence of record IDs")
    try:
        record_ids = list(islice(selected_record_ids, max_records + 1))
    except TypeError as error:
        raise ValueError("selected_record_ids must be an explicit sequence of record IDs") from error
    if not record_ids or any(not isinstance(value, str) or not value.strip() for value in record_ids):
        raise ValueError("select at least one nonempty record ID")
    if len(set(record_ids)) != len(record_ids):
        raise ValueError("selected_record_ids must be unique")
    if len(record_ids) > max_records:
        raise ValueError("selected record count exceeds max_records")

    record_list = list(records)
    resolution = resolve_current_records(record_list, subject_id=subject_id)
    if not resolution["valid"]:
        raise ValueError("subject revision history is invalid")
    current_by_id = {record["id"]: record for record in resolution["currentRecords"]}
    unresolved = sorted(set(record_ids) - set(current_by_id))
    if unresolved:
        raise ValueError(f"selected records must be current records for the subject: {', '.join(unresolved)}")

    events: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    trial_signature: tuple[Any, Any, Any] | None = None
    for record_id in record_ids:
        record = current_by_id[record_id]
        event = record.get("environmentalAffordance")
        if isinstance(event, dict) and event.get("affordanceId") == affordance_id:
            lifecycle_event = event.get("lifecycleEvent")
            if lifecycle_event not in _LIFECYCLE_EVENTS:
                raise ValueError(f"selected lifecycle event has an unsupported event kind: {record_id}")
            if record.get("recordType") != "event" or record.get("eventType") != "environmental_affordance":
                raise ValueError(f"selected lifecycle record is not an environmental-affordance event: {record_id}")
            signature = (event.get("deliveryMode"), event.get("intendedFunction"), event.get("roleFrame"))
            if any(not isinstance(value, str) or not value for value in signature):
                raise ValueError(f"selected lifecycle event is missing stable trial metadata: {record_id}")
            if trial_signature is not None and signature != trial_signature:
                raise ValueError("selected lifecycle events disagree about trial delivery, function, or role")
            trial_signature = signature
            source = record.get("source")
            events.append({
                "recordId": record_id,
                "lifecycleEvent": lifecycle_event,
                "time": record.get("time"),
                "epistemicClass": record.get("epistemicClass"),
                "sourceKind": source.get("kind") if isinstance(source, dict) else None,
            })
            continue
        related = record.get("relatedAffordanceIds", [])
        if isinstance(related, list) and affordance_id in related:
            if record.get("recordType") not in {"observation", "event"}:
                raise ValueError(f"selected experience report is not an observation or event: {record_id}")
            source = record.get("source")
            report = {
                "recordId": record_id,
                "recordType": record.get("recordType"),
                "eventType": record.get("eventType"),
                "domain": record.get("domain"),
                "label": record.get("label"),
                "time": record.get("time"),
                "epistemicClass": record.get("epistemicClass"),
                "sourceKind": source.get("kind") if isinstance(source, dict) else None,
            }
            if isinstance(record.get("value"), dict):
                report["value"] = record["value"]
            reports.append(report)
            continue
        raise ValueError(f"selected record does not belong to affordance trial: {record_id}")

    if not events:
        raise ValueError("at least one selected lifecycle event is required for the affordance trial")
    temporal_pair_count = len(events) * len(reports) + len(events) * (len(events) - 1) // 2
    if temporal_pair_count > max_temporal_pairs:
        raise ValueError("selected lifecycle/report temporal comparisons exceed max_temporal_pairs")

    events.sort(key=lambda item: item["recordId"])
    reports.sort(key=lambda item: item["recordId"])
    event_ids = [item["recordId"] for item in events]
    report_ids = [item["recordId"] for item in reports]
    lifecycle_temporal_relations = [
        describe_temporal_order(
            record_list,
            subject_id=subject_id,
            left_record_id=left_id,
            right_record_id=right_id,
        )
        for index, left_id in enumerate(event_ids)
        for right_id in event_ids[index + 1:]
    ]
    temporal_relations = describe_selected_temporal_relations(
        record_list,
        subject_id=subject_id,
        left_record_ids=event_ids,
        right_record_ids=report_ids,
        max_pairs=max_temporal_pairs,
    ) if report_ids else []
    selected_ids = sorted([*event_ids, *report_ids])
    digest = sha256(
        "\0".join([subject_id, affordance_id, AFFORDANCE_TRIAL_SUMMARY_VERSION, *selected_ids]).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "summaryId": f"affordance-trial:{digest}",
        "subjectId": subject_id,
        "affordanceId": affordance_id,
        "methodVersion": AFFORDANCE_TRIAL_SUMMARY_VERSION,
        "deliveryMode": trial_signature[0],
        "intendedFunction": trial_signature[1],
        "roleFrame": trial_signature[2],
        "inputRecordIds": selected_ids,
        "lifecycleEvents": events,
        "lifecycleTemporalRelations": lifecycle_temporal_relations,
        "experienceReports": reports,
        "eventReportTemporalRelations": temporal_relations,
        "limitations": [
            "Includes only explicitly selected current records for this subject and affordance ID.",
            "Lifecycle events and later reports remain separate records with their own time, source, and epistemic class.",
            "Temporal relations describe recorded timing and precision only; they do not establish benefit, harm, mechanism, or causation.",
            "A missing choice, use event, or experience report means it was not included in this selected record set; it does not mean the event did not happen.",
            "This in-memory summary does not authorize access, create a stored record, or assess appropriateness, safety, or effectiveness.",
        ],
    }


def summarize_authorized_affordance_trial(
    records: Iterable[dict[str, Any]],
    grants: Iterable[dict[str, Any]],
    *,
    subject_id: str,
    affordance_id: str,
    selected_record_ids: Iterable[str],
    purpose: str,
    now: datetime | None = None,
    max_records: int = 100,
    max_temporal_pairs: int = 500,
) -> dict[str, Any]:
    """Authorize exact selected records for local analysis, then summarize.

    This wrapper evaluates consent before calling ``summarize_affordance_trial``.
    It does not authenticate the subject or enforce access at a storage boundary.
    The result is local and in-memory; any later remote processing requires its
    own explicit authorization against these same source records.
    """
    denied = {"eligible": False, "reason": "", "summary": None}
    if not isinstance(subject_id, str) or not subject_id.strip():
        return {**denied, "reason": "invalid_subject_id"}
    if not isinstance(affordance_id, str) or not affordance_id.strip():
        return {**denied, "reason": "invalid_affordance_id"}
    if not isinstance(purpose, str) or not purpose.strip():
        return {**denied, "reason": "invalid_authorization_purpose"}
    if (
        not isinstance(max_records, int) or isinstance(max_records, bool) or max_records < 1
        or not isinstance(max_temporal_pairs, int) or isinstance(max_temporal_pairs, bool) or max_temporal_pairs < 1
    ):
        return {**denied, "reason": "invalid_summary_limits"}
    if isinstance(selected_record_ids, (str, bytes, dict)):
        return {**denied, "reason": "invalid_selected_record_ids"}
    try:
        record_ids = list(islice(selected_record_ids, max_records + 1))
        record_list = list(records)
        grant_list = list(grants)
    except TypeError:
        return {**denied, "reason": "invalid_selected_inputs"}
    if (
        not record_ids
        or any(not isinstance(value, str) or not value.strip() for value in record_ids)
        or len(set(record_ids)) != len(record_ids)
        or len(record_ids) > max_records
    ):
        return {**denied, "reason": "invalid_selected_record_ids"}

    resolution = resolve_current_records(record_list, subject_id=subject_id)
    if not resolution["valid"]:
        return {**denied, "reason": "invalid_subject_revision_history"}
    current_by_id = {record["id"]: record for record in resolution["currentRecords"]}
    if any(record_id not in current_by_id for record_id in record_ids):
        return {**denied, "reason": "selected_record_not_current_for_subject"}
    selected_records = [current_by_id[record_id] for record_id in record_ids]
    try:
        authorization = evaluate_authorization(
            selected_records,
            grant_list,
            subject_id=subject_id,
            purpose=purpose,
            action="analyze",
            now=now,
        )
    except (TypeError, ValueError):
        return {**denied, "reason": "invalid_authorization_context"}
    if not authorization.get("authorized"):
        return {
            **denied,
            "reason": "selected_trial_records_not_authorized",
            "authorization": authorization,
        }
    try:
        summary = summarize_affordance_trial(
            record_list,
            subject_id=subject_id,
            affordance_id=affordance_id,
            selected_record_ids=record_ids,
            max_records=max_records,
            max_temporal_pairs=max_temporal_pairs,
        )
    except ValueError:
        return {
            **denied,
            "reason": "invalid_selected_affordance_trial",
            "authorization": authorization,
        }
    return {
        "eligible": True,
        "reason": "",
        "authorization": authorization,
        "summary": summary,
        "limitations": [
            "Authorization applies only to local analysis under the supplied purpose and current grants.",
            "This wrapper does not authenticate the subject or enforce storage access.",
            "Remote processing requires a separate authorization decision for the selected source records.",
        ],
    }
