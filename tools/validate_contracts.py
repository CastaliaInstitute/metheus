#!/usr/bin/env python3
"""Validate Metheus JSON Schemas and their explicitly paired examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metheus.phase_domains import phase_authorization_domain

SCHEMA_DIR = ROOT / "schema"
EXAMPLE_DIR = ROOT / "examples"
CATALOG_DIR = ROOT / "catalog"

EXAMPLE_SCHEMAS = {
    "assembled-reading.example.json": "assembled-reading.schema.json",
    "assembled-reading-circadian.example.json": "assembled-reading.schema.json",
    "birth-chart-input.example.json": "birth-chart-input.schema.json",
    "birth-input-calculation-consent.example.json": "consent.schema.json",
    "bleeding-onset.example.json": "observation.schema.json",
    "bleeding-onset-correction.example.json": "observation.schema.json",
    "consent-grant.example.json": "consent.schema.json",
    "development-context-infant.example.json": "observation.schema.json",
    "experience-pathway-synthetic.example.json": "experience-pathway.schema.json",
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
    "phase-vocabulary.json": "phase-vocabulary.schema.json",
}

CATALOG_ITEM_SCHEMAS = {
    "endocrine-relations.json": ("relations", "endocrine-relation.schema.json"),
    "evidence-claims.json": ("claims", "evidence-claim.schema.json"),
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


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
        validator = Draft202012Validator(schema, format_checker=format_checker)
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
        validator = Draft202012Validator(schema, format_checker=format_checker)
        for error in sorted(validator.iter_errors(catalog), key=lambda item: tuple(map(str, item.absolute_path))):
            location = "/".join(str(part) for part in error.absolute_path) or "$"
            errors.append(f"catalog/{filename} at {location}: {error.message}")
        item_schema_mapping = CATALOG_ITEM_SCHEMAS.get(filename)
        if item_schema_mapping is not None and isinstance(catalog, dict):
            collection_key, item_schema_filename = item_schema_mapping
            item_schema = schemas.get(item_schema_filename)
            items = catalog.get(collection_key)
            if item_schema is not None and isinstance(items, list):
                item_validator = Draft202012Validator(item_schema, format_checker=format_checker)
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
