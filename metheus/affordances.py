"""Reference checks for optional environmental-affordance trials."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .authorization import evaluate_authorization
from .schema_validation import validate_record_schema, validate_schema_instance


def validate_environmental_affordance_links(
    readings: Iterable[dict[str, Any]],
    records: Iterable[dict[str, Any]],
    *,
    selected_record_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Resolve support options, lifecycle events, and separately reported responses.

    This checks identifiers, subject ownership, and stable trial metadata only.
    It does not assess whether an affordance is appropriate, effective, safe, or
    causally related to a response. Callers should pass all readings needed to
    resolve `sourceReadingId`; selected records identify the records in scope.
    No record text or option text is returned.
    """
    issues: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def issue(code: str, identifier: Any = None) -> None:
        key = (code, identifier if isinstance(identifier, str) else "")
        if key in seen:
            return
        seen.add(key)
        item = {"code": code}
        if isinstance(identifier, str) and identifier:
            item["id"] = identifier
        issues.append(item)

    reading_index: dict[str, dict[str, Any]] = {}
    option_index: dict[tuple[str, str], dict[str, Any]] = {}
    for reading in readings:
        if not isinstance(reading, dict):
            issue("invalid_affordance_source_reading")
            continue
        reading_id = reading.get("id")
        subject_id = reading.get("subjectId")
        if not isinstance(reading_id, str) or not reading_id:
            issue("affordance_source_reading_missing_id")
            continue
        if reading_id in reading_index:
            issue("duplicate_affordance_source_reading_id", reading_id)
            continue
        reading_index[reading_id] = reading
        options = reading.get("reflectionOptions", [])
        if not isinstance(options, list):
            issue("invalid_affordance_reflection_options", reading_id)
            continue
        for option in options:
            if not isinstance(option, dict):
                issue("invalid_affordance_reflection_option", reading_id)
                continue
            if option.get("kind") != "environmental_affordance":
                continue
            option_id = option.get("id")
            if not isinstance(option_id, str) or not option_id:
                issue("affordance_option_missing_id", reading_id)
                continue
            key = (reading_id, option_id)
            if key in option_index:
                issue("duplicate_affordance_option_id", option_id)
                continue
            option_index[key] = {**option, "_subjectId": subject_id}

    record_index: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            issue("invalid_affordance_related_record")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            issue("affordance_related_record_missing_id")
            continue
        if record_id in record_index:
            issue("duplicate_affordance_related_record_id", record_id)
            continue
        record_index[record_id] = record

    if selected_record_ids is None:
        selected_ids = set(record_index)
    elif isinstance(selected_record_ids, (str, bytes, dict)):
        selected_ids = set()
        issue("invalid_selected_affordance_record_ids")
    else:
        try:
            selected_values = list(selected_record_ids)
        except TypeError:
            selected_values = []
            issue("invalid_selected_affordance_record_ids")
        if not all(isinstance(value, str) and value for value in selected_values):
            selected_ids = set()
            if selected_values:
                issue("invalid_selected_affordance_record_ids")
        elif len(set(selected_values)) != len(selected_values):
            selected_ids = set(selected_values)
            issue("duplicate_selected_affordance_record_id")
        else:
            selected_ids = set(selected_values)

    unknown_selected = selected_ids - set(record_index)
    for record_id in sorted(unknown_selected):
        issue("unresolved_selected_affordance_record", record_id)

    trials: dict[str, tuple[str, tuple[Any, ...]]] = {}
    resolved_event_ids: set[str] = set()
    for record_id in sorted(selected_ids.intersection(record_index)):
        record = record_index[record_id]
        event = record.get("environmentalAffordance")
        if not isinstance(event, dict):
            continue
        subject_id = record.get("subjectId")
        trial_id = event.get("affordanceId")
        if not isinstance(trial_id, str) or not trial_id:
            issue("affordance_event_missing_trial_id", record_id)
            continue
        delivery = event.get("deliveryMode")
        function = event.get("intendedFunction")
        role = event.get("roleFrame")
        signature = (delivery, function, role)
        prior = trials.get(trial_id)
        if prior is not None:
            prior_subject, prior_signature = prior
            if prior_subject != subject_id:
                issue("affordance_trial_subject_mismatch", trial_id)
            if prior_signature != signature:
                issue("affordance_trial_metadata_mismatch", trial_id)
        else:
            trials[trial_id] = (subject_id, signature)

        if delivery == "conversational_ai" and role != "tool_or_scaffold":
            issue("ai_affordance_role_must_be_tool_or_scaffold", record_id)

        source_reading_id = event.get("sourceReadingId")
        source_option_id = event.get("sourceOptionId")
        if source_option_id is not None:
            source_reading = reading_index.get(source_reading_id)
            if source_reading is None:
                issue("unresolved_affordance_source_reading", source_reading_id)
                continue
            if source_reading.get("subjectId") != subject_id:
                issue("affordance_source_reading_subject_mismatch", source_reading_id)
                continue
            option = option_index.get((source_reading_id, source_option_id))
            if option is None:
                issue("unresolved_affordance_source_option", source_option_id)
                continue
            if option.get("_subjectId") != subject_id:
                issue("affordance_source_option_subject_mismatch", source_option_id)
                continue
            proposed = option.get("environmentalAffordance")
            if not isinstance(proposed, dict):
                issue("invalid_affordance_source_option", source_option_id)
                continue
            if any(proposed.get(field) != event.get(field) for field in ("deliveryMode", "intendedFunction", "roleFrame")):
                issue("affordance_event_option_mismatch", record_id)
                continue
        resolved_event_ids.add(record_id)

    for record_id in sorted(selected_ids.intersection(record_index)):
        record = record_index[record_id]
        related_ids = record.get("relatedAffordanceIds", [])
        if not isinstance(related_ids, list):
            issue("invalid_related_affordance_ids", record_id)
            continue
        if len(set(value for value in related_ids if isinstance(value, str))) != len(related_ids):
            issue("duplicate_related_affordance_id", record_id)
        for trial_id in related_ids:
            if not isinstance(trial_id, str) or not trial_id:
                issue("invalid_related_affordance_id", record_id)
                continue
            trial = trials.get(trial_id)
            if trial is None:
                issue("unresolved_related_affordance_id", trial_id)
            elif trial[0] != record.get("subjectId"):
                issue("related_affordance_subject_mismatch", trial_id)

    return {
        "valid": not issues,
        "resolvedAffordanceEventIds": sorted(resolved_event_ids),
        "resolvedTrialIds": sorted(trials),
        "issues": issues,
    }


