"""Behavioral coverage for immutable, subject-scoped correction chains."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from metheus import resolve_current_records, summarize_main_sleep


ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples/rhythm-sleep-2026-10-20.example.json").read_text(encoding="utf-8"))


class RecordLifecycleTests(unittest.TestCase):
    def correction_pair(self) -> tuple[dict, dict]:
        original = copy.deepcopy(SOURCE)
        original.update({"revision": 1})
        corrected = copy.deepcopy(SOURCE)
        corrected.update({
            "id": "rhythm-sleep-2026-10-20-correction",
            "revision": 2,
            "supersedes": original["id"],
        })
        corrected["time"]["end"] = "2026-10-21T07:00:00-06:00"
        return original, corrected

    def test_correction_keeps_history_but_selects_only_current_record(self) -> None:
        original, corrected = self.correction_pair()
        result = resolve_current_records([original, corrected], subject_id=SOURCE["subjectId"])
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["currentIds"], [corrected["id"]])
        self.assertEqual(result["supersededIds"], [original["id"]])
        self.assertEqual(original["id"], corrected["supersedes"])

    def test_rhythm_summary_counts_only_corrected_measurement_and_cites_it(self) -> None:
        original, corrected = self.correction_pair()
        summary = summarize_main_sleep(
            [original, corrected],
            subject_id=SOURCE["subjectId"],
            start_date="2026-10-18",
            end_date="2026-10-20",
        )
        self.assertEqual(summary["medianLoggedDurationMinutes"], 540.0)
        self.assertIn(corrected["id"], summary["inputRecordIds"])
        self.assertNotIn(original["id"], summary["inputRecordIds"])
        self.assertEqual(summary["revisionResolution"]["supersededRecordCount"], 1)

    def test_branching_revision_chain_fails_closed(self) -> None:
        original, first_correction = self.correction_pair()
        second_correction = copy.deepcopy(first_correction)
        second_correction["id"] = "other-correction"
        result = resolve_current_records([original, first_correction, second_correction], subject_id=SOURCE["subjectId"])
        self.assertFalse(result["valid"])
        self.assertIn("competing_revision_successors", {item["code"] for item in result["issues"]})

    def test_nonconsecutive_revision_and_cycles_fail_closed(self) -> None:
        original, corrected = self.correction_pair()
        corrected["revision"] = 3
        result = resolve_current_records([original, corrected], subject_id=SOURCE["subjectId"])
        self.assertFalse(result["valid"])
        self.assertIn("nonconsecutive_revision", {item["code"] for item in result["issues"]})

        first = {**original, "supersedes": "second"}
        second = {**corrected, "id": "second", "supersedes": original["id"]}
        first.pop("revision")
        second.pop("revision")
        result = resolve_current_records([first, second], subject_id=SOURCE["subjectId"])
        self.assertFalse(result["valid"])
        self.assertIn("revision_cycle", {item["code"] for item in result["issues"]})

    def test_duplicate_ids_fail_but_other_subject_history_is_isolated(self) -> None:
        original, corrected = self.correction_pair()
        duplicate = resolve_current_records([original, copy.deepcopy(original)], subject_id=SOURCE["subjectId"])
        self.assertFalse(duplicate["valid"])
        self.assertIn("duplicate_record_id", {item["code"] for item in duplicate["issues"]})

        foreign = copy.deepcopy(original)
        foreign["subjectId"] = "other-subject"
        isolated = resolve_current_records([foreign, original, corrected], subject_id=SOURCE["subjectId"])
        self.assertTrue(isolated["valid"], isolated)
        self.assertEqual(isolated["currentIds"], [corrected["id"]])

    def test_pruned_predecessor_is_a_warning_not_an_invented_record(self) -> None:
        _, corrected = self.correction_pair()
        result = resolve_current_records([corrected], subject_id=SOURCE["subjectId"])
        self.assertTrue(result["valid"])
        self.assertEqual(result["currentIds"], [corrected["id"]])
        self.assertIn("superseded_record_not_in_supplied_history", {item["code"] for item in result["warnings"]})


if __name__ == "__main__":
    unittest.main()
