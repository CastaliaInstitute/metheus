# Methean model core: computational specification

**Status:** design specification, version 0.1. This document defines a model architecture and inference boundary. It is not an implemented state-space model, validated physiological model, clinical decision system, or claim that Human Design is scientifically predictive.

## 1. Purpose

The Methean System represents a person's changing lived context alongside a relatively stable Promethean symbolic map. It should help people inspect time, experience, and possible relations without converting a symbolic interpretation into physiology or turning incomplete observations into certainty.

The central computational rule is:

> Symbolic features may shape the questions and language of reflection. They do not enter the physiological state-transition or observation equations unless a separately designed and independently validated empirical study establishes a narrowly scoped relation.

This specification distinguishes a **data model** (what records mean), a **descriptive model** (what can be summarized reproducibly), a **state-estimation model** (what latent state can be estimated under a named method), and a **causal model** (what changes what). Metheus currently implements portions of the first two only.

## 2. Model planes

```text
PROMETHEAN PLANE                      EPIMETHEAN PLANE
symbolic map p                        lived records D(t)
source + lineage + calculation        reports, events, measurements,
          │                           derived summaries, context
          │ reflective prompt                    │
          └──────────────┐       ┌───────────────┘
                         ▼       ▼
                   READING / REFLECTION
          question + cited claims + uncertainty
          person interpretation + correction/feedback
```

The planes meet in the reading interface, not in a shared biological score. A reading may quote a named symbolic tradition and separately describe dated records. It may ask the person whether the juxtaposition is useful. It may not claim that the symbolic map generated, measured, or explains the Epimethean record.

The Epimethean plane has four different computational layers:

1. **Record layer:** immutable, attributable source records, with corrections represented through explicit revision links.
2. **Feature layer:** deterministic summaries of selected records, each versioned and linked to its input IDs.
3. **State-estimation layer:** optional estimates of explicitly defined latent variables using a named, reviewed method and fit-for-purpose inputs.
4. **Interpretation layer:** a person-facing reflection that cites records/features, states uncertainty, and invites correction.

No higher layer may erase or silently rewrite a lower layer. An estimate does not replace its source observations; a reading does not become a new observation unless the person's feedback is separately recorded as such.

## 3. Typed quantities and evidence status

Every model quantity must declare its epistemic kind:

| Kind | Meaning | Example | Model treatment |
|---|---|---|---|
| `measured` | Instrument or laboratory output under a documented method | Laboratory-reported serum analyte with specimen and collection time | Preserve value, unit, method, quality, and source; do not infer beyond its validation |
| `reported` | A person or caregiver describes an event or experience | Reported bleeding, felt sleep quality, caregiver-recorded feed | Attribute to reporter; valid as that person's report, not an assay or another person's inner state |
| `observed` | A directly recorded event or behavior | Timestamped light exposure or activity event | Preserve observer/device, time, and coverage; avoid upgrading it to a latent state |
| `derived` | Reproducible calculation from named inputs | Median logged sleep midpoint | Store method/version, dependencies, window, missingness, and limitations |
| `estimated` | Method-based estimate of a target not directly observed | Circadian phase estimate from an appropriate protocol | Require target definition, validated inputs, calibration/population, uncertainty, and failure conditions |
| `symbolic` | Interpretation attributed to a named Promethean system | A gate or transit interpretation | Confined to source-attributed reflection; never used as an Epimethean measurement |
| `unknown` | Not observed, not estimable, or insufficient evidence | Internal circadian phase from timestamps alone | Keep unknown; do not fill by default, archetype, age, or narrative coherence |

Data absence is not a zero value. Incomplete logging, sensor non-wear, an uncollected specimen, an unreported symptom, and an unknown state are distinct. The model must not impute a missing event as “none happened” unless the collection protocol establishes complete capture for that interval.

## 4. Formal model boundary

For a subject (s) and time (t), define:

- (P_s): optional Promethean map, including source, lineage, calculation, version, and symbolic features;
- (Y_{s,t}): Epimethean source observations and reports available at (t);
- (C_{s,t}): supplied context such as life stage, schedule, environment, access constraints, and events;
- (A_{s,t}): environmental affordances available or offered at time (t), including routines, spaces, people, tools, and optional AI-mediated scaffolds;
- (B_{s,t}): reported behaviors or exposures, with intention/occurrence and route/dose kept distinct;
- (Z_{s,t}): a vector of latent physiological, experiential, or developmental states, usually unknown;
- (F_{s,[a,b]}): deterministic, versioned features computed from explicit records in a window;
- (Q_s): the person's question and chosen interpretation context.

