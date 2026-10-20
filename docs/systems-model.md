# Metheus as a systems model

## The direction

Metheus aims to become a systems model for understanding a life in motion. Human Design offers a relatively stable, birth-derived symbolic map. Metheus can use that kind of map as one interpretive layer, while modeling a person as an evolving system shaped by body, development, relationships, environment, choices, and time.

The goal is not to produce a larger fixed profile. It is to help a person notice how different parts of life interact, what changes at different timescales, and which interpretations remain useful to them. The Promethean layer offers a map of possible patterns. The Epimethean layer attends to what unfolds and becomes knowable through living.

## A layered model

```text
PERSON + LIFE CONTEXT
│
├── Promethean map
│   └── birth-derived symbolic systems and their interpretations
│
├── Epimethean dynamics
│   ├── body and physiology
│   ├── developmental stage
│   ├── learning goals, activities, and supports
│   ├── relationships and care
│   ├── environment and daily conditions
│   ├── behaviors, intentions, sensory exposures, and constraints
│   ├── events, choices, and personal meaning
│   └── observations over time
│
└── Reading
    └── a transparent, revisable reflection returned to the person
```

The model should preserve the origin of every statement. A chart placement is not a biometric measurement. A wearable value is not a hormone assay. A diary entry is not an objective account of another person's inner state. An interpretation is not a fact about the person.

## System dimensions

### 1. Relatively stable structure

Examples include birth time and place, anatomy or other context a person chooses to record, long-running conditions, family and community context, and symbolic chart features. “Stable” does not mean immutable or definitive: these records can be incomplete, corrected, or reinterpreted.

### 2. Development and life stage

Represent transitions and changing developmental needs: prenatal life, birth, infancy, childhood, adolescence, adulthood, pregnancy and postpartum life where relevant, menopause, and aging. These are contextual frames, not universal sequences or deadlines. A baby model should foreground the infant's developing rhythms and capacities, caregiver observations, responsive care, nutrition, safety, health, and learning opportunities.

### 3. Rhythms and processes

Represent processes that vary over time and on different scales:

- **Circadian (roughly day-scale):** internal timing and phase, light/dark exposure, sleep/wake timing, body-temperature rhythm, alertness, and daily routines. Record clock time and, where possible, relation to the person's sleep schedule; do not assume everyone follows a day-oriented schedule.
- **Sleep/wake:** sleep onset and offset, duration, interruptions, naps, subjective rest, and schedule variation. Separate device estimates from a person's report and avoid treating one “ideal” schedule as universal.
- **Feeding and metabolic timing:** meal and snack timing, feeding windows, fasting intervals where voluntarily provided, hydration, and the person's subjective hunger/fullness/energy. This is timing context, not a diet score or recommendation. For infants, represent feeding cues, caregiver-reported feeds, and feeding guidance appropriate to that child; adult fasting concepts do not apply.
- **Ultradian (within-day):** shorter pulses and cycles, including pulsatile endocrine release, activity/rest periods, and sleep-stage variation.
- **Reproductive and hormonal:** cycle dates and symptoms, pregnancy, postpartum/lactation, menopause, and direct hormone results when available.
- **Activity and recovery:** movement, exertion, sedentary periods, rest, and recovery context.
- **Developmental:** growth, movement, language, play, regulation, and changing social engagement.
- **Relational:** connection, conflict, intimacy, caregiving, separation, and repair as personally reported.

These rhythms interact. Light exposure and sleep timing can organize circadian phase; meals, activity, and social schedules can act as timing cues for peripheral physiology; sleep, feeding, and hormones influence one another. A model should look for individual timing and co-variation rather than assume a single universal routine or that timing alone establishes cause. Rhythms can change with shift work, travel, parenting, illness, disability, season, culture, and personal preference.

Metheus should distinguish local clock time, time relative to an observed wake/sleep anchor, and biological phase. The last is not recoverable from ordinary timestamps alone. An eating event can be compared with logged waking, but an event log cannot establish complete intake, a fasting state, metabolic adequacy, or whether the timing is biologically aligned. See the [rhythm system model](rhythm-system.md) for the interaction layers, feature definitions, comparison workflow, and infant-specific constraints.

