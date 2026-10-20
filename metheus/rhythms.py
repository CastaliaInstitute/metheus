"""Descriptive rhythm summaries for Metheus observation records.

These functions summarize logged events. They do not estimate hormones,
diagnose conditions, infer causation, or evaluate whether a schedule is healthy.
Timed values must be ISO 8601 timestamps with an explicit UTC offset. The
bleeding-onset summary also accepts an explicit date-only record where supported.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from math import isfinite
from statistics import median
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .lifecycle import resolve_current_records


METHOD_VERSION = "metheus-rhythm-summary/0.2.0"
SUMMARY_SCHEMA_VERSION = "0.1"
FEEDING_METHOD_VERSION = "metheus-feeding-summary/0.3.0"
WAKE_RELATIVE_METHOD_VERSION = "metheus-wake-relative-meal/0.2.0"
BLEEDING_ONSET_METHOD_VERSION = "metheus-bleeding-onset-gap/0.3.0"
MEASUREMENT_SERIES_METHOD_VERSION = "metheus-numeric-measurement-series/0.2.0"

_MEASUREMENT_SIGNATURE_FIELDS = (
    "sourceKind", "sourceName", "sourceMethod", "sourceVersion", "methodDetails",
    "specimen", "sensorLocation", "deviceOrAssay", "deviceModel",
    "algorithmVersion", "collectionConditions",
)


def measurement_series_source_matches(summary: dict[str, Any], record: dict[str, Any]) -> bool:
    """Return whether a numeric observation belongs to this exact series signature."""
    if record.get("recordType") not in {"observation", "event"}:
        return False
    if record.get("epistemicClass") not in {"measured", "derived", "imported"}:
        return False
    value = record.get("value")
    details = record.get("measurementDetails")
    source = record.get("source")
    signature = summary.get("measurementSeries")
    if not isinstance(value, dict) or not isinstance(details, dict) or not isinstance(source, dict) or not isinstance(signature, dict):
        return False
    if not isinstance(value.get("number"), (int, float)) or isinstance(value.get("number"), bool) or not isfinite(value["number"]):
        return False
    if not isinstance(value.get("unit"), str) or not value["unit"].strip():
        return False
    if record.get("domain") != summary.get("domain") or record.get("epistemicClass") != signature.get("epistemicClass"):
        return False
    if details.get("analyteOrSignal") != signature.get("analyteOrSignal") or value.get("unit") != signature.get("unit"):
        return False
    try:
        first_day, last_day, _ = _window(summary["window"]["startDate"], summary["window"]["endDate"])
        time_data = record.get("time", {})
        if not isinstance(time_data, dict):
            return False
        if time_data.get("precision") == "date_only":
            observed_day = date.fromisoformat(time_data["date"])
        else:
            stamp = time_data.get("observedAt") or time_data.get("start")
            if not stamp:
                return False
            observed_day = _localize(record, stamp).date()
    except (KeyError, TypeError, ValueError):
        return False
    if not first_day <= observed_day <= last_day:
        return False
    actual = {
        "sourceKind": source.get("kind", "unspecified"),
        "sourceName": source.get("name", "unspecified"),
        "sourceMethod": source.get("method", "unspecified"),
        "sourceVersion": source.get("version", "unspecified"),
        "methodDetails": record.get("methodDetails", "unspecified"),
        **{field: details.get(field, "unspecified") for field in _MEASUREMENT_SIGNATURE_FIELDS[5:]},
    }
    return all(actual[field] == signature.get(field) for field in _MEASUREMENT_SIGNATURE_FIELDS)


def measurement_series_summary_valid(summary: dict[str, Any]) -> bool:
    signature = summary.get("measurementSeries")
    metrics = ("nMeasurements", "nDistinctMeasurementDates", "medianNumericValue", "medianAbsoluteDeviationValue", "minimumValue", "maximumValue", "recordsWithQualityFlags", "qualityFlags", "coverage", "bucketDays", "timeBuckets")
    valid_header = bool(
        summary.get("summaryMeasure") == "measurement_series"
        and summary.get("methodVersion") == MEASUREMENT_SERIES_METHOD_VERSION
        and isinstance(summary.get("domain"), str)
        and isinstance(signature, dict)
        and all(isinstance(signature.get(key), str) and signature[key] for key in ("analyteOrSignal", "unit", "epistemicClass", *_MEASUREMENT_SIGNATURE_FIELDS))
        and signature.get("epistemicClass") in {"measured", "derived", "imported"}
        and all(key in summary for key in metrics)
        and isinstance(summary.get("inputRecordIds"), list)
        and all(isinstance(value, str) and value for value in summary["inputRecordIds"])
    )
    if not valid_header or len(set(summary["inputRecordIds"])) != len(summary["inputRecordIds"]):
        return False
    bucket_days = summary.get("bucketDays")
    if isinstance(bucket_days, bool) or not isinstance(bucket_days, int) or not 1 <= bucket_days <= 366:
        return False
    window = summary.get("window")
    if not isinstance(window, dict):
        return False
    try:
        first_day, last_day, window_days = _window(window.get("startDate"), window.get("endDate"))
    except (TypeError, ValueError):
        return False
    if window.get("inclusiveDays") != window_days:
        return False
    buckets = summary.get("timeBuckets")
    expected_count = (window_days + bucket_days - 1) // bucket_days
    if not isinstance(buckets, list) or len(buckets) != expected_count:
        return False

    bucket_measurement_total = 0
    bucket_day_total = 0
    bucket_record_ids: set[str] = set()
    for index, bucket in enumerate(buckets):
        if not isinstance(bucket, dict):
            return False
        offset = index * bucket_days
        expected_start = first_day + timedelta(days=offset)
        expected_end = min(last_day, expected_start + timedelta(days=bucket_days - 1))
        inclusive_days = (expected_end - expected_start).days + 1
        if (
            bucket.get("startDate") != expected_start.isoformat()
            or bucket.get("endDate") != expected_end.isoformat()
            or bucket.get("inclusiveDays") != inclusive_days
        ):
            return False
        count = bucket.get("nMeasurements")
        distinct_dates = bucket.get("nDistinctMeasurementDates")
        record_ids = bucket.get("inputRecordIds")
        days_with_records = bucket.get("daysWithAtLeastOneRecord")
        if (
            isinstance(count, bool) or not isinstance(count, int) or count < 0
            or isinstance(distinct_dates, bool) or not isinstance(distinct_dates, int) or not 0 <= distinct_dates <= count
            or isinstance(days_with_records, bool) or not isinstance(days_with_records, int) or days_with_records != distinct_dates
            or not isinstance(record_ids, list) or len(record_ids) != count
            or not all(isinstance(value, str) and value for value in record_ids)
            or len(set(record_ids)) != len(record_ids)
        ):
            return False
        fraction = bucket.get("fractionOfDaysWithARecord")
        if isinstance(fraction, bool) or not isinstance(fraction, (int, float)) or abs(fraction - distinct_dates / inclusive_days) > 0.000001:
            return False
        if bucket_record_ids.intersection(record_ids):
            return False
        bucket_record_ids.update(record_ids)
        bucket_measurement_total += count
        bucket_day_total += distinct_dates
        bucket_median = bucket.get("medianValue")
        bucket_mad = bucket.get("medianAbsoluteDeviationValue")
        minimum = bucket.get("minimumValue")
        maximum = bucket.get("maximumValue")
        if count == 0:
            if any(value is not None for value in (bucket_median, bucket_mad, minimum, maximum)):
                return False
        elif (
            any(isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) for value in (bucket_median, bucket_mad, minimum, maximum))
            or bucket_mad < 0
            or not minimum <= bucket_median <= maximum
        ):
            return False
    return (
        bucket_measurement_total == summary.get("nMeasurements")
        and bucket_day_total == summary.get("nDistinctMeasurementDates")
        and bucket_record_ids == set(summary.get("inputRecordIds", []))
    )


def _resolve_subject_history(records: Iterable[dict[str, Any]], subject_id: str) -> dict[str, Any]:
    resolution = resolve_current_records(records, subject_id=subject_id)
    if not resolution["valid"]:
        raise ValueError("subject record revision history is ambiguous")
    return resolution


def _revision_resolution_metadata(resolution: dict[str, Any]) -> dict[str, Any]:
    """Expose revision-chain coverage without exposing unrelated record IDs."""
    return {
        "strategy": "latest_visible_successor",
        "supersededRecordCount": len(resolution["supersededIds"]),
        "unresolvedPredecessorCount": len(resolution.get("warnings", [])),
    }


def bleeding_onset_summary_boundary_valid(
    summary: dict[str, Any], source_records: dict[str, dict[str, Any]] | None = None
) -> bool:
    """Check that an optional out-of-window onset remains an authorized dependency."""
    if summary.get("summaryMeasure") != "bleeding_onset_intervals":
        return True
    input_ids = summary.get("inputRecordIds")
    boundary_ids = summary.get("boundaryOnsetRecordIds")
    boundary_date = summary.get("boundaryOnsetDate")
    window = summary.get("window")
    if (
        not isinstance(input_ids, list)
        or not all(isinstance(value, str) and value for value in input_ids)
        or len(set(input_ids)) != len(input_ids)
        or not isinstance(boundary_ids, list)
        or not all(isinstance(value, str) and value for value in boundary_ids)
        or len(set(boundary_ids)) != len(boundary_ids)
        or not isinstance(window, dict)
    ):
        return False
    if boundary_date is None:
        return not boundary_ids
    if not isinstance(boundary_date, str) or not boundary_ids or not set(boundary_ids).issubset(input_ids):
        return False
    try:
        parsed_boundary_date = date.fromisoformat(boundary_date)
        if parsed_boundary_date >= date.fromisoformat(window["startDate"]):
            return False
    except (KeyError, TypeError, ValueError):
        return False
    if source_records is None:
        return True
    for record_id in boundary_ids:
        record = source_records.get(record_id)
        time_data = record.get("time") if isinstance(record, dict) else None
        if not isinstance(time_data, dict):
            return False
        try:
            if time_data.get("precision") == "date_only":
                observed_date = date.fromisoformat(time_data["date"])
            else:
                stamp = time_data.get("observedAt") or time_data.get("start")
                if not isinstance(stamp, str):
                    return False
                observed_date = _localize(record, stamp).date()
        except (KeyError, TypeError, ValueError):
            return False
        if observed_date != parsed_boundary_date:
            return False
    return True


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamps must include an explicit UTC offset")
    return parsed


def _localize(record: dict[str, Any], value: str) -> datetime:
    parsed = _parse_datetime(value)
    zone_name = record.get("time", {}).get("timeZone")
    if zone_name:
        try:
            return parsed.astimezone(ZoneInfo(zone_name))
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return parsed


def _clock_context(record: dict[str, Any], local_time: datetime) -> str:
    zone_name = record.get("time", {}).get("timeZone")
    if zone_name:
        try:
            ZoneInfo(zone_name)
            return zone_name
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return str(local_time.utcoffset())


def _window(start_date: str, end_date: str) -> tuple[date, date, int]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date must be on or after start_date")
    return start, end, (end - start).days + 1


def _clock_minute(value: datetime) -> int:
    return value.hour * 60 + value.minute


def _clock_distance(left: int, right: int) -> int:
    raw = abs(left - right)
    return min(raw, 1440 - raw)


def _clock_medoid(values: list[int]) -> int | None:
    """Return an observed clock time minimizing total circular absolute distance."""
    if not values:
        return None
    candidates = sorted(set(values))
    return min(candidates, key=lambda candidate: sum(_clock_distance(candidate, item) for item in values))


def _format_clock(value: int | None) -> str | None:
    if value is None:
        return None
    return f"{value // 60:02d}:{value % 60:02d}"


def _coverage(observed_days: set[date], window_days: int) -> dict[str, Any]:
    return {
        "daysWithAtLeastOneRecord": len(observed_days),
        "calendarDaysInWindow": window_days,
        "fractionOfDaysWithARecord": round(len(observed_days) / window_days, 3) if window_days else 0.0,
    }


def _summary_id(domain: str, start: date, end: date) -> str:
    # IDs are scoped by subjectId in storage; never encode the subject ID here.
    return f"{domain}:{METHOD_VERSION}:{start.isoformat()}:{end.isoformat()}"


def _summary_metadata(summary_id: str, subject_id: str, measure: str) -> dict[str, Any]:
    return {
        "id": summary_id,
        "summaryId": summary_id,
        "subjectId": subject_id,
        "recordType": "rhythm_summary",
        "schemaVersion": SUMMARY_SCHEMA_VERSION,
        "summaryType": "derived_rhythm_summary",
        "summaryMeasure": measure,
        "epistemicClass": "derived",
    }


def summarize_bleeding_onset_intervals(
    records: Iterable[dict[str, Any]], *, subject_id: str, start_date: str, end_date: str
) -> dict[str, Any]:
    """Describe gaps between explicitly logged bleeding-onset dates.

    This reports calendar-day intervals ending at logged onset dates in the
    inclusive window. The nearest earlier logged onset may fall before the
    window and is exposed as a boundary input. This does not determine whether
    bleeding is menstrual, infer ovulation or hormone phase, predict a future
    event, or evaluate health. Exact times are unnecessary; date-only onset
    records are supported.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    revision_resolution = _resolve_subject_history(records, subject_id)
    current_records = revision_resolution["currentRecords"]
    first_day, last_day, window_days = _window(start_date, end_date)
    onset_records: dict[date, set[str]] = {}
    onset_record_counts: dict[date, int] = {}
    date_only_count = 0
    timed_count = 0

    for record in current_records:
        if record.get("subjectId") != subject_id:
            continue
        if record.get("recordType") not in {"observation", "event"}:
            continue
        if record.get("eventType") != "bleeding_start" or record.get("domain") != "reproductive":
            continue
        if record.get("epistemicClass") in {"derived", "symbolic"}:
            continue

        time_data = record.get("time", {})
        if time_data.get("precision") == "date_only":
            date_value = time_data.get("date")
            if not date_value:
                continue
            onset_date = date.fromisoformat(date_value)
            date_only = True
        else:
            stamp = time_data.get("observedAt") or time_data.get("start")
            if not stamp:
                continue
            onset_date = _localize(record, stamp).date()
            date_only = False

        if first_day <= onset_date <= last_day and date_only:
            date_only_count += 1
        elif first_day <= onset_date <= last_day:
            timed_count += 1
        onset_records.setdefault(onset_date, set())
        onset_record_counts[onset_date] = onset_record_counts.get(onset_date, 0) + 1
        record_id = record.get("id")
        if record_id:
            onset_records[onset_date].add(record_id)

    all_onset_dates = sorted(onset_records)
    onset_dates = [onset_date for onset_date in all_onset_dates if first_day <= onset_date <= last_day]
    interval_pairs = [
        (earlier, later)
        for earlier, later in zip(all_onset_dates, all_onset_dates[1:])
        if first_day <= later <= last_day
    ]
    interval_days = [(later - earlier).days for earlier, later in interval_pairs]
    median_gap = median(interval_days) if interval_days else None
    deviations = [abs(value - median_gap) for value in interval_days] if median_gap is not None else []
    boundary_onset_date = next(
        (onset_date for onset_date in reversed(all_onset_dates) if onset_date < first_day), None
    ) if onset_dates else None
    included_dates = set(onset_dates)
    if boundary_onset_date is not None:
        included_dates.add(boundary_onset_date)
    input_ids = sorted({record_id for onset_date in included_dates for record_id in onset_records[onset_date]})
    boundary_input_ids = sorted(onset_records.get(boundary_onset_date, set())) if boundary_onset_date else []

    summary_id = f"bleeding-onset:{BLEEDING_ONSET_METHOD_VERSION}:{first_day.isoformat()}:{last_day.isoformat()}"
    return {
        **_summary_metadata(summary_id, subject_id, "bleeding_onset_intervals"),
        "domain": "reproductive",
        "label": "calendar-day gaps between logged bleeding-onset dates",
        "methodVersion": BLEEDING_ONSET_METHOD_VERSION,
        "revisionResolution": _revision_resolution_metadata(revision_resolution),
        "window": {"startDate": first_day.isoformat(), "endDate": last_day.isoformat(), "inclusiveDays": window_days},
        "inputRecordIds": input_ids,
        "boundaryOnsetDate": boundary_onset_date.isoformat() if boundary_onset_date else None,
        "boundaryOnsetRecordIds": boundary_input_ids,
        "nOnsetRecords": sum(onset_record_counts.get(onset_date, 0) for onset_date in onset_dates),
        "nDistinctOnsetDates": len(onset_dates),
        "nIntervals": len(interval_days),
        "intervalsDays": interval_days,
        "medianGapDays": round(median_gap, 1) if median_gap is not None else None,
        "medianAbsoluteDeviationDays": round(median(deviations), 1) if deviations else None,
        "dateOnlyRecordCount": date_only_count,
        "timedRecordCount": timed_count,
        "limitations": [
            "Includes only explicitly logged bleeding-onset records for this subject; missing logs are not evidence that bleeding did not occur.",
            "A gap between bleeding-onset dates is a calendar interval, not proof of a menstrual cycle or its biological phase.",
            "Does not infer ovulation, fertility, pregnancy, hormone levels, menopause stage, diagnosis, or a future onset date.",
            "Date-only reports have less timing precision than timestamped events; the source's precision is retained in the input records.",
            "Intervals are between adjacent logged dates and assigned to their later onset date; the nearest preceding logged date may be outside the selected window and is identified as a boundary input.",
            "A preceding boundary input is only the nearest onset in supplied records; incomplete history may omit earlier events.",
        ],
    }


