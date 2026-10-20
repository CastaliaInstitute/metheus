"""Typed descriptions of temporal order between selected Metheus records.

This module compares recorded time windows only. It does not infer biological
phase, co-occurrence mechanisms, association, or causation.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Any, Iterable

from .rhythms import _parse_datetime, _resolve_subject_history


TEMPORAL_RELATION_METHOD_VERSION = "metheus-temporal-order/0.1.0"


def _time_window(record: dict[str, Any]) -> tuple[dict[str, Any], tuple[str, Any, Any] | None]:
    """Return display window and a comparable date or UTC interval, if known."""
    if record.get("recordType") == "phase_annotation":
        window = record.get("window")
        if not isinstance(window, dict):
            return {"kind": "unknown", "start": None, "end": None}, None
        if window.get("kind") == "ongoing":
            display_window = {"kind": "ongoing", "start": window.get("start"), "end": None}
            if isinstance(window.get("timeZone"), str):
                display_window["timeZone"] = window["timeZone"]
            return display_window, None
        start_value, end_value = window.get("start"), window.get("end")
        kind = window.get("kind")
        if not isinstance(start_value, str):
            return {"kind": "unknown", "start": None, "end": None}, None
        if len(start_value) == 10:
            try:
                start_date = date.fromisoformat(start_value)
                if end_value is None:
                    end_date = start_date
                elif isinstance(end_value, str) and len(end_value) == 10:
                    end_date = date.fromisoformat(end_value)
                else:
                    return {"kind": "unknown", "start": start_value, "end": end_value}, None
            except ValueError:
                return {"kind": "unknown", "start": start_value, "end": end_value}, None
            if end_date < start_date:
                return {"kind": "unknown", "start": start_value, "end": end_value}, None
            return {"kind": "date_only", "start": start_value, "end": end_value or start_value}, ("date", start_date, end_date)
        try:
            start_dt = _parse_datetime(start_value).astimezone(timezone.utc)
            if end_value is None:
                end_dt = start_dt
            elif isinstance(end_value, str):
                end_dt = _parse_datetime(end_value).astimezone(timezone.utc)
            else:
                return {"kind": "unknown", "start": start_value, "end": end_value}, None
        except (TypeError, ValueError):
            return {"kind": "unknown", "start": start_value, "end": end_value}, None
        if end_dt < start_dt:
            return {"kind": "unknown", "start": start_value, "end": end_value}, None
        display_window = {"kind": kind, "start": start_value, "end": end_value or start_value}
        if isinstance(window.get("timeZone"), str):
            display_window["timeZone"] = window["timeZone"]
        return display_window, ("instant", start_dt, end_dt)

    time_data = record.get("time")
    if not isinstance(time_data, dict):
        return {"kind": "unknown", "start": None, "end": None}, None
    if time_data.get("precision") == "date_only":
        raw_date = time_data.get("date")
        if not isinstance(raw_date, str):
            return {"kind": "unknown", "start": None, "end": None}, None
        try:
            parsed_date = date.fromisoformat(raw_date)
        except ValueError:
            return {"kind": "unknown", "start": raw_date, "end": raw_date}, None
        return {"kind": "date_only", "start": raw_date, "end": raw_date}, ("date", parsed_date, parsed_date)
    start_value, end_value = time_data.get("start"), time_data.get("end")
    observed_at = time_data.get("observedAt")
    if observed_at is not None:
        start_value = end_value = observed_at
        kind = "point"
    elif isinstance(start_value, str) and isinstance(end_value, str):
        kind = "interval"
    else:
        return {"kind": "unknown", "start": start_value, "end": end_value}, None
    try:
        start_dt = _parse_datetime(start_value).astimezone(timezone.utc)
        end_dt = _parse_datetime(end_value).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return {"kind": "unknown", "start": start_value, "end": end_value}, None
    if end_dt < start_dt:
        return {"kind": "unknown", "start": start_value, "end": end_value}, None
    result = {"kind": kind, "start": start_value, "end": end_value, "precision": time_data.get("precision", "unknown")}
    if isinstance(time_data.get("timeZone"), str):
        result["timeZone"] = time_data["timeZone"]
    return result, ("instant", start_dt, end_dt)


def _classify(left: tuple[str, Any, Any] | None, right: tuple[str, Any, Any] | None) -> tuple[str, float | None]:
    if left is None or right is None or left[0] != right[0]:
        return "indeterminate", None
    left_start, left_end = left[1], left[2]
    right_start, right_end = right[1], right[2]
    if left[0] == "date":
        if left_end < right_start:
            return "precedes", float((right_start - left_end).days)
        if right_end < left_start:
            return "follows", float((left_start - right_end).days)
        if left_start == left_end == right_start == right_end:
            return "same_calendar_date", None
        return "overlaps", None
    if left_start == left_end == right_start == right_end:
        return ("same_instant", None) if left_start == right_start else (
            ("precedes", (right_start - left_end).total_seconds())
            if left_start < right_start else ("follows", (left_start - right_end).total_seconds())
        )
    if left_end <= right_start:
        return "precedes", (right_start - left_end).total_seconds()
    if right_end <= left_start:
        return "follows", (left_start - right_end).total_seconds()
    return "overlaps", None


def _build_relation(
    subject_id: str, left_record_id: str, right_record_id: str,
    left: dict[str, Any], right: dict[str, Any],
) -> dict[str, Any]:
    left_window, left_comparable = _time_window(left)
    right_window, right_comparable = _time_window(right)
    relation, gap = _classify(left_comparable, right_comparable)
    relation_id = sha256(f"{subject_id}\0{left_record_id}\0{right_record_id}\0{TEMPORAL_RELATION_METHOD_VERSION}".encode()).hexdigest()[:16]
    return {
        "relationId": f"temporal-order:{relation_id}",
        "subjectId": subject_id,
        "relationType": "temporal_order",
        "methodVersion": TEMPORAL_RELATION_METHOD_VERSION,
        "leftRecordId": left_record_id,
        "rightRecordId": right_record_id,
        "leftWindow": left_window,
        "rightWindow": right_window,
        "temporalRelation": relation,
        "elapsedGap": gap,
        "elapsedGapUnit": "days" if left_comparable and right_comparable and left_comparable[0] == right_comparable[0] == "date" else "seconds",
        "gapBasis": (
            "not_available" if gap is None
            else "calendar_date_difference" if left_comparable and left_comparable[0] == "date"
            else "elapsed_duration"
        ),
        "limitations": [
            "Compares only the supplied records' stated time windows; it does not establish co-occurrence beyond the recorded precision.",
            "Date-only windows are comparable only with other date-only windows; mixed date and timestamp precision is indeterminate.",
            "Approximate timestamps and intervals retain their source uncertainty; ordering of recorded bounds is not proof of exact event timing.",
            "Temporal order or overlap does not establish biological mechanism, within-person association, or causation.",
            "This in-memory description is not a stored record and does not authorize access to either input.",
        ],
    }


def describe_temporal_order(
    records: Iterable[dict[str, Any]], *, subject_id: str, left_record_id: str,
    right_record_id: str, phase_annotations: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Describe the recorded temporal relation between two same-subject inputs.

    The inputs must be current records in the supplied revision history. Date-only
    windows compare only with other date-only windows; timestamped windows compare
    on the UTC timeline. Mixed precision, open-ended windows, or absent/invalid
    time data produce ``indeterminate``. This result is a descriptive helper, not
    an observation, authorization decision, biological relation, or causal claim.
    """
    if not subject_id or not left_record_id or not right_record_id:
        raise ValueError("subject and both record IDs are required")
    if left_record_id == right_record_id:
        raise ValueError("temporal order requires two distinct records")
    candidates = [*records, *phase_annotations]
    resolution = _resolve_subject_history(candidates, subject_id)
    current = {record.get("id"): record for record in resolution["currentRecords"]}
    left = current.get(left_record_id)
    right = current.get(right_record_id)
    if left is None or right is None:
        raise ValueError("both records must be current and belong to the requested subject")
    allowed = {"observation", "event", "estimate", "context", "interaction_event", "phase_annotation"}
    if left.get("recordType") not in allowed or right.get("recordType") not in allowed:
        raise ValueError("temporal order supports observations, events, interaction events, contexts, estimates, and phase annotations")
    return _build_relation(subject_id, left_record_id, right_record_id, left, right)