#### Rhythm record

For each repeated process, represent (when available):

- event or measurement time, plus time zone and clock-change context;
- process type (sleep, light, meal, feed, activity, symptom, lab, or other);
- start/end or point event, duration, and source;
- regularity and variability over a chosen observation window;
- relation to sleep timing or another reference event, if useful;
- missing data, device changes, and confidence in derived estimates.

Do not force meal events into fixed breakfast/lunch/dinner slots. Do not infer a circadian phase from clock time alone when sleep timing, light exposure, or work schedule is unknown. Do not describe an observed alignment between sleep, meals, temperature, mood, or hormones as causal without evidence that supports that claim.

### 4. State and circumstance

Capture what is happening now: sleep, activity, illness or recovery as self-reported, travel, workload, stressors, meals, location context, relationship events, and the person's current intentions. State is transient and should not be turned into trait.

### 5. Behavior and chosen change

Represent eating patterns, explicit fasting intervals, movement/exercise, supplements, sleep/light routines, sensory practices, and other user-selected or externally imposed exposures as dated behaviors. Distinguish intention, occurrence, dose/amount, route, and later response. Also preserve when an action is constrained by access, disability, caregiving, work, illness, or other circumstance. This is not a universal “controllable factors” panel: agency is contextual, and the Promethean map may prompt reflection but must never prescribe a behavior. See the [Epimethean behavior layer](behavior-layer.md) and its [sensory, aroma, and flavor sublayer](sensory-aroma-flavor-layer.md).

### 6. Observation and interpretation

Each data point should carry its source and uncertainty:

| Kind | Examples | What it can support |
|---|---|---|
| Directly measured | Temperature, HRV, heart rate, light exposure, lab assay | A dated observation from a device or lab, with method and limitations |
| Self-reported | Mood, desire, bleeding, meal timing, hunger/fullness, sleep quality, intimacy, pain | The person's account of their own experience |
| Caregiver-reported | Baby sleep/feeding observations, developmental behavior | An adult observer's account, not direct access to an infant's internal state |
| Derived estimate | Cycle phase, sleep regularity, trend | A calculation from inputs; method and confidence must be visible |
| Symbolic interpretation | Human Design gates, types, profiles, or other chart meanings | A framework for reflection, not empirically measured physiology |
| Joint interpretation | A reading that places observations and symbolic prompts together | A revisable question or hypothesis, not causal proof or diagnosis |

Behavior exposures are records of what was intended or reported, not outcomes. A response—subjective, wearable-derived, or laboratory-measured—must be a separate observation with its own time, source, and method. The schema's optional `behaviorContext` and `sensoryExposure` objects carry exposure details; neither encodes a presumed effect. For aroma/flavor, preserve modality and route because smelling, tasting, and swallowing are materially different exposures.

### 7. Developmental psychology and learning

Learning belongs in the Epimethean layer as a changing interaction among developmental context, prior knowledge, learner goals, task demands, relationships, culture, access, and the learning environment. Record what learning activity and supports were used; keep learner feedback and demonstrated learning evidence as separately sourced observations with their own times and methods. The Promethean map may help the learner frame a question about motivation or preferred conditions; it must not prescribe a method, assign a fixed learning style, or predict a child's abilities. See the [developmental psychology and learning layer](developmental-learning-layer.md).

## Dynamics rather than scores

The model should represent change, feedback, and timing instead of assigning a single “Metheus type” or wellbeing score. A useful conceptual form is:

```text
state(t + Δt) = transition(state(t), context(t), behavior(t), events(t), uncertainty)
observation(t) = observe(state(t), device_or_report, method)
reading(t) = reflect(symbolic_map, observations, life_stage, person's_question)
```

This notation is a design aid, not a validated physiological equation. It makes three commitments visible:

1. **The person changes.** Any model of state is temporary and revisable.
2. **Observations are partial.** Devices and memory sample only parts of lived experience.
3. **Meaning is collaborative.** The system can offer patterns and questions; the person decides what they mean.

