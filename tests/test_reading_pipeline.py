"""Exercise a synthetic observations-to-summary-to-rendered-reading slice."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from metheus import assemble_reading, preflight_subject_reading, render_assembled_reading_html, summarize_main_sleep


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())


class ReadingPipelineTests(unittest.TestCase):
    def test_synthetic_sleep_records_reach_reading_with_consent_and_provenance(self) -> None:
        records = [
            load_example(f"rhythm-sleep-2026-10-{day}.example.json")
            for day in ("18", "19", "20")
        ]
        summary = summarize_main_sleep(
            records,
            subject_id="rhythm-example-subject",
            start_date="2026-10-18",
            end_date="2026-10-20",
        )
        reading = load_example("rhythm-summary-reading.example.json")
        subject_index = load_example("rhythm-subject-index.example.json")
        grant = load_example("rhythm-summary-consent.example.json")

        self.assertEqual(summary["id"], "sleep:metheus-rhythm-summary/0.2.0:2026-10-18:2026-10-20")
        self.assertEqual(summary["medianLoggedDurationMinutes"], 480.0)
        package = assemble_reading(
            reading,
            subject_index,
            [*records, summary],
            [grant],
            now=datetime(2026, 10, 21, 12, tzinfo=timezone.utc),
        )

        self.assertTrue(package["assembled"], package)
        self.assertEqual(package["claims"][0]["sourceIds"], [summary["id"]])
        self.assertEqual(package["claims"][0]["sources"][0]["inputRecordIds"], summary["inputRecordIds"])
        self.assertEqual(package["assembly"]["authorizedAction"], "analyze")

        html = render_assembled_reading_html(package)
        self.assertIn("480", html)
        self.assertIn("rhythm-sleep-2026-10-18", html)
        self.assertIn("Clock-time summary is not an estimate of endogenous circadian phase.", html)

    def test_pipeline_refuses_when_required_sleep_scope_is_removed(self) -> None:
        records = [
            load_example(f"rhythm-sleep-2026-10-{day}.example.json")
            for day in ("18", "19", "20")
        ]
        summary = summarize_main_sleep(
            records,
            subject_id="rhythm-example-subject",
            start_date="2026-10-18",
            end_date="2026-10-20",
        )
        grant = load_example("rhythm-summary-consent.example.json")
        grant["domains"] = ["relationship"]
        result = assemble_reading(
            load_example("rhythm-summary-reading.example.json"),
            load_example("rhythm-subject-index.example.json"),
            [*records, summary],
            [grant],
            now=datetime(2026, 10, 21, 12, tzinfo=timezone.utc),
        )

        self.assertFalse(result["assembled"])
        self.assertEqual(result["reason"], "reading_preflight_failed")
        self.assertFalse(result["preflight"]["preflightPassed"])

    def test_reading_preflight_rejects_subject_mismatch_and_unindexed_input(self) -> None:
        records = [
            load_example(f"rhythm-sleep-2026-10-{day}.example.json")
            for day in ("18", "19", "20")
        ]
        summary = summarize_main_sleep(
            records,
            subject_id="rhythm-example-subject",
            start_date="2026-10-18",
            end_date="2026-10-20",
        )
        reading = load_example("rhythm-summary-reading.example.json")
        subject_index = load_example("rhythm-subject-index.example.json")
        grant = load_example("rhythm-summary-consent.example.json")
        resources = [*records, summary]

        wrong_subject = {**reading, "subjectId": "different-subject"}
        result = preflight_subject_reading(
            wrong_subject, subject_index, resources, [grant],
            now=datetime(2026, 10, 21, 12, tzinfo=timezone.utc),
        )
        self.assertFalse(result["preflightPassed"])
        self.assertEqual(result["reason"], "reading_subject_index_mismatch")

        unindexed_input = {**reading, "inputIds": [*reading["inputIds"], "unindexed-record"]}
        result = preflight_subject_reading(
            unindexed_input, subject_index, resources, [grant],
            now=datetime(2026, 10, 21, 12, tzinfo=timezone.utc),
        )
        self.assertFalse(result["preflightPassed"])
        self.assertEqual(result["reason"], "reading_input_not_indexed")
        self.assertEqual(result["unindexedIds"], ["unindexed-record"])

    def test_cross_layer_reading_keeps_promethean_and_epimethean_sources_distinct(self) -> None:
        subject_id = "synthetic-subject"
        resources = [
            load_example("phase-chart-feature.example.json"),
            load_example("phase-bleeding-observation.example.json"),
            load_example("urinary-lh-home-test.example.json"),
            load_example("phase-promethean.example.json"),
            load_example("phase-epimethean.example.json"),
        ]
        reading = load_example("phase-aware-reading.example.json")
        subject_index = {
            "id": "cross-layer-synthetic-index",
            "subjectId": subject_id,
            "recordType": "subject_index",
            "schemaVersion": "0.1",
            "revision": 1,
            "steward": {"reference": subject_id, "role": "subject"},
            "resourceRefs": [
                {
                    "id": item["id"],
                    "kind": "phase_annotation" if item["recordType"] == "phase_annotation" else "observation",
                    "schemaVersion": item["schemaVersion"],
                }
                for item in resources
            ],
            "createdAt": "2026-04-10T12:00:00Z",
            "updatedAt": "2026-04-10T12:00:00Z",
        }

        def consent(domain: str, record_ids: list[str]) -> dict:
            return {
                "id": f"synthetic-{domain}-grant",
                "subjectId": subject_id,
                "grantor": {"reference": subject_id, "role": "subject"},
                "domains": [domain],
                "purposes": ["personal_reflection"],
                "permittedActions": ["analyze"],
                "recordIds": record_ids,
                "status": "granted",
                "consentTextVersion": "synthetic-cross-layer/1",
                "createdAt": "2026-01-01T00:00:00Z",
                "expiresAt": "2027-01-01T00:00:00Z",
            }

        grants = [
            consent("symbolic", ["synthetic-chart-feature", "phase-promethean-example"]),
            consent("reproductive", ["synthetic-bleeding-observation", "phase-epimethean-example"]),
            consent("hormone_assay", ["synthetic-urinary-lh-test"]),
        ]
        now = datetime(2026, 4, 11, 12, tzinfo=timezone.utc)
        package = assemble_reading(reading, subject_index, resources, grants, now=now)

        self.assertTrue(package["assembled"], package)
        claims = package["claims"]
        self.assertEqual(claims[0]["claimType"], "symbolic_prompt")
        self.assertEqual(claims[0]["phaseAnnotations"][0]["layer"], "promethean")
        self.assertEqual(claims[1]["claimType"], "observation")
        self.assertEqual(claims[1]["phaseAnnotations"][0]["layer"], "epimethean")
        self.assertEqual(claims[1]["sourceIds"], ["synthetic-bleeding-observation"])
        self.assertEqual(claims[3]["sourceIds"], ["synthetic-urinary-lh-test"])

        html = render_assembled_reading_html(package)
        self.assertIn("Promethean symbolic context", html)
        self.assertIn("Epimethean lived context", html)
        self.assertIn("does not establish cycle phase", html)


if __name__ == "__main__":
    unittest.main()
