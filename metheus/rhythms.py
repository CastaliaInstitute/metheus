"""Descriptive rhythm summaries for Metheus observation records.

These functions summarize logged events. They do not estimate hormones,
diagnose conditions, infer causation, or evaluate whether a schedule is healthy.
All timestamps must be ISO 8601 values with an explicit UTC offset.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from statistics import median
from typing import Any, Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


METHOD_VERSION = "metheus-rhythm-summary/0.1.0"


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
    first_day, last_day, window_days = _window(start_date, end_date)
    eligible: list[tuple[datetime, float, datetime, str]] = []
    clock_contexts: set[str] = set()

    for record in records:
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
        "summaryId": _summary_id("sleep", first_day, last_day),
        "subjectId": subject_id,
        "summaryType": "derived_rhythm_summary",
        "epistemicClass": "derived",
        "domain": "sleep",
        "label": "logged main-sleep timing summary",
        "methodVersion": METHOD_VERSION,
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
        "limitations": [
            "Summarizes logged intervals only; missing logs are not evidence that sleep did not occur.",
            "Clock-time summary is not an estimate of endogenous circadian phase.",
            "Does not assess sleep quality, health, or whether this schedule is appropriate.",
            "Clock time uses the record's IANA time zone when valid, otherwise its supplied UTC offset; callers should retain source time-zone metadata.",
        ],
    }


def summarize_feeding_events(
    records: Iterable[dict[str, Any]], *, subject_id: str, start_date: str, end_date: str, include_infant_feeds: bool = False
) -> dict[str, Any]:
    """Summarize logged meal timing, or caregiver-reported infant feeds.

    By default, only eventType=meal is included. Infant feeding records require
    explicit opt-in and eventType=feeding. The result never estimates calories,
    fasting duration, adequacy, hunger, or nutritional status.
    """
    if not subject_id:
        raise ValueError("subject_id is required to prevent cross-subject aggregation")
    first_day, last_day, window_days = _window(start_date, end_date)
    allowed = {"meal", "feeding"} if include_infant_feeds else {"meal"}
    events_by_day: dict[date, list[tuple[int, str]]] = {}
    clock_contexts: set[str] = set()

    for record in records:
        if record.get("subjectId") != subject_id:
            continue
        if record.get("recordType") not in {"observation", "event"}:
            continue
        event_type = record.get("eventType")
        if event_type not in allowed:
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

    event_type_label = (
        "logged meal and caregiver-reported feeding events"
        if include_infant_feeds
        else "logged meal events"
    )
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
    return {
        "summaryId": _summary_id("feeding", first_day, last_day),
        "subjectId": subject_id,
        "summaryType": "derived_rhythm_summary",
        "epistemicClass": "derived",
        "domain": "feeding" if include_infant_feeds else "nutrition",
        "label": event_type_label,
        "methodVersion": METHOD_VERSION,
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
        "limitations": [
            "Summarizes logged events only; it does not establish that all meals or feeds were recorded.",
            "Within-day span is not a fasting interval and is not an eating-window recommendation.",
            "Does not infer appetite, calories, feeding adequacy, nutritional status, or hormone levels.",
            "Infant feed mode is caregiver-report context only and is not a feeding assessment.",
            "Day coverage means days with at least one matching log; it is not sensor or behavioral completeness.",
        ],
    }
