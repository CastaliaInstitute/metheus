# Metheus capability matrix

**Status:** implementation inventory, version 0.1. This matrix separates the intended system from what the repository can currently represent or execute. “Recordable” means a schema can describe synthetic or caller-supplied data; it does not mean Metheus collects, stores, imports, or protects personal data.

## Maturity terms

- **Concept:** described in project documentation.
- **Contract:** a JSON Schema or structured vocabulary defines an interchange shape.
- **Executable:** deterministic in-repository code performs the named operation on caller-supplied objects.
- **Validated model:** a method has been evaluated against an appropriate population or reference standard, with performance and failure conditions documented.
- **Product service:** deployed collection/storage with verified security, consent, lifecycle, and operational controls.

These labels are not a quality score. A domain may have a useful schema and no validated inference method.

## Current capability inventory

| Domain | Concept | Contract | Executable now | Validated model | Product service |
|---|---|---|---|---|---|
| Promethean birth-derived map | Human Design and astrology as optional symbolic lenses | Birth-input, symbolic-map, correspondence, and phase schemas | Resource resolution, consent preflight, and authored-claim assembly; no chart/transit calculation engine | No empirical validation claimed for symbolic interpretation | No |
| Epimethean observations | Measurements, reports, events, behavior, relationships, and context over time | Observation, phase, subject-index, consent, and reading schemas | Runtime input validation, index resolution, and selected-resource consent preflight | No | No collection or storage |
| Sleep/wake timing | Sleep, wake, schedule, and personal context | Observation and rhythm-summary schemas | `summarize_main_sleep` describes logged intervals and coverage | Not validated against polysomnography or clinical sleep assessments | No device integration |
| Meals and caregiver-reported feeds | Logged meal/feed timing as distinct event types | Observation and rhythm-summary schemas | `summarize_feeding_events` reports event timing; adult meal and infant feed outputs stay separate | No nutritional adequacy, metabolic, or infant-feeding model | No logging application |
| Meal timing relative to waking | Meal events compared with explicit wake anchors | Observation and rhythm-summary schemas | `summarize_meal_timing_relative_to_wake` summarizes elapsed time from logged waking | Not a circadian-phase or metabolic-alignment model | No |
| Reported bleeding onset | Gaps between explicitly reported onset dates | Observation and rhythm-summary schemas | `summarize_bleeding_onset_intervals` reports calendar gaps and coverage | Does not infer menstrual cycle, ovulation, hormone level, or health state | No |
| Other rhythms and biometrics (temperature, HRV, heart rate, activity, light) | Candidate measures and interpretation limits | Generic observation measurement details | No corresponding device ingestion or analysis in the current runtime | No | No |
| Laboratory and home-test results (blood, urine, saliva) | Named analytes, specimen, method, unit, and collection context | Generic observation measurement details | No assay capture, import, or clinical interpretation | No | No |
| Endocrine and neurochemical processes | Broad hormone/signal inventory and possible interactions | Documentation only; an observation can represent a named assay result | No hormone-dynamics or neurochemical inference | No | No |
| Reproductive phases, pregnancy, postpartum, menopause | Lived context, reports, and optional phase labels | Phase-annotation schema and optional vocabulary catalog | Validation/representation only; no phase classifier | No | No |
| Development, infancy, childhood, and learning | Context, caregiver reports, activities, supports, and learner feedback | Observation, learning metadata, phase, and reading schemas | Reading assembly can carry authored, sourced records; no developmental assessment | No validated developmental or learning model | No child-facing service |
| Behavior and sensory exposure | Intention, occurrence, route, constraints, and separately recorded response | Observation behavior/sensory fields and documentation | Representation only; no intervention recommendation or effect estimator | No | No |
| Relationships and intimacy | Optional single-subject reports and reflections | Observation and consent domains | Reading preflight preserves selected records; no inference about a partner | No | No multi-party record or shared consent service |
| Evidence and symbolic crosswalks | Source-attributed evidence claims and symbolic correspondences | Evidence-claim and correspondence schemas | In-memory eligibility and reference checks; no governed reviewed catalog | Schema validation is not evidence review | No catalog service |
| Reading assembly | Typed claims that combine selected records and optional symbolic prompts | Input and assembled-reading schemas | In-memory consent/index preflight, provenance checks, and deterministic package assembly | No sentence-level entailment or text quality evaluation | No generated-reading service |
| Privacy, authorization, and data lifecycle | Minimization, scoped consent, child stewardship, intimacy boundaries | Consent and subject-index contracts; design documents | Caller-supplied in-memory decisions only | Not applicable | No authentication, persistent storage, encryption, audit, deletion, or access-control service |

## What the system may say today

The runtime may describe the records it receives and the four timing summaries listed above. It may attach source-attributed symbolic prompts to a reading after preflight. It may not claim to measure hormones from wearable proxies, determine reproductive or developmental phase from ordinary timestamps, explain a person's behavior through a symbolic map, or establish that a pattern is causal. A schema-valid object does not establish measurement quality, clinical meaning, or scientific validity.

## Development order

1. Add focused behavioral assurance for authorization, temporal edge cases, and provenance invariants before expanding real-data collection.
2. Complete the synthetic end-to-end reading path, including source-rendered presentation and review of sentence-level attribution.
3. Establish a governed, source-reviewed evidence catalog with explicit reviewer roles, conflict handling, and re-review dates.
4. Evaluate any proposed physiology or development model against suitable reference data and diverse populations; document calibration, uncertainty, exclusions, and failure cases before calling it validated.
5. Design privacy/security/storage and device/lab integrations only with operational threat, consent, retention, deletion, correction, and audit controls.

Related: [critical review](critical-review.md), [systems model](systems-model.md), [measurement landscape](measurement-landscape.md), [rhythm analysis](rhythm-analysis.md), [evidence claim model](evidence-claim-model.md), and [privacy and consent](privacy-consent-model.md).
