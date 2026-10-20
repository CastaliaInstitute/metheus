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
| **Correspondence** | A sourced relation between a symbolic feature and another concept; not an observation | A source-attributed center/gland association, a reflective pairing, or a separately evidenced mechanism |
| **Observation** | A dated measurement or report of something observed | Temperature reading, sleep interval, reported pain, caregiver-observed feeding |
| **Event** | A dated occurrence that can contextualize observations | Travel, period start, birth, relationship transition, medication change |
| **Behavior episode** | An intended, attempted, completed, partial, skipped, or constrained action/exposure, with status kept separate from response | Explicit fast boundary, exercise session, supplement use, dietary-pattern change |
| **Environmental affordance** | A support made available or offered around a person's chosen goal; availability is separate from use and response | A quiet practice space, a reminder, a peer, an accessible routine, or an optional AI dialogue scaffold |
| **Sensory exposure** | A time-bounded smell, taste, flavor, or combined exposure, with route and composition kept distinct from response | Ambient aroma, inhalation, taste-only mouth rinse, flavor during a meal |
| **Behavior intention** | What a person plans or hopes to try, separately from whether it occurred | Intention to walk after work, planned dietary change |
| **Learning activity** | A time-bounded learning task, approaches, and supports used in a setting | Caregiver-supported play, guided practice, independent retrieval practice, accessible lesson |
| **Learning evidence** | A separately sourced observation of the learner's report or demonstrated knowledge/skill | Learner feedback, prompted or independent demonstration, transfer observation |
| **Estimate** | A derived quantity or phase computed from inputs | Cycle-day estimate, sleep midpoint, deviation from personal baseline |
| **Derived rhythm summary** | A method-versioned descriptive aggregation over explicitly selected source events | Logged sleep duration/timing, meal-event timing, reported bleeding-onset gaps |
| **Phase annotation** | A time-bounded label for a symbolic transit or lived phase; canonical term, optional name, basis, method, and limitations stay together | “The Passing Spark” linked to a named transit calculation; “The Opening Tide” linked to a reported bleeding window |
| **Experience pathway map** | A subject-controlled graph that references separately sourced episode records without flattening them into a score | A noticed cue, appraisal, reported stress/emotion, measured bodily response, action, suffering report, and later reappraisal connected by typed relations |
| **Development context** | Age/stage information and optional developmental observations | Gestational/chronological age, corrected age if supplied, milestone note |
| **Relationship context** | A subject's account of a relationship or interaction | Felt closeness, a personally noted intimacy event, caregiving relation |
| **Reading** | A time-bounded interpretation generated from selected inputs | A reflective prompt with claims, sources, confidence, and revision history |
| **Consent and access policy** | Who may collect, view, share, export, or delete a record | Self-controlled, guardian-managed, child assent/voice increases over time |

## Epistemic classes

Every record MUST have one class:

- `measured`: sensor, laboratory, home-test, or clinician-produced instrument result. Include signal/analyte, method, units, and instrument when known; categorical home-test results may have no numeric unit. A clinician's narrative finding remains `clinician_reported`.
- `self_reported`: the subject's account of their own experience.
- `caregiver_reported`: a caregiver's observation or account about a child or dependent.
- `clinician_reported`: a clinician-provided finding or interpretation. Preserve its author/source and date.
- `derived`: a calculation based on named inputs and a method/version.
- `symbolic`: a feature or meaning defined by a symbolic system; include system and version.
- `imported`: a record from an external source whose original class is not known; preserve original source and avoid upgrading its certainty.

Do not combine distinct classes into one unlabeled score. An interpretation may cite several classes, but each underlying input remains separately inspectable.

The draft schema also checks basic source/class agreement: self-reports identify the subject as reporter; caregiver and clinician reports identify their reporter relation; measured values name an instrument signal and come from a sensor, laboratory, or clinician source; derived records identify an algorithm and input records; imported records preserve an external source; and symbolic features remain in the symbolic domain. These constraints catch contradictory metadata, not inaccurate observations or untrustworthy sources. A valid record is not thereby complete, clinically interpretable, authorized for processing, or true.

## Correspondence evidence status

A correspondence is not an epistemic class for the target observation. Store its relation type, source lineage, evidence status, permitted use, citations, and limitations separately using the draft [`correspondence schema`](../schema/correspondence.schema.json). The bridge distinguishes symbolic doctrine, reflective association, and empirical association. General biomedical or developmental facts use the separate [`evidence-claim schema`](../schema/evidence-claim.schema.json); they are not crosswalks and cannot validate symbolic doctrine. A tradition-attributed pairing may be offered as an optional reflection but may not explain or predict a measured value.

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

Store timestamps in an unambiguous format with offset/time zone when available. If only a calendar date is known, use `time.date` and `precision: "date_only"`; do not fabricate a clock time. For intervals, distinguish start and end. For recurring patterns, store the observation window, method, and coverage. Do not force events into conventional clock-time buckets.

## Rhythm concepts

- **Rhythm event:** an occurrence such as lights-out, waking, a meal, feeding, activity, or symptom.
- **Rhythm series:** repeated events or measurements grouped by a declared rule and time window.
- **Phase estimate:** an estimated position in a rhythm, such as an inferred sleep phase or menstrual-cycle day. Always carry method and uncertainty.
- **Phase annotation:** a named interval or context that may be symbolic, reported, observed, derived, or clinically assessed. Its optional evocative name never replaces canonical terminology or changes the epistemic class of its supporting records. Promethean annotations are source-attributed symbolic interpretations; Epimethean annotations describe lived context and state their basis and method.
- **Regularity:** a summary of variation in timing or interval, never a moralized “good/bad” label.
- **Baseline:** a subject-specific reference computed from an explicit window and adequate coverage. Baseline changes over development and circumstance; do not imply a permanent norm.
- **Alignment / co-variation:** temporal relation between two series. This may suggest a question but does not demonstrate causation.
- **Missingness:** absent or unavailable observations, with reason only when known (not tracked, device off, declined, unknown).

