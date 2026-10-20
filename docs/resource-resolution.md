# Subject resource resolution and authorization

**Status:** executable in-memory prototype, version 0.2. `preflight_subject_reading` validates the subject-index and indexed-resource schemas before checking object relationships and consent inputs supplied by a caller. It does not authenticate the subject or steward, retrieve from storage, or enforce a database boundary.

## Resource graph

The subject index is a pseudonymous navigation record. Each `resourceRefs` entry declares an ID, kind, and schema version. The resolver supports these current kinds:

| Index kind | Required resource `recordType` | Version field |
|---|---|---|
| `birth_chart_input` | `birth_chart_input` | `schemaVersion` |
| `symbolic_map` | `symbolic_map` | `schemaVersion` |
| `observation` | `observation`, `event`, `estimate`, `symbolic_feature`, or `context` | `schemaVersion` |
| `phase_annotation` | `phase_annotation` | `schemaVersion` |
| `rhythm_summary` | `rhythm_summary` | `schemaVersion` |

Readings and consent grants are not index resource kinds. Consent grants remain in the authorization store rather than ordinary profile navigation; readings need an output-access/share contract. Rhythm summaries have a dedicated [`derived summary schema`](../schema/rhythm-summary.schema.json) and may be indexed, but this does not mean Metheus persists them to a store.

A symbolic map also has two explicit dependency lists:

- `calculation.inputRecordIds` must resolve to same-subject `birth_chart_input` resources under the `birth_chart_inputs` domain.
- `calculation.featureRecordIds` must resolve to same-subject `symbolic_feature` observations under the `symbolic` domain.

Both sets of dependencies must appear in the subject index under the expected kinds. The resolver checks the IDs, declared type, schema version and ownership. It does not recalculate a chart or verify the symbolic source's claims.

A `rhythm_summary` also carries `summaryMeasure`, domain, method/schema versions, window, limitations, and `inputRecordIds`. The resolver requires each source ID to resolve to a same-subject observation/event indexed as `observation`, and checks that each event type/domain is compatible with the summary measure. A reading that selects a rhythm summary must also explicitly select those source records. The consent evaluator then checks the summary and each source record under their own grants; the summary never inherits permission from its inputs.

## Resolution is not permission

Index membership allows a client to locate an object; it does not authorize collection, analysis, sharing, or remote processing. Call `resolve_subject_index` to check the index structure and references. Then call `authorize_subject_index_resources` with a separate explicit list of selected resource IDs, the stated purpose, action, and grants. Only those selected resources are sent to the consent evaluator. Remote processing requires both `analyze` and `remote_processing` grants. Sharing still requires a recipient-matched grant.

For a reading, [`preflight_subject_reading`](../metheus/readings.py) combines schema validation, index resolution, reading-reference checks, excluded-domain checks, and consent evaluation. It rejects any personal input that is not in the index, but it never adds indexed resources to the reading's selection. It returns a preflight decision only; it does not generate text or protect a storage boundary.

```python
from metheus import authorize_subject_index_resources, resolve_subject_index

resolution = resolve_subject_index(subject_index, candidate_resources)
if not resolution["valid"]:
    raise ValueError("Subject resource references are invalid")

decision = authorize_subject_index_resources(
    subject_index,
    candidate_resources,
    selected_resource_ids=["synthetic-symbolic-map", "synthetic-chart-feature"],
    grants=consent_grants,
    purpose="personal_reflection",
    action="analyze",
)
if not decision["authorized"]:
    raise PermissionError("Selected resources are outside the active consent scope")
```

This reflection selection does not include the raw birth input. The synthetic [`map reflection grant`](../examples/symbolic-map-reflection-consent.example.json) scopes `analyze` to the map and its feature under `symbolic` + `personal_reflection`. Recalculating the map requires its own `symbolic_calculation` purpose and `birth_chart_inputs` consent, as shown in the separate synthetic [birth-input calculation grant](../examples/birth-input-calculation-consent.example.json). The two domains have no broad fallback to one another.

The [synthetic reading example](../examples/symbolic-map-reading.example.json) adds a selected reading with explicit exclusions. To gate that reading before presentation, pass it with the example index, the three synthetic resources, and the map-reflection grant to `preflight_subject_reading`. The [sleep-summary example set](../examples/rhythm-summary-reading.example.json) shows a derived summary, its three synthetic source events, index pointers, narrow consent grant, and reading claims. A passing result means the references and consent inputs passed this prototype; it does not mean the reading text was generated or proven to follow from its sources.

## Failure behavior

Resolution fails closed when an index pointer is missing, duplicated, ambiguous, has a mismatched kind or schema version, or points to a different subject. It also fails when a symbolic-map or rhythm-summary dependency is unresolved, belongs to another subject, uses the wrong resource type/domain, or is missing from the index. Authorization fails when any explicit selection is absent from the index or any selected object lacks a matching active grant.

The result includes issue codes and resource IDs, not record contents. No record is automatically selected just because another resource refers to it. For example, the map resolver confirms that birth inputs exist, but a reflection reading over the calculated map does not thereby receive or authorize the raw birth values.

## Current limitations

- The resolver trusts that supplied objects came from an appropriate trusted source. The reading preflight validates the index and indexed records against schemas but does not authenticate a source or validate unrelated unindexed candidate objects.
- It checks top-level schema-version strings but cannot prove that a particular calculation implementation produced the feature records.
- The subject index steward role is declared metadata; legal authority and identity require a separate verified service.
- Authorization is still in-memory. Authentication, database row-level enforcement, storage encryption, audit logging, revocation propagation, export, and deletion remain unimplemented.
- All pointers in an index must resolve before this prototype authorizes any selection. A production resolver may need a carefully designed partial-availability model without weakening authorization.

See the [`subject index schema`](../schema/subject-index.schema.json), [`birth-chart input schema`](../schema/birth-chart-input.schema.json), [`symbolic map schema`](../schema/symbolic-map.schema.json), [`rhythm summary schema`](../schema/rhythm-summary.schema.json), and the synthetic [index](../examples/subject-index.example.json), [birth input](../examples/birth-chart-input.example.json), [map](../examples/symbolic-map.example.json), and [rhythm summary reading](../examples/rhythm-summary-reading.example.json).
