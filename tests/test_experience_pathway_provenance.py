"""Behavioral checks for experience-pathway endpoint provenance."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from metheus.pathways import validate_experience_pathway_references


ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "examples/experience-pathway-local-preflight.example.json").read_text(encoding="utf-8"))


class ExperiencePathwayProvenanceTests(unittest.TestCase):
    def test_synthetic_pathway_cites_sources_for_both_link_endpoints(self) -> None:
        pathway = CASE["pathway"]
        result = validate_experience_pathway_references(pathway, CASE["resources"], CASE["evidenceClaims"])

        self.assertTrue(result["valid"], result["issues"])

    def test_reported_link_missing_from_endpoint_source_fails_closed(self) -> None:
        pathway = json.loads(json.dumps(CASE["pathway"]))
        relation = next(item for item in pathway["relations"] if item["relationId"] == "cue-stress")
        relation["basisRecordIds"] = ["synthetic-pathway-stress"]

        result = validate_experience_pathway_references(pathway, CASE["resources"], CASE["evidenceClaims"])

        self.assertFalse(result["valid"])
        self.assertIn(
            "pathway_relation_basis_missing_endpoint_source",
            {item["code"] for item in result["issues"]},
        )

    def test_temporal_edge_must_reference_both_endpoint_sources(self) -> None:
        pathway = json.loads(json.dumps(CASE["pathway"]))
        relation = pathway["relations"][0]
        relation.update({
            "relationType": "temporal_order",
            "basis": "record_times",
            "basisRecordIds": ["synthetic-pathway-cue", "synthetic-pathway-stress"],
        })
        result = validate_experience_pathway_references(pathway, CASE["resources"], CASE["evidenceClaims"])
        self.assertTrue(result["valid"], result["issues"])

        relation["basisRecordIds"] = ["synthetic-pathway-stress"]
        result = validate_experience_pathway_references(pathway, CASE["resources"], CASE["evidenceClaims"])
        self.assertFalse(result["valid"])
        self.assertIn(
            "pathway_relation_basis_missing_endpoint_source",
            {item["code"] for item in result["issues"]},
        )


if __name__ == "__main__":
    unittest.main()
