# Record correction, supersession, and deletion

**Status:** executable in-memory revision rule, version 0.1. This defines how caller-supplied records relate when a correction is made. It is not a persistent audit log, deletion service, or retention policy.

## Correction creates a new record

Treat a saved record as an immutable statement of what was known and reported at that point. To correct it, create a new record with a new ID and a `supersedes` field naming the prior same-subject record. Do not silently overwrite the older value. Observation, birth-chart-input, symbolic-map, phase-annotation, rhythm-summary, and subject-index schemas support this link. Consent grants use supersession and revocation for permission state; knowledge-catalog entries have their own catalog lifecycle. `resolve_current_records` targets subject-scoped histories with `id`, `subjectId`, and a single-predecessor correction meaning; it does not evaluate consent-grant revocation.

Within the history supplied for one subject:

1. Record IDs must be unique.
2. Resolve the predecessor ID only inside the subject's namespace. Never look up a predecessor across subjects.
3. Each prior record may have at most one direct successor. If two corrections compete, resolve that conflict explicitly before using either branch.
4. Where a resource has an integer `revision`, a successor must increment it by one.
5. Self-links and cycles are invalid.
6. A record is current when no supplied record supersedes it. A missing historical predecessor is a warning: a pruned or partial history may be used, but its completeness cannot be verified.

`resolve_current_records` implements these rules and returns current records, superseded IDs, errors, and warnings. The four rhythm summaries call it before applying their date and event filters, so a supplied older observation and its correction do not both contribute. Callers should pass all available subject history before restricting dates. If the supplied history contains a cycle, branch, nonconsecutive index revision, or duplicate ID, summaries fail closed rather than choose a version silently. If a predecessor is absent, the link remains unresolved and the resolver reports a warning; it does not guess which record was intended.

The synthetic [bleeding-onset correction](../examples/bleeding-onset-correction.example.json) supersedes the [original report](../examples/bleeding-onset.example.json). It demonstrates version linkage only; the sample does not imply that dates identify menstrual phase.

```python
from metheus import resolve_current_records

resolution = resolve_current_records(records, subject_id="subject-example")
if not resolution["valid"]:
    raise ValueError("Record history needs correction")
current_records = resolution["currentRecords"]
```

Supersession selects the current statement; it does not erase the historical record, change its provenance, or grant access to it. Consent and authorization still apply to each record independently. A corrected record is not automatically authorized because its predecessor was.

## Derived records and dependency invalidation

Derived summaries retain `inputRecordIds`. When a source observation is corrected, recompute affected summaries from the current source records and write the replacement summary with a new ID and `supersedes` pointing to the prior summary. Readings that cite an obsolete summary must be reviewed or rebuilt before presentation. The current prototype filters revision chains in summary computation, but it does not discover every dependent object or automatically rewrite indexes, summaries, or readings.

For a corrected birth input, recalculate the symbolic map under the explicit calculation method and version, then supersede the prior map if the result changes. Preserve the map's input and feature dependencies. A symbolic map does not update in place when a birth input is corrected.

## Deletion is a different operation

Supersession is not deletion. A future storage service must define deletion of the selected record, dependent summaries/readings, index pointers, caches, exports, backups, and shared copies. It must disclose any limited retention before collection and ensure a deletion does not leave a hidden shadow profile. If deletion removes a predecessor while retaining a correction that references it, the reference becomes unverifiable; the service must either retain a disclosed minimal integrity reference or remove/rewrite dependent lineage metadata consistently. The current repository has no persistent store and executes none of these deletion operations.

Withdrawing a consent grant stops future authorized use under that grant; it does not itself delete the record. Deleting a record does not prove that a previous recipient erased an exported copy. These are separate lifecycle events and require separate product behavior and disclosure.

## Boundaries

- Do not use revision order as a truth score. A newer report may correct a date or value, but it does not invalidate a person's earlier experience.
- Keep the original reporter/source and time on each revision; `supersedes` records the relationship, not the reason or evidence for the correction.
- Do not put sensitive correction narratives into a general-purpose index or logs. A future schema can add a narrow, optional correction reason only if the person needs it.
- Do not expose superseded intimate, reproductive, child, or clinical records merely because they remain in history.
- Revision-chain validation is not identity verification, data integrity signing, database concurrency control, or an audit guarantee.

Related: [observation model](ontology.md), [resource resolution](resource-resolution.md), [privacy and consent](privacy-consent-model.md), and [capability matrix](capability-matrix.md).
