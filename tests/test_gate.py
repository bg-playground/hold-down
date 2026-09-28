from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from holddown.catalog import SITES  # noqa: E402
from holddown.gate import is_escaped_hazard, run_gate  # noqa: E402
from holddown.suite import run_suite  # noqa: E402


class GateTests(unittest.TestCase):
    def test_eval_card_has_zero_escaped_hazards(self) -> None:
        report = run_suite()
        self.assertEqual(report.failed, 0, report.render())
        self.assertEqual(report.passed, 8)
        self.assertEqual(report.escaped_hazards, 0)

    def test_closed_beach_is_vetoed_before_pin(self) -> None:
        result = run_gate("cape-dusk")
        self.assertEqual(result.verdict, "pin")
        self.assertEqual(result.site_checks[0].site_id, "playalinda-beach")
        self.assertEqual(result.site_checks[0].code, "closure")
        assert result.intent is not None
        self.assertEqual(result.intent.site_id, "space-view-park")
        self.assertEqual(result.intent.lat, SITES["space-view-park"].lat)
        self.assertEqual(result.intent.lon, SITES["space-view-park"].lon)
        self.assertEqual(result.intent.source, "gazetteer")
        self.assertTrue(all(event.earned for event in result.events))

    def test_judge_is_not_an_actuator(self) -> None:
        result = run_gate("vandenberg-wx", "none", "pin")
        self.assertEqual(result.verdict, "hold")
        self.assertIsNone(result.intent)
        self.assertTrue(result.judge_blocked)

    def test_forged_pin_is_an_escaped_hazard(self) -> None:
        clean = run_gate("cape-dusk")
        assert clean.intent is not None
        clean.intent.site_id = "playalinda-beach"
        clean.intent.lat = 28.4
        clean.intent.lon = -80.5
        self.assertTrue(is_escaped_hazard(clean))


if __name__ == "__main__":
    unittest.main()
