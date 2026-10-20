"""Build a local reported-cycle-day view from explicitly selected, consented records."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from metheus import describe_authorized_reported_cycle_day_view, validate_schema_instance


def _load_list(path: Path, key: str) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    items = value.get(key) if isinstance(value, dict) else value
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f"{path}: expected a JSON array or an object with a '{key}' array")
    return items


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
    parser.add_argument("--records", required=True, type=Path, help="local JSON array of records, or object containing a records array")
    parser.add_argument("--grants", required=True, type=Path, help="local JSON array of consent grants, or object containing a grants array")
    parser.add_argument("--subject-id", required=True, help="pseudonymous subject ID shared by the selected records and grants")
    parser.add_argument("--marker-id", action="append", required=True, help="explicit self-reported cycle-day-one record ID; repeat for each selected marker")
    parser.add_argument("--observation-id", action="append", required=True, help="explicit observation/event record ID to include; repeat for each selected record")
    parser.add_argument("--output", type=Path, help="new private JSON file for the view; omitted means write JSON to stdout")
    args = parser.parse_args(argv)

    try:
        records = _load_list(args.records, "records")
        grants = _load_list(args.grants, "grants")
        invalid_grants = [
            index for index, grant in enumerate(grants)
            if not validate_schema_instance(grant, "consent.schema.json").get("valid")
        ]
        if invalid_grants:
            raise ValueError(f"{args.grants}: consent grant schema validation failed for {len(invalid_grants)} entr{'y' if len(invalid_grants) == 1 else 'ies'}")
        result = describe_authorized_reported_cycle_day_view(
            records,
            grants,
            subject_id=args.subject_id,
            cycle_day_one_record_ids=args.marker_id,
            observation_record_ids=args.observation_id,
        )
        if not result.get("eligible"):
            raise ValueError(f"cycle-day view was not created: {result.get('reason', 'authorization or input checks failed')}")
        serialized = json.dumps(result["view"], ensure_ascii=False, indent=2) + "\n"
        if args.output:
            _write_private_new_file(args.output, serialized)
            print(f"Created a private reported-cycle-day view at {args.output}; no records were uploaded.", file=sys.stderr)
        else:
            sys.stdout.write(serialized)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
