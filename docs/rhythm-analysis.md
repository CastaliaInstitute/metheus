# First executable Metheus rhythm summaries

**Status:** prototype, version 0.1. The standard-library functions in [`metheus/rhythms.py`](../metheus/rhythms.py) summarize selected event records. They do not perform circadian physiology, nutritional, endocrine, sleep-quality, or developmental assessment.

Before filtering by date or event type, each summary resolves visible same-subject `supersedes` chains and excludes prior revisions. Supply the broadest available subject history. Each summary reports the number of visible prior revisions excluded and unresolved predecessor links in `revisionResolution`; cycles, branches, and duplicate IDs cause the summary to fail closed. See the [record lifecycle rules](record-lifecycle.md).

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

`summarize_feeding_events(records, subject_id=..., start_date=..., end_date=..., event_kind="meal")` summarizes one event class at a time. `event_kind="meal"` summarizes explicitly logged meal events; `event_kind="feeding"` summarizes caregiver-reported feeding events. The schema does not establish age or clinical feeding context, so the output must not label a record “infant” unless that context is separately and explicitly supplied. It reports event counts, days with events, median events per observed day, typical clock time, variation in event clock time, and median within-day span for days with at least two events.

Meal and caregiver-reported feeding events are never combined in one statistic. Feeding summaries include only `feeding` events whose epistemic class is `caregiver_reported`. These are event logs, not a measure of intake or adequacy.

The reported within-day span is **not** an inferred fasting duration or a recommended eating window. Missing meal/feed records do not show that no meal/feed occurred. The functions do not calculate calories, infer appetite, assess nutrition, or infer hormone levels.

### Meal timing relative to waking

`summarize_meal_timing_relative_to_wake(records, subject_id=..., start_date=..., end_date=..., max_interval_hours=36.0)` compares logged `meal` events with explicit `wake` events. Wake records must use `eventType: "wake"` and domain `sleep` or `circadian`. The function measures elapsed minutes between wake timestamps on the UTC timeline, and reports the median time to the **first logged** meal per complete wake-to-next-wake interval plus the median time of all logged meals relative to wake.

Only intervals with a following explicit wake event are considered, so the final wake in a dataset is not summarized until its next wake is recorded. Intervals longer than `max_interval_hours` are excluded as possible missing-wake gaps; the 36-hour default is a data-quality heuristic, not a biological boundary. The date window selects the local date of the interval's starting wake. Caregiver-reported `feeding` events are always excluded; infant feeding must not be analyzed as adult meal timing. This is behavioral timing, not a biological circadian phase estimate.

Example wake record:

```json
{
  "id": "wake-2026-10-18",
  "subjectId": "local-subject-7f23",
  "recordType": "event",
  "eventType": "wake",
  "epistemicClass": "self_reported",
  "time": {
    "observedAt": "2026-10-18T06:30:00-06:00",
    "timeZone": "America/Denver",
    "precision": "approximate",
    "scale": "circadian"
  },
  "source": { "kind": "subject", "reportedByRelation": "self" },
  "domain": "sleep",
  "label": "woke for the day"
}
```

Use the function from the package:

```python
from metheus import summarize_meal_timing_relative_to_wake

summary = summarize_meal_timing_relative_to_wake(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-10-12",
    end_date="2026-10-18",
)
```

### Gaps between logged bleeding-onset dates

`summarize_bleeding_onset_intervals(records, subject_id=..., start_date=..., end_date=...)` describes calendar-day gaps between adjacent, explicitly logged `bleeding_start` dates, assigning each gap to its later onset date in the selected window. Candidate events must belong to the requested subject, use `domain: "reproductive"`, and satisfy the observation/event schema; symbolic, derived, and schema-invalid events are excluded. Duplicate records on the same local date are grouped as one onset date. If an earlier onset is available before the window, the nearest such date is included as a `boundaryOnsetDate` and its source IDs are listed separately in `boundaryOnsetRecordIds`; those IDs are also part of `inputRecordIds` and require their own authorization. The boundary record is not counted in the in-window onset and precision counts. Incomplete history may omit earlier events, so the nearest logged date is not necessarily the person's actual previous onset.

The output calls these **gaps between logged bleeding-onset dates**, not menstrual-cycle lengths. Bleeding may have different causes, entries may be missing, and the summary does not infer ovulation, hormone phase, fertility, pregnancy, menopause stage, diagnosis, or a future onset. Intervals ending inside the selected window may use one explicitly identified earlier boundary onset outside it.

Date-only reports use `time.date` with `precision: "date_only"`; see the [synthetic date-only bleeding-onset record](../examples/bleeding-onset.example.json) and [windowed summary with a boundary input](../examples/bleeding-onset-summary.example.json).

### Intervals between a person's marked menstrual cycle day-one dates

