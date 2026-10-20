"""Ensure source correspondences and scientific evidence stay separate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from metheus.readings import validate_reading_references


ROOT = Path(__file__).resolve().parents[1]
READING = json.loads((ROOT / "examples/gate-correspondence-reading.example.json").read_text(encoding="utf-8"))
CORRESPONDENCE_CATALOG = json.loads((ROOT / "catalog/gate-endocrine-correspondences.json").read_text(encoding="utf-8"))
EVIDENCE_CATALOG = json.loads((ROOT / "catalog/evidence-claims.json").read_text(encoding="utf-8"))
CORRESPONDENCE = next(item for item in CORRESPONDENCE_CATALOG["correspondences"] if item["id"] == "gate-6-reproductive-hormone-source-attribution")
UNREVIEWED_EVIDENCE = EVIDENCE_CATALOG["claims"][0]


class ReadingReferenceEligibilityTests(unittest.TestCase):
    def validate(self, reading: dict, *, correspondences: list[dict] | None = None, evidence: list[dict] | None = None) -> dict:
        return validate_reading_references(
            reading,
            records=[],
            phase_annotations=[],
            correspondences=correspondences or [],
            evidence_claims=evidence or [],
        )

    def test_selected_source_attributed_correspondence_is_valid_for_symbolic_prompt(self) -> None:
        result = self.validate(READING, correspondences=[CORRESPONDENCE])
        self.assertTrue(result["valid"], result)

    def test_correspondence_must_be_selected_and_claim_must_be_symbolic_or_question(self) -> None:
        unselected = {**READING, "referenceIds": []}
        result = self.validate(unselected, correspondences=[CORRESPONDENCE])
        self.assertIn("correspondence_not_selected", {item["code"] for item in result["issues"]})

        factual_claim = copy.deepcopy(READING)
        factual_claim["claims"][0]["claimType"] = "observation"
        result = self.validate(factual_claim, correspondences=[CORRESPONDENCE])
        self.assertIn("correspondence_claim_type_not_permitted", {item["code"] for item in result["issues"]})

    def test_candidate_scientific_evidence_is_not_eligible_for_a_reading(self) -> None:
        reading = copy.deepcopy(READING)
        reading["referenceIds"] = [UNREVIEWED_EVIDENCE["id"]]
        reading["claims"] = [{
            "claimType": "boundary",
            "text": "Evidence has not completed review.",
            "sourceIds": [],
            "evidenceClaimIds": [UNREVIEWED_EVIDENCE["id"]],
            "support": {"confidence": "high", "coverage": "adequate", "rationale": "Candidate remains under review."},
        }]
        result = self.validate(reading, evidence=[UNREVIEWED_EVIDENCE])
        codes = {item["code"] for item in result["issues"]}
        self.assertFalse(result["valid"])
        self.assertIn("evidence_claim_not_reviewed", codes)
        self.assertIn("evidence_claim_not_permitted_in_reading", codes)

    def test_person_owned_and_cross_catalog_ambiguous_references_are_rejected(self) -> None:
        owned = {**CORRESPONDENCE, "subjectId": "synthetic-subject"}
        result = self.validate(READING, correspondences=[owned])
        self.assertIn("subject_owned_correspondence_cannot_be_catalog_reference", {item["code"] for item in result["issues"]})

        collision = {**UNREVIEWED_EVIDENCE, "id": CORRESPONDENCE["id"]}
        result = self.validate(READING, correspondences=[CORRESPONDENCE], evidence=[collision])
        self.assertIn("ambiguous_reference_id", {item["code"] for item in result["issues"]})


if __name__ == "__main__":
    unittest.main()