The observation schema uses `eventType` to distinguish sleep/wake, meals/feeds, explicit `fasting_start` and `fasting_end`, `bleeding_start`, `dietary_pattern`, `learning_activity`, `environmental_affordance`, `exercise_session`, `supplement_use`, medication changes, light exposure, sensory exposures, and other events. A fasting interval is only represented when explicitly reported; missing meal events are never used to infer fasting. A fasting, exercise, supplement-use, or dietary-pattern event requires a matching `behaviorContext.kind`; the schema preserves the category of the reported action without requiring a goal or health outcome. A `learning_activity` requires `learningActivity` metadata and `domain: "learning"`; separate learning observations retain their own source, time, and method. `main_sleep` is a person's or data-source's designation for the principal sleep interval in a cycle; it is not inferred automatically from clock time. `wake` is an explicit wake observation or report, not automatically the end of a sleep interval. A `meal` event is a logged meal, not proof that all food intake was logged. A `feeding` event is separate and may represent caregiver-reported infant feeding; adult meal-window and fasting summaries must never be applied to infant feeds. A device-derived event must use `epistemicClass: "derived"` and preserve its method and source records, even if the originating sensor measurements were direct. Optional `behaviorContext`, `learningActivity`, `environmentalAffordance`, and `sensoryExposure` keep intentions, approaches, supports, agency, modality, route, and exposure details distinct from later outcomes. See the [behavior layer](behavior-layer.md), [learning layer](developmental-learning-layer.md), [environmental affordance layer](environmental-affordance-layer.md), and [sensory exposure layer](sensory-aroma-flavor-layer.md). The rhythm prototype summarizes intervals between explicit bleeding-onset reports as calendar gaps only; it does not classify them as menstrual cycles or estimate phase.

The draft [experience-pathway schema](../schema/experience-pathway.schema.json) represents a subject-authored graph over source observation IDs. Its current relation set is limited to record-time order/co-occurrence, person-reported links, evidence-cited population-level associations and general mechanisms, explicit hypotheses, and reported reappraisal. The graph is a separate map, not a derived clinical or psychological state; sources remain separately consented and the graph cannot introduce a causal-effect claim.

Environmental affordances are not actions: a tool or practice can be offered without being chosen, available without being accessible, or used without producing the intended response. An `environmental_affordance` event records one lifecycle step; `validate_environmental_affordance_links` resolves selected event-to-option and response-to-trial links in memory, while leaving lifecycle ordering and outcomes uninterpreted. A Promethean theme may serve as an optional reflection question, but the specific affordance must be grounded in a non-symbolic goal, task, access need, developmental context, or other selected source. The reading contract represents an optional proposal only; it does not implement an affordance recommender or AI service. See the [environmental affordance layer](environmental-affordance-layer.md).

## Reading model

A reading is a versioned object with:

- the person's question or purpose;
- the time window and life-stage context considered;
- selected input record identifiers;
- selected phase annotations cited by claim, with canonical labels and optional evocative names kept visibly distinct;
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

The machine-readable starters include the [`subject index schema`](../schema/subject-index.schema.json), a pseudonymous resource navigator rather than a full profile; the [`birth-chart input schema`](../schema/birth-chart-input.schema.json), which isolates exact and approximate chart inputs under a separate consent domain; the [`symbolic map schema`](../schema/symbolic-map.schema.json), which ties a named calculation version to feature-record IDs; the [`observation schema`](../schema/observation.schema.json), which defines one time-bounded record at a time; the [`rhythm summary schema`](../schema/rhythm-summary.schema.json), which describes method-versioned rhythm aggregates and source-event dependencies; the [`temporal relation schema`](../schema/temporal-relation.schema.json), which describes an in-memory temporal-order comparison between two selected records; the [`phase annotation schema`](../schema/phase-annotation.schema.json), which defines optional time-bounded phase labels; the [`reading schema`](../schema/reading.schema.json), which distinguishes personal `inputIds` from non-personal catalog `referenceIds`; the [`correspondence schema`](../schema/correspondence.schema.json), which defines a source-attributed crosswalk; and the [`consent schema`](../schema/consent.schema.json), which models scoped, revisable permissions. Optional `measurementDetails` preserves assay/device context; `behaviorContext` preserves a reported action or intention without treating it as a health outcome; `learningActivity` records what learning approaches and supports were used; `sensoryExposure` distinguishes smell, taste, and ingestion. Profile pointers are not permissions; [`resource resolution`](resource-resolution.md) checks object links while authorization remains a separate explicit selection. See the [measurement landscape](measurement-landscape.md), [phase naming framework](phase-naming-framework.md), [behavior layer](behavior-layer.md), [developmental learning layer](developmental-learning-layer.md), [sensory exposure layer](sensory-aroma-flavor-layer.md), [Promethean–Epimethean bridge](promethean-epimethean-bridge.md), and [privacy/consent model](privacy-consent-model.md).

## Open design questions

- Which fields are required for a useful record without pressuring users to overshare?
- How should the system represent uncertain dates, approximate birth times, calendar changes, and retrospective notes?
- Which rhythm summaries are transparent and understandable to a person without implying clinical significance?
- How should adult self-control transition to child assent and then independent control?
- Which symbolic systems and licensed source materials can be represented, with what provenance and versioning?
- What review and evidence thresholds are needed before any generated biological interpretation is shown?
