"""Tests for opt-in symbolic complement selection."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from metheus.affordances import (
    select_authorized_complementary_gate_affordances,
    select_complementary_gate_affordances,
)


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = json.loads((ROOT / "catalog/human-design-bodygraph-topology.json").read_text(encoding="utf-8"))
AFFORDANCES = json.loads((ROOT / "catalog/gate-ai-affordances.json").read_text(encoding="utf-8"))


def chart_map(active_gates: list[int], *, scope: str = "natal", status: str = "calculated") -> dict:
    """Synthetic fixture; it contains no real birth input or calculated chart."""
    bodygraph = {
        "topologyCatalogId": TOPOLOGY["catalogId"],
        "topologyVersion": TOPOLOGY["version"],
        "chartScope": scope,
        "activatedGateNumbers": active_gates,
    }
    if scope == "transit":
        bodygraph["validAt"] = "2026-10-20T12:00:00Z"
    return {
        "id": "synthetic-chart-map",
        "subjectId": "synthetic-subject",
        "sourceSystem": {"name": "Human Design", "version": "synthetic-fixture"},
        "calculation": {
            "status": status,
            "bodygraph": bodygraph,
        },
    }


class ComplementaryGateAffordanceTests(unittest.TestCase):
    def select(self, symbolic_map: dict, *, enabled: bool = True) -> dict:
        return select_complementary_gate_affordances(
            symbolic_map,
            TOPOLOGY,
            AFFORDANCES,
            chart_aware_enabled=enabled,
        )

    def test_gate_11_surfaces_gate_56_idea_for_channel_11_56(self) -> None:
        result = self.select(chart_map([11]))

        self.assertTrue(result["eligible"])
        candidate = next(item for item in result["candidates"] if item["channelId"] == "ch-11-56")
        self.assertEqual(candidate["activeGateNumber"], 11)
        self.assertEqual(candidate["complementaryGateNumber"], 56)
        self.assertEqual(candidate["complementaryGateTitle"], "Stimulation")
        self.assertIn("story", candidate["aiAffordance"])
        self.assertIn("short, user-paced story", candidate["examplePrompt"])
        self.assertIn("not gate activation", candidate["framing"])

    def test_disabled_chart_aware_mode_returns_no_candidates(self) -> None:
        result = self.select(chart_map([11]), enabled=False)

        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "chart_aware_mode_not_enabled")
        self.assertEqual(result["candidates"], [])

    def test_partial_chart_returns_no_candidates(self) -> None:
        result = self.select(chart_map([11], status="partial"))

        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "chart_is_not_fully_calculated")
        self.assertEqual(result["candidates"], [])

    def test_transit_map_returns_no_candidates(self) -> None:
        result = self.select(chart_map([11], scope="transit"))

        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "natal_chart_map_required")
        self.assertEqual(result["candidates"], [])

    def test_channel_with_both_gates_active_has_no_complement_candidate(self) -> None:
        result = self.select(chart_map([11, 56]))

        self.assertTrue(result["eligible"])
        self.assertFalse(any(item["channelId"] == "ch-11-56" for item in result["candidates"]))

    def authorized_inputs(self, *, selected: bool = True, subject: str = "synthetic-subject") -> tuple[dict, dict, list]:
        chart = chart_map([11])
        chart.update({
            "recordType": "symbolic_map", "domain": "symbolic", "schemaVersion": "0.1",
            "createdAt": "2026-10-20T12:00:00Z",
            "calculation": {
                **chart["calculation"], "method": "synthetic fixture", "methodVersion": "1",
                "calculatedAt": "2026-10-20T12:00:00Z", "inputRecordIds": ["synthetic-birth"],
                "featureRecordIds": ["synthetic-feature"], "limitations": ["Synthetic fixture only."],
                "engine": {"name": "synthetic fixture engine", "version": "1"},
                "executionMode": "local",
                "verificationStatus": "asserted_not_independently_verified",
                "inputPrecision": {"birthDate": "exact", "birthTime": "exact"},
                "timeZoneDatabase": {"source": "unresolved", "version": "not applicable"},
            },
        })
        reading = {
            "id": "synthetic-reading", "subjectId": subject, "version": "0.1",
            "purpose": "personal_reflection", "question": "Explore a symbolic prompt.",
            "timeWindow": {"start": "2026-10-20T00:00:00Z", "end": "2026-10-21T00:00:00Z", "precision": "exact"},
            "inputIds": [chart["id"]] if selected else [], "claims": [], "generatedAt": "2026-10-20T12:00:00Z",
        }
        grant = {
            "id": "synthetic-grant", "subjectId": "synthetic-subject",
            "grantor": {"reference": "synthetic-subject", "role": "subject"},
            "domains": ["symbolic"], "purposes": ["personal_reflection"],
            "permittedActions": ["analyze"], "recordIds": [chart["id"]], "status": "granted",
            "consentTextVersion": "synthetic/1", "createdAt": "2026-01-01T00:00:00Z",
            "expiresAt": "2027-01-01T00:00:00Z",
        }
        return reading, chart, [grant]

    def authorized_select(self, reading: dict, chart: dict, grants: list, *, remote: bool = False) -> dict:
        return select_authorized_complementary_gate_affordances(
            reading, chart, TOPOLOGY, AFFORDANCES, grants,
            chart_aware_enabled=True, remote_processing=remote,
        )

    def test_authorized_wrapper_requires_selected_map_and_same_subject(self) -> None:
        reading, chart, grants = self.authorized_inputs(selected=False)
        self.assertEqual(self.authorized_select(reading, chart, grants)["reason"], "symbolic_map_not_selected")
        reading, chart, grants = self.authorized_inputs(subject="another-subject")
        self.assertEqual(self.authorized_select(reading, chart, grants)["reason"], "symbolic_map_subject_mismatch")

    def test_authorized_wrapper_requires_explicit_analysis_consent(self) -> None:
        reading, chart, _ = self.authorized_inputs()
        result = self.authorized_select(reading, chart, [])
        self.assertEqual(result["reason"], "symbolic_map_analysis_not_authorized")
        self.assertEqual(result["candidates"], [])

    def test_authorized_wrapper_requires_remote_processing_scope(self) -> None:
        reading, chart, grants = self.authorized_inputs()
        result = self.authorized_select(reading, chart, grants, remote=True)
        self.assertEqual(result["reason"], "remote_processing_not_authorized")
        self.assertEqual(result["candidates"], [])

    def test_authorized_wrapper_emits_minimal_audit_with_candidate(self) -> None:
        reading, chart, grants = self.authorized_inputs()
        result = self.authorized_select(reading, chart, grants)
        self.assertTrue(result["eligible"])
        self.assertEqual(result["audit"]["symbolicMapId"], chart["id"])
        self.assertNotIn("birthDate", result["audit"])
        context = result["aiContext"]
        self.assertEqual(context["contextType"], "optional_symbolic_chart_context")
        self.assertEqual(context["chartProvenance"]["kind"], "calculated_natal_map")
        self.assertEqual(context["chartProvenance"]["chartBinding"], "selected_subject_map")
        self.assertEqual(context["activatedGateNumbers"], [11])
        self.assertIn("few varied questions", context["activatedGates"][0]["examplePrompt"])
        self.assertEqual(context["definedChannelIds"], [])
        self.assertNotIn("subjectId", context)
        self.assertIn("Never infer biology", " ".join(context["assistantGuidance"]))
        guidance = " ".join(context["assistantGuidance"])
        self.assertIn("complete activated-gate set for each chart-aware request", guidance)
        self.assertIn("use a relevant activity to shape the help itself", guidance)
        self.assertIn("choose the most relevant active-gate activity", guidance)
        self.assertIn("Answer the user's stated question or goal first", guidance)
        self.assertIn("only to that subject's reflection", guidance)
        self.assertIn("proactively offer at most one", guidance)
        self.assertIn("Distinguish a complementary activity from the already activated gates", guidance)
        self.assertIn("easy to skip", guidance)

    def test_ai_context_includes_every_activated_gate_and_defined_channel(self) -> None:
        reading, chart, grants = self.authorized_inputs()
        chart["calculation"]["bodygraph"]["activatedGateNumbers"] = [1, 8, 11, 56]
        result = self.authorized_select(reading, chart, grants)
        self.assertTrue(result["eligible"], result)
        context = result["aiContext"]
        self.assertEqual(context["activatedGateNumbers"], [1, 8, 11, 56])
        self.assertEqual(context["definedChannelIds"], ["ch-1-8", "ch-11-56"])
        self.assertEqual(context["definedCenterIds"], ["ajna", "g_identity", "throat"])


if __name__ == "__main__":
    unittest.main()
