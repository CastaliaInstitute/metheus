# Critical review of Metheus

**Review scope:** repository design, schemas, examples, static site, and current Python prototypes. This is an architecture review, not clinical, legal, security, or community validation. The repository describes a concept and local prototypes; it does not currently collect or store personal records.

## Assessment

Metheus has a useful central distinction: Promethean interpretation is symbolic, while Epimethean records describe reported, measured, observed, or derived experience over time. The documentation repeatedly protects this distinction from being collapsed into an endocrine explanation, diagnosis, or deterministic profile. The ontology, measurement landscape, consent model, rhythm model, reading grammar, and phase annotations give the project a broad conceptual base.

The main weakness is the gap between the breadth of the vision and the narrowness of what is executable. Metheus is currently a static concept site, draft schemas, synthetic examples, and a small set of deterministic summaries and in-memory policy/reference functions. It is not yet a coherent personal model, a validated physiological model, a secure health-data service, or a complete reading engine. The next work should build traceable vertical slices and validate the contracts end to end, rather than adding more biological categories to prose alone.

## Findings

### 1. The system has no subject/profile contract

The ontology names `Subject`, `Profile context`, and `Symbolic map`, but there is no schema for a subject container or profile. Birth inputs, timezone and unit preferences, life-stage context, chart features, and their correction/version history therefore have no single contract that declares ownership and links them to observations. The observation and phase schemas are not substitutes for that container.

**Impact:** A future application could invent incompatible profile shapes, duplicate sensitive data, or blur stable chart inputs with changing life context.

**Recommendation:** Define a minimal profile/index schema that stores pseudonymous subject identity and references to separately consented records. Keep exact birth data, chart calculations, and life context in distinct, versioned resources; do not make a comprehensive profile mandatory.

### 2. Reading references needed a real runtime boundary

The reading schema supports `correspondenceIds` and `evidenceClaimIds`, but the original reference checker resolved only subject records and phase annotations. That meant a reading could carry an unresolved knowledge ID or use an internal/under-review evidence item without the preflight noticing.

**Change in this review:** `reading.schema.json` now distinguishes personal `inputIds` from non-personal `referenceIds`. The reading preflight can resolve correspondence and evidence catalogs separately, requires each cited reference to be selected, and checks permitted use, review status, citations, scope, limitations, and compatible claim type. Unevaluated/internal evidence is rejected; unsupported or conflicting evidence can only support a boundary claim. These knowledge references are not treated as the subject's personal records for consent evaluation.

**Remaining limitation:** This is still a caller-supplied in-memory preflight. It does not validate all JSON Schema constraints, authenticate a catalog, verify source URLs or reviewer qualifications, or enforce a storage boundary. A future service must validate schemas and use a trusted, versioned catalog before rendering.

### 3. No end-to-end reading engine exists

The reading grammar is extensive, but there is no engine that selects inputs, resolves every source, checks coverage, renders claims with citations, and records subject feedback/revision. `validate_reading_references` checks selected IDs and several cross-object rules; `authorize_reading_inputs` adds consent preflight; neither produces a reading or proves that natural-language text is entailed by its cited inputs.

**Impact:** The most consequential product behavior—turning records into language—has no executable safety or provenance boundary.

**Recommendation:** Implement a synthetic-data-only reading pipeline with deterministic claim assembly first. Every rendered sentence should map to typed claim records and resolved IDs. Add generation only after a claim-level attribution/evaluation process can detect unsupported text, missing alternatives, and scope drift.

### 4. The physiology is organized, not modeled

The hormone and rhythm references are broad, and the rhythm functions intentionally summarize logged timing only. They do not model hormone dynamics, neurochemistry, developmental trajectories, or interactions among cycles, behavior, sleep, and environment. That restraint is good, but the phrase “systems model” can sound more scientifically operational than the current implementation warrants.

**Impact:** Readers may assume that an extensive hormone inventory or time-series vocabulary means Metheus can infer an endocrine state. The docs disclaim this, but the product should make its actual capabilities just as visible.

**Recommendation:** Keep a capability matrix that marks each domain as conceptual, recordable, summarizable, experimentally modeled, or clinically validated. Do not describe a domain as modeled until equations/methods, validation population, uncertainty, and failure cases are documented.

