# Metheus privacy, consent, and data stewardship model

**Status:** product design requirements, version 0.2. These requirements are not a privacy policy, security certification, or statement of legal compliance. Metheus currently includes a static PWA, caller-supplied in-memory data functions, and an undeployed Matrix bot prototype. The bot implements a room-wide consent gate for explicit AI requests and a temporary per-sender chart setting, but there is no personal-record collection or storage service, wearable connection, persistent profile consent service, export, or deletion facility.

## Why this is part of the system

Metheus may represent exact birth details, body measurements, laboratory results, reproductive and menopause context, intimate experience, learning observations, and a child's developmental history. These domains can be identifying or deeply personal, especially when combined. Privacy and agency therefore belong in the model's data architecture, not only in explanatory copy.

## Consent is scoped and revisable

Consent must attach to a **subject**, **data domain**, and **purpose**. A person may allow a reading to use sleep timing while excluding reproductive notes, or allow a private analysis while declining sharing. A symbolic chart calculation from birth date/time/place is a separate purpose from storing or analyzing biometrics. Raw `birth_chart_inputs` and derived `symbolic` map records are also separate domains: granting access to the inputs does not authorize use of the derived map, and map access does not authorize recalculation from raw birth details. A blanket “agree to Metheus” control is insufficient for optional sensitive domains.

Represent these separately:

1. **Collection:** permission to create or import a record.
2. **Analysis:** permission to include selected records in a derived summary or reading.
3. **Sharing:** permission to disclose selected records or readings to a named role/recipient.
4. **Processing:** whether a task runs on the local device or sends selected data to a remote service. Remote processing is a separate permission from analysis; a remote reading requires both `analyze` and `remote_processing` authorization.

The permission state must be inspectable and revocable. Withdrawing permission stops future use within that scope. Deletion, retention, or records required by a connected service depend on the actual storage architecture and must be made explicit before collection begins.

An example chart workflow keeps both domain and purpose explicit:

| Resource/action | Example scope | Meaning |
|---|---|---|
| Create or calculate from a birth input | `birth_chart_inputs` + `symbolic_calculation` + `collect`/`analyze` | Use only the selected birth-detail record for the named symbolic calculation. |
| Create a derived symbolic map | `symbolic` + `symbolic_calculation` + `collect` | Store a versioned map and links to its feature records. |
| Use the map in a reflective reading | `symbolic` + `personal_reflection` + `analyze` | Use the selected map/features without reopening the raw birth inputs. |
| Use active gates to select a complementary AI prompt | `symbolic` + `personal_reflection` + `analyze`, plus `remote_processing` for a remote AI | The chart owner explicitly enables this mode; send only the gate IDs and source/topology version needed for matching, not raw birth details. Label whether the list is calculated or sender-supplied and unverified. |

These are separate grants or grant scopes; possession of a map pointer is not consent for any of these actions. A deployed system must define how revocation of birth-input access affects recalculation and how deletion propagates to derived maps and readings.

Chart-aware AI is a separate, visible use of the derived map, not an automatic consequence of calculating or storing a chart. The subject must be able to turn it off, inspect the chart version being used, and ask for the same AI support without symbolic matching. For a shared couple/family room, the chart owner must explicitly choose to use their map in that room, all currently joined members must separately consent to the remote AI question, and the interface must say that replies are visible to the room. Never merge one person's chart into a couple or family profile or use a partner's chart to interpret another person's behavior. Keep private chart exploration private by default.

The Matrix bot has two prototype chart-aware paths. `ask-chart` accepts a gate list in one visible command and uses it for that request only. `chart-set` lets a sender explicitly enable their self-attested, unverified gate list for their own later `ask` turns in that room; the sender can clear it with `chart-clear`. This list is personal and non-time-bound; it is not a live transit or momentary activation record. All current room members must have opted into the room's AI processing. The temporary setting is held only in bot process memory and is cleared on opt-out, membership change, or restart. Every chart-aware turn uses only that sender's current question and chart context; it neither receives nor updates shared conversation history. Commands and replies are visible to the room and may remain in Matrix history. The model receives a temporary room-local speaker label, not a Matrix user ID, and chart ownership is not authenticated. The chart context is framed as applying only to the submitting speaker and must not be used to interpret another member. This is an explicit sender action but not an authenticated chart-owner check or a replacement for a future per-chart consent/profile service.

## Stewardship roles

| Context | Default steward | Design requirement |
|---|---|---|
| Adult's own profile and observations | The subject | Private to the subject unless they explicitly share a selected scope |
| Infant/child record | Responsible guardian for necessary care records | Collect the minimum useful context; include the child's developing voice and assent as communication and understanding grow; create a path to age-appropriate control and eventual independent access |
| Clinician, educator, or caregiver collaboration | The subject or guardian who initiates a limited share | Share only selected records for a stated purpose, with recipient and time/scope visible; do not grant a general account view by default |
| Relationship/intimacy context | Each participant controls their own account | A person may record their own experience; do not create a partner profile or store third-party intimate details without that person's informed participation |
| Imported wearable/lab information | The subject, with source limits retained | Request the narrowest practical data scope; preserve source, method, units, and date; do not assume an import authorizes broader analysis or onward sharing |