def describe_selected_temporal_relations(
    records: Iterable[dict[str, Any]], *, subject_id: str,
    left_record_ids: Iterable[str], right_record_ids: Iterable[str],
    phase_annotations: Iterable[dict[str, Any]] = (), max_pairs: int = 500,
) -> list[dict[str, Any]]:
    """Compare explicitly selected cross-set pairs by their recorded times.

    This supports descriptive timelines such as a selected behavior beside
    separately recorded observations. It computes no effect, association, or
    mechanism. Every selected ID must resolve to a current same-subject source
    record or phase annotation, and the explicit cross product is bounded.
    Callers must authorize all selected inputs before invoking the helper.
    """
    if not isinstance(max_pairs, int) or isinstance(max_pairs, bool) or max_pairs < 1:
        raise ValueError("max_pairs must be a positive integer")
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("subject_id is required")
    left_ids = list(left_record_ids)
    right_ids = list(right_record_ids)
    if not left_ids or not right_ids:
        raise ValueError("explicit left and right record ID lists are required")
    selected_ids = left_ids + right_ids
    if not all(isinstance(value, str) and value for value in selected_ids):
        raise ValueError("selected IDs must be nonempty strings")
    if len(set(left_ids)) != len(left_ids) or len(set(right_ids)) != len(right_ids):
        raise ValueError("selected IDs must be unique within each list")
    if set(left_ids).intersection(right_ids):
        raise ValueError("a record ID cannot appear on both sides of a temporal relation")
    if len(left_ids) * len(right_ids) > max_pairs:
        raise ValueError("selected record combinations exceed max_pairs")

    record_list = list(records)
    phase_list = list(phase_annotations)
    resolution = _resolve_subject_history([*record_list, *phase_list], subject_id)
    current = {record.get("id"): record for record in resolution["currentRecords"]}
    allowed = {"observation", "event", "interaction_event", "estimate", "context", "phase_annotation"}
    for record_id in selected_ids:
        record = current.get(record_id)
        if record is None or record.get("recordType") not in allowed:
            raise ValueError("every selected ID must resolve to a current same-subject source record or phase annotation")

    return [
        _build_relation(subject_id, left_id, right_id, current[left_id], current[right_id])
        for left_id in left_ids
        for right_id in right_ids
    ]


