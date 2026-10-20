# Metheus privacy, consent, and data stewardship model

**Status:** product design requirements, version 0.1. These requirements are not a privacy policy, security certification, or statement of legal compliance. The current Metheus site is a static concept site and does not implement personal record collection, storage, wearable connections, consent management, export, or deletion.

## Why this is part of the system

Metheus may represent exact birth details, body measurements, laboratory results, reproductive and menopause context, intimate experience, learning observations, and a child's developmental history. These domains can be identifying or deeply personal, especially when combined. Privacy and agency therefore belong in the model's data architecture, not only in explanatory copy.

## Consent is scoped and revisable

Consent must attach to a **subject**, **data domain**, and **purpose**. A person may allow a reading to use sleep timing while excluding reproductive notes, or allow a private analysis while declining sharing. A symbolic chart calculation from birth date/time/place is a separate purpose from storing or analyzing biometrics. A blanket “agree to Metheus” control is insufficient for optional sensitive domains.

Represent these separately:

1. **Collection:** permission to create or import a record.
2. **Analysis:** permission to include selected records in a derived summary or reading.
3. **Sharing:** permission to disclose selected records or readings to a named role/recipient.
4. **Processing:** whether a task runs on the local device or sends selected data to a remote service.

The permission state must be inspectable and revocable. Withdrawing permission stops future use within that scope. Deletion, retention, or records required by a connected service depend on the actual storage architecture and must be made explicit before collection begins.

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
- Prefer a narrow event or user-described context over broad free-text diaries. Do not request a partner's identity for a subject's own relationship reflection.
- Treat birth time and location, reproductive history, intimacy, child records, and clinical results as sensitive even if a user does not label them that way.

### Keep provenance and access separate

- Every observation retains source and epistemic class; permission metadata does not change whether a record is measured, reported, estimated, or symbolic.
- Store consent grants and sharing events as auditable records separate from the observation payload.
- Derived summaries retain the IDs of their inputs. When an input is deleted or excluded, dependent summaries and readings must be recomputed, withdrawn, or clearly marked as no longer supported.
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
- scope/recipient when sharing is involved;
- status: pending, granted, denied, withdrawn, expired;
- grant time, optional expiry, withdrawal time, and the consent-text/version shown;
- child assent or dissent state when relevant, without treating guardian permission as the child's own assent;
- a source/audit reference, without copying sensitive observations into the grant record.

A consent grant must not be assumed from device connection, chart calculation, prior use, a caregiver's relationship, or a general service account. A permission to analyze one reading does not silently authorize future readings or sharing.

The [synthetic consent example](../examples/consent-grant.example.json) permits local collection and analysis for learning support and personal reflection, while granting no sharing or remote processing. It is an illustration of the data shape, not an active permission or deployed consent flow.

## Reading and inference boundaries

- Respect a user's excluded domains even when those data could make a reading appear more complete.
- Do not infer consent, desire, fertility, pregnancy, diagnosis, ability, or a third party's internal state from chart features, biometrics, proxies, or correlations.
- Do not treat a parent's or caregiver's account as direct access to a child's private internal experience.
- Keep a symbolic feature, a sensor signal, a lab result, and a person's interpretation separately attributable.
- When a person asks for deletion or withdraws participation, do not pressure them to continue tracking to preserve model quality.

## Implementation gate

Before any personal data collection or integration ships, the product needs a tested data-flow and threat model; consent and withdrawal behaviors; domain-level access control; export/deletion semantics including derived data; child and intimate-data handling review; and clear disclosures for every third-party device, laboratory import, cloud service, and model-processing path. Until then, Metheus remains a concept site and local schema/design work, not a personal health data service.
