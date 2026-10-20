# Promethean and Epimethean phase names

**Status:** design proposal, version 0.1. Evocative labels are optional interpretive language. Canonical phase names, window kind (point, interval, or ongoing), dates, source, method, and uncertainty remain visible wherever a label appears.

## Purpose

Metheus can give meaningful names to periods of change while retaining a precise account of what each period represents. The name is a mnemonic or reflective prompt, not a measurement, diagnosis, prediction, or claim that all people move through the same stages.

A phase annotation should keep two layers distinct:

- **Promethean:** a phase calculated from a named symbolic system, such as a Human Design transit or an astrological transit. The astronomical positions and calculation can be documented; the meaning assigned by a symbolic tradition remains attributed interpretation.
- **Epimethean:** a phase or context based on lived events, reports, observations, or measurements: menstrual-cycle context, pregnancy and postpartum, menopause transition, development, sleep-wake timing, and other changing rhythms. State whether a phase is directly reported, observed, estimated, or clinically assessed.

The name may be poetic. The canonical label and provenance may not be omitted.

## Naming principles

1. **Pair evocative and canonical labels.** Example: “The Returning Tide — luteal phase (calendar estimate).”
2. **Let the person choose.** Names can be changed, hidden, or replaced with neutral terms. Do not assign identity, destiny, temperament, or value to a phase.
3. **Avoid a required sequence.** Life stages can overlap, recur, pause, be unknown, or not apply. Pregnancy, birth, postpartum, lactation, and menopause are contexts and transitions, not a universal ladder.
4. **Show the basis.** Include dates or time window, source, method/version, and confidence or uncertainty. A wearable proxy is not an assay; a calendar estimate is not an observed hormone state.
5. **Avoid evaluative or gendered language.** No “good/bad,” “productive/resting,” “motherhood,” or “decline” defaults. People of different genders and bodies may experience these events.
6. **Respect privacy and control.** Reproductive, sexual, infant, and intimate phase labels are sensitive. Collect only if useful and wanted; allow correction, export, hiding, and deletion.
7. **Do not make a label causal.** Temporal overlap with a Promethean feature does not show that a transit caused a physiological change.

## Starter vocabulary

These are optional editorial suggestions, not official biomedical stage definitions. A person can choose another name or no name.

The [machine-readable phase vocabulary catalog](../catalog/phase-vocabulary.json) provides the starter names, descriptions, basis guidance, and constraints as structured entries. It is validated against the [phase vocabulary schema](../schema/phase-vocabulary.schema.json). Applications should treat these as suggestions, preserve canonical labels and provenance, and allow the person to choose a different or neutral name.

