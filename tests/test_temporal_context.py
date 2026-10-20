"""Keep symbolic and lived phase provenance visible in temporal comparisons."""

from __future__ import annotations

import unittest

from metheus.temporal import describe_phase_observation_relations


SUBJECT = "synthetic-subject"


def observation(record_id: str) -> dict:
    return {
        "id": record_id,
        "subjectId": SUBJECT,
        "recordType": "observation",
        "schemaVersion": "0.1",
        "domain": "physiology",
        "epistemicClass": "measured",
        "source": {"kind": "sensor", "name": "synthetic test fixture"},
        "label": "Synthetic measurement",
        "value": {"number": 1, "unit": "arbitrary"},
        "measurementDetails": {"analyteOrSignal": "synthetic signal"},
        "time": {
            "observedAt": "2026-04-05T12:00:00Z",
            "precision": "exact",
        },
    }


def phase(record_id: str, *, layer: str, phase_system: str, start: str, end: str) -> dict:
    is_symbolic = layer == "promethean"
    return {
        "id": record_id,
        "subjectId": SUBJECT,
        "recordType": "phase_annotation",
        "schemaVersion": "0.1",
        "layer": layer,
        "phaseSystem": phase_system,
        "canonicalPhase": "exact_contact" if is_symbolic else "bleeding_interval",
        "window": {"kind": "interval", "start": start, "end": end},
        "basis": "derived" if is_symbolic else "reported",
        "interpretation": "symbolic" if is_symbolic else "descriptive",
        **({"sourceSystem": {"name": "Human Design", "version": "fixture-v1"}, "methodVersion": "fixture-v1"} if is_symbolic else {}),
        "basisRecordIds": ["synthetic-source"],
        "method": "synthetic fixture",
        "uncertainty": "synthetic only",
        "limitations": ["Synthetic test fixture."],
    }


class TemporalContextTests(unittest.TestCase):
    def relate(self, phase_record: dict) -> dict:
        source = observation("synthetic-observation")
        return describe_phase_observation_relations(
            [source],
            subject_id=SUBJECT,
            observation_record_ids=[source["id"]],
            phase_annotation_ids=[phase_record["id"]],
            phase_annotations=[phase_record],
        )[0]

    def test_lived_phase_and_measurement_keep_distinct_context(self) -> None:
        relation = self.relate(phase(
            "reported-cycle-window",
            layer="epimethean",
            phase_system="menstrual_cycle",
            start="2026-04-01T00:00:00Z",
            end="2026-04-10T00:00:00Z",
        ))

        self.assertEqual(relation["relationType"], "temporal_order")
        self.assertEqual(relation["temporalRelation"], "overlaps")
        self.assertEqual(relation["leftContext"]["epistemicClass"], "measured")
        self.assertEqual(relation["rightContext"]["layer"], "epimethean")
        self.assertEqual(relation["rightContext"]["phaseSystem"], "menstrual_cycle")
        self.assertIn("does not establish biological mechanism", " ".join(relation["limitations"]))

    def test_symbolic_transit_remains_promethean_and_symbolic(self) -> None:
        relation = self.relate(phase(
            "symbolic-transit-window",
            layer="promethean",
            phase_system="human_design_transit",
            start="2026-04-01T00:00:00Z",
            end="2026-04-10T00:00:00Z",
        ))

        self.assertEqual(relation["rightContext"]["layer"], "promethean")
        self.assertEqual(relation["rightContext"]["interpretation"], "symbolic")
        self.assertEqual(relation["rightContext"]["phaseSystem"], "human_design_transit")
        self.assertNotIn("hormone", " ".join(relation["limitations"]).lower())


if __name__ == "__main__":
    unittest.main()
