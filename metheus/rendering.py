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


def _render_measurement_summary(source: dict[str, Any]) -> str:
    """Render a bucketed numeric summary as descriptive, source-linked context."""
    summary = source.get("derivedSummary")
    if not isinstance(summary, dict) or summary.get("summaryMeasure") != "measurement_series":
        return ""
    signature = summary.get("measurementSeries")
    if not isinstance(signature, dict):
        return ""
    unit = signature.get("unit", "")
    analyte = signature.get("analyteOrSignal", "numeric signal")
    window = summary.get("window", {})
    window_label = " – ".join(
        _text(window.get(key)) for key in ("startDate", "endDate")
        if isinstance(window, dict) and window.get(key) is not None
    )
    detail_fields = (
        ("epistemicClass", "record class"), ("sourceKind", "source type"),
        ("sourceName", "source"), ("sourceMethod", "source method"),
        ("sourceVersion", "source version"), ("methodDetails", "method details"),
        ("specimen", "specimen"), ("sensorLocation", "sensor location"),
        ("deviceOrAssay", "device/assay"), ("deviceModel", "device model"),
        ("algorithmVersion", "algorithm version"), ("collectionConditions", "collection conditions"),
    )
    signature_text = " · ".join(
        f"{label}: {_text(signature.get(field))}"
        for field, label in detail_fields
        if signature.get(field) not in (None, "", "unspecified")
    )
    bucket_rows = []
    buckets = summary.get("timeBuckets", [])
    if isinstance(buckets, list):
        for bucket in buckets:
            if not isinstance(bucket, dict):
                continue
            bucket_window = " – ".join(
                _text(bucket.get(key)) for key in ("startDate", "endDate")
                if bucket.get(key) is not None
            )
            count = bucket.get("nMeasurements", 0)
            n_dates = bucket.get("nDistinctMeasurementDates", 0)
            days = bucket.get("inclusiveDays", 0)
            if count:
                median_value = bucket.get("medianValue")
                mad = bucket.get("medianAbsoluteDeviationValue")
                metrics = (
                    f"median {_text(median_value)} {_text(unit)}; "
                    f"median absolute deviation {_text(mad)} {_text(unit)}"
                )
                coverage = f"{_text(n_dates)} of {_text(days)} dates with records"
            else:
                metrics = "no eligible measurements recorded"
                coverage = f"0 of {_text(days)} dates with records"
            ids = bucket.get("inputRecordIds", [])
            id_list = _list(ids, "compact-list")
            bucket_rows.append(
                '<li class="measurement-bucket">'
                f'<strong>{bucket_window}</strong>: {_text(count)} measurements; {metrics}; {coverage}'
                f'{("<details><summary>Bucket source records</summary>" + id_list + "</details>") if id_list else ""}'
                "</li>"
            )
    overall = (
        f'<p class="detail">{_text(summary.get("nMeasurements"))} measurements across '
        f'{_text(summary.get("nDistinctMeasurementDates"))} dates; overall median '
        f'{_text(summary.get("medianNumericValue"))} {_text(unit)}; median absolute deviation '
        f'{_text(summary.get("medianAbsoluteDeviationValue"))} {_text(unit)}; '
        f'range {_text(summary.get("minimumValue"))}–{_text(summary.get("maximumValue"))} {_text(unit)}.</p>'
    )
    buckets_html = f'<ul class="measurement-buckets">{"".join(bucket_rows)}</ul>' if bucket_rows else ""
    bucket_days = summary.get("bucketDays")
    return (
        '<section class="derived-measurement-summary">'
        f'<h4>Descriptive measurement summary: {_text(analyte)}</h4>'
        f'<p class="detail">Window: {window_label} · method {_text(summary.get("methodVersion"))} · fixed {_text(bucket_days)}-day buckets anchored at the window start.</p>'
        f'<p class="detail">Source signature: {_text(signature_text)}</p>'
        f'{overall}{buckets_html}'
        '<p class="detail">These are summaries of logged measurements. They do not establish a trend, '
        'biological phase, hormone state, clinical range, or cause.</p>'
        f'{_list(summary.get("limitations"), "compact-list")}'
        '</section>'
    )


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

        measurement_summaries = [
            _render_measurement_summary(source)
            for source in claim["sources"]
            if isinstance(source, dict) and source.get("recordType") == "rhythm_summary"
        ]
        measurement_summaries = [item for item in measurement_summaries if item]
        if measurement_summaries:
            provenance.append("".join(measurement_summaries))

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

    reflection_options: list[str] = []
    for option in package.get("reflectionOptions", []):
        affordance = option.get("environmentalAffordance", {})
        details: list[str] = []
        if affordance:
            details.append(
                '<p class="detail">Support type: '
                f'{_text(affordance.get("deliveryMode", "")).replace("_", " ")} · '
                f'Intended function: {_text(affordance.get("intendedFunction", "")).replace("_", " ")} · '
                f'Role frame: {_text(affordance.get("roleFrame", "")).replace("_", " ")}</p>'
            )
            if affordance.get("userDefinedDescription"):
                details.append(f'<p class="detail">Description: {_text(affordance["userDefinedDescription"])}</p>')
            if affordance.get("trialWindow"):
                details.append(f'<p class="detail">User-chosen review point: {_text(affordance["trialWindow"])}</p>')
            safeguards = affordance.get("aiSafeguards", {})
            if safeguards:
                safeguard_names = []
                if safeguards.get("identityTransparent") is True:
                    safeguard_names.append("AI identity transparency")
                if safeguards.get("privacyBoundariesDisclosed") is True:
                    safeguard_names.append("privacy-boundary disclosure")
                if safeguards.get("notHumanRelationshipSubstitute") is True:
                    safeguard_names.append("not a human-relationship substitute")
                if safeguard_names:
                    details.append(
                        '<p class="detail">Proposed safeguard requirements: '
                        f'{_text("; ".join(safeguard_names))}. These are design requirements, not verification of a service.</p>'
                    )
        source_ids = option.get("sourceIds", [])
        source_section = ""
        if source_ids:
            source_items = "".join(f"<li><code>{_text(source_id)}</code></li>" for source_id in source_ids)
            source_section = f'<details><summary>Selected basis</summary><ul>{source_items}</ul></details>'
        reflection_options.append(
            '<article class="claim reflection-option">'
            f'<p class="claim-kind">{_text(option["kind"]).replace("_", " ")} · status: {_text(option["subjectStatus"]).replace("_", " ")}</p>'
            f'<p class="claim-text">{_text(option["text"])}</p>'
            f'{"".join(details)}'
            f'{_list(option.get("limitations"), "compact-list")}'
            f'{source_section}'
            '</article>'
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
    .reflection-option {{ border-style: dashed; }}
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
    .measurement-buckets {{ margin-block: .5rem; font-size: .92rem; }}
    .measurement-bucket {{ margin-block: .35rem; }}
    .derived-measurement-summary {{ margin-top: .8rem; border-left: 2px solid color-mix(in srgb, CanvasText 24%, transparent); padding-left: .8rem; }}
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
    {("<section aria-label=\"Optional reflection options\"><h2>Optional ideas to consider</h2><p class=\"detail\">These are invitations, not recommendations. You can decline or revise them.</p>" + "".join(reflection_options) + "</section>") if reflection_options else ""}
    {("<section><h2>Reading limitations</h2>" + limitations + "</section>") if limitations else ""}
    <p class="notice">This page presents supplied claim text and provenance. It does not generate or verify the claims, diagnose, or provide medical advice.</p>
  </main>
</body>
</html>
"""