| Layer / system | Canonical phase or context | Optional evocative name | Description and guardrail |
|---|---|---|---|
| Promethean / Human Design transit | Named planetary transit to a chart feature (include body, gate/line/center, exact interval, chart and ephemeris versions) | **The Passing Spark** | A moving symbolic prompt crossing a fixed chart reference. State the Human Design source/lineage. The prompt is not a physiological event or prediction. |
| Promethean / astrology | Named transit/aspect and exact interval | **The Moving Constellation** | A symbolic reading of calculated planetary positions. Keep astronomy/calculation separate from the tradition's interpretation; do not imply biological causation. |
| Epimethean / menstrual-cycle context | Bleeding reported | **The Opening Tide** | A reported bleeding event/window. Bleeding alone does not establish cycle phase, ovulation, hormone level, or cause. |
| Epimethean / menstrual-cycle context | Follicular phase, if method-supported | **The First Light** | Use only with a named estimation/assessment method and uncertainty. A calendar day alone does not prove follicular hormone state. |
| Epimethean / menstrual-cycle context | Ovulatory window, if method-supported | **The Threshold** | An estimate or assessment must say how it was derived. Do not imply fertility certainty or predict conception. |
| Epimethean / menstrual-cycle context | Luteal phase, if method-supported | **The Returning Tide** | State method and confidence. Do not infer progesterone or mood from a date, temperature trend, or HRV alone. |
| Epimethean / pregnancy | Pregnancy, with gestational age only if provided or clinically dated | **The Becoming** | A user-selected reflection label. It does not describe fetal health, development, or outcome. |
| Epimethean / birth | Birth event and recovery context, as reported | **The Arrival** | A dated event, not a guarantee of a particular emotional or physical experience. |
| Epimethean / postpartum | Postpartum context; optional user-defined subwindows | **The Reweaving** | Postpartum experiences vary, may be nonlinear, and can overlap with lactation, recovery, sleep change, or other contexts. Avoid imposing “fourth trimester” as a fixed phase or deadline. |
| Epimethean / menopause | Menopause transition, if self-reported or clinically assessed | **The Changing Tide** | A context label, not inferred from age, symptoms, or one hormone result alone. |
| Epimethean / menopause | Menopause milestone, if established under relevant clinical convention | **The Still Point** | Poetic name only. Keep the canonical milestone, basis, and clinician/source context; do not present it as a single hormonal state. |
| Epimethean / menopause | Postmenopause context, if reported/assessed | **The New Baseline** | A flexible context, not a promise that symptoms stop or that physiology is uniform. |
| Epimethean / development | Infant development, user- or clinician-described context | **The First Discoveries** | Organize around observed skills, support, and context, not a prediction or score. Do not infer a baby's internal state from a label. |
| Epimethean / development | Child or adolescent transition, when relevant and supplied | **The Expanding World** | A flexible reflective label. Avoid deadlines, comparisons, and deterministic forecasts. |
| Epimethean / sleep-wake | Observed or estimated sleep-wake interval | **The Nightward Arc** | Retain timestamps, time zone, and source. Clock time is not biological circadian phase. |

## Expanded phase palette

The names below are a consistent vocabulary proposal, not standardized biomedical terminology. Treat the evocative name as a display layer: keep the canonical phase, time window, evidence basis, and uncertainty adjacent to it. A phase may be unnamed, skipped, overlapping, or personalized.

### How a phase name should read

Use a name to make a cycle easier to notice and remember, not to imply that every cycle has the same shape. A complete label can be read as: **evocative name · canonical phase · basis · window · uncertainty**. In Metheus, “Promethean” names belong to symbolic map cycles; “Epimethean” names belong to lived, observed, reported, or measured cycles. A shared poetic style does not make the two kinds of evidence interchangeable.

### Promethean cycles and transits

Promethean labels describe positions or periods within a named symbolic system. The system's canonical vocabulary and lineage take precedence; these names are optional editorial handles.

| Canonical phase/context | Optional evocative name | Description |
|---|---|---|
| Natal/birth chart reference | **The Given Pattern** | A fixed symbolic map calculated from the birth data and named system. It is not a measured trait or a developmental verdict. |
| Transit approaching an exact contact | **The Approaching Current** | A symbolic period leading toward a calculated contact. Show the calculation window and orb/method; do not imply an event is destined. |
| Exact transit/contact | **The Meeting Point** | The exact or closest calculated contact to a chart feature. The astronomical calculation and the tradition's interpretation remain separate. |
| Transit separating from contact | **The Passing Spark** | A symbolic prompt for a contact that is moving beyond its exact point. It does not establish that a life event occurred. |
| Transit retrograde station / apparent reversal, if part of the named system | **The Turning Mirror** | A calculated change in apparent direction can mark a symbolic review prompt. It is not a reversal in the planet's physical orbit or a prediction that someone will revisit an event. |
| Transit return to a previously crossed point | **The Second Crossing** | A later calculated contact in a named transit sequence. Label the calculation and sequence; do not treat repetition as proof of a lesson or outcome. |
| Return cycle (for example, a named planetary return) | **The Returning Wheel** | A calculated return to a defined chart position. Name the body, reference position, system, and calculation method; avoid assigning a universal age-based meaning. |
| Recurring cycle within a named system | **The Resonant Rhythm** | A repeatable symbolic cycle whose start, period, and phase conventions must be supplied by that system. Do not imply physiological periodicity. |

### Epimethean reproductive and life-course contexts

