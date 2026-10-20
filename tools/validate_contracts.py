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
SCHEMA_DIR = ROOT / "schema"
EXAMPLE_DIR = ROOT / "examples"
CATALOG_DIR = ROOT / "catalog"

EXAMPLE_SCHEMAS = {
    "birth-chart-input.example.json": "birth-chart-input.schema.json",
    "birth-input-calculation-consent.example.json": "consent.schema.json",
    "bleeding-onset.example.json": "observation.schema.json",
    "consent-grant.example.json": "consent.schema.json",
    "learner-feedback.example.json": "observation.schema.json",
    "learning-activity.example.json": "observation.schema.json",
    "learning-reading.example.json": "reading.schema.json",
    "phase-aware-reading.example.json": "reading.schema.json",
    "phase-bleeding-observation.example.json": "observation.schema.json",
    "phase-chart-feature.example.json": "observation.schema.json",
    "phase-epimethean.example.json": "phase-annotation.schema.json",
    "phase-promethean.example.json": "phase-annotation.schema.json",
    "promethean-feature.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-18.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-19.example.json": "observation.schema.json",
    "rhythm-sleep-2026-10-20.example.json": "observation.schema.json",
    "rhythm-sleep-summary.example.json": "rhythm-summary.schema.json",
    "rhythm-subject-index.example.json": "subject-index.schema.json",
    "rhythm-summary-consent.example.json": "consent.schema.json",
    "rhythm-summary-reading.example.json": "reading.schema.json",
    "subject-index.example.json": "subject-index.schema.json",
    "symbolic-map-reading.example.json": "reading.schema.json",
    "symbolic-map-reflection-consent.example.json": "consent.schema.json",
    "symbolic-map.example.json": "symbolic-map.schema.json",
}

CATALOG_SCHEMAS = {
    "phase-vocabulary.json": "phase-vocabulary.schema.json",
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

    if errors:
        print("Metheus contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(schemas)} JSON Schemas, {len(EXAMPLE_SCHEMAS)} mapped examples, and {len(CATALOG_SCHEMAS)} mapped catalogs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
