# Metheus evidence-claim review protocol

**Status:** operating proposal, version 0.1. No claim is considered reviewed merely because this protocol exists or a record passes schema validation.

## Purpose and boundary

This protocol governs when a general scientific or developmental statement may move from the candidate catalog into a reviewed catalog. It does not review person-specific records, diagnose, recommend treatment, validate a Promethean framework, or establish that an evidence claim applies to an individual. Reviewers assess an exact proposition within a defined scope.

Until Metheus has an authenticated review service, review artifacts are maintained as internal project records. The public claim's `reviewerRole` is descriptive metadata, not proof of identity, credentials, independence, or approval. Candidate claims stay `under_review` and `internal_only`; a local edit must never silently make one eligible for a reading.

## Review roles

Assign a reviewer whose training and current practice fit the claim's domain and method. Examples include laboratory medicine or endocrinology for assay interpretation, reproductive-health expertise for cycle measurement, sleep medicine for sleep measurement, and pediatric/developmental expertise for child claims. A methods reviewer may be needed for statistics, measurement validation, or evidence synthesis. The person who drafted a claim should disclose that role and should not be its sole reviewer.

For claims that could materially affect reproductive, pediatric, diagnostic, or intervention-related decisions, require two independent reviewers with relevant expertise and resolve disagreements explicitly. This is an internal governance threshold, not a statement that two reviews make a claim clinically validated. Lived-experience review can identify harms, missing contexts, or misleading language; it does not replace domain-method review, and domain review does not replace lived-experience input.

## Review packet

For each claim, preserve an internal packet containing:

1. Stable claim ID, exact proposed wording, claim type, and a version or change history.
2. A narrowly framed question and scope: population, setting, exposure/signal, route or specimen, comparator, outcome, timeframe, and exclusions where relevant.
3. Search date, databases or source collections checked, search terms, inclusion/exclusion rules, and the reason each source was selected.
4. Source list with stable identifiers/URLs and page, section, table, figure, or protocol locators. Check that each citation actually supports the wording and scope.
5. For each relevant source: design/type, population, methods, measurement quality, key results, uncertainty, limitations, funding/conflict disclosures when available, and applicability limits.
6. Null, contrary, conflicting, and indirect findings, including sources that would narrow or weaken the proposed claim.
7. Reviewer roles, review date, independence/conflict declarations, decision rationale, unresolved issues, and next review trigger/date.
8. Approved public claim wording, permitted use, explicit limitations, and the exact prior version it supersedes, if any.

The packet is not a user profile and must not contain personal health records. Keep sensitive reviewer contact or credential-verification material out of the public catalog. A future service needs authenticated identities, controlled access, immutable audit history, and a documented correction/revocation path.

## Review sequence

1. **Freeze the proposition.** Write one testable sentence before selecting favorable sources. Split compound claims into separately reviewable statements.
2. **Set scope and use.** Decide whether the claim is a mechanism description, measurement-validity statement, intervention effect, developmental context, or other statement. State whether it could appear as general education or only as a boundary on what a record cannot establish.
3. **Search for the full evidence shape.** Prefer an appropriate synthesis for broad claims and primary studies for specific methods or effects. Search for null, contrary, adverse, and replication evidence; do not infer support from citation count.
4. **Assess source-to-claim fit.** Check population, protocol, outcome, timeframe, and measurement against the exact wording. Distinguish professional guidance from primary evidence and record when guidance rather than a primary study supports a boundary statement.
5. **Grade without false precision.** Record design, bias, imprecision, consistency, directness, and generalizability in prose. Metheus has no validated numeric evidence score; do not invent one.
6. **Resolve and record.** Choose a status under the decision table below, explain why, identify limitations, and obtain the required independent reviews for high-stakes claims.
7. **Publish only the approved version.** A reviewed catalog is immutable/versioned. A material change to wording, population, method, or use returns the claim to review; corrections create a new version and preserve supersession links.
8. **Revisit.** Re-review on a material new guideline or synthesis, a relevant safety signal, a source correction/retraction, a scope expansion, or a scheduled review date. Until a review service can enforce dates, expired claims should be treated as internal-only by policy.

## Status and permitted-use decisions

| Evidence status | Meaning within the reviewed scope | Permitted use |
|---|---|---|
| `under_review` | Review is incomplete, disputed, or awaiting a required reviewer. | `internal_only` |
| `supported_for_scope` | The exact, limited statement is adequately supported for the stated scope, with material uncertainty and contrary evidence represented. | `educational_context` or `reading_boundary`, as approved |
| `not_supported` | The available evidence does not support the stated proposition or its wording is too strong. | `reading_boundary` only when the bounded statement accurately describes what cannot be established; otherwise internal only |
| `conflicting` | Relevant evidence is materially inconsistent or the conclusion depends on unresolved methods/populations. | `reading_boundary` or educational context that explicitly communicates the conflict; never a one-sided recommendation |
| `not_evaluated` | No substantive review has been completed. | `internal_only` |

Do not mark a claim `supported_for_scope` merely because a single authoritative reference states it. Do not use a boundary claim as a backdoor diagnosis or individual prediction. Intervention claims describe studied conditions and outcomes; they never prescribe an action to a reader.

## Promotion checklist

A claim is not eligible for a reading unless every item below is true:

- The source-to-wording match and scope have been reviewed and documented.
- The appropriate reviewer(s), dates, roles, and conflicts are recorded in an auditable packet.
- Contrary, null, and limiting evidence is represented; uncertainty and population limits are explicit.
- The evidence status and permitted use agree with the decision table.
- The public claim, citations, limitations, and review metadata pass the schema and runtime eligibility checks.
- The catalog version is trusted by the rendering service, and the claim is current and not superseded.
- The reading uses the claim only for the approved purpose and does not exceed its scope.

The current repository meets only part of this checklist: schemas and in-memory eligibility checks exist, but reviewer authentication, packet storage, catalog signing, expiry enforcement, and service-level trust do not. Therefore all existing candidate entries remain unavailable to readings.

## Change control

Every catalog change should identify the exact claim IDs affected, the source additions/removals, the scope or wording delta, reviewers, and downstream uses to re-evaluate. When evidence becomes weaker, conflicting, outdated, or retracted, disable eligibility first and then publish a versioned correction. Do not delete history in a way that leaves prior readings appearing current; dependent readings need a visible stale-reference or revocation state in a future service.
