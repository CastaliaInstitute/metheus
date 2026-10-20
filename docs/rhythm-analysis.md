# First executable Metheus rhythm summaries

**Status:** prototype, version 0.1. The standard-library functions in [`metheus/rhythms.py`](../metheus/rhythms.py) summarize selected event records. They do not perform circadian physiology, nutritional, endocrine, sleep-quality, or developmental assessment.

## Implemented summaries

### Main sleep

`summarize_main_sleep(records, subject_id=..., start_date=..., end_date=...)` accepts records explicitly marked `eventType: "main_sleep"`, `domain: "sleep"`, with start and end timestamps. It returns:

- number of intervals and days with at least one interval in the inclusive date window;
- median logged duration;
- median logged start and midpoint clock times, using a circular medoid so times near midnight are handled correctly;
- median absolute deviation of logged midpoint clock times;
- input record IDs, declared coverage, method version, and limitations.

This is a summary of logged main-sleep intervals. It is **not** circadian-phase estimation, a sleep-quality score, or a judgment about schedule adequacy. Nap and generic sleep-episode events are excluded unless the source explicitly classifies an interval as `main_sleep`.

### Meals and caregiver-reported feeds

`summarize_feeding_events(records, subject_id=..., start_date=..., end_date=...)` summarizes explicitly logged `meal` events. It reports event counts, days with events, median events per observed day, typical clock time, variation in event clock time, and median within-day span for days with at least two events.

Set `include_infant_feeds=True` only when a caregiver explicitly requests a combined summary. This additionally includes `feeding` events only when their epistemic class is `caregiver_reported`. These are feed logs, not a measure of infant intake or adequacy.

The reported within-day span is **not** an inferred fasting duration or a recommended eating window. Missing meal/feed records do not show that no meal/feed occurred. The functions do not calculate calories, infer appetite, assess nutrition, or infer hormone levels.

## Time and subject handling

- A `subject_id` is required. Records for other subjects are ignored before aggregation.
- Timestamps must include an explicit UTC offset. If `time.timeZone` is a valid IANA zone, it is used to interpret local clock time and daylight-saving changes; otherwise the supplied offset is used.
- Durations are computed on the UTC timeline. Clock-time summaries are suppressed when inputs use more than one time-zone context because those local clock times are not directly comparable.
- Date windows are inclusive and are evaluated using each record's local date.
- Summary IDs are deterministic for domain, method version, and date window. Storage identity must scope that ID by `subjectId`; the identifier itself contains no subject key.
- Day coverage counts dates with at least one matching log. It does not estimate sensor uptime or completeness of the underlying behavior.

## Example input

```json
{
  "id": "sleep-2026-10-18",
  "subjectId": "local-subject-7f23",
  "recordType": "observation",
  "eventType": "main_sleep",
  "epistemicClass": "derived",
  "time": {
    "start": "2026-10-18T23:12:00-06:00",
    "end": "2026-10-19T06:48:00-06:00",
    "timeZone": "America/Denver",
    "precision": "approximate",
    "scale": "interval"
  },
  "source": { "kind": "algorithm", "name": "example wearable", "method": "sleep interval estimate", "version": "device-firmware-example" },
  "domain": "sleep",
  "label": "main sleep interval",
  "derivedFrom": ["sleep-sensor-observations-for-2026-10-18"],
  "methodVersion": "device-firmware-example",
  "uncertainty": { "level": "moderate", "notes": "device-estimated interval" }
}
```

The record is illustrative. It contains no health conclusion. Because the device estimated the interval from lower-level sensor observations, the example classifies it as `derived` and keeps its source records and method version.

## Using the functions

```python
from metheus import summarize_feeding_events, summarize_main_sleep

sleep_summary = summarize_main_sleep(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-10-12",
    end_date="2026-10-18",
)
meal_summary = summarize_feeding_events(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-10-12",
    end_date="2026-10-18",
)
```

These function outputs are **derived feature summaries**, not persisted observation records. If a future reading refers to one, it should cite the returned `summaryId`, `methodVersion`, and `inputRecordIds`. The subject, chosen window, coverage, and limitations must remain attached. A future storage adapter can map each numeric feature into the observation schema once feature-level units and validity rules are reviewed.

## Current boundary

This prototype computes descriptive timing summaries only. It does not yet calculate light-based circadian phase, model endocrine dynamics, join multiple rhythms, estimate personal baselines, generate readings, or store any data. Those require separate, reviewed methods and must not be implied by these functions.
