#!/usr/bin/env python3
"""Create a local, consent-checked summary from one Metheus affordance trial export."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from metheus import summarize_authorized_affordance_trial, validate_record_schema, validate_schema_instance


def _load_records(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    records = value.get("records") if isinstance(value, dict) else value
    if not isinstance(records, list) or not records or any(not isinstance(record, dict) for record in records):
        raise ValueError(f"{path}: expected a non-empty record array or an object containing a records array")
    return records


def _load_grants(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    grants = value.get("grants", value) if isinstance(value, dict) else value
    if isinstance(grants, dict):
        grants = [grants]
    if not isinstance(grants, list) or any(not isinstance(grant, dict) for grant in grants):
        raise ValueError(f"{path}: expected a consent grant object, grant array, or object containing a grants array")
    for index, grant in enumerate(grants):
        result = validate_schema_instance(grant, "consent.schema.json")
        if not result.get("valid"):
            raise ValueError(f"{path}: consent grant {index + 1} does not match consent.schema.json")
    return grants


def _write_private_new_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", required=True, type=Path, help="one PWA JSON export containing records for a single affordance trial")
    parser.add_argument("--grants", required=True, type=Path, help="local consent grant JSON for the exported subject and selected records")
    parser.add_argument("--purpose", required=True, help="authorized analysis purpose, such as personal_reflection or learning_support")
    parser.add_argument("--output", type=Path, help="new private JSON summary file; omitted means write the summary to stdout")
    args = parser.parse_args(argv)

    try:
        records = _load_records(args.records)
        grants = _load_grants(args.grants)
        invalid_records = [
            record.get("id", "<missing id>")
            for record in records
            if not validate_record_schema(record).get("valid")
        ]
        if invalid_records:
            raise ValueError(f"{args.records}: record schema validation failed for {len(invalid_records)} record(s)")

        subject_ids = {record.get("subjectId") for record in records}
        if len(subject_ids) != 1 or not all(isinstance(value, str) and value for value in subject_ids):
            raise ValueError("the export must contain records for exactly one nonempty subjectId")
        subject_id = next(iter(subject_ids))
        trial_ids = {
            record["environmentalAffordance"].get("affordanceId")
            for record in records
            if isinstance(record.get("environmentalAffordance"), dict)
        }
        if len(trial_ids) != 1 or not all(isinstance(value, str) and value for value in trial_ids):
            raise ValueError("the export must contain lifecycle records for exactly one affordanceId")
        affordance_id = next(iter(trial_ids))

        result = summarize_authorized_affordance_trial(
            records,
            grants,
            subject_id=subject_id,
            affordance_id=affordance_id,
            selected_record_ids=[record["id"] for record in records],
            purpose=args.purpose,
        )
        if not result.get("eligible"):
            raise ValueError(f"trial summary was not created: {result.get('reason', 'authorization or input checks failed')}")
        summary = result["summary"]
        validation = validate_schema_instance(summary, "environmental-affordance-trial-summary.schema.json")
        if not validation.get("valid"):
            raise ValueError("generated trial summary does not match its schema")
        serialized = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            _write_private_new_file(args.output, serialized)
            print(f"Created a private local trial summary at {args.output}; no records were uploaded.", file=sys.stderr)
        else:
            sys.stdout.write(serialized)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
