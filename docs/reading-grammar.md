# Metheus reading grammar

**Status:** working draft, version 0.1. This describes how a future Metheus reader should construct a reflection from heterogeneous records. It is not an automated clinical interpretation protocol.

## Purpose

A Metheus reading is a short, revisable synthesis that helps a person examine a question across the Promethean symbolic map and Epimethean lived system. It should describe what is known, distinguish it from what is estimated or interpreted, and return the next step of meaning-making to the person.

The reader does not decide who the person is. It assembles sourced observations and possible patterns into a useful question.

## Inputs

A reading request may include:

1. **Question or intention** from the subject (required for a personalized reading).
2. **Time window** and relevant time zone.
3. **Promethean features** from a named symbolic system, with calculation inputs, source, and version where available.
4. **Epimethean records** selected by the subject: measurements, self-reports, caregiver reports, events, estimates, developmental context, and life circumstances.
5. **Preferences and boundaries:** which data domains to include, exclude, or keep private; preferred tone, length, and accessibility needs.

If the subject has not supplied enough information, provide a general reflection or ask one low-burden question. Do not infer missing facts from identity, appearance, relationship status, or statistical averages.

## Claim types

Every sentence that makes a substantive claim belongs to one of these types:

| Type | Form | Example |
|---|---|---|
| `observation` | What a source recorded or the person reported | “You logged later bedtimes on four of the last seven nights.” |
| `estimate` | A calculation from observations, with method and uncertainty | “Your sleep midpoint appears later this week; the estimate uses five nights of device data.” |
| `symbolic_prompt` | Meaning attributed to a named symbolic framework | “In this Human Design interpretation, this feature is often read as an invitation to wait for clarity.” |
| `interpretive_question` | An open question connecting selected layers without asserting causation | “Does that prompt fit the way your schedule has shifted this week?” |
| `hypothesis` | A tentative, testable possibility, explicitly non-causal unless evidence supports stronger language | “One possibility to explore is that the later meals and later sleep are moving together for you.” |
| `boundary` | What the data cannot establish | “These logs do not show why the schedule changed or whether it affects how rested you feel.” |

The user-facing text need not show enum names, but the system should preserve claim type and source links internally.

## Construction sequence

### 1. Establish scope

Restate or silently honor the user's question, chosen time window, and exclusions. Select only records relevant to that question. Sensitive domains should not be included merely because they are available.

### 2. Check provenance and coverage

For each candidate input, inspect epistemic class, source, timestamp, method, completeness, and uncertainty. Exclude records with unknown subject, unreliable time alignment, or unclear permission. For derived inputs, inspect the input record IDs and method version.

### 3. Establish context before pattern

Check known development/life stage and relevant context such as shift work, travel, caregiving, pregnancy/postpartum, illness, medication change, or device change—but only when supplied and relevant. Do not assume a context from a chart or demographic category.

### 4. Describe observations before interpreting them

Present the salient measurements and reports in plain language. Preserve disagreement between sources. For example, if a wearable estimates short sleep while the person says they feel rested, show both rather than choosing one as “truth.”

### 5. Compare over appropriate timescales

Use the timescale that matches the question: within-day, circadian, weekly, reproductive, developmental, or life-course. Do not infer a monthly rhythm from a few observations, a stable trait from a state, or a developmental delay from one marker. Personal baselines require declared windows and adequate coverage.

### 6. Add the symbolic layer as a prompt

Include a Promethean feature only when relevant to the person's question. Name the framework and make clear that the interpretation comes from that framework. Do not use symbolic language to explain measured physiology or override lived experience.

### 7. Offer one bounded synthesis

Connect at most a few relevant threads. State whether the connection is co-occurrence, an estimate, or a tentative hypothesis. Name at least one plausible alternative explanation when proposing a pattern. Avoid a global score or definitive personality summary.

### 8. Return agency

Close with one or two questions or options the person can accept, reject, or revise. Do not prescribe medical, reproductive, relationship, or high-impact decisions. If the person flags a medical or developmental concern, direct them to appropriate professional support without diagnosing.

## Inclusion and wording rules

- Every factual claim must resolve to one or more record IDs, symbolic-source IDs, or an explicitly general knowledge source.
- Confidence attaches to each claim, not to the person as a whole. Confidence describes support/coverage, not whether a person's experience is valid.
- Prefer “you recorded,” “the device estimated,” “in this framework,” “may,” “one possibility,” and “does this fit?”
- Do not say “your hormones caused,” “your body wants,” “you are a…,” or “this proves” without appropriate direct evidence and reviewed domain logic; in most reflective readings, avoid causal language entirely.
- Do not generate a finding from a single noisy or isolated datapoint. If the input is sparse, say so and keep the reflection general.
- Do not rank, shame, or moralize sleep timing, meal timing, feeding, cycle regularity, emotion, productivity, or development.
- Do not infer consent, desire, attachment, compatibility, fertility, diagnosis, identity, or destiny from symbolic features, proxies, correlations, or another person's report.
- Do not use a child's observation to assign temperament, attachment quality, future ability, or an endocrine state.

