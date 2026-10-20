"""Render a schema-valid assembled reading JSON package as static HTML."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from metheus.rendering import render_assembled_reading_html


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="assembled-reading JSON package")
    parser.add_argument("destination", type=Path, help="HTML output path")
    args = parser.parse_args(argv)

    try:
        package = json.loads(args.source.read_text(encoding="utf-8"))
        rendered = render_assembled_reading_html(package)
        args.destination.parent.mkdir(parents=True, exist_ok=True)
        args.destination.write_text(rendered, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Rendered {args.source} -> {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