def select_complementary_gate_affordances(
    symbolic_map: dict[str, Any],
    topology_catalog: dict[str, Any],
    affordance_catalog: dict[str, Any],
    *,
    chart_aware_enabled: bool,
) -> dict[str, Any]:
    """Select optional gate-theme ideas from an explicitly enabled natal chart.

    This is a symbolic lookup, not a need or deficit detector and not an
    affordance recommender. It only emits an unranked partner-gate activity
    when exactly one endpoint of a topology channel is active in a calculated
    Human Design map. Callers must authorize the map and any remote processing
    before calling. Transit and partial/illustrative maps are not eligible.
    """
    empty = {"eligible": False, "reason": "", "candidates": []}
    if chart_aware_enabled is not True:
        return {**empty, "reason": "chart_aware_mode_not_enabled"}
    if not isinstance(symbolic_map, dict) or not isinstance(topology_catalog, dict) or not isinstance(affordance_catalog, dict):
        return {**empty, "reason": "invalid_chart_or_catalog"}
    source_system = symbolic_map.get("sourceSystem")
    if not isinstance(source_system, dict) or source_system.get("name") != "Human Design":
        return {**empty, "reason": "unsupported_symbolic_system"}
    if topology_catalog.get("catalogId") != "human-design-bodygraph-topology-v1":
        return {**empty, "reason": "unsupported_topology_catalog"}
    if affordance_catalog.get("catalogId") != "metheus-gate-ai-affordances-v1":
        return {**empty, "reason": "unsupported_affordance_catalog"}
    calculation = symbolic_map.get("calculation")
    if not isinstance(calculation, dict) or calculation.get("status") != "calculated":
        return {**empty, "reason": "chart_is_not_fully_calculated"}
    bodygraph = calculation.get("bodygraph")
    if not isinstance(bodygraph, dict) or bodygraph.get("chartScope") != "natal":
        return {**empty, "reason": "natal_chart_map_required"}
    expected_topology_id = topology_catalog.get("catalogId")
    expected_topology_version = topology_catalog.get("version")
    if (
        bodygraph.get("topologyCatalogId") != expected_topology_id
        or bodygraph.get("topologyVersion") != expected_topology_version
        or affordance_catalog.get("topologyCatalogId") != expected_topology_id
        or affordance_catalog.get("topologyVersion") != expected_topology_version
    ):
        return {**empty, "reason": "topology_version_mismatch"}
    active_values = bodygraph.get("activatedGateNumbers")
    if not isinstance(active_values, list) or any(
        not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > 64
        for value in active_values
    ):
        return {**empty, "reason": "invalid_activated_gate_list"}
    if len(set(active_values)) != len(active_values):
        return {**empty, "reason": "duplicate_activated_gate"}
    channels = topology_catalog.get("channels")
    entries = affordance_catalog.get("entries")
    if not isinstance(channels, list) or not isinstance(entries, list):
        return {**empty, "reason": "invalid_topology_or_affordance_catalog"}
    active = set(active_values)
    affordances_by_gate = {
        entry.get("gateNumber"): entry
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("gateNumber"), int)
    }
    candidates: list[dict[str, Any]] = []
    for channel in channels:
        if not isinstance(channel, dict):
            continue
        gate_a, gate_b = channel.get("gateA"), channel.get("gateB")
        if not isinstance(gate_a, int) or not isinstance(gate_b, int) or (gate_a in active) == (gate_b in active):
            continue
        active_gate, complement_gate = (gate_a, gate_b) if gate_a in active else (gate_b, gate_a)
        entry = affordances_by_gate.get(complement_gate)
        if entry is None or not isinstance(entry.get("aiAffordance"), str):
            continue
        candidates.append({
            "channelId": channel.get("id"),
            "activeGateNumber": active_gate,
            "complementaryGateNumber": complement_gate,
            "complementaryGateTitle": entry.get("title"),
            "interactionModes": entry.get("interactionModes"),
            "aiAffordance": entry["aiAffordance"],
            "examplePrompt": entry.get("examplePrompt"),
            "framing": "Optional symbolic exploration; not gate activation, a chart change, or evidence of a missing ability.",
        })
    return {
        "eligible": True,
        "reason": "",
        "candidates": candidates,
        "limitations": [
            "Candidate selection follows the named symbolic chart and topology only; it does not establish need, fit, or benefit.",
            "The subject must choose whether to use, revise, or dismiss each candidate.",
        ],
    }