def summarize_main_sleep(
    records: Iterable[dict[str, Any]], *, subject_id: str, start_date: str, end_date: str
) -> dict[str, Any]:
    """Summarize explicitly tagged main-sleep intervals in an inclusive date window.

    The sleep date is the local calendar date at interval start. The summary
    reports duration and observed clock timing; it does not claim to estimate
    endogenous circadian phase or sleep quality.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    revision_resolution = _resolve_subject_history(records, subject_id)
    current_records = revision_resolution["currentRecords"]
    first_day, last_day, window_days = _window(start_date, end_date)
    eligible: list[tuple[datetime, float, datetime, str]] = []
    clock_contexts: set[str] = set()

    for record in current_records:
        if record.get("subjectId") != subject_id:
            continue
        if record.get("recordType") not in {"observation", "event"}:
            continue
        if record.get("eventType") != "main_sleep" or record.get("domain") != "sleep":
            continue
        interval = record.get("time", {})
        if not interval.get("start") or not interval.get("end"):
            continue
        start = _localize(record, interval["start"])
        end = _localize(record, interval["end"])
        local_day = start.date()
        if not first_day <= local_day <= last_day:
            continue
        elapsed = end.astimezone(timezone.utc) - start.astimezone(timezone.utc)
        if elapsed.total_seconds() <= 0:
            continue
        clock_contexts.add(_clock_context(record, start))
        midpoint_utc = start.astimezone(timezone.utc) + elapsed / 2
        midpoint = midpoint_utc.astimezone(start.tzinfo)
        duration_minutes = elapsed.total_seconds() / 60
        eligible.append((start, duration_minutes, midpoint, record.get("id", "")))

    durations: list[float] = []
    midpoints: list[int] = []
    start_times: list[int] = []
    observed_days: set[date] = set()
    source_ids: list[str] = []
    for start, duration_minutes, midpoint, record_id in eligible:
        observed_days.add(start.date())
        durations.append(duration_minutes)
        midpoints.append(_clock_minute(midpoint))
        start_times.append(_clock_minute(start))
        if record_id:
            source_ids.append(record_id)

    clock_comparable = len(clock_contexts) <= 1
    median_midpoint = _clock_medoid(midpoints) if clock_comparable else None
    midpoint_deviations = [float(_clock_distance(item, median_midpoint)) for item in midpoints] if median_midpoint is not None else []
    median_start = _clock_medoid(start_times) if clock_comparable else None
    return {
        **_summary_metadata(_summary_id("sleep", first_day, last_day), subject_id, "main_sleep"),
        "domain": "sleep",
        "label": "logged main-sleep timing summary",
        "methodVersion": METHOD_VERSION,
        "revisionResolution": _revision_resolution_metadata(revision_resolution),
        "window": {"startDate": first_day.isoformat(), "endDate": last_day.isoformat(), "inclusiveDays": window_days},
        "inputRecordIds": sorted(set(source_ids)),
        "nIntervals": len(eligible),
        "coverage": _coverage(observed_days, window_days),
        "medianLoggedDurationMinutes": round(median(durations), 1) if durations else None,
        "medianLoggedStartClockTime": _format_clock(median_start),
        "medianLoggedMidpointClockTime": _format_clock(median_midpoint),
        "medianAbsoluteMidpointDeviationMinutes": round(median(midpoint_deviations), 1) if midpoint_deviations else None,
        "clockTimesComparable": clock_comparable,
        "clockTimeContextCount": len(clock_contexts),
        "clockTimeContexts": sorted(clock_contexts),
        "limitations": [
            "Summarizes logged intervals only; missing logs are not evidence that sleep did not occur.",
            "Clock-time summary is not an estimate of endogenous circadian phase.",
            "Does not assess sleep quality, health, or whether this schedule is appropriate.",
            "Clock time uses the record's IANA time zone when valid, otherwise its supplied UTC offset; callers should retain source time-zone metadata.",
        ],
    }


def summarize_feeding_events(
    records: Iterable[dict[str, Any]], *, subject_id: str, start_date: str, end_date: str, event_kind: str = "meal"
) -> dict[str, Any]:
    """Summarize either logged meals or caregiver-reported feeding events.

    The event types are intentionally summarized separately; a meal statistic
    and infant-feed statistic are not combined. The result never estimates
    calories, fasting duration, adequacy, hunger, or nutritional status.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    if event_kind not in {"meal", "feeding"}:
        raise ValueError("event_kind must be 'meal' or 'feeding'")
    revision_resolution = _resolve_subject_history(records, subject_id)
    current_records = revision_resolution["currentRecords"]
    first_day, last_day, window_days = _window(start_date, end_date)
    events_by_day: dict[date, list[tuple[int, str]]] = {}
    clock_contexts: set[str] = set()

    for record in current_records:
        if record.get("subjectId") != subject_id:
            continue
        if record.get("recordType") not in {"observation", "event"}:
            continue
        event_type = record.get("eventType")
        if event_type != event_kind:
            continue
        if event_type == "meal" and record.get("domain") not in {"feeding", "nutrition"}:
            continue
        if event_type == "feeding" and record.get("domain") != "feeding":
            continue
        time_data = record.get("time", {})
        stamp = time_data.get("observedAt") or time_data.get("start")
        if not stamp:
            continue
        if event_type == "feeding" and record.get("epistemicClass") != "caregiver_reported":
            continue
        observed_at = _localize(record, stamp)
        local_day = observed_at.date()
        if not first_day <= local_day <= last_day:
            continue
        clock_contexts.add(_clock_context(record, observed_at))
        events_by_day.setdefault(local_day, []).append((_clock_minute(observed_at), record.get("id", "")))

    event_type_label = "caregiver-reported feeding events" if event_kind == "feeding" else "logged meal events"
    event_count = sum(len(events) for events in events_by_day.values())
    recorded_spans: list[float] = []
    clock_comparable = len(clock_contexts) <= 1
    if clock_comparable:
        for events in events_by_day.values():
            if len(events) < 2:
                continue
            minutes = sorted(item[0] for item in events)
            # A within-day span is descriptive only. Do not wrap overnight into a presumed fast.
            recorded_spans.append(float(minutes[-1] - minutes[0]))

    daily_counts = [len(events) for events in events_by_day.values()]
    time_values = [minute for events in events_by_day.values() for minute, _ in events]
    center = _clock_medoid(time_values) if clock_comparable else None
    deviations = [float(_clock_distance(item, center)) for item in time_values] if center is not None else []
    source_ids = [record_id for events in events_by_day.values() for _, record_id in events if record_id]
    measure = "caregiver_feeding_events" if event_kind == "feeding" else "meal_events"
    summary_id = f"{event_kind}:{FEEDING_METHOD_VERSION}:{first_day.isoformat()}:{last_day.isoformat()}"
    return {
        **_summary_metadata(summary_id, subject_id, measure),
        "domain": "feeding" if event_kind == "feeding" else "nutrition",
        "label": event_type_label,
        "methodVersion": FEEDING_METHOD_VERSION,
        "revisionResolution": _revision_resolution_metadata(revision_resolution),
        "window": {"startDate": first_day.isoformat(), "endDate": last_day.isoformat(), "inclusiveDays": window_days},
        "inputRecordIds": sorted(set(source_ids)),
        "nEvents": event_count,
        "daysWithEvents": len(events_by_day),
        "coverage": _coverage(set(events_by_day), window_days),
        "medianEventsPerObservedDay": round(median(daily_counts), 1) if daily_counts else None,
        "medianEventClockTime": _format_clock(center),
        "medianAbsoluteEventTimeDeviationMinutes": round(median(deviations), 1) if deviations else None,
        "medianRecordedWithinDaySpanMinutes": round(median(recorded_spans), 1) if recorded_spans else None,
        "clockTimesComparable": clock_comparable,
        "clockTimeContextCount": len(clock_contexts),
        "clockTimeContexts": sorted(clock_contexts),
        "limitations": [
            "Summarizes logged events only; it does not establish that all meals or feeds were recorded.",
            "Within-day span is not a fasting interval and is not an eating-window recommendation.",
            "Does not infer appetite, calories, feeding adequacy, nutritional status, or hormone levels.",
            "Feeding mode includes caregiver reports only and is not an intake or feeding assessment.",
            "Day coverage means days with at least one matching log; it is not sensor or behavioral completeness.",
        ],
    }


