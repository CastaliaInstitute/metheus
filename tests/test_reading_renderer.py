"""Keep symbolic and lived phase provenance distinct in rendered readings."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from metheus.rendering import render_assembled_reading_html


ROOT = Path(__file__).resolve().parents[1]


class ReadingRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = json.loads((ROOT / "examples/assembled-reading.example.json").read_text())

    def test_epimethean_phase_with_a_source_system_stays_labeled_as_lived_context(self) -> None:
        package = copy.deepcopy(self.package)
        phase = package["claims"][0]["phaseAnnotations"][0]
        phase["sourceSystem"] = {"name": "Cycle diary", "version": "2"}

        document = render_assembled_reading_html(package)

        self.assertIn("Epimethean lived context", document)
        self.assertIn("Source system: Cycle diary · 2", document)
        self.assertNotIn("Symbolic source: Cycle diary", document)
        self.assertIn("reported", document)
        self.assertIn("descriptive", document)

    def test_promethean_phase_source_is_explicitly_symbolic(self) -> None:
        package = copy.deepcopy(self.package)
        package["claims"][0]["phaseAnnotations"][0].update({
            "layer": "promethean",
            "phaseSystem": "human_design_transit",
            "canonicalPhase": "separating_contact",
            "basis": "derived",
            "interpretation": "symbolic",
            "sourceSystem": {"name": "Human Design", "version": "test-v1"},
        })

        document = render_assembled_reading_html(package)

        self.assertIn("Promethean symbolic context", document)
        self.assertIn("Symbolic source: Human Design · test-v1", document)


if __name__ == "__main__":
    unittest.main()