These are product design goals. Rules about guardianship, minors, education records, health data, and retention vary by place and context; the design must receive appropriate legal and domain review before deployment.

## Data lifecycle controls

### Minimize collection

- Make every domain optional and off until the subject chooses to include it.
- Ask only for fields needed by the current question. Exact birth location, complete menstrual/sexual histories, detailed food logs, or full wearable exports should not be defaults.
- Treat a child's exact age and prematurity context as sensitive. Prefer an optional age anchored to an observation over collecting a date of birth when the calendar date is not needed; do not infer age or life stage from unrelated records.
- Prefer a narrow event or user-described context over broad free-text diaries. Do not request a partner's identity for a subject's own relationship reflection.
- Treat birth time and location, reproductive history, intimacy, child records, and clinical results as sensitive even if a user does not label them that way.
- Keep exact or approximate birth-chart inputs in the separate [`birth-chart input schema`](../schema/birth-chart-input.schema.json), authorized under `birth_chart_inputs`; a subject index or symbolic-map pointer does not authorize their use. Do not copy birth details into the index or a reading. A calculated map and each feature record remain separately versioned resources.

### Keep provenance and access separate

- Every observation retains source and epistemic class; permission metadata does not change whether a record is measured, reported, estimated, or symbolic.
- Store consent grants and sharing events as auditable records separate from the observation payload.
- Derived summaries retain the IDs of their inputs. When an input is deleted or excluded, dependent summaries and readings must be recomputed, withdrawn, or clearly marked as no longer supported.
- Corrections create a new version linked with `supersedes`; they do not overwrite or delete the prior record. Superseded records retain their own consent scope. Revision links and in-memory current-record selection are described in the [record lifecycle rules](record-lifecycle.md); deletion, retention, and dependency invalidation still require a persistent service design.
- A reading uses only the selected record IDs and domains in its request. Availability in the profile is not permission to include a record in every reading.

### Protect processing

Before collecting personal records, define and document the storage location, encryption at rest and in transit, authentication, authorization, backup, retention, incident response, and deletion behavior. Keep credentials and wearable tokens out of observation records and source control. Remote model processing must be disclosed separately, send only the minimum selected context, and not make optional sensitive data available for model training by default. These controls are requirements to design and verify; they are not implemented by the present static site.

### Make sharing explicit

For every export or share, show the selected domains, date range, recipients, whether data are raw or derived, and whether symbolic chart information is included. Provide a preview and a way to revoke future access. Revocation cannot retract a recipient's prior copy, so disclose that limit at the time of sharing.

### Support correction, export, and deletion

Subjects should be able to inspect, correct, export, and delete their records and generated summaries. Preserve correction history only when needed for integrity and explain it clearly. Do not keep a hidden “shadow profile” after deletion. If a service must retain anything for a defined operational or legal reason, identify that before collection and scope the retained copy.

## Consent record draft

A future `consentGrant` record should include:

- pseudonymous subject and grantor references, and the grantor's relationship/authority;
- requested domains and purposes;
- allowed actions: collect, analyze, share, remote-process;
- explicit record IDs or a date window when sharing or remote processing is involved, plus recipient when sharing is involved;
- status: pending, granted, denied, withdrawn, expired;
- grant time, optional expiry, withdrawal time, and the consent-text/version shown;
- child assent or dissent state when relevant, without treating guardian permission as the child's own assent;
- a source/audit reference, without copying sensitive observations into the grant record.

A consent grant must not be assumed from device connection, chart calculation, prior use, a caregiver's relationship, or a general service account. A permission to analyze one reading does not silently authorize future readings or sharing.

In the draft schema, `permittedActions` means currently authorized actions, not requested actions: it must be empty while permission is pending, denied, withdrawn, or expired. An expired grant must carry its expiry time. These structural checks do not enforce authorization at runtime; a future service must check the subject, domain, purpose, time window, recipient, and requested action against active grants before every collection, analysis, export, or remote-processing operation.

The current in-memory policy prototype is [`metheus/authorization.py`](../metheus/authorization.py), policy version `metheus-consent-policy/0.5.0`. The shared phase-system/canonical-phase to consent-domain crosswalk lives in [`metheus/phase_domains.py`](../metheus/phase_domains.py); contract validation checks that every phase in the evocative vocabulary catalog has a crosswalk entry. `evaluate_authorization` requires every selected source record or phase annotation to match an active grant for the same subject, purpose, action, and domain; it checks duplicate record IDs, ambiguous grant IDs within a subject, creation/expiry time, record-ID/date scopes, share recipient, remote-processing disclosure, same-subject supersession/revocation references, explicit child dissent, and bleeding-summary boundary inputs that must match an explicitly selected source event. It accepts only known purposes, record-type/domain pairings, consent domains, actions, and purposes in grants; unknown or malformed values fail closed. A share recipient must have a nonempty reference and an allowed recipient role. Symbolic transits map to `symbolic`, reproductive contexts to `reproductive`, development to `development`, sleep/wake to `sleep`, circadian rhythms to `circadian`, eating rhythms to `nutrition`, and supported ultradian phases to `feeding` or `activity`. An unrecognized phase system/canonical phase has no consent domain and is rejected. A phase annotation and its source basis records are separate selected items and each must be authorized; one phase annotation cannot serve as another's basis. Date scopes must contain the full date span of an interval, including phase-annotation windows, not just the start date. An `ongoing` phase annotation has no finite end, so it cannot be covered by a date-scoped grant; use a specifically record-scoped grant if that ongoing context is authorized. Narrow consent domains are preferred; legacy broad scopes cover only the subdomains listed in that module. For a remote analysis, callers must require both `analyze` and `remote_processing`; for sharing, they must pass the exact recipient. Any denied record makes the batch unauthorized. These checks are a minimum policy guard, not a substitute for validating the complete grant and record schemas when writing them to a trusted store.

