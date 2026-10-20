#!/usr/bin/env python3
"""Validate Metheus JSON Schemas and their explicitly paired examples."""

from __future__ import annotations

import json
import sys
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
    "assembled-reading.example.json": "assembled-reading.schema.json",
    "assembled-reading-circadian.example.json": "assembled-reading.schema.json",
    "assembled-reading-ai-affordance.example.json": "assembled-reading.schema.json",
    "birth-chart-input.example.json": "birth-chart-input.schema.json",
    "birth-input-calculation-consent.example.json": "consent.schema.json",
    "bleeding-onset.example.json": "observation.schema.json",
    "bleeding-onset-correction.example.json": "observation.schema.json",
    "consent-grant.example.json": "consent.schema.json",
    "development-context-infant.example.json": "observation.schema.json",
    "development-context-preterm-birth.example.json": "observation.schema.json",
    "development-context-preterm-corrected-age.example.json": "observation.schema.json",
    "experience-pathway-synthetic.example.json": "experience-pathway.schema.json",
    "experience-pathway-local-preflight.example.json": "experience-pathway-case.schema.json",
    "environmental-affordance-ai-use.example.json": "observation.schema.json",
    "environmental-affordance-linked-case.example.json": "environmental-affordance-case.schema.json",
    "environmental-affordance-response.example.json": "observation.schema.json",
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
    "endocrine-relations.json": "endocrine-relations-catalog.schema.json",
    "evidence-claims.json": "evidence-catalog.schema.json",
    "human-design-bodygraph-topology.json": "human-design-bodygraph-topology.schema.json",
    "phase-vocabulary.json": "phase-vocabulary.schema.json",
}

CATALOG_ITEM_SCHEMAS = {
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
    return errors


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


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
            for index, relation in enumerate(relations):
                if not isinstance(relation, dict):
                    continue
                for endpoint in ("fromNodeId", "toNodeId"):
                    endpoint_id = relation.get(endpoint)
                    if not isinstance(endpoint_id, str) or endpoint_id not in known_node_ids:
                        errors.append(f"examples/{filename} at relations/{index}/{endpoint}: unresolved pathway node")

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

    if errors:
        print("Metheus contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(schemas)} JSON Schemas, {len(EXAMPLE_SCHEMAS)} mapped examples, and {len(CATALOG_SCHEMAS)} mapped catalogs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
