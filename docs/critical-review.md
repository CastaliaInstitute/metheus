# Critical review of Metheus

**Review scope:** repository design, schemas, examples, static site, and current Python prototypes. This is an architecture review, not clinical, legal, security, or community validation. The repository describes a concept and local prototypes; it does not currently collect or store personal records.

## Assessment

Metheus has a useful central distinction: Promethean interpretation is symbolic, while Epimethean records describe reported, measured, observed, or derived experience over time. The documentation repeatedly protects this distinction from being collapsed into an endocrine explanation, diagnosis, or deterministic profile. The ontology, measurement landscape, consent model, rhythm model, reading grammar, and phase annotations give the project a broad conceptual base.

The main weakness is the gap between the breadth of the vision and the narrowness of what is executable. Metheus is currently a static concept site, draft schemas, synthetic examples, and a small set of deterministic summaries and in-memory policy/reference functions. It is not yet a coherent personal model, a validated physiological model, a secure health-data service, or a complete reading engine. The next work should build traceable vertical slices and validate the contracts end to end, rather than adding more biological categories to prose alone.

## Findings

### 1. The subject/profile contract is new and not yet enforced end to end

This review adds a minimal [`subject index schema`](../schema/subject-index.schema.json), a separate [`birth-chart input schema`](../schema/birth-chart-input.schema.json), and a [`symbolic map schema`](../schema/symbolic-map.schema.json). The index contains pseudonymous ownership and versioned pointers, while exact birth details and calculated symbolic features remain in separate resources. This corrects the previous absence of any profile/index or symbolic-map contract.

**Impact:** A future application could invent incompatible profile shapes, duplicate sensitive data, or blur stable chart inputs with changing life context.

**Change in this review:** `resolve_subject_index` checks caller-supplied pointers against resource kind, schema version, and subject ownership. It follows symbolic-map input and feature IDs, and now follows rhythm-summary source event IDs to indexed, same-subject observations with measure-compatible event/domain pairs. The rhythm summary has its own schema and consent requires both summary and source events to be selected. `authorize_subject_index_resources` requires an explicit selected-ID list and checks consent only for those resources; index membership is not permission.

**Remaining work:** This is an in-memory cross-object check, not a storage authorization boundary. Integrate the resolver with a trusted store, validate resources when they are written, and define correction, deletion, and supersession behavior; do not make a comprehensive profile mandatory.

**Authorization hardening:** Policy version `metheus-consent-policy/0.3.0` rejects unknown consent purposes/actions/domains, unrecognized record-type/domain pairings, malformed share recipients, invalid action/purpose entries inside grants, and ambiguous grant IDs for a subject. Supersession and revocation references are subject-scoped. This is a narrow fail-closed policy layer, not proof that records or grants satisfy every schema constraint.

**Consent correction in this review:** The authorization policy previously let `birth_chart_inputs` act as a broad fallback for the `symbolic` domain. That collapsed permission for private source details with permission to use a derived map. The fallback is removed; the learning example now grants only its selected learning and symbolic records, while birth inputs require their own explicit domain/purpose scope.

### 2. Reading references needed a real runtime boundary

The reading schema supports `correspondenceIds` and `evidenceClaimIds`, but the original reference checker resolved only subject records and phase annotations. That meant a reading could carry an unresolved knowledge ID or use an internal/under-review evidence item without the preflight noticing.

**Change in this review:** `reading.schema.json` now distinguishes personal `inputIds` from non-personal `referenceIds`. The reading preflight can resolve correspondence and evidence catalogs separately, requires each cited reference to be selected, and checks permitted use, review status, citations, scope, limitations, and compatible claim type. Unevaluated/internal evidence is rejected; unsupported or conflicting evidence can only support a boundary claim. These knowledge references are not treated as the subject's personal records for consent evaluation.