| Canonical phase/context | Optional evocative name | Description |
|---|---|---|
| Menarche / first reported menstrual bleeding | **The First Tide** | A milestone reported by the person or caregiver when appropriate. It is not a measure of maturity, fertility, or readiness. |
| Bleeding onset / menstruation | **The Opening Tide** | A reported bleeding event or interval. Bleeding alone does not establish cycle phase, ovulation, hormone levels, or cause. |
| Menstrual bleeding interval, as reported | **The Tide in Motion** | A name for the recorded interval itself. It does not claim that the person is in a particular endocrine state or experiencing a particular mood. |
| Follicular phase, if method-supported | **The First Light** | A method-qualified phase estimate or assessment. A calendar day alone does not establish hormone state. |
| Later follicular context, if method-supported | **The Gathering Light** | An optional sublabel within a method-supported follicular estimate. It is not a claim of rising energy, estrogen, or readiness unless those are separately measured or reported. |
| Ovulatory event/window, if method-supported | **The Threshold** | State whether this is an estimate, observation, or clinical assessment and how it was established. Do not imply fertility certainty. |
| Luteal phase, if method-supported | **The Returning Tide** | A method-qualified estimate or assessment. Do not infer progesterone or mood from dates, temperature, or HRV alone. |
| Later luteal context, if method-supported | **The Waning Light** | An optional sublabel for a method-supported late-luteal window. It must not predict fatigue, irritability, or other symptoms; those remain individually reported observations. |
| Premenstrual symptoms, when self-reported | **The Nearing Edge** | A person's own symptom-window label, if useful. It is not a diagnosis and should not be inferred from a cycle calendar. |
| Conception attempt or fertility care, if the person chooses to record it | **The Open Question** | A private context that records only the person's chosen event or process. Do not infer conception, pregnancy, fertility status, or another person's intent. |
| Pregnancy | **The Becoming** | A user-selected reflection label for a reported or clinically documented pregnancy context; not a description of fetal health or outcome. |
| Birth event | **The Arrival** | A dated event as recorded by the person or authorized caregiver; it does not predict emotional or physical experience. |
| Postpartum context | **The Reweaving** | A flexible, potentially overlapping context for recovery and changed routines/relationships. No fixed duration, emotional course, or outcome is assumed. |
| Early postpartum days/weeks, if the person chooses this distinction | **The First Reweaving** | A person-defined early recovery context, not a universal “fourth trimester” clock. Birth recovery, feeding, sleep, mood, and support can change at different rates. |
| Ongoing postpartum adjustment, if the person chooses this distinction | **The Woven Days** | A flexible label for continuing adjustment and care. It does not imply recovery is complete, linear, or the same for every family. |
| Lactation / feeding context, if relevant and chosen | **The Shared Rhythm** | A descriptive label for a reported feeding or lactation context. It must not assume lactation, feeding method, or caregiver identity. |
| Perimenopause / menopause transition | **The Changing Tide** | A variable transition described by the person or clinician. Keep the canonical term and basis visible; do not infer it from age alone. |
| Final menstrual period / menopause milestone, when established | **The Still Point** | A retrospective milestone with the applicable clinical convention and source recorded. It is not a single hormone state. |
| Postmenopause context | **The New Baseline** | A flexible context after the menopause milestone; it does not promise symptoms stop or imply uniform physiology. |
| Intimacy or sexual encounter, if privately recorded by the person | **The Shared Moment** | A person-reported event label, not a measure of hormones, desire, relationship quality, or a partner's consent. Never infer another person's participation or experience. |
| Personal reflection after intimacy, if chosen | **The Quiet Afterglow** | A subjective reflection window that may include the person's own sensations or feelings. It is not a physiological phase or a proxy for another person's response. |

