"""Reference checks for optional environmental-affordance trials."""

from __future__ import annotations

from typing import Any, Iterable


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
        selected_values = list(selected_record_ids)
        if not all(isinstance(value, str) and value for value in selected_values):
            selected_ids = set()
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