A future state-space implementation might be written:

```text
Z(t + Δt) = fθ(Z(t), B(t), C(t), A(t), ε(t))
Y(t)      = gφ(Z(t), method(t), device(t), reporter(t), η(t))
F[a,b]   = hν(selected Y[a,b], coverage, revision state)
R        = r(P, F, Y, C, A, Q, evidence catalog, uncertainty)
```

Here (A) means an opportunity that is present or offered, not that the subject chose, used, or benefited from it; those are separately recorded in (B) and (Y). (ε) and (η) represent process and observation uncertainty; (θ), (φ), and (ν) identify explicit model/method versions. These equations are an architecture, not a claim that the variables or functions have been fitted. At present Metheus has no implemented (f_θ), (g_φ), or latent (Z) estimator. Existing descriptive helpers implement a small subset of (h_ν): they summarize logged intervals and numeric measurements, and compare explicitly selected recorded windows using pairwise temporal-order relations.

**Non-interference constraint:** (P_s) is not an input to (f_θ), (g_φ), or any health/development estimate. With explicit chart-aware permission, a calculated Promethean feature—or a clearly identified, user-supplied gate list in the Matrix prototype—may provide candidates from the source-versioned AI affordance catalog, such as a partner gate on a channel edge whose other gate is active. This is symbolic prompt selection, not a physiological input or an inference about deficit, need, ability, or likely benefit. The AI may offer at most one candidate when it clearly advances the stated goal; the person can accept, revise, or dismiss it. An empirically studied Promethean–Epimethean association would need its own preregistered feature definition, comparison group, outcomes, confounder plan, replication, and independent review; even then, association would not establish causation or individual predictive value.

An undefined Promethean gate or channel does not define a deficit. In chart-aware mode, the AI receives the complete active-gate set and may use a fitting catalog activity to shape its response to the user's stated goal. A complementary partner-gate activity is a separate optional suggestion, limited to one and shown only when relevant. Neither choice establishes need, ability, or likely benefit. Any practical support should still fit the person's stated purpose, task, access context, or lived situation. A conversational AI is a tool/scaffold the person can choose; its presence does not complete or activate a Human Design channel, and a later response does not validate the symbolic pairing. Metheus has a local consent-checked selector for calculated maps and a Matrix bot prototype with one-request `ask-chart` plus an explicitly enabled per-sender in-memory `chart-set`; the bot does not calculate or verify charts and does not persist chart profiles. See the [environmental affordance layer](environmental-affordance-layer.md).

## 5. Temporal structure

Metheus must not force every domain into one periodic cycle. Each time-bearing record declares whether it is a point event, interval, sampled series, date-only report, or open-ended context. Each domain retains a suitable native timescale:

| Scale | Examples | Valid initial operations |
|---|---|---|
| Seconds/minutes | pulse samples, short sensory exposures, acute symptoms | Preserve signal and quality; aggregate only under a named sampling method |
| Hours/within-day | sleep episodes, feeds, meals, activity/rest | Count, duration, overlap, and elapsed time relative to explicit anchors |
| Day-scale | light, sleep/wake, temperature series, routine | Describe repeated timing and within-person variability; clock time does not equal biological phase |
| Multi-day/reproductive | reported bleeding, cycle estimates, pregnancy/postpartum/lactation context | Summarize explicit event intervals; estimate phase only with named evidence and uncertainty |
| Developmental/life-course | infancy, childhood, puberty, adulthood, menopause, aging | Store a supplied stage and optional age anchored to record time; distinguish prenatal gestational age, gestational age at birth, postmenstrual age, chronological age, and source-described or caller-term-referenced corrected age; do not assume a fixed stage sequence or developmental deadline |
| Symbolic cycle | transits and source-defined Promethean periods | Calculate only with a named symbolic convention and version; meaning stays attributed interpretation |

Across scales, preserve local timestamp, UTC offset, IANA zone when known, precision, duration, and clock-change/travel context. Comparison must declare the reference: wall-clock time, time since waking, time within a reported event, or a validated biological-phase estimate. Never silently substitute one reference for another.

## 6. Relations, not an untyped correlation soup

