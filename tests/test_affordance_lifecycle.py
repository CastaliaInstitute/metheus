"""Keep an offered support, its use, and later response as distinct records."""

from __future__ import annotations

import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from metheus import assemble_reading, preflight_subject_reading, render_assembled_reading_html, validate_environmental_affordance_links


ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "examples/environmental-affordance-linked-case.example.json").read_text(encoding="utf-8"))


class AffordanceLifecycleTests(unittest.TestCase):
    def test_optional_ai_offer_use_and_uncertain_response_resolve_separately(self) -> None:
        result = validate_environmental_affordance_links(
            CASE["sourceReadings"],
            CASE["records"],
            selected_record_ids=CASE["selectedRecordIds"],
        )
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["resolvedAffordanceEventIds"], ["synthetic-ai-affordance-use-01"])
        self.assertEqual(result["resolvedTrialIds"], ["synthetic-ai-dialogue-practice-01"])

        event = next(record for record in CASE["records"] if record["id"] == "synthetic-ai-affordance-use-01")
        response = next(record for record in CASE["records"] if record["id"] == "synthetic-ai-affordance-response-01")
        self.assertEqual(event["environmentalAffordance"]["lifecycleEvent"], "used")
        self.assertEqual(response["value"]["category"], "uncertain")
        self.assertEqual(response["relatedAffordanceIds"], [event["environmentalAffordance"]["affordanceId"]])
        self.assertNotIn("effect", response["value"])
        self.assertFalse(any("effective" in limitation.lower() for limitation in CASE["limitations"]))

    def test_selected_scope_controls_which_lifecycle_events_are_resolved(self) -> None:
        event_only = validate_environmental_affordance_links(
            CASE["sourceReadings"], CASE["records"],
            selected_record_ids=["synthetic-ai-affordance-use-01"],
        )
        self.assertTrue(event_only["valid"], event_only)

        response_only = validate_environmental_affordance_links(
            CASE["sourceReadings"], CASE["records"],
            selected_record_ids=["synthetic-ai-affordance-response-01"],
        )
        self.assertFalse(response_only["valid"])
        self.assertIn("unresolved_related_affordance_id", {issue["code"] for issue in response_only["issues"]})

    def test_option_and_trial_must_keep_delivery_function_and_role_stable(self) -> None:
        records = copy.deepcopy(CASE["records"])
        event = next(record for record in records if record["id"] == "synthetic-ai-affordance-use-01")
        event["environmentalAffordance"]["roleFrame"] = "human_relationship"
        result = validate_environmental_affordance_links(
            CASE["sourceReadings"], records, selected_record_ids=CASE["selectedRecordIds"],
        )
        self.assertFalse(result["valid"])
        self.assertIn("affordance_event_option_mismatch", {issue["code"] for issue in result["issues"]})

    def test_cross_subject_and_trial_metadata_mismatch_fail_closed(self) -> None:
        records = copy.deepcopy(CASE["records"])
        response = next(record for record in records if record["id"] == "synthetic-ai-affordance-response-01")
        response["subjectId"] = "another-subject"
        result = validate_environmental_affordance_links(
            CASE["sourceReadings"], records, selected_record_ids=CASE["selectedRecordIds"],
        )
        self.assertFalse(result["valid"])
        self.assertIn("related_affordance_subject_mismatch", {issue["code"] for issue in result["issues"]})

        source_event = next(record for record in records if record["id"] == "synthetic-ai-affordance-use-01")
        conflicting_event = copy.deepcopy(source_event)
        conflicting_event["id"] = "second-event"
        conflicting_event["environmentalAffordance"]["sourceOptionId"] = None
        conflicting_event["environmentalAffordance"]["intendedFunction"] = "different_function"
        records.append(conflicting_event)
        result = validate_environmental_affordance_links(
            CASE["sourceReadings"], records, selected_record_ids=[*CASE["selectedRecordIds"], "second-event"],
        )
        self.assertFalse(result["valid"])
        self.assertIn("affordance_trial_metadata_mismatch", {issue["code"] for issue in result["issues"]})

    def test_follow_up_reading_requires_consent_for_use_and_response_separately(self) -> None:
        subject_id = "example-subject-01"
        records = copy.deepcopy(CASE["records"])
        use_event, response = records
        reading = {
            "id": "synthetic-ai-affordance-follow-up",
            "subjectId": subject_id,
            "version": "0.1",
            "purpose": "learning_support",
            "question": "How did the optional practice feel afterward?",
            "timeWindow": {
                "start": "2026-10-21T10:00:00-06:00",
                "end": "2026-10-21T10:30:00-06:00",
                "timeZone": "America/Denver",
                "precision": "approximate",
            },
            "inputIds": [use_event["id"], response["id"]],
            "claims": [
                {
                    "claimType": "observation",
                    "text": "You reported trying an optional AI dialogue rehearsal.",
                    "sourceIds": [use_event["id"]],
                    "support": {"confidence": "high", "coverage": "adequate", "rationale": "This is a summary of the selected use event."},
                },
                {
                    "claimType": "observation",
                    "text": "You later reported being unsure whether the practice changed confidence.",
                    "sourceIds": [response["id"]],
                    "support": {"confidence": "high", "coverage": "adequate", "rationale": "This preserves the selected self-report."},
                },
                {
                    "claimType": "boundary",
                    "text": "These records do not establish benefit, harm, or a learning effect.",
                    "sourceIds": [use_event["id"], response["id"]],
                    "support": {"confidence": "high", "coverage": "adequate", "rationale": "No independent outcome or comparison is present."},
                },
            ],
            "limitations": ["Synthetic fixture only; the AI scaffold is a tool, not a relationship or proven intervention."],
            "generatedAt": "2026-10-21T11:00:00-06:00",
        }
        subject_index = {
            "id": "synthetic-affordance-follow-up-index",
            "subjectId": subject_id,
            "recordType": "subject_index",
            "schemaVersion": "0.1",
            "revision": 1,
            "steward": {"reference": subject_id, "role": "subject"},
            "resourceRefs": [
                {"id": record["id"], "kind": "observation", "schemaVersion": record["schemaVersion"]}
                for record in records
            ],
            "createdAt": "2026-10-21T11:00:00-06:00",
            "updatedAt": "2026-10-21T11:00:00-06:00",
        }
        grant = {
            "id": "synthetic-affordance-follow-up-consent",
            "subjectId": subject_id,
            "grantor": {"reference": subject_id, "role": "subject"},
            "domains": ["learning"],
            "purposes": ["learning_support"],
            "permittedActions": ["analyze"],
            "recordIds": [use_event["id"], response["id"]],
            "status": "granted",
            "consentTextVersion": "synthetic-affordance/1",
            "createdAt": "2026-10-20T00:00:00Z",
            "expiresAt": "2027-01-01T00:00:00Z",
        }
        now = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)
        package = assemble_reading(
            reading, subject_index, records, [grant], now=now,
            affordance_source_readings=CASE["sourceReadings"],
        )
        self.assertTrue(package["assembled"], package)
        self.assertEqual(package["claims"][0]["sourceIds"], [use_event["id"]])
        self.assertEqual(package["claims"][1]["sourceIds"], [response["id"]])
        self.assertNotIn("promethean-feature-example-01", reading["inputIds"])

        html = render_assembled_reading_html(package)
        self.assertIn("You reported trying an optional AI dialogue rehearsal.", html)
        self.assertIn("These records do not establish benefit, harm, or a learning effect.", html)

        missing_response_scope = {**grant, "recordIds": [use_event["id"]]}
        denied = preflight_subject_reading(
            reading, subject_index, records, [missing_response_scope], now=now,
            affordance_source_readings=CASE["sourceReadings"],
        )
        self.assertFalse(denied["preflightPassed"])
        self.assertFalse(denied["authorization"]["authorized"])


if __name__ == "__main__":
    unittest.main()
