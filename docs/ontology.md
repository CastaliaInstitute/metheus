# Metheus ontology: core concepts

**Status:** working draft, version 0.1. This vocabulary is intended to guide future storage and reading logic. It is not a clinical ontology, diagnostic vocabulary, or claim that all listed domains should be collected.

## Modeling commitments

1. A person is a changing, situated system; a profile is only a partial representation.
2. Time, source, and uncertainty are part of every observation, not optional metadata.
3. A measured value, a person's account, a caregiver's observation, a derived estimate, and a symbolic feature are different entity types.
4. A reading is an interpretation over selected evidence, with provenance back to its inputs.
5. Missing data are meaningful as missingness, not as zero, absence, or permission to guess.
6. A relationship is not an object that one person may fully describe on behalf of another. Store a person's own experience and minimize third-party identifiers.

## Core entities

| Entity | Meaning | Examples |
|---|---|---|
| **Subject** | Person whose life or observations are represented | Self, infant/child represented by a guardian, participant in a reading |
| **Profile context** | Relatively stable, revisable information | Birth data, time zone, preferred units, optional life context |
| **Symbolic map** | Features defined by a named interpretive system | Human Design type/profile/gates, calculation inputs, source/version |
| **Observation** | A dated measurement or report of something observed | Temperature reading, sleep interval, reported pain, caregiver-observed feeding |
| **Event** | A dated occurrence that can contextualize observations | Travel, period start, birth, relationship transition, medication change |
| **Estimate** | A derived quantity or phase computed from inputs | Cycle-day estimate, sleep midpoint, deviation from personal baseline |
| **Development context** | Age/stage information and optional developmental observations | Gestational/chronological age, corrected age if supplied, milestone note |
| **Relationship context** | A subject's account of a relationship or interaction | Felt closeness, a personally noted intimacy event, caregiving relation |
| **Reading** | A time-bounded interpretation generated from selected inputs | A reflective prompt with claims, sources, confidence, and revision history |
| **Consent and access policy** | Who may collect, view, share, export, or delete a record | Self-controlled, guardian-managed, child assent/voice increases over time |

## Epistemic classes

Every record MUST have one class:

- `measured`: sensor or laboratory result. Include method, units, and instrument when known.
- `self_reported`: the subject's account of their own experience.
- `caregiver_reported`: a caregiver's observation or account about a child or dependent.
- `clinician_reported`: a clinician-provided finding or interpretation. Preserve its author/source and date.
- `derived`: a calculation based on named inputs and a method/version.
- `symbolic`: a feature or meaning defined by a symbolic system; include system and version.
- `imported`: a record from an external source whose original class is not known; preserve original source and avoid upgrading its certainty.

Do not combine distinct classes into one unlabeled score. An interpretation may cite several classes, but each underlying input remains separately inspectable.

## Temporal model

Use a single event/observation timeline while retaining multiple timescales:

| Timescale | Examples |
|---|---|
| Instant / interval | HRV sample, a meal, a waking, pain interval |
| Ultradian | Sleep-stage cycles, hormone pulses, feeding bouts |
| Circadian | Light exposure, sleep-wake timing, daily temperature variation |
| Multi-day / weekly | Work/rest sequences, recovery, social routines |
| Reproductive / monthly | Bleeding observations, cycle estimates, symptoms |
| Developmental | Growth and changing skills, puberty, postpartum transitions |
| Life-course | Birth, menopause, caregiving changes, aging, major life events |

Store timestamps in an unambiguous format with offset/time zone when available. For intervals, distinguish start and end. For recurring patterns, store the observation window, method, and coverage. Do not force events into conventional clock-time buckets.

## Rhythm concepts

- **Rhythm event:** an occurrence such as lights-out, waking, a meal, feeding, activity, or symptom.
- **Rhythm series:** repeated events or measurements grouped by a declared rule and time window.
- **Phase estimate:** an estimated position in a rhythm, such as an inferred sleep phase or menstrual-cycle day. Always carry method and uncertainty.
- **Regularity:** a summary of variation in timing or interval, never a moralized “good/bad” label.
- **Baseline:** a subject-specific reference computed from an explicit window and adequate coverage. Baseline changes over development and circumstance; do not imply a permanent norm.
- **Alignment / co-variation:** temporal relation between two series. This may suggest a question but does not demonstrate causation.
- **Missingness:** absent or unavailable observations, with reason only when known (not tracked, device off, declined, unknown).

The observation schema uses `eventType` to distinguish `main_sleep`, `sleep_episode`, `nap`, `meal`, `feeding`, `light_exposure`, `activity`, `bleeding_start`, and other point or interval events. `main_sleep` is a person's or data-source's designation for the principal sleep interval in a cycle; it is not inferred automatically from clock time. A `meal` event is a logged meal, not proof that all food intake was logged. A `feeding` event is separate and may represent caregiver-reported infant feeding; adult meal-window and fasting summaries must never be applied to infant feeds. A device-derived event must use `epistemicClass: "derived"` and preserve its method and source records, even if the originating sensor measurements were direct.

## Reading model

A reading is a versioned object with:

- the person's question or purpose;
- the time window and life-stage context considered;
- selected input record identifiers;
- claims or prompts, each labeled as observation, estimate, symbolic interpretation, or hypothesis;
- the rationale and relevant alternative explanations;
- confidence/coverage limits;
- generation time, model/rule version, and revision history;
- subject feedback such as “resonates,” “does not fit,” or “uncertain,” without treating that feedback as validation of a causal claim.

## Relationship and intimacy boundary

Relationship events are optional and belong to the subject's perspective. A personal record may represent that the subject chose to note an interaction or how they experienced it. It MUST NOT infer or assert another person's consent, desire, emotional state, health, or compatibility. Do not collect identifiable partner data without that person's informed participation. Do not treat intimacy timing alongside a hormonal estimate as proof that hormones caused desire or behavior.

## Development and child boundary

For a child, identify who made each observation and distinguish caregiver report from direct measurement and clinical assessment. Developmental markers are descriptive prompts, not a score or prediction. Keep the child's data private, minimal, exportable, and deletable; design for the child's increasing voice, assent, and control. Do not infer hormone/neurochemical levels, attachment security, diagnosis, or future ability from sleep, crying, feeding, temperament, or a single milestone.

## Draft JSON Schema

The machine-readable starter is [`../schema/observation.schema.json`](../schema/observation.schema.json). It defines one record at a time and intentionally avoids a complete person profile. A future profile/container schema should reference records rather than embed all sensitive history in a single object.

## Open design questions

- Which fields are required for a useful record without pressuring users to overshare?
- How should the system represent uncertain dates, approximate birth times, calendar changes, and retrospective notes?
- Which rhythm summaries are transparent and understandable to a person without implying clinical significance?
- How should adult self-control transition to child assent and then independent control?
- Which symbolic systems and licensed source materials can be represented, with what provenance and versioning?
- What review and evidence thresholds are needed before any generated biological interpretation is shown?