**Remaining limitation:** Runtime preflight now validates the reading, subject index, indexed resource records, selected grants, and selected knowledge references against their schemas. It is still caller-supplied and in-memory: it does not authenticate a catalog, verify source URLs or reviewer qualifications, validate unrelated unselected resources, or enforce a storage boundary. A future service must use a trusted, versioned catalog before rendering.

### 3. Reading assembly now preserves typed provenance, but text entailment remains open

`preflight_subject_reading` composes schema validation, subject-index resolution, reading references, domain exclusions, and consent for a supplied reading. The `assemble_reading` step preserves authored claims in order and attaches source IDs, phase metadata, general-reference citations, support, and limitations. It is deterministic and does not generate prose. No component proves that natural-language text is entailed by its cited inputs, validates the assembler's output against an output schema, or records subject feedback/revision.

**Impact:** The initial claim assembly has a provenance boundary, but there is still no executable check that authored or generated language is supported by its cited records and references.

**Recommendation:** Continue the synthetic-data-only pipeline by making the assembler consume validated schemas and by adding claim-level attribution/evaluation. Every rendered claim block must map to a typed claim and resolved IDs; sentence-level rendering needs explicit boundaries if a claim contains multiple sentences. Add language generation only after evaluation can detect unsupported text, missing alternatives, and scope drift.

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

### 8. Contract validation now runs in CI; behavioral assurance is still missing

The Pages workflow now checks all JSON Schemas and their explicitly paired examples with a Draft 2020-12 validator on pull requests and before deployment. The repository still has no behavioral suite for the consent evaluator, resource resolver, reading preflight, or assembler. Static schema validation does not verify temporal edge cases, permission revocation, duplicate IDs, child stewardship, reference eligibility, or whether claim text is supported by the selected sources.

**Impact:** A future contributor can change a safety boundary without an executable signal that the behavior changed.

**Recommendation:** Before expanding data collection, add a focused behavioral suite for authorization and reference resolution, including adversarial and missing-data cases. Then add contract tests from synthetic observation through derived summary to assembled reading, including claim/source integrity and temporal edge cases. The current work adds schema/example validation but does not add or run behavioral tests.

## Recommended order of work

1. **Close data-contract seams:** add a minimal profile/index schema and define versioning, correction, and references across profiles, symbolic maps, observations, summaries, readings, and consent.
2. **Make contracts executable:** schema/example validation now runs in CI; add behavioral coverage for reference resolution, consent, temporal windows, and child/relationship boundaries.
3. **Complete one synthetic vertical slice:** profile references → consented synthetic observations → one deterministic rhythm summary → typed reading claims → provenance-carrying assembled output. The summary contract, dependency resolution, runtime input-schema validation, and a synthetic sleep-summary reading fixture now represent the path; behavioral verification, output-schema validation, source-rendered display, and claim text evaluation remain. Keep persistence and real user data out of this prototype.
4. **Govern evidence:** create the review process and a small curated evidence catalog; do not treat citation presence as evidence quality.
5. **Review high-stakes populations/domains:** infant development, reproductive health, intimate data, and any future intervention-related display with appropriate lived-experience and domain reviewers.
6. **Only then design real storage/integrations:** threat model, authentication, encryption, scoped authorization at the data boundary, remote-processing disclosure, audit, export, correction, deletion, backups, and vendor review.

## Current capability statement

At this review, Metheus can present its concept and documentation, represent draft subject-index, birth-input, symbolic-map, observation, phase, reading, consent, reference, and derived-rhythm-summary records, validate repository schemas and mapped examples in CI, validate selected runtime reading inputs against schemas, summarize selected logged rhythms descriptively, run caller-supplied in-memory reference/index/consent preflights, and assemble authored claims with source/phase/reference provenance. It cannot generate or entailment-check reading text, validate assembled output against a reading-output schema, ingest device or laboratory data, retain personal histories, enforce authorization at a storage boundary, produce validated endocrine or developmental models, or provide a secure health-data service. That limitation should remain prominent until the corresponding capabilities are implemented and verified.