Where enough data exist, Metheus may describe an individual's baseline and deviations from it. It must label missingness, sensor changes, estimated intervals, and alternative explanations. Correlation between two time series can motivate a question; it does not by itself identify a mechanism.

## How the two layers relate

The Promethean and Epimethean layers should be allowed to inform a reading without being treated as equivalent evidence:

- The **Promethean** layer may suggest a symbolic theme or reflective prompt.
- The **Epimethean** layer may add temporal observations, physiology, development, relationships, and circumstances.
- The **reading** may ask whether the theme resonates with the person's own history and current context.
- If the observations disagree with the symbolic story, the observations and the person's account remain visible; the model must not force them to fit.

For Human Design center/gland correspondences, gate/channel associations, or chakra language, preserve the named lineage and classify the link as symbolic doctrine unless it has independent empirical support. The [Promethean–Epimethean bridge](promethean-epimethean-bridge.md) defines relation types and a reading sequence for this.

This is a systems analogy to Human Design in the sense that both aim to orient self-understanding through a structured map. Metheus' distinctive contribution is to make the map time-aware and situated within the person's changing, interconnected life. It does not make the symbolic system a scientific measurement instrument.

## Baby and child model

For infants, use a caregiver-supported record with a strong duty of care:

- Keep age and developmental context explicit, including prematurity/corrected age only when known and relevant.
- Record observations in plain language with time, source, and context; avoid assigning hidden emotions or hormones.
- Center health, adequate nutrition, safety, responsive caregiving, and early learning opportunities.
- Treat developmental markers as prompts to observe and discuss, not scores, diagnoses, rankings, or predictions.
- Encourage appropriate pediatric or developmental consultation when caregivers have concerns.
- Minimize data collection, protect records, prohibit public-by-default sharing, and provide deletion/export controls.
- Design for the child's growing voice, assent, and privacy as they mature.

## Product principles implied by the model

1. **Provenance:** Every claim can be traced to chart convention, sensor, lab, person, caregiver, or algorithm.
2. **Timescale awareness:** A daily fluctuation, monthly rhythm, developmental transition, and life event are not interchangeable.
3. **Uncertainty:** Missing or approximate data reduce confidence; they do not invite confident guessing.
4. **Pluralism:** A person can decline any data type, and the model should remain useful with sparse information.
5. **Privacy and agency:** Sensitive information is optional, minimized, private by default, and under the subject's control.
6. **Behavior without blame:** Record choices, attempts, and constraints without turning them into compliance or virtue scores.
7. **Non-determinism:** Never infer identity, character, consent, fertility, diagnosis, or destiny from a chart, hormone, wearable proxy, or correlation.
8. **Revision:** Interpretations should be revisitable when new information or the person's understanding changes.

### Consent and stewardship

Sensitive data are included only for a subject-selected purpose and scope. Collection, analysis, sharing, and remote processing are separate permissions; withdrawal and deletion must propagate to dependent summaries/readings according to the disclosed storage model. Child records require careful guardian stewardship and an increasing role for the child's own voice; intimate records remain each participant's own. See the [privacy and consent model](privacy-consent-model.md) and draft [consent schema](../schema/consent.schema.json). The repository's current static site does not collect or store personal records.

## Practical development path

1. **Ontology:** Define the concepts and relationships, including source, timescale, uncertainty, and consent/ownership.
2. **Observation model:** Specify data contracts for device measures, lab results, self-reports, caregiver observations, derived estimates, and symbolic data.
3. **Temporal model:** Represent events and repeated measurements across day, within-day, reproductive, and developmental scales without assuming regular cycles, conventional meal schedules, or complete tracking.
4. **Reading grammar:** Create rules for combining layers while preserving provenance and avoiding causal overstatement.
5. **Prototype:** Build sample readings for different ages and life contexts, including sparse-data and conflicting-signal cases.
6. **Review:** Seek input from people with lived experience, pediatric/developmental experts for child contexts, and endocrine expertise for physiology claims.

Metheus is currently a concept, not a validated model or clinical product. This document describes a direction for design and research.
