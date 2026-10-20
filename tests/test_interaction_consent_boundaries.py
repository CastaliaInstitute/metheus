"""Each relationship or intimacy record remains owned by its recorder."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import unittest

from metheus.resources import authorize_subject_index_resources


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text())


class InteractionConsentBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = load_example("interaction-intimacy.example.json")
        self.index = load_example("interaction-subject-index.example.json")
        self.grant = load_example("interaction-intimacy-consent.example.json")
        self.now = datetime(2026, 10, 21, tzinfo=timezone.utc)

    def authorize(self, record: dict, index: dict, grant: dict) -> dict:
        return authorize_subject_index_resources(
            index,
            [record],
            [record["id"]],
            [grant],
            purpose="personal_reflection",
            action="analyze",
            now=self.now,
        )

    def test_intimacy_event_requires_its_narrow_intimacy_grant(self) -> None:
        allowed = self.authorize(self.record, self.index, self.grant)
        self.assertTrue(allowed["authorized"])

        broader_relationship_grant = {**self.grant, "domains": ["relationships"]}
        denied = self.authorize(self.record, self.index, broader_relationship_grant)
        self.assertFalse(denied["authorized"])

    def test_recorder_grant_cannot_authorize_another_subjects_record(self) -> None:
        other_person_record = {**self.record, "subjectId": "subject-b"}
        denied = self.authorize(other_person_record, self.index, self.grant)
        self.assertFalse(denied["authorized"])
        self.assertEqual(denied["reason"], "invalid_subject_index_references")

    def test_record_stays_a_single_recorder_account_not_a_partner_attestation(self) -> None:
        self.assertEqual(self.record["subjectId"], "subject-a")
        recorders = [
            participant for participant in self.record["participantReferences"]
            if participant["relationToRecorder"] == "recorder"
        ]
        self.assertEqual(len(recorders), 1)
        self.assertIn(
            "does not establish another participant's consent",
            self.record["limitations"][0],
        )


if __name__ == "__main__":
    unittest.main()
