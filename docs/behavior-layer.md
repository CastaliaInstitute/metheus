# Epimethean behavior layer

**Status:** working design, version 0.1. The behavior layer records actions and exposures that a person chooses to track, including changes they try. It is not a lifestyle score, medical treatment plan, or recommendation engine.

## Why this layer belongs in Metheus

The Promethean map offers symbolic prompts. Epimethean records show what is happening in the person's body and life. A distinct behavior layer captures what the person does, tries, intends, or cannot readily change. This makes the model more complete without pretending that every behavior is fully controllable or that a chart should prescribe it.

```text
Promethean feature / question
              │ may shape a reflection, never a prescription
              ▼
Person's chosen aim ──> behavior or exposure ──> lived response
         │                       │                     │
         └── circumstances ──────┴──── physiology ────┘
```

This is a conceptual graph. It does not assume an effect, direction, or lag. The same behavior can have different meanings and effects in different bodies, life stages, environments, and relationships.

## What can be represented

| Domain | Optional events or context | Possible descriptive comparisons | Do not infer |
|---|---|---|---|
| Eating pattern | Meal/snack timing, food categories, eating pattern the person names, hydration | Logged meal timing relative to waking or sleep; changes in self-reported hunger, energy, or symptoms | Complete intake from partial logs, nutrient adequacy, metabolic state, or that a dietary pattern caused a change |
| Fasting | Explicitly reported start/end, reason if the person wants, whether planned/attempted/completed, associated symptoms if volunteered | What was recorded before, during, and after a stated interval | A fast from missing meal records; suitability, safety, benefit, or a recommendation to extend it |
| Movement / exercise | Type, start/end, self-described intensity, perceived effort, recovery, whether chosen or constrained | Activity timing and volume alongside sleep, pain, mood, HR, or HRV records | Calories burned, fitness, recovery status, or a health outcome from steps or HRV alone |
| Supplements | Product and ingredient names, formulation, serving/dose as labeled or reported, route, timing, start/stop, actual use, source/brand if known | Timing of reported use alongside symptoms, lab records, or other behavior changes | Ingredient purity, efficacy, safety, deficiency, or a hormone effect from a product label or time overlap |
| Sleep and light routines | Chosen bedtime routine, outdoor/light exposure, device use if the person wants to record it | Routine timing alongside sleep intervals and subjective rest | Circadian phase or a clinical sleep conclusion from routine logs alone |
| Other chosen practices | Breathwork, meditation, social support, or another user-defined practice | User-described experience and timing | A biochemical mechanism or universal benefit without evidence |

Sensory practices and exposures (ambient aromas, inhaled scents, taste-only exposures, and flavors in food or drink) have their own [sensory, aroma, and flavor layer](sensory-aroma-flavor-layer.md). Keep that record distinct from any hormone assay or subjective response. A flavor within a swallowed meal is not equivalent to a taste-only exposure, and neither can be treated as proof of a hormone effect.

Medication is a separate, clinician-relevant treatment context. If a person chooses to record medication changes, preserve the medication/source and reported timing as its own record; do not frame prescribed treatment as a self-optimization behavior or suggest changing it. Supplement use and medication exposure can be analyzed as distinct, potentially interacting contexts, not as interchangeable “inputs.”

## Behavior is not the same as control

Use terms such as **chosen**, **attempted**, **completed**, **partial**, **constrained**, and **unclear**. Do not call a behavior “controllable” as a fixed trait. Food access, cost, work schedules, disability, illness, pain, culture, caregiving, safety, medication, and other people's needs can shape what is possible. A person can record an intention without having completed it; an absence of a record is not non-adherence.

Separate these record kinds:

1. **Intention:** what the person hopes or plans to try.
2. **Occurrence:** what they report doing or what a device directly records.
3. **Exposure details:** amount, duration, product, route, or intensity when known and willingly supplied.
4. **Response:** later self-reports, measurements, symptoms, or assays; these remain independently sourced.
5. **Interpretation:** a possible relationship across those records, labeled as uncertain and revisable.

Do not collapse those into an adherence score. A result that did not match an intention can reveal a constraint, not a character flaw.

## Relating behavior to Promethean and Epimethean layers

The chart may help choose a reflective question; it must not choose a diet, fasting protocol, workout, supplement, or hormone intervention. The behavior layer is a bridge from intention to lived experiment:

- **Promethean:** name the selected center/gate/channel theme and its lineage. Keep it symbolic.
- **Aim:** let the person state the question in their own terms (for example, “Does an evening walk change how I feel at bedtime?”).
- **Behavior:** record what happened, with timing and actual dose/intensity where known.
- **Epimethean context:** place the behavior alongside chosen sleep, cycle, developmental, clinical, environmental, and self-report records.
- **Reading:** describe any observed co-occurrence, missing coverage, alternative explanations, and the person's own sense of relevance.