For conventional clinical terminology, Menopause Society definitions distinguish perimenopause/menopause transition, the final menstrual period, and postmenopause; terminology and criteria belong in the canonical field, not in the poetic label ([Menopause Society glossary](https://menopause.org/patient-education/menopause-glossary)). Menstrual cycle conventions count from the first day of one period to the first day of the next, but cycle timing alone is not hormone measurement ([ACOG amenorrhea FAQ](https://www.acog.org/womens-health/faqs/amenorrhea-absence-of-periods)).

### Epimethean development, especially infancy

These names organize observations and support, not developmental scoring. Age bands are optional context, not deadlines or a claim that development follows a single path. Use the child's and caregiver's preferred language, respect assent and privacy as the child grows, and rely on qualified assessment for clinical questions.

| Canonical stage/context | Optional evocative name | Description |
|---|---|---|
| Prenatal context | **The Before-Beginning** | A pregnancy-period context, if relevant and authorized. Do not represent the fetus as a measured psychological subject. |
| Newborn period | **The First Landing** | A context around birth and early adaptation. Record actual observations and care context separately; the name is not a wellbeing assessment. |
| Early infancy | **The Nearing World** | A flexible context for early interaction, sensory experience, sleep, and feeding observations. Do not infer internal state from a schedule. |
| Later infancy | **The Widening Reach** | A reflection label for emerging interaction and exploration when those are actually observed. No skill is presumed from age or label. |
| Toddlerhood / early childhood | **The Moving Horizon** | A flexible context for changing communication, movement, play, and autonomy as observed by the child and caregivers. |
| Middle childhood | **The Growing Constellation** | A context for evolving interests, relationships, and learning environments; not a fixed ability profile. |
| Adolescence | **The Thresholding Years** | A broad, person-defined transition context. Avoid assuming puberty timing, identity, emotional pattern, or readiness. |
| Adulthood / later life | **The Long Becoming** / **The Continuing Arc** | Optional life-course labels for change and continuity without treating any stage as decline, completion, or destiny. |

WHO materials describe the first 1,000 days as conception to age two and distinguish a further early-childhood period from ages two to five; these are useful planning frames, not individual developmental schedules ([WHO/PMNCH overview](https://pmnch.who.int/news-and-events/events/item/2024/11/19/partner-events/new-lancet-series-early-childhood-development-and-the-next-1000-days)).

A phase name should not encode a medical conclusion. If the user wants neutral display, use the canonical label alone.

## Data representation

A phase annotation is separate from the observation records that support it. It may be a user-authored name or a system-suggested name. Its supporting records remain independently consented and provenance-tagged.

```json
{
  "id": "phase-annotation-example",
  "subjectId": "subject-example",
  "recordType": "phase_annotation",
  "layer": "epimethean",
  "phaseSystem": "menstrual_cycle",
  "canonicalPhase": "bleeding_reported",
  "evocativeName": "The Opening Tide",
  "description": "A bleeding window entered by the person.",
  "window": { "kind": "interval", "start": "2026-04-03", "end": "2026-04-06" },
  "basis": "reported",
  "interpretation": "descriptive",
  "basisRecordIds": ["observation-example"],
  "method": "person-reported event; no phase inference",
  "methodVersion": "1.0",
  "uncertainty": "Does not establish cycle phase, ovulation, or hormone levels.",
  "nameSource": "metheus_suggestion"
}
```

For transit annotations, use `layer: "promethean"`, `basis: "derived"`, and `interpretation: "symbolic"`. Supply the named symbolic `phaseSystem`, source name and version, and retain the chart/transit feature, calculation method/version, and interval. The calculated position is a derived astronomical input; its meaning is symbolic interpretation. The two are related but distinct claims.

## Display grammar

Prefer a compact, inspectable form:

> **The Reweaving** · postpartum context · person-reported · dates supplied by the person · overlapping and nonlinear; no standard duration assumed

> **The Passing Spark** · Saturn transit to Gate 18 · named Human Design source/version · calculated interval · symbolic prompt, not a physiological claim

> **The Returning Tide** · luteal-phase estimate · method and confidence shown · not hormone-assayed

If evidence is insufficient, show the canonical context with “unknown” or “not estimated”; do not fill gaps with evocative certainty.

## Boundaries

Phase annotations may organize reflection and descriptive timelines. They must not diagnose, prescribe medication or supplements, estimate fertility certainty, infer desire or consent, assess infant wellbeing, or turn symbolic systems into clinical evidence. A phase label does not replace a person's account or qualified clinical care.

Related specifications: [rhythm system](rhythm-system.md), [Promethean-Epimethean bridge](promethean-epimethean-bridge.md), [ontology](ontology.md), and [reading grammar](reading-grammar.md).
