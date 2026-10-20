#!/usr/bin/env python3
"""Validate Metheus JSON Schemas and their explicitly paired examples."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metheus.phase_domains import phase_authorization_domain

SCHEMA_DIR = ROOT / "schema"
EXAMPLE_DIR = ROOT / "examples"
CATALOG_DIR = ROOT / "catalog"

EXAMPLE_SCHEMAS = {
    "chart-calculation-authorized.example.json": "chart-calculation-preflight.schema.json",
    "chart-calculation-denied.example.json": "chart-calculation-preflight.schema.json",
    "chart-calculation-readiness.example.json": "chart-calculation-preflight.schema.json",
    "assembled-reading.example.json": "assembled-reading.schema.json",
    "assembled-reading-correspondence.example.json": "assembled-reading.schema.json",
    "assembled-reading-circadian.example.json": "assembled-reading.schema.json",
    "assembled-reading-ai-affordance.example.json": "assembled-reading.schema.json",
    "assembled-reading-measurement-series.example.json": "assembled-reading.schema.json",
    "assembled-reading-promethean-maps.example.json": "assembled-reading.schema.json",
    "chart-aware-ai-context-unverified.example.json": "chart-aware-ai-context.schema.json",
    "chart-aware-ai-context-calculated-natal.example.json": "chart-aware-ai-context.schema.json",
    "birth-chart-input.example.json": "birth-chart-input.schema.json",
    "birth-input-calculation-consent.example.json": "consent.schema.json",
    "bleeding-onset.example.json": "observation.schema.json",
    "bleeding-onset-correction.example.json": "observation.schema.json",
    "bleeding-onset-summary.example.json": "rhythm-summary.schema.json",
    "menstrual-cycle-day-one-2026-09-02.example.json": "observation.schema.json",
    "menstrual-cycle-day-one-2026-10-01.example.json": "observation.schema.json",
    "menstrual-cycle-day-one-2026-10-30.example.json": "observation.schema.json",
    "menstrual-cycle-day-one-2026-11-29.example.json": "observation.schema.json",
    "menstrual-cycle-day-one-summary.example.json": "rhythm-summary.schema.json",
    "reported-cycle-day-view.example.json": "reported-cycle-day-view.schema.json",
    "consent-grant.example.json": "consent.schema.json",
    "development-context-infant.example.json": "observation.schema.json",
    "development-context-preterm-birth.example.json": "observation.schema.json",
    "development-context-preterm-corrected-age.example.json": "observation.schema.json",
    "experience-pathway-synthetic.example.json": "experience-pathway.schema.json",
    "experience-pathway-local-preflight.example.json": "experience-pathway-case.schema.json",
    "gate-correspondence-reading.example.json": "reading.schema.json",
    "interaction-intimacy.example.json": "interaction-event.schema.json",
    "interaction-intimacy-correction.example.json": "interaction-event.schema.json",
    "interaction-intimacy-consent.example.json": "consent.schema.json",
    "interaction-corrected-subject-index.example.json": "subject-index.schema.json",
    "interaction-subject-index.example.json": "subject-index.schema.json",
    "environmental-affordance-ai-use.example.json": "observation.schema.json",
    "environmental-affordance-linked-case.example.json": "environmental-affordance-case.schema.json",
    "environmental-affordance-response.example.json": "observation.schema.json",
    "affordance-trial-summary.example.json": "environmental-affordance-trial-summary.schema.json",
    "affordance-trial-consent.example.json": "consent.schema.json",
    "learner-feedback.example.json": "observation.schema.json",
    "learning-activity.example.json": "observation.schema.json",
    "learning-reading.example.json": "reading.schema.json",
    "measurement-series-2026-10-18.example.json": "observation.schema.json",
    "measurement-series-2026-10-19.example.json": "observation.schema.json",
    "measurement-series-summary.example.json": "rhythm-summary.schema.json",
    "phase-aware-reading.example.json": "reading.schema.json",
    "phase-bleeding-observation.example.json": "observation.schema.json",
    "phase-chart-feature.example.json": "observation.schema.json",
    "phase-circadian.example.json": "phase-annotation.schema.json",
    "phase-eating.example.json": "phase-annotation.schema.json",
    "phase-epimethean.example.json": "phase-annotation.schema.json",
    "phase-promethean.example.json": "phase-annotation.schema.json",
    "phase-observation-relation.example.json": "temporal-relation.schema.json",
    "phase-ultradian-infant-feed.example.json": "phase-annotation.schema.json",
    "urinary-lh-home-test.example.json": "observation.schema.json",
    "promethean-feature.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-18.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-19.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-20.example.json": "observation.schema.json",
    "rhythm-sleep-summary.example.json": "rhythm-summary.schema.json",
    "rhythm-subject-index.example.json": "subject-index.schema.json",
    "rhythm-summary-consent.example.json": "consent.schema.json",
    "rhythm-summary-reading.example.json": "reading.schema.json",
    "serum-tsh-laboratory.example.json": "observation.schema.json",
    "subject-index.example.json": "subject-index.schema.json",
    "symbolic-map-reading.example.json": "reading.schema.json",
    "symbolic-map-reflection-consent.example.json": "consent.schema.json",
    "symbolic-map.example.json": "symbolic-map.schema.json",
    "temporal-order.example.json": "temporal-relation.schema.json",
}

CATALOG_SCHEMAS = {
    "gate-endocrine-correspondences.json": "correspondence-catalog.schema.json",
    "gate-ai-affordances.json": "gate-ai-affordance-catalog.schema.json",
    "endocrine-relations.json": "endocrine-relations-catalog.schema.json",
    "evidence-claims.json": "evidence-catalog.schema.json",
    "human-design-bodygraph-topology.json": "human-design-bodygraph-topology.schema.json",
    "phase-vocabulary.json": "phase-vocabulary.schema.json",
}

CATALOG_ITEM_SCHEMAS = {
    "gate-endocrine-correspondences.json": ("correspondences", "correspondence.schema.json"),
    "endocrine-relations.json": ("relations", "endocrine-relation.schema.json"),
    "evidence-claims.json": ("claims", "evidence-claim.schema.json"),
}

EXPECTED_CENTER_GATE_COUNTS = {
    "head": 3,
    "ajna": 6,
    "throat": 11,
    "g_identity": 8,
    "heart": 4,
    "solar_plexus": 7,
    "sacral": 9,
    "spleen": 7,
    "root": 9,
}
SVG_CENTER_IDS = {
    "head": "head",
    "ajna": "ajna",
    "throat": "throat",
    "g": "g_identity",
    "ego": "heart",
    "solar": "solar_plexus",
    "sacral": "sacral",
    "spleen": "spleen",
    "root": "root",
}



def validate_correspondence_source_register(catalog: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(catalog, dict):
        return errors
    correspondences = catalog.get("correspondences")
    sources = catalog.get("sourceRegister")
    if not isinstance(correspondences, list) or not isinstance(sources, list):
        return errors
    entries = {item.get("id"): item for item in correspondences if isinstance(item, dict) and isinstance(item.get("id"), str)}
    def string_set(value: Any) -> set[str]:
        return {item for item in value if isinstance(item, str)} if isinstance(value, list) else set()

    seen_source_ids: set[str] = set()
    registered_entries: dict[str, str] = {}
    for source_index, source in enumerate(sources):
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        path = f"catalog/gate-endocrine-correspondences.json at sourceRegister/{source_index}"
        if isinstance(source_id, str):
            if source_id in seen_source_ids:
                errors.append(f"{path}/id: duplicate source ID {source_id}")
            seen_source_ids.add(source_id)
        included_ids = source.get("includedEntryIds", [])
        if not isinstance(included_ids, list):
            continue
        included_gates: set[str] = set()
        for entry_id in included_ids:
            if not isinstance(entry_id, str):
                continue
            if entry_id in registered_entries:
                errors.append(f"{path}/includedEntryIds: entry {entry_id} is registered more than once")
            registered_entries[entry_id] = source_id if isinstance(source_id, str) else "<unknown>"
            entry = entries.get(entry_id)
            if entry is None:
                errors.append(f"{path}/includedEntryIds: unresolved correspondence {entry_id}")
                continue
            source_system = entry.get("sourceSystem")
            source_system = source_system if isinstance(source_system, dict) else {}
            if source_system.get("lineage") != source.get("lineage"):
                errors.append(f"{path}/lineage: does not match correspondence {entry_id}")
            feature = entry.get("sourceFeature")
            feature = feature if isinstance(feature, dict) else {}
            gate_id = feature.get("id")
            if feature.get("kind") != "gate" or not isinstance(gate_id, str):
                errors.append(f"{path}/includedEntryIds: correspondence {entry_id} is not a gate entry")
                continue
            included_gates.add(gate_id)
            if gate_id not in string_set(source.get("coveredGateIds")):
                errors.append(f"{path}/coveredGateIds: does not cover correspondence gate {gate_id}")
            prefix = source.get("citationUrlPrefix")
            citations = entry.get("sourceCitations", [])
            if isinstance(prefix, str) and not any(
                isinstance(citation, dict) and isinstance(citation.get("url"), str) and citation["url"].startswith(prefix)
                for citation in citations
            ):
                errors.append(f"{path}/citationUrlPrefix: no source citation for correspondence {entry_id} matches the registered source")
        declared_gates = string_set(source.get("includedGateIds"))
        if included_gates != declared_gates:
            errors.append(f"{path}/includedGateIds: does not match gates in includedEntryIds")
        covered_gates = string_set(source.get("coveredGateIds"))
        excluded_gates = string_set(source.get("excludedGateIds"))
        if declared_gates & excluded_gates or declared_gates | excluded_gates != covered_gates:
            errors.append(f"{path}: included and excluded gates must partition coveredGateIds")
    for entry_id in entries:
        if entry_id not in registered_entries:
            errors.append(f"catalog/gate-endocrine-correspondences.json: correspondence {entry_id} is absent from sourceRegister")
    return errors


def validate_bodygraph_topology(catalog: Any) -> list[str]:
    """Check graph integrity beyond what JSON Schema can express."""
    if not isinstance(catalog, dict):
        return ["catalog/human-design-bodygraph-topology.json: expected an object"]

    errors: list[str] = []
    centers = catalog.get("centers", [])
    gates = catalog.get("gates", [])
    channels = catalog.get("channels", [])
    if not all(isinstance(items, list) for items in (centers, gates, channels)):
        return ["catalog/human-design-bodygraph-topology.json: centers, gates, and channels must be arrays"]

    center_ids = [center.get("id") for center in centers if isinstance(center, dict) and isinstance(center.get("id"), str)]
    if len(center_ids) != len(set(center_ids)) or set(center_ids) != set(EXPECTED_CENTER_GATE_COUNTS):
        errors.append("catalog/human-design-bodygraph-topology.json: centers must contain each expected center exactly once")

    gate_by_number: dict[int, dict[str, Any]] = {}
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict) or not isinstance(gate.get("number"), int):
            continue
        number = gate["number"]
        if number in gate_by_number:
            errors.append(f"catalog/human-design-bodygraph-topology.json at gates/{index}/number: duplicate gate {number}")
        gate_by_number[number] = gate
    if set(gate_by_number) != set(range(1, 65)):
        errors.append("catalog/human-design-bodygraph-topology.json: gates must cover each number from 1 through 64 exactly once")

    center_membership: dict[int, str] = {}
    for index, center in enumerate(centers):
        if not isinstance(center, dict):
            continue
        center_id = center.get("id")
        gate_numbers = center.get("gateNumbers", [])
        if not isinstance(gate_numbers, list):
            continue
        expected_count = EXPECTED_CENTER_GATE_COUNTS.get(center_id) if isinstance(center_id, str) else None
        if len(gate_numbers) != expected_count:
            errors.append(f"catalog/human-design-bodygraph-topology.json at centers/{index}/gateNumbers: unexpected gate count for {center_id}")
        for number in gate_numbers:
            if not isinstance(number, int) or isinstance(number, bool):
                continue
            if number in center_membership:
                errors.append(f"catalog/human-design-bodygraph-topology.json at centers/{index}/gateNumbers: gate {number} occurs in multiple centers")
            center_membership[number] = center_id
            gate = gate_by_number.get(number)
            if gate is not None and gate.get("centerId") != center_id:
                errors.append(f"catalog/human-design-bodygraph-topology.json: gate {number} has inconsistent center membership")
    if set(center_membership) != set(range(1, 65)):
        errors.append("catalog/human-design-bodygraph-topology.json: center gate lists must partition all 64 gates")

    channel_by_id: dict[str, dict[str, Any]] = {}
    unordered_pairs: set[tuple[int, int]] = set()
    gate_channels: dict[int, set[str]] = {number: set() for number in range(1, 65)}
    for index, channel in enumerate(channels):
        if not isinstance(channel, dict):
            continue
        channel_id = channel.get("id")
        gate_a, gate_b = channel.get("gateA"), channel.get("gateB")
        if isinstance(channel_id, str):
            if channel_id in channel_by_id:
                errors.append(f"catalog/human-design-bodygraph-topology.json at channels/{index}/id: duplicate channel ID {channel_id}")
            channel_by_id[channel_id] = channel
        if (
            not isinstance(gate_a, int)
            or isinstance(gate_a, bool)
            or not isinstance(gate_b, int)
            or isinstance(gate_b, bool)
        ):
            continue
        pair = tuple(sorted((gate_a, gate_b)))
        if gate_a == gate_b or pair in unordered_pairs:
            errors.append(f"catalog/human-design-bodygraph-topology.json at channels/{index}: channel endpoints must be unique")
        unordered_pairs.add(pair)
        expected_id = f"ch-{gate_a}-{gate_b}"
        if channel_id != expected_id:
            errors.append(f"catalog/human-design-bodygraph-topology.json at channels/{index}/id: ID must match ordered gate endpoints")
        if gate_a in gate_channels:
            gate_channels[gate_a].add(channel_id)
        if gate_b in gate_channels:
            gate_channels[gate_b].add(channel_id)
        if center_membership.get(gate_a) != channel.get("centerA") or center_membership.get(gate_b) != channel.get("centerB"):
            errors.append(f"catalog/human-design-bodygraph-topology.json at channels/{index}: center endpoints do not match gate membership")
    if len(channels) != 36 or len(unordered_pairs) != 36:
        errors.append("catalog/human-design-bodygraph-topology.json: expected 36 unique channel edges")

    for number, gate in gate_by_number.items():
        declared = gate.get("channelIds")
        if isinstance(declared, list) and all(isinstance(item, str) for item in declared) and set(declared) != gate_channels.get(number, set()):
            errors.append(f"catalog/human-design-bodygraph-topology.json: gate {number} channel references are inconsistent")

    # chat/ is generated by the PWA build and ignored by GitHub. Validate the
    # canonical checked-in asset so clean CI checkouts do not depend on a local build.
    reference_path = ROOT / "pwa" / "public" / "bodygraph-reference.svg"
    try:
        reference_root = ET.parse(reference_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [*errors, f"pwa/public/bodygraph-reference.svg: cannot parse reference topology: {exc}"]
    if reference_root.get("data-topology-catalog-id") != catalog.get("catalogId"):
        errors.append("pwa/public/bodygraph-reference.svg: topology catalog ID does not match the source catalog")
    if reference_root.get("data-topology-version") != catalog.get("version"):
        errors.append("pwa/public/bodygraph-reference.svg: topology version does not match the source catalog")

    svg_gate_centers: dict[int, str] = {}
    for element in reference_root.iter():
        gate_value = element.get("data-gate")
        if gate_value is None:
            continue
        try:
            gate_number = int(gate_value)
        except ValueError:
            errors.append(f"pwa/public/bodygraph-reference.svg: invalid data-gate value {gate_value!r}")
            continue
        center_id = SVG_CENTER_IDS.get(element.get("data-center", ""))
        if gate_number in svg_gate_centers:
            errors.append(f"pwa/public/bodygraph-reference.svg: duplicate gate marker {gate_number}")
        elif center_id is None:
            errors.append(f"pwa/public/bodygraph-reference.svg: gate {gate_number} has an unknown center marker")
        else:
            svg_gate_centers[gate_number] = center_id

    if set(svg_gate_centers) != set(range(1, 65)):
        errors.append("pwa/public/bodygraph-reference.svg: expected one marker for every gate from 1 through 64")
    for number in range(1, 65):
        catalog_gate = gate_by_number.get(number)
        if catalog_gate is not None and catalog_gate.get("centerId") != svg_gate_centers.get(number):
            errors.append(f"catalog/human-design-bodygraph-topology.json: gate {number} center differs from the PWA reference graphic")

    svg_channel_pairs: set[tuple[int, int]] = set()
    for element in reference_root.iter():
        if "channel-group" not in element.get("class", "").split():
            continue
        channel_value = element.get("data-channel")
        try:
            gate_a, gate_b = (int(part) for part in (channel_value or "").split("-", maxsplit=1))
        except (ValueError, TypeError):
            errors.append(f"pwa/public/bodygraph-reference.svg: invalid data-channel value {channel_value!r}")
            continue
        pair = tuple(sorted((gate_a, gate_b)))
        if pair in svg_channel_pairs:
            errors.append(f"pwa/public/bodygraph-reference.svg: duplicate channel marker {channel_value}")
        svg_channel_pairs.add(pair)
    if svg_channel_pairs != unordered_pairs:
        errors.append("catalog/human-design-bodygraph-topology.json: channel pairs differ from the PWA reference graphic")
    return errors


def validate_gate_ai_affordances(catalog: Any) -> list[str]:
    """Keep the optional AI idea catalog keyed to the versioned gate topology."""
    path = "catalog/gate-ai-affordances.json"
    if not isinstance(catalog, dict):
        return [f"{path}: expected an object"]
    try:
        topology = load_json(CATALOG_DIR / "human-design-bodygraph-topology.json")
    except (json.JSONDecodeError, OSError) as exc:
        return [f"{path}: cannot read gate topology reference: {exc}"]
    if not isinstance(topology, dict) or not isinstance(topology.get("gates"), list):
        return [f"{path}: referenced gate topology must contain a gates array"]
    source_gates = {
        gate.get("number"): gate
        for gate in topology.get("gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("number"), int)
    }
    if catalog.get("topologyCatalogId") != topology.get("catalogId") or catalog.get("topologyVersion") != topology.get("version"):
        return [f"{path}: topologyCatalogId/topologyVersion must match the referenced topology catalog"]
    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        return [f"{path}: entries must be an array"]
    errors: list[str] = []
    seen: set[int] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("gateNumber"), int) or isinstance(entry.get("gateNumber"), bool):
            continue
        number = entry["gateNumber"]
        if number in seen:
            errors.append(f"{path} at entries/{index}/gateNumber: duplicate gate {number}")
        seen.add(number)
        source = source_gates.get(number)
        if source is None:
            errors.append(f"{path} at entries/{index}/gateNumber: gate {number} is absent from the topology catalog")
            continue
        for field, expected in (("title", source.get("title")), ("centerId", source.get("centerId")), ("channelIds", source.get("channelIds"))):
            if entry.get(field) != expected:
                errors.append(f"{path} at entries/{index}/{field}: differs from topology gate {number}")
    if seen != set(range(1, 65)):
        errors.append(f"{path}: entries must contain every gate from 1 through 64 exactly once")
    return errors


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous JSON objects instead of silently keeping the last key."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise json.JSONDecodeError(f"duplicate object key {key!r}", "", 0)
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=_reject_duplicate_json_keys)


def phase_name_provenance_rules(schema: dict[str, Any], *, assembled: bool) -> list[dict[str, Any]]:
    """Extract the name/source conditionals shared by phase input and output contracts."""
    if assembled:
        phase_schema = schema.get("$defs", {}).get("phaseAnnotation", {})
    else:
        phase_schema = schema
    conditions = phase_schema.get("allOf", [])
    if not isinstance(conditions, list):
        return []
    rules = []
    for condition in conditions:
        if not isinstance(condition, dict):
            continue
        condition_if = condition.get("if", {})
        marker_properties = condition_if.get("properties", {}) if isinstance(condition_if, dict) else {}
        required = condition_if.get("required", []) if isinstance(condition_if, dict) else []
        name_source = marker_properties.get("nameSource", {}) if isinstance(marker_properties, dict) else {}
        if (
            "evocativeName" in required
            or "nameSource" in required
            or (isinstance(name_source, dict) and name_source.get("const") == "source_attributed")
        ):
            rules.append({"if": condition.get("if"), "then": condition.get("then")})
    return rules


def _reject_remote_schema_retrieval(uri: str) -> Resource[Any]:
    """Keep validation local; all cross-schema references must be registered."""
    raise NoSuchResource(ref=uri)


def main() -> int:
    errors: list[str] = []
    schemas: dict[str, dict[str, Any]] = {}

    for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        try:
            schema = load_json(schema_path)
            Draft202012Validator.check_schema(schema)
            schemas[schema_path.name] = schema
        except (json.JSONDecodeError, OSError, SchemaError) as exc:
            errors.append(f"{schema_path.relative_to(ROOT)}: invalid schema: {exc}")

    phase_schema = schemas.get("phase-annotation.schema.json")
    assembled_schema = schemas.get("assembled-reading.schema.json")
    if phase_schema is not None and assembled_schema is not None:
        input_name_rules = phase_name_provenance_rules(phase_schema, assembled=False)
        output_name_rules = phase_name_provenance_rules(assembled_schema, assembled=True)
        if len(input_name_rules) != 3 or input_name_rules != output_name_rules:
            errors.append(
                "schema/phase-annotation.schema.json and schema/assembled-reading.schema.json: "
                "phase name provenance rules must match for required attribution and source citation"
            )

    registry = Registry(retrieve=_reject_remote_schema_retrieval)
    for schema in schemas.values():
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))

    actual_examples = {path.name for path in EXAMPLE_DIR.glob("*.example.json")}
    mapped_examples = set(EXAMPLE_SCHEMAS)
    for filename in sorted(actual_examples - mapped_examples):
        errors.append(f"examples/{filename}: no schema mapping")
    for filename in sorted(mapped_examples - actual_examples):
        errors.append(f"examples/{filename}: mapped example file is missing")

    format_checker = FormatChecker()
    for filename, schema_filename in sorted(EXAMPLE_SCHEMAS.items()):
        example_path = EXAMPLE_DIR / filename
        schema = schemas.get(schema_filename)
        if not example_path.is_file() or schema is None:
            continue
        try:
            instance = load_json(example_path)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"examples/{filename}: cannot read JSON: {exc}")
            continue
        validator = Draft202012Validator(schema, format_checker=format_checker, registry=registry)
        for error in sorted(validator.iter_errors(instance), key=lambda item: tuple(map(str, item.absolute_path))):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            errors.append(f"examples/{filename} at {location}: {error.message}")
        if filename == "experience-pathway-synthetic.example.json" and isinstance(instance, dict):
            nodes = instance.get("nodes", [])
            relations = instance.get("relations", [])
            nodes = nodes if isinstance(nodes, list) else []
            relations = relations if isinstance(relations, list) else []
            node_ids = [node.get("nodeId") for node in nodes if isinstance(node, dict) and isinstance(node.get("nodeId"), str)]
            relation_ids = [relation.get("relationId") for relation in relations if isinstance(relation, dict) and isinstance(relation.get("relationId"), str)]
            if len(node_ids) != len(set(node_ids)):
                errors.append(f"examples/{filename}: duplicate pathway node IDs")
            if len(relation_ids) != len(set(relation_ids)):
                errors.append(f"examples/{filename}: duplicate pathway relation IDs")
            known_node_ids = set(node_ids)
            try:
                evidence_catalog = load_json(CATALOG_DIR / "evidence-claims.json")
            except (json.JSONDecodeError, OSError) as exc:
                errors.append(f"examples/{filename}: cannot load evidence catalog: {exc}")
                evidence_catalog = {}
            evidence_by_id = {
                claim.get("id"): claim
                for claim in evidence_catalog.get("claims", [])
                if isinstance(claim, dict) and isinstance(claim.get("id"), str)
            }
            expected_claim_types = {
                "literature_association": "biomedical_association",
                "literature_mechanism": "biomedical_mechanism",
                "literature_intervention": "intervention_effect",
                "literature_measurement": "measurement_validity",
            }
            for index, relation in enumerate(relations):
                if not isinstance(relation, dict):
                    continue
                for endpoint in ("fromNodeId", "toNodeId"):
                    endpoint_id = relation.get(endpoint)
                    if not isinstance(endpoint_id, str) or endpoint_id not in known_node_ids:
                        errors.append(f"examples/{filename} at relations/{index}/{endpoint}: unresolved pathway node")
                relation_type = relation.get("relationType")
                expected_type = expected_claim_types.get(relation_type)
                evidence_ids = relation.get("evidenceClaimIds", [])
                if evidence_ids and expected_type is None:
                    errors.append(f"examples/{filename} at relations/{index}/evidenceClaimIds: evidence attached to non-literature relation")
                for claim_id in evidence_ids:
                    claim = evidence_by_id.get(claim_id)
                    if claim is None:
                        errors.append(f"examples/{filename} at relations/{index}/evidenceClaimIds: unresolved evidence claim")
                    elif claim.get("claimType") != expected_type:
                        errors.append(f"examples/{filename} at relations/{index}/evidenceClaimIds: evidence claim type mismatch")
        if filename == "gate-correspondence-reading.example.json" and isinstance(instance, dict):
            catalog_path = CATALOG_DIR / "gate-endocrine-correspondences.json"
            try:
                catalog = load_json(catalog_path)
            except (json.JSONDecodeError, OSError) as exc:
                errors.append(f"examples/{filename}: cannot load correspondence catalog: {exc}")
                catalog = {}
            known_correspondences = {
                item.get("id") for item in catalog.get("correspondences", [])
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            selected_references = set(instance.get("referenceIds", []))
            for index, claim in enumerate(instance.get("claims", [])):
                if not isinstance(claim, dict):
                    continue
                for correspondence_id in claim.get("correspondenceIds", []):
                    if correspondence_id not in known_correspondences:
                        errors.append(f"examples/{filename} at claims/{index}/correspondenceIds: unresolved correspondence {correspondence_id}")
                    if correspondence_id not in selected_references:
                        errors.append(f"examples/{filename} at claims/{index}/correspondenceIds: correspondence {correspondence_id} is not selected in referenceIds")
                if claim.get("correspondenceIds") and claim.get("claimType") not in {"symbolic_prompt", "interpretive_question"}:
                    errors.append(f"examples/{filename} at claims/{index}/claimType: correspondence requires a symbolic prompt or interpretive question")

    actual_catalogs = {path.name for path in CATALOG_DIR.glob("*.json")} if CATALOG_DIR.exists() else set()
    mapped_catalogs = set(CATALOG_SCHEMAS)
    for filename in sorted(actual_catalogs - mapped_catalogs):
        errors.append(f"catalog/{filename}: no schema mapping")
    for filename in sorted(mapped_catalogs - actual_catalogs):
        errors.append(f"catalog/{filename}: mapped catalog file is missing")

    for filename, schema_filename in sorted(CATALOG_SCHEMAS.items()):
        catalog_path = CATALOG_DIR / filename
        schema = schemas.get(schema_filename)
        if not catalog_path.is_file() or schema is None:
            continue
        try:
            catalog = load_json(catalog_path)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"catalog/{filename}: cannot read JSON: {exc}")
            continue
        validator = Draft202012Validator(schema, format_checker=format_checker, registry=registry)
        for error in sorted(validator.iter_errors(catalog), key=lambda item: tuple(map(str, item.absolute_path))):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            errors.append(f"catalog/{filename} at {location}: {error.message}")
        if filename == "human-design-bodygraph-topology.json":
            errors.extend(validate_bodygraph_topology(catalog))
        if filename == "gate-ai-affordances.json":
            errors.extend(validate_gate_ai_affordances(catalog))
            public_copy = ROOT / "pwa/public/gate-ai-affordances.json"
            try:
                public_catalog = load_json(public_copy)
            except (json.JSONDecodeError, OSError) as exc:
                errors.append(f"pwa/public/gate-ai-affordances.json: cannot read public catalog copy: {exc}")
            else:
                if public_catalog != catalog:
                    errors.append("pwa/public/gate-ai-affordances.json: must match catalog/gate-ai-affordances.json")
        if filename == "gate-endocrine-correspondences.json":
            errors.extend(validate_correspondence_source_register(catalog))
        item_schema_mapping = CATALOG_ITEM_SCHEMAS.get(filename)
        if item_schema_mapping is not None and isinstance(catalog, dict):
            collection_key, item_schema_filename = item_schema_mapping
            item_schema = schemas.get(item_schema_filename)
            items = catalog.get(collection_key)
            if item_schema is not None and isinstance(items, list):
                item_validator = Draft202012Validator(item_schema, format_checker=format_checker, registry=registry)
                item_ids: set[str] = set()
                for index, item in enumerate(items):
                    for error in sorted(item_validator.iter_errors(item), key=lambda item_error: tuple(map(str, item_error.absolute_path))):
                        location = "/".join(str(part) for part in (collection_key, index, *error.absolute_path)) or "$"
                        errors.append(f"catalog/{filename} at {location}: {error.message}")
                    if isinstance(item, dict):
                        item_id = item.get("id")
                        if isinstance(item_id, str) and item_id in item_ids:
                            errors.append(f"catalog/{filename} at {collection_key}/{index}/id: duplicate claim ID {item_id}")
                        elif isinstance(item_id, str):
                            item_ids.add(item_id)
                        if catalog.get("catalogStatus") == "candidate_only" and (
                            item.get("evidenceStatus") != "under_review"
                            or item.get("permittedUse") != "internal_only"
                        ):
                            errors.append(
                                f"catalog/{filename} at {collection_key}/{index}: candidate-only entries must remain under_review and internal_only"
                            )
        phase_keys: set[tuple[str, str, str]] = set()
        for index, phase in enumerate(catalog.get("phases", []) if isinstance(catalog, dict) else []):
            if not isinstance(phase, dict):
                continue
            key = (phase.get("layer"), phase.get("phaseSystem"), phase.get("canonicalPhase"))
            if key in phase_keys:
                errors.append(f"catalog/{filename} at phases/{index}: duplicate phase key {key}")
            phase_keys.add(key)
            expected_layer = "promethean" if phase.get("phaseSystem") in {"human_design_transit", "astrological_transit"} else "epimethean"
            if phase.get("layer") != expected_layer:
                errors.append(f"catalog/{filename} at phases/{index}/layer: layer does not match phaseSystem")
            if phase_authorization_domain(phase.get("phaseSystem"), phase.get("canonicalPhase")) is None:
                errors.append(
                    f"catalog/{filename} at phases/{index}: phase has no authorization-domain mapping"
                )
        if filename == "phase-vocabulary.json":
            allowed_by_system: dict[str, set[str]] = {}
            for phase in catalog.get("phases", []) if isinstance(catalog, dict) else []:
                if not isinstance(phase, dict):
                    continue
                system = phase.get("phaseSystem")
                canonical = phase.get("canonicalPhase")
                if isinstance(system, str) and system != "other" and isinstance(canonical, str):
                    allowed_by_system.setdefault(system, set()).add(canonical)
            phase_schema = schemas.get("phase-annotation.schema.json", {})
            conditions = phase_schema.get("$defs", {}).get("phaseVocabularyConstraint", {}).get("allOf", [])
            schema_by_system = {}
            for condition in conditions:
                if not isinstance(condition, dict):
                    continue
                system = condition.get("if", {}).get("properties", {}).get("phaseSystem", {}).get("const")
                labels = condition.get("then", {}).get("properties", {}).get("canonicalPhase", {}).get("enum")
                if isinstance(system, str) and isinstance(labels, list) and all(isinstance(value, str) for value in labels):
                    schema_by_system[system] = set(labels)
            if schema_by_system != allowed_by_system:
                errors.append("schema/phase-annotation.schema.json: canonical phase labels do not match catalog/phase-vocabulary.json")

    if errors:
        print("Metheus contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(schemas)} JSON Schemas, {len(EXAMPLE_SCHEMAS)} mapped examples, and {len(CATALOG_SCHEMAS)} mapped catalogs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
