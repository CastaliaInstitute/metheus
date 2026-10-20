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

    if errors:
        print("Metheus contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(schemas)} JSON Schemas and {len(EXAMPLE_SCHEMAS)} mapped examples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