def summarize_meal_timing_relative_to_wake(
    records: Iterable[dict[str, Any]],
    *,
    subject_id: str,
    start_date: str,
    end_date: str,
    max_interval_hours: float = 36.0,
) -> dict[str, Any]:
    """Describe logged meal timing within complete intervals between explicit wake events.

    A wake event anchors a behavioral day. Only meal events between one wake and
    the next recorded wake are included. Feeding events are excluded, including
    caregiver-reported infant feeds. The function does not infer fasting,
    completeness of meal logging, circadian phase, or an appropriate schedule.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    if not isfinite(max_interval_hours) or max_interval_hours <= 0:
        raise ValueError("max_interval_hours must be a finite number greater than zero")
    revision_resolution = _resolve_subject_history(records, subject_id)
    current_records = revision_resolution["currentRecords"]
    first_day, last_day, window_days = _window(start_date, end_date)
    subject_records = [
        record
        for record in current_records
        if record.get("subjectId") == subject_id
        and record.get("recordType") in {"observation", "event"}
    ]

    wakes: list[tuple[datetime, date, str]] = []
    meals: list[tuple[datetime, str]] = []
    for record in subject_records:
        event_type = record.get("eventType")
        if event_type not in {"wake", "meal"}:
            continue
        if event_type == "wake" and record.get("domain") not in {"sleep", "circadian"}:
            continue
        if event_type == "meal" and record.get("domain") not in {"feeding", "nutrition"}:
            continue
        time_data = record.get("time", {})
        stamp = time_data.get("observedAt") or time_data.get("start")
        if not stamp:
            continue
        observed_at = _localize(record, stamp)
        instant = observed_at.astimezone(timezone.utc)
        if event_type == "wake":
            wakes.append((instant, observed_at.date(), record.get("id", "")))
        else:
            meals.append((instant, record.get("id", "")))

    # Deduplicate identical wake instants, preserving one provenance ID. Without
    # this, a duplicated sync record could create a zero-length behavioral day.
    wakes_by_instant: dict[datetime, tuple[datetime, date, str]] = {}
    for wake in sorted(wakes, key=lambda item: item[0]):
        wakes_by_instant.setdefault(wake[0], wake)
    ordered_wakes = list(wakes_by_instant.values())
    meals.sort(key=lambda item: item[0])

    eligible_cycles: list[tuple[datetime, datetime, date, str, str, list[tuple[datetime, str]]]] = []
    excluded_gap_ids: set[str] = set()
    candidate_interval_count = 0
    for index, wake in enumerate(ordered_wakes[:-1]):
        start, wake_day, wake_id = wake
        next_start, _, next_wake_id = ordered_wakes[index + 1]
        if not first_day <= wake_day <= last_day or next_start <= start:
            continue
        candidate_interval_count += 1
        if (next_start - start).total_seconds() > max_interval_hours * 3600:
            excluded_gap_ids.update(record_id for record_id in (wake_id, next_wake_id) if record_id)
            continue
        cycle_meals = [meal for meal in meals if start <= meal[0] < next_start]
        eligible_cycles.append((start, next_start, wake_day, wake_id, next_wake_id, cycle_meals))

    intervals_with_meals = [cycle for cycle in eligible_cycles if cycle[5]]
    first_meal_delays = [
        (cycle[5][0][0] - cycle[0]).total_seconds() / 60
        for cycle in intervals_with_meals
    ]
    all_meal_delays = [
        (meal[0] - cycle[0]).total_seconds() / 60
        for cycle in eligible_cycles
        for meal in cycle[5]
    ]
    input_ids = {
        record_id
        for cycle in eligible_cycles
        for record_id in (cycle[3], cycle[4])
        if record_id
    }
    input_ids.update(
        record_id
        for cycle in eligible_cycles
        for _, record_id in cycle[5]
        if record_id
    )
    input_ids.update(excluded_gap_ids)
    observed_days = {cycle[2] for cycle in eligible_cycles}

    summary_id = f"meal-wake-relative:{WAKE_RELATIVE_METHOD_VERSION}:{first_day.isoformat()}:{last_day.isoformat()}"
    return {
        **_summary_metadata(summary_id, subject_id, "meal_timing_relative_to_wake"),
        "domain": "nutrition",
        "label": "logged meal timing relative to explicit wake events",
        "methodVersion": WAKE_RELATIVE_METHOD_VERSION,
        "revisionResolution": _revision_resolution_metadata(revision_resolution),
        "timeReference": "elapsed_minutes_from_explicit_wake_event",
        "window": {"startDate": first_day.isoformat(), "endDate": last_day.isoformat(), "inclusiveDays": window_days},
        "inputRecordIds": sorted(input_ids),
        "nWakeToWakeIntervals": len(eligible_cycles),
        "nCandidateWakeToWakeIntervals": candidate_interval_count,
        "nIntervalsExcludedForGap": candidate_interval_count - len(eligible_cycles),
        "maximumIntervalHours": max_interval_hours,
        "nIntervalsWithLoggedMeals": len(intervals_with_meals),
        "nLoggedMeals": len(all_meal_delays),
        "coverage": {
            "wakeDatesWithCompleteWakeToWakeInterval": len(observed_days),
            "calendarDaysInWindow": window_days,
            "fractionOfDaysWithCompleteInterval": round(len(observed_days) / window_days, 3) if window_days else 0.0,
        },
        "medianFirstLoggedMealMinutesAfterWake": round(median(first_meal_delays), 1) if first_meal_delays else None,
        "medianLoggedMealMinutesAfterWake": round(median(all_meal_delays), 1) if all_meal_delays else None,
        "limitations": [
            "Includes only explicit wake-to-next-wake intervals; intervals without a following recorded wake are excluded.",
            "Intervals longer than maximumIntervalHours are excluded as possible missing-wake gaps; the default is a data-quality rule, not a biological boundary.",
            "Meal records may be incomplete; the first logged meal is not necessarily the first meal eaten.",
            "Caregiver-reported feeding events are excluded and must not be interpreted with adult meal summaries.",
            "Elapsed time from waking is a behavioral reference, not endogenous circadian phase.",
            "Does not infer fasting, appetite, calories, nutrition adequacy, metabolic state, or a recommended schedule.",
        ],
    }


def summarize_numeric_measurements(
    records: Iterable[dict[str, Any]], *, subject_id: str, start_date: str, end_date: str,
    analyte_or_signal: str, bucket_days: int = 7,
) -> list[dict[str, Any]]:
    """Summarize repeated numeric records without interpreting their biology.

    Results are split by domain, explicit unit, epistemic class, and exact
    source/method signature. Date-only records retain their stated date; timed
    records use local date where a valid time zone is supplied. This reports
    sample distributions and fixed-width calendar-bucket distributions. Empty
    buckets are visible as missing coverage, not imputed values. The summary
    fits no trend or personal baseline and estimates no latent state or cause.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    if not isinstance(analyte_or_signal, str) or not analyte_or_signal.strip():
        raise ValueError("analyte_or_signal is required")
    if isinstance(bucket_days, bool) or not isinstance(bucket_days, int) or not 1 <= bucket_days <= 366:
        raise ValueError("bucket_days must be an integer from 1 through 366")
    revision_resolution = _resolve_subject_history(records, subject_id)
    first_day, last_day, window_days = _window(start_date, end_date)
    if (window_days + bucket_days - 1) // bucket_days > 1000:
        raise ValueError("the requested window would create more than 1000 measurement buckets")
    groups: dict[tuple[Any, ...], list[tuple[date, dict[str, Any], float]]] = {}
    eligible_classes = {"measured", "derived", "imported"}

    for record in revision_resolution["currentRecords"]:
        if record.get("subjectId") != subject_id or record.get("epistemicClass") not in eligible_classes:
            continue
        value = record.get("value")
        details = record.get("measurementDetails")
        if not isinstance(value, dict) or not isinstance(details, dict):
            continue
        number, unit = value.get("number"), value.get("unit")
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not isfinite(number):
            continue
        if not isinstance(unit, str) or not unit.strip() or details.get("analyteOrSignal") != analyte_or_signal:
            continue
        if record.get("recordType") not in {"observation", "event"}:
            continue
        time_data = record.get("time", {})
        if not isinstance(time_data, dict):
            continue
        try:
            if time_data.get("precision") == "date_only":
                observed_day = date.fromisoformat(time_data["date"])
            else:
                stamp = time_data.get("observedAt") or time_data.get("start")
                if not stamp:
                    continue
                observed_day = _localize(record, stamp).date()
        except (KeyError, TypeError, ValueError):
            continue
        if not first_day <= observed_day <= last_day:
            continue
        source = record.get("source", {})
        if not isinstance(source, dict) or not isinstance(record.get("domain"), str):
            continue
        signature = {
            "analyteOrSignal": analyte_or_signal,
            "unit": unit,
            "epistemicClass": record["epistemicClass"],
            **{
                "sourceKind": source.get("kind", "unspecified"),
                "sourceName": source.get("name", "unspecified"),
                "sourceMethod": source.get("method", "unspecified"),
                "sourceVersion": source.get("version", "unspecified"),
                "methodDetails": record.get("methodDetails", "unspecified"),
                **{field: details.get(field, "unspecified") for field in _MEASUREMENT_SIGNATURE_FIELDS[5:]},
            },
        }
        key = (record.get("domain"), *(signature[field] for field in ("analyteOrSignal", "unit", "epistemicClass", *_MEASUREMENT_SIGNATURE_FIELDS)))
        groups.setdefault(key, []).append((observed_day, record, float(number)))

    summaries: list[dict[str, Any]] = []
    for key, observations in sorted(groups.items(), key=lambda item: tuple(str(value) for value in item[0])):
        domain = key[0]
        values = [item[2] for item in observations]
        med = median(values)
        mad = median([abs(value - med) for value in values])
        observed_days = {item[0] for item in observations}
        flags = sorted({
            flag
            for _, record, _ in observations
            for flag in (record.get("measurementDetails", {}).get("qualityFlags", []) if isinstance(record.get("measurementDetails", {}).get("qualityFlags", []), list) else [])
            if isinstance(flag, str) and flag
        })
        signature = {
            "analyteOrSignal": analyte_or_signal,
            "unit": key[2],
            "epistemicClass": key[3],
            **{field: key[4 + index] for index, field in enumerate(_MEASUREMENT_SIGNATURE_FIELDS)},
        }
        signature_hash = sha256(repr((domain, tuple(signature.items()))).encode("utf-8")).hexdigest()[:12]
        bucket_groups: dict[int, list[tuple[date, dict[str, Any], float]]] = {}
        for item in observations:
            bucket_index = (item[0] - first_day).days // bucket_days
            bucket_groups.setdefault(bucket_index, []).append(item)
        time_buckets = []
        for bucket_index, offset in enumerate(range(0, window_days, bucket_days)):
            bucket_start = first_day + timedelta(days=offset)
            bucket_end = min(last_day, bucket_start + timedelta(days=bucket_days - 1))
            bucket_items = bucket_groups.get(bucket_index, [])
            bucket_values = [item[2] for item in bucket_items]
            bucket_dates = {item[0] for item in bucket_items}
            bucket_median = median(bucket_values) if bucket_values else None
            bucket_mad = median([abs(value - bucket_median) for value in bucket_values]) if bucket_values else None
            bucket_flags = sorted({
                flag
                for _, record, _ in bucket_items
                for flag in (record.get("measurementDetails", {}).get("qualityFlags", []) if isinstance(record.get("measurementDetails", {}).get("qualityFlags", []), list) else [])
                if isinstance(flag, str) and flag
            })
            bucket_window_days = (bucket_end - bucket_start).days + 1
            time_buckets.append({
                "startDate": bucket_start.isoformat(),
                "endDate": bucket_end.isoformat(),
                "inclusiveDays": bucket_window_days,
                "inputRecordIds": sorted({record["id"] for _, record, _ in bucket_items if isinstance(record.get("id"), str)}),
                "nMeasurements": len(bucket_values),
                "nDistinctMeasurementDates": len(bucket_dates),
                "medianValue": round(bucket_median, 6) if bucket_median is not None else None,
                "medianAbsoluteDeviationValue": round(bucket_mad, 6) if bucket_mad is not None else None,
                "minimumValue": min(bucket_values) if bucket_values else None,
                "maximumValue": max(bucket_values) if bucket_values else None,
                "recordsWithQualityFlags": sum(
                    bool(record.get("measurementDetails", {}).get("qualityFlags"))
                    for _, record, _ in bucket_items
                    if isinstance(record.get("measurementDetails", {}).get("qualityFlags", []), list)
                ),
                "qualityFlags": bucket_flags,
                "daysWithAtLeastOneRecord": len(bucket_dates),
                "fractionOfDaysWithARecord": round(len(bucket_dates) / bucket_window_days, 6),
            })
        summary_id = f"measurement-series:{MEASUREMENT_SERIES_METHOD_VERSION}:{first_day.isoformat()}:{last_day.isoformat()}:{bucket_days}:{signature_hash}"
        summaries.append({
            **_summary_metadata(summary_id, subject_id, "measurement_series"),
            "domain": domain,
            "label": f"descriptive series for {analyte_or_signal} ({signature['unit']})",
            "methodVersion": MEASUREMENT_SERIES_METHOD_VERSION,
            "revisionResolution": _revision_resolution_metadata(revision_resolution),
            "window": {"startDate": first_day.isoformat(), "endDate": last_day.isoformat(), "inclusiveDays": window_days},
            "bucketDays": bucket_days,
            "timeBuckets": time_buckets,
            "inputRecordIds": sorted({record["id"] for _, record, _ in observations if isinstance(record.get("id"), str)}),
            "measurementSeries": signature,
            "nMeasurements": len(values),
            "nDistinctMeasurementDates": len(observed_days),
            "medianNumericValue": round(med, 6),
            "medianAbsoluteDeviationValue": round(mad, 6),
            "minimumValue": min(values),
            "maximumValue": max(values),
            "recordsWithQualityFlags": sum(
                bool(record.get("measurementDetails", {}).get("qualityFlags"))
                for _, record, _ in observations
                if isinstance(record.get("measurementDetails", {}).get("qualityFlags", []), list)
            ),
            "qualityFlags": flags,
            "coverage": _coverage(observed_days, window_days),
            "limitations": [
                "Describes only eligible numeric records present in the selected subject history; missing records are not evidence that no measurement occurred.",
                "Series are kept separate by domain, unit, epistemic class, source, method, specimen, device, and collection signature.",
                "Median, spread, minimum, and maximum are descriptive statistics, not clinical reference-range judgments or personal baselines.",
                "Fixed-width date buckets anchored to the selected start date show descriptive summaries for each interval, including empty intervals; they are not a fitted trend, cycle phase, or response estimate.",
                "Does not estimate hormone or neurochemical state, infer a trend or cause, or recommend an action.",
            ],
        })
    return summaries