Every relation between quantities must be typed before it can appear in a model or reading:

| Relation type | What it says | Minimum requirements |
|---|---|---|
| `temporal_order` | A precedes, overlaps, or follows B | Compatible timestamps, precision, and interval semantics |
| `co_occurrence` | A and B appear in the same declared window | Window rule, source coverage, and missingness disclosure |
| `literature_association` | A source reports a population-level statistical association between constructs | Evidence claim with matching population, setting, measures, and limitations; no causal or mechanistic inference |
| `within_person_association` | A and B vary together for one person in observed data | Prespecified features/window, adequate repeated observations, uncertainty, alternative explanations; no causal language |
| `literature_mechanism` | A source supports a biological mechanism within a declared population and context | Scoped, reviewed evidence claim; a general mechanism does not establish that it occurred in an individual's episode |
| `model_hypothesis` | An explicit, unresolved proposal that A may relate to B | Mark as a question for inquiry; do not present as evidence, mechanism, or individual finding |
| `causal_effect` | Changing A would change B under specified conditions | A suitable causal design and assumptions; observational co-variation is insufficient |
| `symbolic_correspondence` | A named tradition links a symbolic feature to another concept | Store as a source-attributed correspondence, not a physiological or episode-graph edge |
| `person_interpretation` | The person says a juxtaposition or pattern is meaningful to them | Store as subject feedback/interpretation with date and permission; it does not become general evidence |
| `person_reported_link` | The person reports a relationship between two episode records or experiences | Attribute it to the person; cite source records supporting both endpoints; the link does not establish cause or another person's state |
| `reappraisal` | The person reports a later reinterpretation of an earlier appraisal | Preserve the earlier and later records separately; do not infer why the interpretation changed |

These relation types do not belong to one interchangeable edge set. `temporal_order`, `co_occurrence`, `person_reported_link`, `literature_association`, `literature_mechanism`, `literature_intervention`, `literature_measurement`, `model_hypothesis`, and `reappraisal` are episode-graph relations in the current pathway contract. A symbolic correspondence belongs in the correspondence catalog; a person's meaning belongs in their interpretation/feedback; `within_person_association` and `causal_effect` are future analysis outputs and are not pathway edges. Reading `claimType` values (such as `observation`, `symbolic_prompt`, `hypothesis`, and `boundary`) describe statements presented to the person, not relations in the evidence graph.

The default relation produced by a timeline is `temporal_order` or `co_occurrence`, never mechanism or cause. An exploratory within-person association is a question-generating feature, not a health recommendation or a transferable profile of other people. `literature_mechanism` names a sourced general mechanism; `model_hypothesis` names a proposed relation that is not yet established. Neither asserts an individual state.

The draft [experience-pathway graph contract](../schema/experience-pathway.schema.json) includes `temporal_order`, `co_occurrence`, `person_reported_link`, `literature_association`, `literature_mechanism`, `literature_intervention`, `literature_measurement`, `model_hypothesis`, and `reappraisal`. Runtime reference validation requires a `temporal_order`, `co_occurrence`, `person_reported_link`, or `reappraisal` edge to cite at least one source record supporting each endpoint node. It also resolves literature claim references and matches each literature relation to its evidence claim type. These checks establish source coverage and reference-type consistency; they do not prove semantic support, timestamp agreement, scientific quality, or causality. The pathway contract deliberately has no `symbolic_correspondence`, `person_interpretation`, `within_person_association`, or `causal_effect` relation type. The first two have separate correspondence/feedback representations; the latter two require separate analysis designs and review.

## 7. Personal reference patterns

When enough observations exist, Metheus may compare records with that person's own historical distribution. This must be described as a reference pattern, not an ideal or normal range. A reference window should:

- be selected with the person and declared before interpreting a deviation;
- report record/day coverage, gaps, source and device/method changes, and life-context transitions;
- use a robust statistic suited to the signal and time scale, with its method/version visible;
- avoid combining different devices, developmental contexts, or major transitions without explicit justification;
- expose the comparison values and uncertainty rather than only a colored status or score;
- allow the person to reject the comparison or mark an omitted context.

No generic minimum sample count or abnormality threshold is supplied here; those depend on the measurement and purpose and require method-specific evidence. Until a method defines adequate coverage and validation, report the descriptive records and mark a personal baseline as unavailable.

## 8. Reading generation contract

A future Metheus reading should be assembled in this order:

