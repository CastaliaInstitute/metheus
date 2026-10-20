"""Deterministic, escaped HTML presentation for assembled Metheus readings.

This renderer presents supplied claims and provenance. It does not generate,
rewrite, summarize, or verify claim text, and it does not persist the result.
"""

from __future__ import annotations

from html import escape
from typing import Any

from .schema_validation import validate_schema_instance


def _text(value: Any) -> str:
    """Escape a scalar value for HTML text or quoted attribute context."""
    if isinstance(value, (str, int, float)) and not isinstance(value, bool):
        return escape(str(value), quote=True)
    return ""


def _list(items: Any, class_name: str) -> str:
    if not isinstance(items, list) or not items:
        return ""
    rendered = "".join(
        f"<li>{_text(item)}</li>"
        for item in items
        if isinstance(item, (str, int, float)) and not isinstance(item, bool)
    )
    class_attribute = f' class="{_text(class_name)}"' if class_name else ""
    return f"<ul{class_attribute}>{rendered}</ul>" if rendered else ""


def render_assembled_reading_html(package: dict[str, Any]) -> str:
    """Render a schema-valid assembled package as a self-contained HTML page.

    All supplied text is escaped and citations are displayed as text rather
    than active links. The caller must pass the direct result of a successful
    assembly/preflight: schema validation here does not authenticate the
    package or re-check consent and cross-object provenance. Source records
    are not reinterpreted or included wholesale.
    """
    validation = validate_schema_instance(package, "assembled-reading.schema.json")
    if not validation["valid"]:
        raise ValueError("package does not satisfy the assembled-reading schema")

    window = package["timeWindow"]
    date_range = f'{_text(window["start"])} – {_text(window["end"])}'
    claims: list[str] = []
    for claim in package["claims"]:
        support = claim["support"]
        provenance: list[str] = []

        source_ids = claim["sourceIds"]
        if source_ids:
            items = "".join(f"<li><code>{_text(source_id)}</code></li>" for source_id in source_ids)
            provenance.append(f'<section><h4>Selected records</h4><ul>{items}</ul></section>')

        phase_items = []
        for phase in claim["phaseAnnotations"]:
            phase_label = phase.get("evocativeName") or phase.get("canonicalPhase")
            window = phase.get("window", {})
            window_values = [window.get("start")]
            if window.get("end") is not None:
                window_values.append(window["end"])
            window_text = " – ".join(_text(value) for value in window_values if value is not None)
            if window.get("timeZone"):
                window_text += f' · {_text(window["timeZone"])}'
            source_system = phase.get("sourceSystem", {})
            source_parts = [source_system.get(key) for key in ("name", "lineage", "version")]
            source_text = " · ".join(_text(value) for value in source_parts if value)
            phase_metadata = [
                phase.get("canonicalPhase"), phase.get("layer"),
                phase.get("phaseSystem"), phase.get("basis"),
            ]
            phase_details = ""
            if phase.get("description"):
                phase_details += f'<p class="detail">{_text(phase["description"])}</p>'
            if window_text:
                phase_details += f'<p class="detail">Window: {window_text}</p>'
            if phase.get("method"):
                phase_details += f'<p class="detail">Basis method: {_text(phase["method"])}</p>'
            if phase.get("uncertainty"):
                phase_details += f'<p class="detail">Uncertainty: {_text(phase["uncertainty"])}</p>'
            if source_text:
                phase_details += f'<p class="detail">Symbolic source: {source_text}</p>'
            phase_items.append(
                '<li class="phase-context">'
                f'<strong>{_text(phase_label)}</strong>'
                f'<p class="detail">{" · ".join(_text(value) for value in phase_metadata if value)}</p>'
                f'{phase_details}'
                f'{_list(phase.get("limitations"), "compact-list")}'
                "</li>"
            )
        if phase_items:
            provenance.append(f'<section><h4>Phase context</h4><ul>{"".join(phase_items)}</ul></section>')

        reference_items = []
        for reference in claim["references"]:
            citations = []
            for citation in reference.get("sourceCitations", []):
                if not isinstance(citation, dict):
                    continue
                title = _text(citation.get("title"))
                url = _text(citation.get("url"))
                locator = _text(citation.get("locator"))
                citation_text = " · ".join(part for part in (title, url, locator) if part)
                if citation_text:
                    citations.append(f"<li>{citation_text}</li>")
            reference_items.append(
                "<li>"
                f'<strong>{_text(reference.get("kind"))}</strong>: '
                f'{_text(reference.get("claimText"))}'
                f'{_list(reference.get("limitations"), "compact-list")}'
                f'{("<ul>" + "".join(citations) + "</ul>") if citations else ""}'
                "</li>"
            )
        if reference_items:
            provenance.append(f'<section><h4>General references</h4><ul>{"".join(reference_items)}</ul></section>')

        rationale = support.get("rationale")
        alternatives = _list(support.get("alternatives"), "compact-list")
        support_summary = (
            f'<p class="support">Support: {_text(support.get("confidence"))} confidence '
            f'· {_text(support.get("coverage"))} coverage</p>'
        )
        if rationale:
            support_summary += f'<p class="detail">{_text(rationale)}</p>'
        if alternatives:
            support_summary += f'<div class="detail"><h4>Other possibilities</h4>{alternatives}</div>'

        details = "".join(provenance)
        claims.append(
            '<article class="claim">'
            f'<p class="claim-kind">{_text(claim["claimType"]).replace("_", " ")}</p>'
            f'<p class="claim-text">{_text(claim["text"])}</p>'
            f'{support_summary}'
            f'{("<details><summary>Sources and context</summary>" + details + "</details>") if details else ""}'
            "</article>"
        )

    limitations = _list(package["limitations"], "")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Metheus reading</title>
  <style>
    :root {{ color-scheme: light dark; font: 16px/1.65 system-ui, sans-serif; }}
    body {{ margin: 0; padding: 2rem 1rem; background: Canvas; color: CanvasText; }}
    main {{ max-width: 48rem; margin: auto; }}
    .eyebrow, .claim-kind {{ color: #80694f; font-size: .72rem; font-weight: 650; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ max-width: 42rem; font: 400 clamp(2rem, 7vw, 3.5rem)/1.08 Georgia, serif; }}
    .window, .support, .detail {{ color: GrayText; font-size: .9rem; }}
    .claim {{ margin-block: 1.2rem; border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .65rem; padding: 1.25rem; }}
    .claim-kind {{ margin: 0; }}
    .claim-text {{ margin-block: .6rem; font-size: 1.1rem; }}
    .support {{ margin-bottom: 0; }}
    details {{ margin-top: 1rem; border-top: 1px solid color-mix(in srgb, CanvasText 18%, transparent); padding-top: .8rem; }}
    summary {{ cursor: pointer; font-size: .9rem; }}
    section {{ margin-top: .8rem; }}
    h2 {{ margin-top: 2rem; font: 400 1.6rem Georgia, serif; }}
    h4 {{ margin: .6rem 0 .2rem; font-size: .85rem; }}
    ul {{ padding-left: 1.25rem; }}
    .compact-list {{ margin-block: .2rem; font-size: .88rem; }}
    code {{ overflow-wrap: anywhere; }}
    .notice {{ margin-top: 2rem; border-left: 3px solid #a48761; padding: .3rem 0 .3rem 1rem; color: GrayText; font-size: .88rem; }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Metheus · reflective reading</p>
    <h1>{_text(package["question"])}</h1>
    <p class="window">Selected time window: {date_range}</p>
    <section aria-label="Reading claims">{"".join(claims)}</section>
    {("<section><h2>Reading limitations</h2>" + limitations + "</section>") if limitations else ""}
    <p class="notice">This page presents supplied claim text and provenance. It does not generate or verify the claims, diagnose, or provide medical advice.</p>
  </main>
</body>
</html>
"""