Example: if a person asks about a Root-centered theme and begins walking after work, Metheus can compare the person's reported walk times with their sleep, energy, and workload notes. It cannot say the chart prescribed walking, that walking “balanced cortisol,” or that a change in sleep proves the behavior caused it.

Concurrent changes deserve special care. If a person changes food, exercise, a supplement, sleep timing, and medication together, the system should show that several exposures changed and avoid assigning an outcome to just one. Where the person is deliberately exploring a change, the system can help them define a baseline window, one stated change, an observation window, and an end/review point—but it must not choose a medically appropriate intervention, dose, or duration.

## Minimum useful record

The optional `behaviorContext` in the observation schema can capture:

- behavior kind and whether it was planned, attempted, completed, partial, skipped, or unknown;
- whether it was chosen, constrained, clinician-guided, caregiver-directed, externally imposed, or unclear;
- user-defined intention and reported action;
- amount and unit, duration in the time interval, and self-described intensity when applicable;
- supplement product/formulation/ingredients and serving amount when voluntarily provided;
- source, timestamp, life-stage context, and privacy level already carried by the base observation.

Behavior-specific event types require a matching `behaviorContext.kind` in the schema: explicit fasting boundaries use `fasting`, `exercise_session` uses `exercise`, `supplement_use` uses `supplement_use`, and `dietary_pattern` uses `dietary_pattern`. This prevents a logged occurrence from silently losing the kind of action it describes. It does not require a goal, health outcome, or personal explanation.

Example of a self-reported movement episode (illustrative only):

```json
{
  "id": "movement-2026-10-20-a",
  "subjectId": "local-subject-7f23",
  "recordType": "event",
  "eventType": "exercise_session",
  "epistemicClass": "self_reported",
  "time": {
    "start": "2026-10-20T17:30:00-06:00",
    "end": "2026-10-20T18:00:00-06:00",
    "timeZone": "America/Denver",
    "precision": "approximate",
    "scale": "interval"
  },
  "source": { "kind": "subject", "reportedByRelation": "self" },
  "domain": "activity",
  "label": "walk",
  "behaviorContext": {
    "kind": "exercise",
    "status": "completed",
    "agencyContext": "chosen",
    "reportedAction": "Walked outside",
    "perceivedIntensity": "light"
  },
  "privacy": {
    "sensitivity": "personal",
    "subjectControlled": true,
    "sharing": "private"
  }
}
```

Any later sleep, symptom, HRV, or laboratory record remains a separate record. The example does not imply that walking is a treatment or that an observed change was caused by the walk.

Do not require a user to state a reason, goal, product brand, body measurement, or outcome. Avoid storing a detailed food diary when meal timing or a broad category is enough for the user's question. Keep supplement and intimate behavior records sensitive and user-controlled.

## Special boundaries

- **Infants and children:** never apply adult fasting or supplement protocols. Feeding and activity are caregiver/clinician contexts organized around the child's needs and guidance; the behavior layer must not turn them into targets, scores, or optimization experiments.
- **Pregnancy, postpartum, lactation, menopause, adolescence, chronic conditions, or medication use:** record life stage only when relevant and user-provided. Do not generate fasting, supplement, exercise, or dietary protocols for these contexts.
- **Supplements:** product labels do not establish safety or effectiveness. FDA says it does not approve dietary supplements for safety and effectiveness before marketing; NCCIH notes possible drug interactions and product contamination. If a person records a supplement, preserve product identity and distinguish use from clinical advice. [FDA: Dietary supplements](https://www.fda.gov/consumers/consumer-updates/fda-101-dietary-supplements), [NCCIH: Safe use](https://www.nccih.nih.gov/health/safety), [NCCIH: Medication-supplement interactions](https://www.nccih.nih.gov/health/know-science/how-medications-and-supplements-can-interact/interactions-with-over-the-counter-medications).
- **No hormone hacking:** do not recommend a food, fast, exercise pattern, supplement, or intimacy behavior as a way to “balance,” “boost,” or “reset” a hormone based on a chart, a proxy, or a correlation.

## Implementation boundary

The draft observation schema has an optional `behaviorContext` object and event vocabulary for explicit fasting boundaries, exercise sessions, and supplement-use reports. The rhythm prototype summarizes logged sleep and meals/feeds, meal timing relative to waking, and calendar gaps between reported bleeding onsets. It does not model outcomes of behavior changes or suggest behavior plans.
