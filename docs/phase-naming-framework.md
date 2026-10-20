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