def describe_phase_observation_relations(
    records: Iterable[dict[str, Any]], *, subject_id: str,
    observation_record_ids: Iterable[str], phase_annotation_ids: Iterable[str],
    phase_annotations: Iterable[dict[str, Any]], max_pairs: int = 500,
) -> list[dict[str, Any]]:
    """Describe temporal relations between explicitly selected records/phases.

    This computes the Cartesian product of the selected observation and phase
    IDs. Both lists are explicit to avoid silently broadening a reading's scope.
    The caller must authorize every selected input before invoking this helper.
    The returned pairwise objects are ephemeral; they do not assign biological
    phase or association.
    """
    if not isinstance(max_pairs, int) or isinstance(max_pairs, bool) or max_pairs < 1:
        raise ValueError("max_pairs must be a positive integer")
    observation_ids = list(observation_record_ids)
    phase_ids = list(phase_annotation_ids)
    if not observation_ids or not phase_ids:
        raise ValueError("explicit observation and phase annotation IDs are required")
    if not all(isinstance(value, str) and value for value in observation_ids + phase_ids):
        raise ValueError("selected IDs must be nonempty strings")
    if len(set(observation_ids)) != len(observation_ids) or len(set(phase_ids)) != len(phase_ids):
        raise ValueError("selected IDs must be unique within each list")
    if set(observation_ids).intersection(phase_ids):
        raise ValueError("an ID cannot be both an observation and a phase annotation")
    if len(observation_ids) * len(phase_ids) > max_pairs:
        raise ValueError("selected record and phase combination exceeds max_pairs")

    record_list = list(records)
    phase_list = list(phase_annotations)
    resolution = _resolve_subject_history([*record_list, *phase_list], subject_id)
    current = {record.get("id"): record for record in resolution["currentRecords"]}
    for record_id in observation_ids:
        record = current.get(record_id)
        if record is None or record.get("recordType") not in {"observation", "event", "estimate", "context"}:
            raise ValueError("every selected observation ID must resolve to a current same-subject source record")
    phase_index = {item.get("id"): item for item in phase_list if isinstance(item, dict)}
    for phase_id in phase_ids:
        annotation = current.get(phase_id)
        if annotation is None or annotation.get("recordType") != "phase_annotation" or phase_index.get(phase_id) is not annotation:
            raise ValueError("every selected phase ID must resolve to a current same-subject phase annotation")

    return [
        _build_relation(subject_id, record_id, phase_id, current[record_id], current[phase_id])
        for record_id in observation_ids
        for phase_id in phase_ids
    ]