## Cross-layer conflict rules

When layers disagree, preserve the disagreement:

1. Do not rewrite an observation to fit a symbolic interpretation.
2. Do not dismiss the subject's report because it conflicts with a device estimate.
3. Do not treat a symbolic interpretation as a measurement or a measurement as a complete account of meaning.
4. Offer the mismatch as a possible inquiry only if it serves the subject's question.
5. Allow the subject to say the interpretation does not fit; store that as feedback about the reading, not evidence that either the person or the framework is wrong.

## Worked examples

All examples below are synthetic and illustrate wording, not validated rules or recommendations.

### A. Adult: circadian, feeding, and symbolic prompt

**Question:** “Why has this week felt different?”

**Available records:** six nights of wearable sleep intervals; five self-reported meal-time logs; two late work shifts; one Human Design feature with a versioned interpretation. No hormone assay. The person says energy feels lower on two mornings.

**Reading:**

> You logged later sleep timing on the two nights after late work shifts, and your meal notes also show later evening meals on those days. Your energy felt lower on two mornings. These records show timing overlap, but they do not identify a cause; workload, light exposure, stress, and other factors could also matter. In the Human Design framework you selected, this feature is commonly used as a prompt to notice your own timing and decision process. Does that prompt connect with how this week unfolded, or does another part of the week feel more relevant?

**Why this fits:** sleep and meals are separately sourced; reported energy is not converted to a hormone state; the symbolic feature is labeled; overlap is not claimed as causation.

### B. Baby: caregiver observations and development

**Question:** “Can you help me understand this change in my baby's routine?”

**Available records:** caregiver-reported feeds and sleep intervals over ten days; caregiver says the baby recently began spending more time reaching for nearby objects. No clinical assessment. The caregiver has not provided gestational age or medical context.

**Reading:**

> Your notes show that feeds and sleep have varied from day to day, and you have noticed more reaching during awake time. Those are caregiver observations, not a developmental assessment. Babies' routines and emerging skills vary, and these notes do not explain why the pattern changed. Would it help to keep noting the situations around feeds and sleep, or is there a specific concern you want to discuss with your pediatrician?

**Why this fits:** no age norm is assumed; the caregiver's report is labeled; no attachment, hormone, or diagnosis is inferred; professional support remains available for concern.

### C. Adult: cycle and intimacy reflection

**Question:** “Do my cycle notes relate to how connected I feel?”

**Available records:** four months of self-reported bleeding dates; weekly self-reported closeness ratings; two optional intimacy notes; no hormone testing. Some weeks are missing.

**Reading:**

> In the weeks you recorded, you sometimes noted lower closeness near the days you estimated as late-cycle; other weeks do not show that pairing, and several weeks are missing. The phase is calendar-estimated, not hormone-measured, and this pattern cannot show cause or predict desire. If useful, you could keep noting what “closeness” means to you and what else is happening in those weeks. You can also leave intimacy out of future readings.

**Why this fits:** phase estimate is not presented as measured hormone; non-matching and missing observations remain visible; personal experience is not generalized to a partner.

### D. Sparse information: no false precision

**Question:** “What do my hormones say about my mood?”

**Available records:** one mood note and no hormone assay.

**Reading:**

> These records do not include hormone measurements, so they cannot show your hormone levels or explain your mood. If you want, we can reflect on the mood note in its own context, or you could bring a specific hormone question to a clinician.

**Why this fits:** the model refuses to infer neurochemistry from mood and still offers a useful next step.

## Output shape

A reading should carry these fields internally:

1. `id`, `subjectId`, and reading/rule version;
2. purpose/question and time window;
3. selected input IDs and exclusions where useful;
4. ordered claims, each with `claimType`, text, source IDs, confidence/coverage, and rationale;
5. user-facing synthesis and optional reflective question;
6. boundaries/limitations;
7. generated timestamp and subject feedback/revision status.

The draft output contract is [`../schema/reading.schema.json`](../schema/reading.schema.json).

## Quality review checklist

- Can every claim be traced to an input or named symbolic source?
- Are observation, estimate, symbolism, and hypothesis clearly distinguished?
- Does the time window support the described pattern?
- Are missing data and source disagreement represented honestly?
- Has the reading avoided diagnosing, predicting, prescribing, and inferring another person's internal state?
- Does the subject have an easy way to disagree, exclude a domain, or revise the reading?
