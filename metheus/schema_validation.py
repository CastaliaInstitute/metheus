"""Runtime validation helpers for Metheus JSON Schema contracts."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from referencing import Registry, Resource


SCHEMA_DIRECTORY = Path(__file__).resolve().parents[1] / "schema"

_SCHEMA_BY_RECORD_TYPE = {
    "birth_chart_input": "birth-chart-input.schema.json",
    "symbolic_map": "symbolic-map.schema.json",
    "observation": "observation.schema.json",
    "event": "observation.schema.json",
    "estimate": "observation.schema.json",
    "symbolic_feature": "observation.schema.json",
    "context": "observation.schema.json",
    "interaction_event": "interaction-event.schema.json",
    "phase_annotation": "phase-annotation.schema.json",
    "rhythm_summary": "rhythm-summary.schema.json",
    "subject_index": "subject-index.schema.json",
}


@lru_cache(maxsize=None)
def _load_schema(schema_name: str, schema_directory: str) -> dict[str, Any]:
    path = Path(schema_directory) / schema_name
    with path.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    return schema


@lru_cache(maxsize=None)
def _schema_registry(schema_directory: str) -> Registry[Any]:
    """Resolve cross-schema references only from the local schema directory."""
    directory = Path(schema_directory)
    registry: Registry[Any] = Registry()
    for path in sorted(directory.glob("*.schema.json")):
        try:
            with path.open(encoding="utf-8") as stream:
                schema = json.load(stream)
        except (OSError, json.JSONDecodeError):
            continue
        schema_id = schema.get("$id") if isinstance(schema, dict) else None
        if isinstance(schema_id, str):
            registry = registry.with_resource(schema_id, Resource.from_contents(schema))
    return registry


def schema_for_record(record: dict[str, Any]) -> str | None:
    """Return the schema filename for a supported Metheus record type."""
    if not isinstance(record, dict):
        return None
    return _SCHEMA_BY_RECORD_TYPE.get(record.get("recordType"))


def validate_schema_instance(
    instance: Any,
    schema_name: str,
    *,
    schema_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Validate one instance and return value-free issue locations.

    Error results intentionally omit rejected instance values to avoid copying
    sensitive data into logs or authorization decisions.
    """
    try:
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError
    except ImportError:
        return {"valid": False, "issues": [{"code": "jsonschema_dependency_unavailable"}]}

    if not isinstance(schema_name, str) or not schema_name.endswith(".schema.json") or "/" in schema_name or "\\" in schema_name:
        return {"valid": False, "issues": [{"code": "invalid_schema_name"}]}

    directory = Path(schema_directory) if schema_directory is not None else SCHEMA_DIRECTORY
    try:
        schema = _load_schema(schema_name, str(directory.resolve()))
    except (OSError, json.JSONDecodeError):
        return {"valid": False, "issues": [{"code": "schema_unavailable"}]}

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError:
        return {"valid": False, "issues": [{"code": "invalid_schema_definition"}]}

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
        registry=_schema_registry(str(directory.resolve())),
    )
    issues = []
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: tuple(map(str, error.absolute_path)),
    )
    for error in errors:
        issues.append({
            "code": "schema_constraint_failed",
            "instancePath": "/".join(str(part) for part in error.absolute_path),
            "schemaPath": "/".join(str(part) for part in error.absolute_schema_path),
            "keyword": str(error.validator),
        })
    return {"valid": not issues, "issues": issues}


def validate_record_schema(record: Any) -> dict[str, Any]:
    """Validate a supported subject record using its declared record type."""
    if not isinstance(record, dict):
        return {"valid": False, "issues": [{"code": "invalid_record_shape"}]}
    schema_name = schema_for_record(record)
    if schema_name is None:
        return {"valid": False, "issues": [{"code": "unsupported_record_type"}]}
    return validate_schema_instance(record, schema_name)
