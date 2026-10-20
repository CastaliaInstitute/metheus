# Metheus evidence claim model

**Status:** design specification, version 0.1. This model separates general scientific or developmental knowledge from both person-level records and symbolic correspondences. It is not a clinical knowledge base or a substitute for expert review.

## Three different kinds of support

Metheus readings can draw on three separately attributable sources:

| Source class | Answers | Example | Does not establish |
|---|---|---|---|
| **Observation** | What was measured, reported, or derived for this subject? | A laboratory-reported serum cortisol result with collection time and assay metadata | A cause, diagnosis, or general mechanism by itself |
| **Correspondence** | What symbolic relation or prompt is attributed to a named tradition or explicitly chosen for reflection? | A source-specific Human Design center/gland correspondence | A physiological fact, a person's hormone state, or a validated prediction |
| **Evidence claim** | What general statement is supported within a defined scientific/developmental scope? | A protocol-specific statement about the validity of a named measurement method | That the finding applies to this individual or validates a symbolic crosswalk |

The distinction prevents “the chart names a gland” plus “the gland has a known hormone pathway” from being presented as evidence that the chart measures or predicts that pathway. A biological mechanism may explain how a biological process works; it does not explain why a person has a particular chart feature or prove that the feature forecasts an observation.

## Claim record

Each claim has a stable ID, exact claim text, claim type, scope, evidence status, citations, permitted use, limitations, and (for reviewed claims) review date and reviewer role. Scope should identify relevant population, setting, exposure or signal, route/specimen, comparator, outcome, and timeframe when known. Do not generalize beyond the population and protocol represented in the source.

Claim types include:

- `biomedical_mechanism` — a biological process or mechanism;
- `measurement_validity` — what an instrument, assay, or proxy can validly measure under specified conditions;
- `intervention_effect` — an outcome associated with an intervention in an identified study scope;
- `developmental_context` — a developmental or learning-science statement;
- `other` — a sourced general claim that does not fit the categories above.

## Evidence status and allowed use

- `not_evaluated` or `under_review` claims are internal research notes and must not be cited in a user reading.
- `supported_for_scope`, `not_supported`, or `conflicting` claims may be used in educational context or as a reading boundary only when citations, review date, and reviewer role are present.
- A `reading_boundary` states what a record set or method cannot establish. It must not be turned into a diagnosis or an individual prediction.
- An evidence status is an editorial judgment, not a validated score. Citations and reviewer metadata do not by themselves prove that the claim is true or that the source is adequate.

The [evidence-claim schema](../schema/evidence-claim.schema.json) captures these fields. The [correspondence schema](../schema/correspondence.schema.json) handles symbolic relations separately. The reading schema permits correspondence IDs only on symbolic prompts or interpretive questions, and evidence-claim IDs only on bounded hypotheses or limitations. A future reader service must resolve each ID, verify its permitted use and current status, and check the subject's consent before rendering it; JSON Schema cannot ensure those database-level relationships.

## Evidence review workflow

1. State the exact proposition before searching; do not choose a claim after seeing a favorable result.
2. Define the scope: population, setting, exposure, route/specimen, comparator, outcome, and timescale.
3. Prefer direct primary research for a specific effect and systematic reviews or authoritative guidelines for synthesis; retain null, conflicting, and contrary evidence.
4. Assess design, sample, measurement validity, bias, replication, effect size, uncertainty, and generalizability.
5. Assign status and permitted use only for that scope; record review date and reviewer role.
6. Re-review when the source base changes or the claim's scope is expanded.

No evidence-claim record should recommend a behavior, supplement, hormone treatment, educational placement, or medical action. Intervention evidence describes studied conditions and outcomes; it does not automatically make an intervention appropriate for a specific person.

## Current boundary

The repository contains broad reference documents and draft schemas, but it does not yet contain a reviewed evidence-claim library, qualified review workflow, citation-quality scoring process, or runtime ID/permission resolver. Until those exist, the new schema is an architectural contract, not an evidence-backed feature.
