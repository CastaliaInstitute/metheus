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
- (B_{s,t}): reported behaviors or exposures, with intention/occurrence and route/dose kept distinct;
- (Z_{s,t}): a vector of latent physiological, experiential, or developmental states, usually unknown;
- (F_{s,[a,b]}): deterministic, versioned features computed from explicit records in a window;
- (Q_s): the person's question and chosen interpretation context.

A future state-space implementation might be written:

```text
Z(t + Δt) = fθ(Z(t), B(t), C(t), ε(t))
Y(t)      = gφ(Z(t), method(t), device(t), reporter(t), η(t))
F[a,b]   = hν(selected Y[a,b], coverage, revision state)
R        = r(P, F, Y, C, Q, evidence catalog, uncertainty)
```

Here (ε) and (η) represent process and observation uncertainty; (θ), (φ), and (ν) identify explicit model/method versions. These equations are an architecture, not a claim that the variables or functions have been fitted. At present Metheus has no implemented (f_θ), (g_φ), or latent (Z) estimator. Existing rhythm functions implement a small subset of (h_ν): they summarize logged intervals and events.

**Non-interference constraint:** (P_s) is not an input to (f_θ), (g_φ), or any health/development estimate. A Promethean feature may be included as a separately typed input to (r) for a source-attributed symbolic prompt only. An empirically studied Promethean–Epimethean association would need its own preregistered feature definition, comparison group, outcomes, confounder plan, replication, and independent review; even then, association would not establish causation or individual predictive value.

## 5. Temporal structure

Metheus must not force every domain into one periodic cycle. Each time-bearing record declares whether it is a point event, interval, sampled series, date-only report, or open-ended context. Each domain retains a suitable native timescale:

| Scale | Examples | Valid initial operations |
|---|---|---|
| Seconds/minutes | pulse samples, short sensory exposures, acute symptoms | Preserve signal and quality; aggregate only under a named sampling method |
| Hours/within-day | sleep episodes, feeds, meals, activity/rest | Count, duration, overlap, and elapsed time relative to explicit anchors |
| Day-scale | light, sleep/wake, temperature series, routine | Describe repeated timing and within-person variability; clock time does not equal biological phase |
| Multi-day/reproductive | reported bleeding, cycle estimates, pregnancy/postpartum/lactation context | Summarize explicit event intervals; estimate phase only with named evidence and uncertainty |
| Developmental/life-course | infancy, childhood, puberty, adulthood, menopause, aging | Store supplied context and dated observations; do not assume a fixed stage sequence or developmental deadline |
| Symbolic cycle | transits and source-defined Promethean periods | Calculate only with a named symbolic convention and version; meaning stays attributed interpretation |

Across scales, preserve local timestamp, UTC offset, IANA zone when known, precision, duration, and clock-change/travel context. Comparison must declare the reference: wall-clock time, time since waking, time within a reported event, or a validated biological-phase estimate. Never silently substitute one reference for another.

## 6. Relations, not an untyped correlation soup

Every relation between quantities must be typed before it can appear in a model or reading:

| Relation type | What it says | Minimum requirements |
|---|---|---|
| `temporal_order` | A precedes, overlaps, or follows B | Compatible timestamps, precision, and interval semantics |
| `co_occurrence` | A and B appear in the same declared window | Window rule, source coverage, and missingness disclosure |
| `within_person_association` | A and B vary together for one person in observed data | Prespecified features/window, adequate repeated observations, uncertainty, alternative explanations; no causal language |
| `mechanistic_hypothesis` | A proposed biological process could connect A and B | Evidence claim with matching scope; distinguish established mechanism from individual application |
| `causal_effect` | Changing A would change B under specified conditions | A suitable causal design and assumptions; observational co-variation is insufficient |
| `symbolic_correspondence` | A named tradition links two symbolic concepts | Source and lineage; explicitly not a biological association |
| `person_interpretation` | The person says the relation is meaningful to them | Person's own words, date, and permission; does not become general evidence |

The default relation produced by a timeline is `temporal_order` or `co_occurrence`, never mechanism or cause. An exploratory within-person association is a question-generating feature, not a health recommendation or a transferable profile of other people.

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
5. Separate supported general evidence, subject-specific association, symbolic prompt, and person interpretation into distinct claim types.
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
| Time-window summaries | Sleep, meal/feed, meal-to-wake, and bleeding-onset-gap summaries | Selected M1 descriptive operations; no biological phase estimate |
| Cross-layer reading | Typed claims, evidence/correspondence references, preflight, deterministic assembly | M1 assembly of authored claims; no prose generation or entailment check |
| Physiological/developmental latent state | Documentation and hormone/reference catalogs | M0 conceptual vocabulary; no fitted or validated model |
| Evidence governance | Candidate-only claim catalog and written review protocol | No completed Metheus claim reviews; no authenticated review/catalog service |
| Personal data product | Static Pages site and caller-supplied in-memory functions | No ingestion, persistence, authentication, or storage authorization |

Related specifications: [systems model](systems-model.md), [ontology](ontology.md), [rhythm system](rhythm-system.md), [measurement landscape](measurement-landscape.md), [reading grammar](reading-grammar.md), [evidence review protocol](evidence-review-protocol.md), [capability matrix](capability-matrix.md), and [privacy/consent model](privacy-consent-model.md).