def select_authorized_complementary_gate_affordances(
    reading: dict[str, Any],
    symbolic_map: dict[str, Any],
    topology_catalog: dict[str, Any],
    affordance_catalog: dict[str, Any],
    grants: Iterable[dict[str, Any]],
    *,
    chart_aware_enabled: bool,
    remote_processing: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Select chart-aware ideas only for the reading's selected, consented map.

    This is still an in-memory policy check, not an authentication or storage
    boundary. The caller must establish identity, load only authorized inputs,
    and ensure this returned data is not sent to a remote service unless remote
    processing was explicitly checked.
    """
    empty = {"eligible": False, "reason": "", "candidates": []}
    if not isinstance(reading, dict) or not isinstance(symbolic_map, dict):
        return {**empty, "reason": "invalid_reading_or_map"}
    if not isinstance(reading.get("inputIds"), list) or symbolic_map.get("id") not in reading["inputIds"]:
        return {**empty, "reason": "symbolic_map_not_selected"}
    subject_id = reading.get("subjectId")
    if not isinstance(subject_id, str) or symbolic_map.get("subjectId") != subject_id:
        return {**empty, "reason": "symbolic_map_subject_mismatch"}
    reading_check = validate_schema_instance(reading, "reading.schema.json")
    map_check = validate_record_schema(symbolic_map)
    if not reading_check["valid"] or not map_check["valid"]:
        return {**empty, "reason": "invalid_reading_or_map_schema"}
    if symbolic_map.get("recordType") != "symbolic_map" or symbolic_map.get("domain") != "symbolic":
        return {**empty, "reason": "not_a_symbolic_map_record"}
    purpose = reading.get("purpose")
    try:
        grant_list = list(grants)
        analyze = evaluate_authorization(
            [symbolic_map], grant_list, subject_id=subject_id,
            purpose=purpose, action="analyze", now=now,
        )
        remote = None
        if remote_processing:
            remote = evaluate_authorization(
                [symbolic_map], grant_list, subject_id=subject_id,
                purpose=purpose, action="remote_processing", now=now,
            )
    except (TypeError, ValueError):
        return {**empty, "reason": "invalid_authorization_context"}
    if not analyze.get("authorized"):
        return {**empty, "reason": "symbolic_map_analysis_not_authorized", "authorization": analyze}
    if remote_processing and not remote.get("authorized"):
        return {**empty, "reason": "remote_processing_not_authorized", "authorization": remote}
    result = select_complementary_gate_affordances(
        symbolic_map, topology_catalog, affordance_catalog,
        chart_aware_enabled=chart_aware_enabled,
    )
    if result.get("eligible"):
        bodygraph = symbolic_map["calculation"]["bodygraph"]
        active_gates = sorted(bodygraph["activatedGateNumbers"])
        active_gate_set = set(active_gates)
        active_channels = [
            {
                "channelId": channel["id"],
                "gateNumbers": sorted([channel["gateA"], channel["gateB"]]),
            }
            for channel in topology_catalog["channels"]
            if isinstance(channel, dict)
            and isinstance(channel.get("id"), str)
            and isinstance(channel.get("gateA"), int)
            and isinstance(channel.get("gateB"), int)
            and channel["gateA"] in active_gate_set
            and channel["gateB"] in active_gate_set
        ]
        activated_gates = []
        for gate_number in active_gates:
            entry = next(
                (item for item in affordance_catalog["entries"]
                 if isinstance(item, dict) and item.get("gateNumber") == gate_number),
                None,
            )
            if entry is None:
                return {**empty, "reason": "activated_gate_missing_affordance_entry"}
            activated_gates.append({
                "gateNumber": gate_number,
                "sourceTitle": entry.get("title"),
                "centerId": entry.get("centerId"),
                "channelIds": entry.get("channelIds"),
                "interactionModes": entry.get("interactionModes"),
                "optionalActivityIdea": entry.get("aiAffordance"),
                "examplePrompt": entry.get("examplePrompt"),
            })
        defined_centers = sorted({
            center_id
            for channel in topology_catalog["channels"]
            if isinstance(channel, dict)
            and isinstance(channel.get("gateA"), int)
            and isinstance(channel.get("gateB"), int)
            and channel["gateA"] in active_gate_set
            and channel["gateB"] in active_gate_set
            for center_id in (channel.get("centerA"), channel.get("centerB"))
            if isinstance(center_id, str)
        })
        ai_context = {
            "contextType": "optional_symbolic_chart_context",
            "contextScope": "calculated_natal_map",
            "chartAwareness": {
                "mode": "explicit_chart_context",
                "mapScope": "calculated_natal_map",
                "providedActivatedGateCount": len(active_gates),
                "providedGateNumbers": active_gates,
                "providedDefinedChannelCount": len(active_channels),
                "liveStateAccess": False,
                "priorChartAwareTurnMemory": False,
                "statement": "This request includes only the selected natal map and topology-derived channels. It does not include live transits, momentary state, or prior chart-aware exchanges.",
            },
            "sourceSystem": symbolic_map["sourceSystem"],
            "chartProvenance": {
                "kind": "calculated_natal_map",
                "calculationStatus": "calculated",
                "calculationEngine": symbolic_map["calculation"]["engine"],
                "calculationMethod": symbolic_map["calculation"]["method"],
                "calculationMethodVersion": symbolic_map["calculation"]["methodVersion"],
                "executionMode": symbolic_map["calculation"]["executionMode"],
                "timeZoneDatabase": symbolic_map["calculation"]["timeZoneDatabase"],
                "inputPrecision": symbolic_map["calculation"]["inputPrecision"],
                "verificationStatus": "asserted_not_independently_verified",
                "chartScope": "natal",
                "chartBinding": "selected_subject_map",
            },
            "topologyCatalogId": topology_catalog["catalogId"],
            "topologyVersion": topology_catalog["version"],
            "affordanceCatalogId": affordance_catalog["catalogId"],
            "affordanceCatalogVersion": affordance_catalog["version"],
            "activatedGateNumbers": active_gates,
            "activatedGates": activated_gates,
            "definedChannelIds": sorted(item["channelId"] for item in active_channels),
            "definedCenterIds": defined_centers,
            "activeChannels": active_channels,
            "complementaryGateCandidates": [
                {
                    "channelId": item["channelId"],
                    "activeGateNumber": item["activeGateNumber"],
                    "complementaryGateNumber": item["complementaryGateNumber"],
                    "complementaryGateTitle": item["complementaryGateTitle"],
                    "interactionModes": item["interactionModes"],
                    "optionalActivityIdea": item["aiAffordance"],
                    "examplePrompt": item.get("examplePrompt"),
                    "framing": item["framing"],
                }
                for item in result["candidates"]
            ],
            "assistantGuidance": [
                "Treat chartAwareness as the complete scope of what you know about this person's selected map for this turn. Do not claim broader or more current awareness than the listed gates and derived channels.",
                "Use this only as an optional, source-attributed symbolic lens when relevant to the user's request.",
                "Apply this selected subject's chart only to that subject's reflection, never to another person.",
                "This context is a natal chart map, not a time-bounded transit or live activation reading.",
                "The calculation method and version are reported from the selected map; Metheus has not independently verified this chart calculation.",
                "Answer the user's stated question or goal first; do not make a gate suggestion the default response.",
                "Read the complete activated-gate set for each chart-aware request and use a relevant activity to shape the help itself, but choose the most relevant active-gate activity for the user's stated goal and offer at most one; combine active activities only when the task benefits from it, otherwise answer normally.",
                "Use interaction-mode labels as practical activity-format hints, never as descriptions of the user's traits or abilities.",
                "For a listed active channel, use its gateNumbers to find the two corresponding activities in activatedGates. Combine only those catalog activities when the combination fits the stated goal; do not invent a separate channel meaning. Frame the combination as an optional symbolic lens, never a fixed trait or biological function.",
                "Choose by the user's stated goal, not by chart-only ranking; do not let chart activity displace the direct answer or repeat a suggestion within this response. Chart-aware turns are stateless and do not include prior chart-aware suggestions, so do not claim to remember or adapt to them. These activities are options, not traits, needs, or abilities.",
                "Consider the supplied complementary-gate candidates as optional environmental activities that may offer a way to explore a channel's partner end. When one clearly helps with the stated goal, proactively offer at most one even if the user did not ask for channel analysis; choose by task fit, not chart-only ranking.",
                "Distinguish a complementary activity from the already activated gates.",
                "Describe any activity in plain language before naming its gate or channel, and make it easy to skip or ask for a non-chart-based alternative.",
                "Never infer biology, hormones, health, personality, ability, need, deficit, or outcome from gates, centers, or channels.",
                "A complementary gate prompt is an invitation, not evidence of a missing capacity or a gate being activated by AI.",
                "Keep practical support useful without chart framing, grounded in the user's stated goal.",
            ],
        }
        context_check = validate_schema_instance(ai_context, "chart-aware-ai-context.schema.json")
        if not context_check["valid"]:
            return {**empty, "reason": "invalid_chart_aware_ai_context"}
        result["aiContext"] = ai_context
        result["audit"] = {
            "readingId": reading.get("id"),
            "subjectId": subject_id,
            "symbolicMapId": symbolic_map.get("id"),
            "sourceSystem": symbolic_map.get("sourceSystem"),
            "topologyCatalogId": topology_catalog.get("catalogId"),
            "topologyVersion": topology_catalog.get("version"),
            "affordanceCatalogId": affordance_catalog.get("catalogId"),
            "affordanceCatalogVersion": affordance_catalog.get("version"),
            "analysisAuthorization": analyze.get("authorized"),
            "remoteProcessingAuthorization": remote.get("authorized") if remote is not None else False,
        }
    return result