### 5. Evidence review is a schema, not a governed knowledge base

The evidence-claim schema provides status, scope, citations, reviewer role, and limitations. The repository has an in-memory resolver, but no reviewed evidence library, qualified review workflow, or trusted catalog service. A schema-valid item is not proof of scientific quality, and a reviewer-role string is not credential verification.

**Impact:** There is not yet an auditable basis for claims about measurement validity, hormone mechanisms, interventions, sensory effects, or development.

**Recommendation:** Establish a small, source-reviewed catalog with explicit inclusion criteria and named review roles before using evidence claims in readings. Preserve conflicting and null findings. Require a real review record and re-review cadence; keep intervention content educational and prohibit individualized treatment advice.

### 6. Infant and child contexts require stronger product boundaries

The documentation correctly prioritizes caregiver-source labeling, responsive care, privacy, and avoiding scores or inferred inner states. But child stewardship, assent, legal authority, pediatric escalation, and retention are currently design statements and schema checks, not a complete product protocol. Developmental stage labels and evocative names could still be mistaken for expected milestones if shown without observed context.

**Impact:** A baby-facing implementation has unusually high stakes and third-party data concerns. A reflective label can become an implicit evaluation even when the documentation says otherwise.

**Recommendation:** Do not ship child-record collection or developmental interpretation until the age-appropriate consent/assent, guardian authority, deletion/transfer, safety escalation, and clinical-boundary workflows have been reviewed with caregivers, pediatric/developmental experts, and relevant legal/privacy specialists. Present concrete observations and caregiver questions before any named stage.

### 7. Relationship and intimacy data remain single-subject accounts

The project appropriately says that one person cannot represent a partner's consent, feelings, or physiology. The current record model can capture a person's own report, but there is no multi-party provenance/permission model for shared events, nor should there be a default partner profile.

**Impact:** If later features treat an intimacy event as jointly observed or use it to infer a partner's state, the current data model cannot support that claim.

**Recommendation:** Keep each person's record independent. If a genuinely shared record is ever needed, require each participant's separate contribution and permission, and define withdrawal and deletion behavior for the shared artifact before implementation.

### 8. There is no evidence of implementation-level quality gates

The tracked repository has no automated test suite or schema/example-validation workflow; its only GitHub Actions workflow deploys the static Pages site. The docs themselves say the consent evaluator is not covered by behavioral tests. Static schemas and examples are helpful but do not verify temporal edge cases, permission revocation, duplicate IDs, child stewardship, reference eligibility, or the claims they are meant to prevent.

**Impact:** A future contributor can change a safety boundary without an executable signal that the behavior changed.

**Recommendation:** Before expanding data collection, add schema/example validation and a focused behavioral suite for authorization and reference resolution, including adversarial and missing-data cases. Then add contract tests from synthetic observation through derived summary to rendered reading. The current review turn did not add or run tests.

## Recommended order of work

1. **Close data-contract seams:** add a minimal profile/index schema and define versioning, correction, and references across profiles, symbolic maps, observations, summaries, readings, and consent.
2. **Make contracts executable:** validate each schema and example; add behavioral coverage for reference resolution, consent, temporal windows, and child/relationship boundaries.
3. **Build one synthetic vertical slice:** profile references → consented synthetic observations → one deterministic rhythm summary → typed reading claims → source-rendered output. Keep persistence and real user data out of this prototype.
4. **Govern evidence:** create the review process and a small curated evidence catalog; do not treat citation presence as evidence quality.
5. **Review high-stakes populations/domains:** infant development, reproductive health, intimate data, and any future intervention-related display with appropriate lived-experience and domain reviewers.
6. **Only then design real storage/integrations:** threat model, authentication, encryption, scoped authorization at the data boundary, remote-processing disclosure, audit, export, correction, deletion, backups, and vendor review.

## Current capability statement

At this review, Metheus can present its concept and documentation, represent draft observation/phase/reading/consent/reference records, summarize selected logged rhythms descriptively, and run caller-supplied in-memory reference/consent preflights. It cannot ingest device or laboratory data, retain personal histories, produce validated endocrine or developmental models, or provide a secure health-data service. That limitation should remain prominent until the corresponding capabilities are implemented and verified.