`authorize_reading_inputs` in [`metheus/readings.py`](../metheus/readings.py) combines reference checks with consent evaluation for a reading's `analyze` or `remote_processing` action. It selects only personal objects named by the reading's `inputIds`; it also rejects unresolved or cross-subject phase bases and unresolved/ineligible references before evaluating grants. Pass the general correspondence and evidence-claim catalogs separately when the reading cites them. These catalog entries must not be subject-owned; a person's private reflective association belongs in a subject-scoped record with its own consent path. General references are checked for existence and permitted use but are not treated as subject records or covered by the subject's consent. The `symbolic` and `birth_chart_inputs` domains have no broad-category fallback to each other. Remote processing returns separate decisions for analysis and remote processing, and authorizes only if both pass. Sharing a reading still requires `evaluate_authorization` with `action="share"`, the selected recipient, and every personal input item; these helpers remain preflight prototypes, not storage-boundary controls.

For profile-linked resources, [`resolve_subject_index`](../metheus/resources.py) verifies pointer existence, kind, schema version, subject ownership, and symbolic-map input/feature dependencies. [`authorize_subject_index_resources`](../metheus/resources.py) then requires a separate explicit selection and checks grants only for those selected records. The index itself never widens the selection. See the [resource resolution contract](resource-resolution.md) for supported kinds and failure behavior.

```python
from metheus import authorize_reading_inputs

decision = authorize_reading_inputs(
    reading,
    candidate_source_records,
    candidate_phase_annotations,
    consent_grants,
    action="remote_processing",
    correspondences=correspondence_catalog,
    evidence_claims=evidence_claim_catalog,
)
if not decision["authorized"]:
    raise PermissionError("Reading inputs are not authorized for remote processing")
```

Development phase annotations require an explicit life stage. Child stages remain subject to the guardian-steward check even when represented by a derived phase label. The evaluator still cannot verify that the label is accurate or that the grantor has legal authority.

Example call shape:

```python
from metheus import evaluate_authorization

decision = evaluate_authorization(
    selected_source_records,
    consent_grants,
    subject_id="example-subject-01",
    purpose="learning_support",
    action="analyze",
)
if not decision["authorized"]:
    raise PermissionError("Selected records are outside the active consent scope")
```

When a reading includes phase annotations, pass each annotation itself and every supporting record named by its `basisRecordIds` in the evaluator's `records` argument. The evaluator checks that those supporting records are included, then evaluates each item's own consent scope.

The synthetic [consent example](../examples/consent-grant.example.json) demonstrates record-ID and date-window scope for learning records and a symbolic reflection. It deliberately excludes `birth_chart_inputs`. Subject-directed export is a data-access capability, not an additional consent action; a share with another recipient still requires `share` authorization.

This is a policy evaluator, not a complete authorization service: it does not authenticate a subject or grantor, verify guardian authority, validate incoming records against JSON Schema, persist an audit trail, mediate database access, or execute deletion/export. `authorized_delegate` grants also fail closed until their delegated authority can be verified. Callers must fail closed and enforce its decision at the storage and processing boundary. The evaluator is not yet covered by behavioral tests.

The [synthetic consent example](../examples/consent-grant.example.json) permits local collection and analysis for learning support and personal reflection, while granting no sharing or remote processing. It is an illustration of the data shape, not an active permission or deployed consent flow.

## Reading and inference boundaries

- Respect a user's excluded domains even when those data could make a reading appear more complete.
- Do not infer consent, desire, fertility, pregnancy, diagnosis, ability, or a third party's internal state from chart features, biometrics, proxies, or correlations.
- Do not treat a parent's or caregiver's account as direct access to a child's private internal experience.
- Keep a symbolic feature, a sensor signal, a lab result, and a person's interpretation separately attributable.
- When a person asks for deletion or withdraws participation, do not pressure them to continue tracking to preserve model quality.

## Implementation gate

Before any personal data collection or integration ships, the product needs a tested data-flow and threat model; consent and withdrawal behaviors; domain-level access control; export/deletion semantics including derived data; child and intimate-data handling review; and clear disclosures for every third-party device, laboratory import, cloud service, and model-processing path. Until then, Metheus remains a concept site and local schema/design work, not a personal health data service.