1. State the subject's question and chosen date window.
2. Identify the Promethean feature, named source/lineage, and symbolic status, if the person selected one.
3. List the Epimethean records/features actually selected, including source, epistemic kind, time basis, and coverage.
4. State direct descriptive results before offering interpretation.
5. Use one substantive sentence or atomic proposition per ordered claim object; separate supported general evidence, subject-specific association, symbolic prompt, and person interpretation into distinct claim types and citations.
6. Surface missingness, plausible alternatives, and non-claims adjacent to the relevant statement.
7. Invite the person to correct, contextualize, disagree, or leave the pattern unexplored.

A reading must not generate an unreferenced latent state, causal story, diagnosis, treatment, developmental score, fertility conclusion, consent inference, fixed learning style, or identity claim. Child-focused readings additionally require the child/guardian stewardship and age-appropriate voice controls defined in the privacy model before any product collection exists.

## 9. Maturity and validation gates

Use these levels to describe every proposed operation:

| Level | Capability | Gate to next level |
|---|---|---|
| M0 — represent | Contract can preserve a source record and its provenance | Schema review, privacy/domain review, explicit unknown/missing states |
| M1 — describe | Deterministic feature summarizes selected records | Reproducible method/version, edge-case behavioral assurance, source/dependency integrity |
| M2 — estimate | Method estimates a named latent quantity | Reference standard, target-population evaluation, calibration, uncertainty, failure modes, independent domain review |
| M3 — associate | Model estimates a relation among quantities | Prespecified analysis, confounding/missingness strategy, suitable validation and replication, restricted claims |
| M4 — causal/decision support | Model estimates effect or informs action | Appropriate causal/clinical evidence, safety evaluation, governance, qualified oversight, applicable regulation review |

Passing a lower-level gate does not imply a higher-level capability. Metheus currently has M0 contracts and selected M1 descriptive rhythm operations. It has no validated M2 estimates, M3 association model, or M4 decision support. A model's status must be visible in the capability matrix and user-facing description.

Before any M2 or higher feature, publish a model card describing target, intended use, excluded use, inputs and collection requirements, training/evaluation population, reference standard, performance and calibration, uncertainty, missing-data handling, known failure modes, subgroup limitations, versioning, reviewer, and monitoring/revocation plan. For child, reproductive, intimate, or intervention-related use, include appropriate domain and lived-experience review before collection or release.

## 10. Current implementation map

| Core element | Current evidence in repository | Current status |
|---|---|---|
| Promethean source features | Birth input and symbolic-map schemas/examples; no chart calculator | M0 representation only |
| Epimethean source records | Observation schema, provenance, consent, index, and lifecycle rules | M0 contract; no persistent user service |
| Time-window and measurement summaries | Sleep, meal/feed, meal-to-wake, bleeding-onset-gap, same-signature numeric-series summaries, and pairwise temporal order with endpoint provenance | Selected M1 descriptive operations; no biological phase estimate, trend model, or clinical interpretation |
| Cross-layer reading | Typed claims, evidence/correspondence references, preflight, deterministic assembly | M1 assembly of authored claims; no prose generation or entailment check |
| Environmental affordances | User-chosen supports, separately recorded lifecycle events and responses, and chart-aware symbolic prompts | M0 contracts, synthetic linked records, lifecycle-link resolver, consent-checked local selector/context builder for a supplied calculated natal map, and Matrix bot prototype with one-request `ask-chart` plus a temporary per-sender room `chart-set`; no chart calculator, verified/persistent profile service, deployed recommender, or outcome evaluation |
| Physiological/developmental latent state | Documentation and hormone/reference catalogs | M0 conceptual vocabulary; no fitted or validated model |
| Evidence governance | Candidate-only claim catalog, candidate-only typed endocrine-relation catalog, and written review protocol | No completed Metheus claim reviews; no authenticated review/catalog service; endocrine edges remain internal and are not reading-eligible |
| Personal data product | Static Pages site and caller-supplied in-memory functions | No ingestion, persistence, authentication, or storage authorization |

Related specifications: [systems model](systems-model.md), [ontology](ontology.md), [rhythm system](rhythm-system.md), [measurement landscape](measurement-landscape.md), [reading grammar](reading-grammar.md), [evidence review protocol](evidence-review-protocol.md), [capability matrix](capability-matrix.md), and [privacy/consent model](privacy-consent-model.md).