`menstrual_cycle_day_one` is a distinct, self-reported event: the person explicitly marks a date as day one for their own cycle tracking. It is never inferred from a generic `bleeding_start` record. The common convention that cycle day one is the first day of menstrual bleeding is described by the [NHS](https://www.nhs.uk/conditions/periods/fertility-in-the-menstrual-cycle/) and [ACOG](https://www.acog.org/womens-health/faqs/your-first-period); Metheus preserves the marker as the person's own report rather than verifying its clinical meaning.

`summarize_reported_cycle_day_one_intervals(records, subject_id=..., start_date=..., end_date=...)` reports calendar-day differences between adjacent, current, schema-valid, self-reported cycle day-one markers. Each interval is assigned to its later marker date in the inclusive window. If available, the nearest earlier marker is included as an explicitly named boundary input. The result labels the dates and interval as reported, includes only the selected source IDs, and returns no intervals when fewer than two usable markers are present. Date-only records remain date-only; timestamped records use their local calendar date.

This is a descriptive organizer for a person's chosen markers. It does not infer cycle day from other records, judge regularity or health, determine whether bleeding was menstrual, predict a next date, or infer ovulation, fertility, conception, phase, or hormone levels. Missing logs and changes in marker convention can affect the series. See the four synthetic [cycle day-one event examples](../examples/menstrual-cycle-day-one-2026-09-02.example.json) and the [summary example](../examples/menstrual-cycle-day-one-summary.example.json).

### View selected records by reported cycle day

`describe_authorized_reported_cycle_day_view(records, grants, subject_id=..., cycle_day_one_record_ids=..., observation_record_ids=...)` maps each explicitly selected, current, same-subject observation/event to a calendar-day offset from the latest selected self-reported `menstrual_cycle_day_one` marker. Day one is the marker's local calendar date; the next date is day two. Date-only records remain date-only, and timestamped records use the source time zone's local calendar date. The latest marker is shown as an open reported interval until another marker is selected and reported. Its method version is `metheus-reported-cycle-day-view/0.1.0`.

Every marker and observation must be separately selected and covered by an active `rhythm_summary` / `analyze` grant before any view is returned. The helper emits identifiers, local dates, precision, reported-day offsets, and whether a date falls between selected markers or after the latest one, along with each selected record's label, domain, epistemic class, source, known measurement-method fields, and optional value object. Values may contain sensitive text, and source details may identify a device or service. The view includes an unsigned, value-free consent-preflight receipt mapping every source record ID to the matching grant ID. It records the local policy decision; it does not authenticate a subject/grantor or prove legal authority. The PWA displays that limitation. The method does not fill gaps, infer unselected markers, or classify hormonal/cycle phases. See the synthetic [reported cycle-day view](../examples/reported-cycle-day-view.example.json).

The local CLI writes the authorized view file for the PWA without a server or upload:

```sh
python tools/build_reported_cycle_day_view.py \
  --records ./records.json \
  --grants ./grants.json \
  --subject-id local-subject-7f23 \
  --marker-id cycle-day-one-2026-10-01 \
  --marker-id cycle-day-one-2026-10-30 \
  --observation-id hrv-2026-10-12 \
  --output ./reported-cycle-day-view.json
```

The records and grants inputs may be JSON arrays or objects containing `records` and `grants` arrays. Every grant must satisfy the consent schema, and the analysis helper requires active consent for every explicitly selected record. The CLI creates a new output file with owner-only permissions and refuses to overwrite an existing file. If `--output` is omitted, the JSON is written to stdout for piping. A view includes each selected record's label, domain, epistemic class, source, known measurement-method fields, and optional value object so the display remains interpretable; values may contain sensitive text, and source details may identify a device or service. Keep the generated view private and select only the records needed.

### Repeated numeric measurement series

`summarize_numeric_measurements` groups numeric observations by exact analyte/signal, unit, domain, epistemic class, and source/method signature. It reports the sample count, distinct observed dates, median, median absolute deviation, minimum, maximum, quality-flag coverage, and dates with at least one record. It also partitions the requested date window into contiguous, fixed-width date buckets anchored at the selected `start_date` (`bucket_days`, default 7; range 1–366) and reports the same descriptive statistics and coverage for every bucket, including buckets with no measurements. The final bucket is clipped to the requested `end_date`. Bucket input-record IDs provide per-bucket provenance, and the union of those IDs must match the summary's overall input IDs. The bucket width is an explicit display/aggregation choice, not a calendar week or biological period. Records from different assays, devices, algorithms, specimens, methods, or collection conditions remain in separate summaries. Missing signature fields are represented as `unspecified`; they are never treated as equivalent to a known method.

The function requires an explicitly named signal and an inclusive date window. It resolves same-subject revision chains first and carries the current input record IDs into each result. It excludes symbolic, self-reported, and caregiver-reported values; only measured, imported, and derived numeric records with an explicit unit are eligible. Empty buckets remain explicitly empty; the function never interpolates missing values. If the whole window has no eligible measurement for the requested signal, it returns no series objects; that means no eligible series was observed, not a zero-valued series. This operation describes a recorded series only: it does not decide whether the values are clinically normal, fit a trend or personal baseline, infer hormone/neurochemical state, or explain behavior. The [synthetic measurement-series example](../examples/measurement-series-summary.example.json) illustrates the output contract.

### Temporal order between two records

`describe_temporal_order(records, subject_id=..., left_record_id=..., right_record_id=..., phase_annotations=...)` compares the recorded windows for two current same-subject observations, events, estimates, contexts, or phase annotations. Selected endpoint records must satisfy their declared JSON Schemas, including the evidence-basis rules for method-derived cycle estimates. It returns a typed relation (`precedes`, `follows`, `overlaps`, `same_instant`, `same_calendar_date`, or `indeterminate`) and a gap only when the time basis supports one. A `gapBasis` field distinguishes elapsed duration from calendar-date difference. Timestamped windows are compared on the UTC timeline; date-only windows compare only with date-only windows. Mixed precision, missing/invalid time, and open-ended phase windows produce `indeterminate`. Boundary-touching timestamp windows count as ordered with a zero gap.

This is a descriptive helper, not a stored subject record; callers must authorize the source records before using it. `describe_phase_observation_relations` applies it to the explicit Cartesian product of selected source-record IDs and phase-annotation IDs, with a default maximum of 500 pairs. Both inputs must be current, same-subject records; neither the phase nor source list is expanded from the subject index. Every output carries each endpoint's record type, domain, epistemic class, and any phase layer/system/canonical label, so a measured Epimethean observation remains visibly distinct from a symbolic Promethean transit. The relation remains strictly temporal: it does not infer biological phase, co-occurrence mechanism, within-person association, or causation. Approximate source times retain their uncertainty, and every output carries limitations. The [temporal relation schema](../schema/temporal-relation.schema.json) defines each result; see the [generic temporal-order example](../examples/temporal-order.example.json) and [phase-observation example](../examples/phase-observation-relation.example.json).

For a selected exposure-to-response timeline, `describe_selected_temporal_relations(records, subject_id=..., left_record_ids=..., right_record_ids=..., phase_annotations=...)` compares an explicit cross product of two record sets, including behavior events, sensory exposures, measurements, symptoms, and phase annotations. It applies the same 500-pair default bound and current same-subject rule. For example, a person may choose one aroma exposure and several of their own later observations to see which recorded windows precede, overlap, or follow it. The output remains pairwise temporal order: it does not calculate an effect size, within-person association, hormone response, or causal effect. The caller must authorize every source before comparison.

Use the function from the package:

```python
from metheus import summarize_bleeding_onset_intervals

summary = summarize_bleeding_onset_intervals(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-01-01",
    end_date="2026-10-31",
)
```


## Time and subject handling

- A `subject_id` is required. Records for other subjects are ignored before aggregation.
- Timed values must include an explicit UTC offset. If `time.timeZone` is a valid IANA zone, it is used to interpret local clock time and daylight-saving changes; otherwise the supplied offset is used. Date-only bleeding-onset reports use an explicit `time.date` field and are not assigned an artificial time of day.
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
from metheus import (
    summarize_bleeding_onset_intervals,
    summarize_feeding_events,
    summarize_main_sleep,
    summarize_numeric_measurements,
)

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
bleeding_gap_summary = summarize_bleeding_onset_intervals(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-01-01",
    end_date="2026-10-31",
)
heart_rate_series = summarize_numeric_measurements(
    records,
    subject_id="local-subject-7f23",
    start_date="2026-10-12",
    end_date="2026-10-18",
    analyte_or_signal="heart_rate",
)
```

These function outputs are **versioned derived rhythm-summary resources**, not ordinary observations. Each has `id` (equal to the compatibility field `summaryId`), `recordType: rhythm_summary`, `schemaVersion`, `summaryMeasure`, `methodVersion`, `inputRecordIds`, chosen window, coverage, metrics, and limitations. The [`rhythm summary schema`](../schema/rhythm-summary.schema.json) defines the output contract. A subject index may reference the summary only when every input event is also indexed as an observation and matches the declared measure. A selected numeric-series summary carries its fixed-width buckets and per-bucket source IDs through reading assembly; the HTML renderer labels these as descriptive measurement summaries and displays the method/signature, window, coverage, and limitations. The [synthetic sleep-summary set](../examples/rhythm-summary-reading.example.json) and [numeric-series assembled reading](../examples/assembled-reading-measurement-series.example.json) illustrate the separate paths.

Selecting a summary for a reading requires selecting its `inputRecordIds` too. Both the derived summary and every source event require their own active consent coverage; the summary does not inherit its inputs' permission. The current code returns summaries in memory and does not persist them. No automatic reading-text generation or storage adapter is implemented.

## Current boundary

This prototype computes descriptive timing summaries, same-signature numeric measurement series, and an in-memory temporal-order description. It does not calculate light-based circadian phase, infer menstrual phase or ovulation, model endocrine dynamics, estimate personal baselines, generate readings, or store any data. Those require separate, reviewed methods and must not be implied by these functions.
