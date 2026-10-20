# Subject resource resolution and authorization

**Status:** executable in-memory prototype, version 0.1. These helpers check object relationships and consent inputs supplied by a caller. They do not validate complete JSON Schema compliance, authenticate the subject or steward, retrieve from storage, or enforce a database boundary.

## Resource graph

The subject index is a pseudonymous navigation record. Each `resourceRefs` entry declares an ID, kind, and schema version. The resolver supports these current kinds:

| Index kind | Required resource `recordType` | Version field |
|---|---|---|
| `birth_chart_input` | `birth_chart_input` | `schemaVersion` |
| `symbolic_map` | `symbolic_map` | `schemaVersion` |
| `observation` | `observation`, `event`, `estimate`, `symbolic_feature`, or `context` | `schemaVersion` |
| `phase_annotation` | `phase_annotation` | `schemaVersion` |

Readings, consent grants, and derived summaries are not currently index resource kinds. Consent grants remain in the authorization store rather than ordinary profile navigation; readings need an output-access/share contract; derived summaries need a persistence schema before they can be added safely.

A symbolic map also has two explicit dependency lists:

- `calculation.inputRecordIds` must resolve to same-subject `birth_chart_input` resources under the `birth_chart_inputs` domain.
- `calculation.featureRecordIds` must resolve to same-subject `symbolic_feature` observations under the `symbolic` domain.

Both sets of dependencies must appear in the subject index under the expected kinds. The resolver checks the IDs, declared type, schema version and ownership. It does not recalculate a chart or verify the symbolic source's claims.

## Resolution is not permission

Index membership allows a client to locate an object; it does not authorize collection, analysis, sharing, or remote processing. Call `resolve_subject_index` to check the index structure and references. Then call `authorize_subject_index_resources` with a separate explicit list of selected resource IDs, the stated purpose, action, and grants. Only those selected resources are sent to the consent evaluator. Remote processing requires both `analyze` and `remote_processing` grants. Sharing still requires a recipient-matched grant.

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

## Failure behavior

Resolution fails closed when an index pointer is missing, duplicated, ambiguous, has a mismatched kind or schema version, or points to a different subject. It also fails when a symbolic map dependency is unresolved, belongs to another subject, uses the wrong resource type/domain, or is missing from the index. Authorization fails when any explicit selection is absent from the index or any selected object lacks a matching active grant.

The result includes issue codes and resource IDs, not record contents. No record is automatically selected just because another resource refers to it. For example, the map resolver confirms that birth inputs exist, but a reflection reading over the calculated map does not thereby receive or authorize the raw birth values.

## Current limitations

- The resolver trusts that supplied objects were loaded from a trusted source and parsed correctly. It does not run a JSON Schema validator.
- It checks top-level schema-version strings but cannot prove that a particular calculation implementation produced the feature records.
- The subject index steward role is declared metadata; legal authority and identity require a separate verified service.
- Authorization is still in-memory. Authentication, database row-level enforcement, storage encryption, audit logging, revocation propagation, export, and deletion remain unimplemented.
- All pointers in an index must resolve before this prototype authorizes any selection. A production resolver may need a carefully designed partial-availability model without weakening authorization.

See the [`subject index schema`](../schema/subject-index.schema.json), [`birth-chart input schema`](../schema/birth-chart-input.schema.json), [`symbolic map schema`](../schema/symbolic-map.schema.json), and the synthetic [index](../examples/subject-index.example.json), [birth input](../examples/birth-chart-input.example.json), and [map](../examples/symbolic-map.example.json).
