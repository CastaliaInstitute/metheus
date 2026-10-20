"""Structural summaries preserve branching without implying causation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from metheus.pathways import summarize_experience_pathway_structure


ROOT = Path(__file__).resolve().parents[1]


class ExperiencePathwayStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pathway = json.loads((ROOT / "examples/experience-pathway-synthetic.example.json").read_text())

    def test_summarizes_choice_branches_and_reported_reflection_cycle_separately(self) -> None:
        result = summarize_experience_pathway_structure(self.pathway)

        self.assertTrue(result["valid"])
        self.assertTrue(result["topologyOnly"])
        branches = {item["nodeId"]: item for item in result["branchPoints"]}
        self.assertEqual(branches["stress"]["outgoingRelationCount"], 3)
        self.assertEqual(set(branches["stress"]["relationTypes"]), {"person_reported_link"})
        self.assertTrue(any(set(component) == {"appraisal", "anger", "rumination"}
                            for component in result["personReportedLinkCycles"]))
        self.assertEqual(result["relationCounts"]["literature_mechanism"], 2)
        self.assertIn("not a measured or established feedback mechanism", " ".join(result["limitations"]))
        self.assertNotIn("label", result)

    def test_literature_edges_do_not_create_person_reported_cycles(self) -> None:
        pathway = copy.deepcopy(self.pathway)
        pathway["relations"] = [
            relation for relation in pathway["relations"]
            if relation["relationType"] == "literature_mechanism"
        ]

        result = summarize_experience_pathway_structure(pathway)

        self.assertTrue(result["valid"])
        self.assertEqual(result["personReportedLinkCycles"], [])

    def test_invalid_or_duplicate_graph_endpoints_fail_closed(self) -> None:
        pathway = copy.deepcopy(self.pathway)
        pathway["relations"][0]["toNodeId"] = "missing"
        self.assertEqual(summarize_experience_pathway_structure(pathway)["reason"], "unresolved_pathway_node_reference")

        pathway = copy.deepcopy(self.pathway)
        pathway["nodes"].append(copy.deepcopy(pathway["nodes"][0]))
        self.assertEqual(summarize_experience_pathway_structure(pathway)["reason"], "duplicate_pathway_node_id")


if __name__ == "__main__":
    unittest.main()
