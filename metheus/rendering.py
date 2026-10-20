"""Deterministic, escaped HTML presentation for assembled Metheus readings.

This renderer presents supplied claims and provenance. It does not generate,
rewrite, summarize, or verify claim text, and it does not persist the result.
"""

from __future__ import annotations

from html import escape
import json
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


def render_affordance_trial_summary_html(summary: dict[str, Any]) -> str:
    """Present a validated, ephemeral affordance-trial summary with provenance."""
    validation = validate_schema_instance(summary, "environmental-affordance-trial-summary.schema.json")
    if not validation["valid"]:
        raise ValueError("summary does not satisfy the environmental-affordance trial-summary schema")

    lifecycle_items = []
    for event in summary["lifecycleEvents"]:
        when = json.dumps(event["time"], ensure_ascii=False, sort_keys=True) if event["time"] is not None else "time not recorded"
        lifecycle_items.append(
            f'<li><strong>{_text(event["lifecycleEvent"])}</strong> · {_text(event["recordId"])}'
            f'<p class="detail">Recorded time: {_text(when)} · source: {_text(event["sourceKind"])}'
            f' · record class: {_text(event["epistemicClass"])}</p></li>'
        )

    report_items = []
    for report in summary["experienceReports"]:
        when = json.dumps(report["time"], ensure_ascii=False, sort_keys=True) if report["time"] is not None else "time not recorded"
        value = json.dumps(report["value"], ensure_ascii=False, sort_keys=True) if isinstance(report.get("value"), dict) else "not included"
        report_items.append(
            f'<li><strong>{_text(report["label"] or report["eventType"] or report["recordType"])}</strong>'
            f'<p class="detail">Record: {_text(report["recordId"])} · domain: {_text(report["domain"])}'
            f' · source: {_text(report["sourceKind"])} · record class: {_text(report["epistemicClass"])}</p>'
            f'<p class="detail">Recorded time: {_text(when)} · recorded value: {_text(value)}</p></li>'
        )

    temporal_items = []
    for relation in [*summary["lifecycleTemporalRelations"], *summary["eventReportTemporalRelations"]]:
        gap = relation["elapsedGap"]
        gap_text = f' · recorded gap: {_text(gap)} {_text(relation["elapsedGapUnit"])}' if gap is not None else ""
        temporal_items.append(
            f'<li><code>{_text(relation["leftRecordId"])}</code> → <code>{_text(relation["rightRecordId"])}</code>: '
            f'{_text(relation["temporalRelation"])}{gap_text} '
            f'(basis: {_text(relation["gapBasis"])})</li>'
        )

    source_ids = _list(summary["inputRecordIds"], "compact-list")
    limitations = _list(summary["limitations"], "compact-list")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Metheus support-trial summary</title>
  <style>
    :root {{ color-scheme: light dark; font: 16px/1.6 system-ui, sans-serif; }}
    body {{ margin: 0; padding: 2rem 1rem; background: Canvas; color: CanvasText; }}
    main {{ max-width: 48rem; margin: auto; }}
    .eyebrow,.detail {{ color: GrayText; font-size: .9rem; }}
    section {{ margin-top: 1.5rem; }}
    h2 {{ font: 400 1.35rem Georgia, serif; }}
    li {{ margin-block: .65rem; }}
    ul {{ padding-left: 1.3rem; }}
    code {{ overflow-wrap: anywhere; }}
    .notice {{ margin-top: 2rem; border-left: 3px solid #a48761; padding-left: 1rem; color: GrayText; }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Metheus · ephemeral support-trial summary · {_text(summary["methodVersion"])}</p>
    <h1>What was offered, chosen, or used</h1>
    <p>Support: {_text(summary["deliveryMode"])} · intended function: {_text(summary["intendedFunction"])} · role: {_text(summary["roleFrame"])}</p>
    <section><h2>Lifecycle records</h2><ul>{"".join(lifecycle_items)}</ul></section>
    <section><h2>Separate experience reports</h2>{"<ul>" + "".join(report_items) + "</ul>" if report_items else "<p>No experience reports were selected.</p>"}</section>
    <section><h2>Recorded timing comparisons</h2>{"<ul>" + "".join(temporal_items) + "</ul>" if temporal_items else "<p>No pairwise timing comparisons were available.</p>"}<p class="detail">These relations describe recorded time windows and their precision. They do not establish an effect, benefit, harm, or cause.</p></section>
    <section><h2>Selected source records</h2>{source_ids}</section>
    <section><h2>Limits</h2>{limitations}</section>
    <p class="notice">This is an in-memory description of selected records, not a stored observation or effectiveness assessment.</p>
  </main>
</body>
</html>
"""


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
    def uncertainty_text(metadata: Any) -> str:
        if not isinstance(metadata, dict) or not isinstance(metadata.get("levelCounts"), dict):
            return "recorded uncertainty labels unavailable"
        counts = metadata["levelCounts"]
        labels = ", ".join(
            f'{label.replace("_", " ")} {_text(counts.get(label, 0))}'
            for label in ("low", "moderate", "high", "unknown", "not_reported")
        )
        return f'recorded uncertainty labels: {labels}; uncertainty object on {_text(metadata.get("recordsWithUncertaintyObject", 0))} records'
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
                f'<strong>{bucket_window}</strong>: {_text(count)} measurements; {metrics}; {coverage}; {uncertainty_text(bucket.get("uncertaintyMetadata"))}'
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
    overall += f'<p class="detail">{uncertainty_text(summary.get("uncertaintyMetadata"))}.</p>'
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


def _render_summary_sources(source: dict[str, Any]) -> str:
    """Expose method, window, limitations, and inputs for a derived summary."""
    summary = source.get("derivedSummary")
    if not isinstance(summary, dict):
        return ""
    details = []
    if summary.get("methodVersion"):
        details.append(f'<p class="detail">Summary method: {_text(summary["methodVersion"])}</p>')
    window = summary.get("window")
    if isinstance(window, dict):
        window_parts = [
            _text(window[key]) for key in ("startDate", "endDate", "start", "end")
            if window.get(key) is not None
        ]
        if window_parts:
            details.append(f'<p class="detail">Summary window: {" – ".join(window_parts)}</p>')
    input_ids = summary.get("inputRecordIds")
    source_list = ""
    if isinstance(input_ids, list) and input_ids:
        items = _list(input_ids, "compact-list")
        if items:
            source_list = f'<h4>Summary source records</h4>{items}'
    limitations = _list(summary.get("limitations"), "compact-list")
    limitations_section = f'<h4>Summary limits</h4>{limitations}' if limitations else ""
    if not details and not source_list and not limitations_section:
        return ""
    return (
        '<section class="derived-summary-sources">'
        f'{"".join(details)}{source_list}{limitations_section}'
        '</section>'
    )


def _render_symbolic_map_source(source: dict[str, Any]) -> str:
    """Render non-identifying chart provenance without treating it as biology."""
    if source.get("recordType") != "symbolic_map":
        return ""
    calculation = source.get("calculation")
    if not isinstance(calculation, dict):
        return ""
    bodygraph = calculation.get("bodygraph")
    bodygraph = bodygraph if isinstance(bodygraph, dict) else {}
    scope = bodygraph.get("chartScope", "unspecified")
    if scope == "natal":
        scope_label = "Natal symbolic map"
    elif scope == "transit":
        scope_label = "Dated symbolic transit map"
    else:
        scope_label = "Symbolic map"
    details = [
        f'<p class="detail">Map status: {_text(calculation.get("status", "unspecified"))} · scope: {_text(scope_label)}</p>'
    ]
    if bodygraph.get("validAt"):
        details.append(f'<p class="detail">Transit valid at: {_text(bodygraph["validAt"])}</p>')
    gate_numbers = bodygraph.get("activatedGateNumbers")
    if isinstance(gate_numbers, list):
        gate_text = ", ".join(_text(number) for number in sorted(
            (number for number in gate_numbers if isinstance(number, int) and not isinstance(number, bool))
        )) or "none listed"
        details.append(f'<p class="detail">Gate numbers in this map: {gate_text}</p>')
    system = source.get("sourceSystem")
    if isinstance(system, dict):
        lineage = " · ".join(
            _text(system[field]) for field in ("name", "lineage", "version")
            if system.get(field)
        )
        if lineage:
            details.append(f'<p class="detail">Symbolic source: {lineage}</p>')
    method = calculation.get("method")
    if method:
        details.append(f'<p class="detail">Calculation method: {_text(method)} · version {_text(calculation.get("methodVersion", "unspecified"))}</p>')
    engine = calculation.get("engine")
    if isinstance(engine, dict):
        details.append(f'<p class="detail">Engine: {_text(engine.get("name", "unspecified"))} · {_text(engine.get("version", "unspecified"))}</p>')
    precision = calculation.get("inputPrecision")
    if isinstance(precision, dict):
        details.append(
            f'<p class="detail">Input precision: birth date {_text(precision.get("birthDate", "unspecified"))} · '
            f'birth time {_text(precision.get("birthTime", "unspecified"))}</p>'
        )
    if calculation.get("verificationStatus"):
        details.append(f'<p class="detail">Verification status: {_text(calculation["verificationStatus"])}</p>')
    if calculation.get("calculatedAt"):
        details.append(f'<p class="detail">Calculated at: {_text(calculation["calculatedAt"])}</p>')
    details.append('<p class="detail">This is symbolic chart context, not a measurement or explanation of physiology, feelings, or behavior.</p>')
    limits = _list(calculation.get("limitations"), "compact-list")
    if limits:
        details.append(f'<h5>Map limitations</h5>{limits}')
    return '<section class="symbolic-map-source"><h4>Promethean chart context</h4>' + "".join(details) + '</section>'


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
    claim_type_explanations = {
        "observation": "A description grounded in the selected records; it reports what was recorded.",
        "estimate": "A value or phase calculated from stated inputs and a method; it can be uncertain.",
        "symbolic_prompt": "A reflection prompt from a symbolic system, not a measured fact or biological explanation.",
        "interpretive_question": "An open question to help you decide what meaning, if any, fits.",
        "hypothesis": "A possible relationship to explore, not a conclusion or proof of cause.",
        "boundary": "A limit on what the selected evidence or model can support.",
    }
    present_claim_types = list(dict.fromkeys(claim.get("claimType") for claim in package["claims"]))
    claim_legend = ""
    if present_claim_types:
        legend_items = "".join(
            f'<li><strong>{_text(claim_type.replace("_", " "))}:</strong> '
            f'{_text(claim_type_explanations[claim_type])}</li>'
            for claim_type in present_claim_types
        )
        claim_legend = (
            '<section class="claim-legend" aria-label="How to read these labels">'
            '<h2>How to read these labels</h2>'
            f'<ul class="compact-list">{legend_items}</ul>'
            '<p class="detail">Source records and symbolic references are listed separately under each claim. '
            'Support describes the assembly author\'s stated confidence and coverage; it is not a clinical rating.</p>'
            '</section>'
        )
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

        summary_source_lists = [
            _render_summary_sources(source)
            for source in claim["sources"]
            if isinstance(source, dict) and source.get("recordType") == "rhythm_summary"
        ]
        summary_source_lists = [item for item in summary_source_lists if item]
        if summary_source_lists:
            provenance.extend(summary_source_lists)

        symbolic_map_details = [
            _render_symbolic_map_source(source)
            for source in claim["sources"]
            if isinstance(source, dict) and source.get("recordType") == "symbolic_map"
        ]
        symbolic_map_details = [item for item in symbolic_map_details if item]
        if symbolic_map_details:
            provenance.extend(symbolic_map_details)

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
            layer = phase.get("layer")
            layer_label = {
                "promethean": "Promethean symbolic context",
                "epimethean": "Epimethean lived context",
            }.get(layer, layer)
            phase_metadata = [
                value for value in (
                    layer_label,
                    phase.get("phaseSystem", "").replace("_", " "),
                    phase.get("canonicalPhase", "").replace("_", " "),
                    phase.get("basis", "").replace("_", " "),
                    phase.get("interpretation", "").replace("_", " "),
                ) if value
            ]
            phase_details = ""
            name_source = {
                "metheus_suggestion": "Suggested name: Metheus",
                "user_authored": "Name authored by the person",
            }.get(phase.get("nameSource"))
            if phase.get("evocativeName") and name_source:
                phase_details += f'<p class="detail">{_text(name_source)}</p>'
            elif phase.get("evocativeName") and phase.get("nameSource") == "source_attributed":
                name_attribution = source_text or "named source"
                phase_details += f'<p class="detail">Evocative name attributed to: {_text(name_attribution)}</p>'
                if source_system.get("citation"):
                    phase_details += f'<p class="detail">Evocative name citation: {_text(source_system["citation"])}</p>'
            if phase.get("description"):
                phase_details += f'<p class="detail">{_text(phase["description"])}</p>'
            if window_text:
                phase_details += f'<p class="detail">Window: {window_text}</p>'
            if phase.get("method"):
                phase_details += f'<p class="detail">Basis method: {_text(phase["method"])}</p>'
            if phase.get("uncertainty"):
                phase_details += f'<p class="detail">Uncertainty: {_text(phase["uncertainty"])}</p>'
            if source_text:
                source_label = "Symbolic source" if layer == "promethean" else "Source system"
                phase_details += f'<p class="detail">{source_label}: {source_text}</p>'
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
            if reference.get("kind") == "correspondence":
                feature = reference.get("sourceFeature", {})
                concept = reference.get("targetConcept", {})
                system = reference.get("sourceSystem", {})
                feature_label = feature.get("label") or feature.get("id")
                concept_label = concept.get("label") or concept.get("id")
                source_label = " · ".join(
                    _text(system.get(field)) for field in ("name", "lineage", "version")
                    if system.get(field)
                )
                attribution = "Source-attributed symbolic correspondence"
                if feature_label or concept_label:
                    attribution += f": {_text(feature_label)} → {_text(concept_label)}"
                if source_label:
                    attribution += f" · source: {source_label}"
                if reference.get("evidenceStatus") == "not_evaluated":
                    attribution += " · not evaluated as a biological association"
                attribution = f'<p class="detail correspondence-attribution">{attribution}</p>'
            else:
                attribution = ""
            reference_items.append(
                "<li>"
                f'{attribution}<strong>{_text(reference.get("kind"))}</strong>: '
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
    provenance_audit_html = ""
    if isinstance(package.get("assembly", {}).get("provenanceAudit"), dict):
        audit_claims = package.get("claims", [])
        total = len(audit_claims)
        linked = sum(
            bool(claim.get("sources") or claim.get("phaseAnnotations") or claim.get("references"))
            for claim in audit_claims if isinstance(claim, dict)
        )
        record_linked = sum(bool(claim.get("sources")) for claim in audit_claims if isinstance(claim, dict))
        phase_linked = sum(bool(claim.get("phaseAnnotations")) for claim in audit_claims if isinstance(claim, dict))
        reference_linked = sum(bool(claim.get("references")) for claim in audit_claims if isinstance(claim, dict))
        provenance_audit_html = (
            '<section class="provenance-audit"><h2>Source-link check</h2>'
            f'<p>{_text(linked)} of {_text(total)} claims have at least one linked record, phase, or reference.</p>'
            f'<p class="detail">Linked claims: {_text(record_linked)} with records, {_text(phase_linked)} with phase annotations, {_text(reference_linked)} with general references.</p>'
            '<p class="detail">This counts links present in this package. It does not independently resolve source records or check whether a source supports the wording of a claim.</p>'
            '</section>'
        )
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
    .correspondence-attribution {{ border-left: 2px solid #9a5eac; padding-left: .55rem; }}
    .provenance-audit {{ border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .65rem; padding: .75rem 1rem; }}
    code {{ overflow-wrap: anywhere; }}
    .notice {{ margin-top: 2rem; border-left: 3px solid #a48761; padding: .3rem 0 .3rem 1rem; color: GrayText; font-size: .88rem; }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Metheus · reflective reading</p>
    <h1>{_text(package["question"])}</h1>
    <p class="window">Selected time window: {date_range}</p>
    {claim_legend}
    <section aria-label="Reading claims">{"".join(claims)}</section>
    {provenance_audit_html}
    {("<section aria-label=\"Optional reflection options\"><h2>Optional ideas to consider</h2><p class=\"detail\">These are invitations, not recommendations. You can decline or revise them.</p>" + "".join(reflection_options) + "</section>") if reflection_options else ""}
    {("<section><h2>Reading limitations</h2>" + limitations + "</section>") if limitations else ""}
    <p class="notice">This page presents supplied claim text and provenance. It does not generate or verify the claims, diagnose, or provide medical advice.</p>
  </main>
</body>
</html>
"""
