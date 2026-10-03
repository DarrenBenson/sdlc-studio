"""BG0924: the Minutes actual's reason names the pair that is missing.

Under BG0898's like-for-like rule the Minutes actual sums the measured minutes of the units that
also carry a forecast. When units carry measured minutes but none carries a forecast, the actual
is NOT MEASURED and its reason read "no unit carries a measured time" - false, since units do.
It now says no unit carries both a forecast and a measured time; a run with no measured minutes
still reads that no unit carries a measured time.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_report as lean  # noqa: E402 - the report fixture, shared

sr = lean.sr

PAIR = "no unit carries both a forecast and a measured time"
NONE = "no unit carries a measured time"
LIVE = ("US0001", "US0002", "US0004", "US0005")


class MinutesReasonTrueTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean.lean_run(self.root)

    def _set(self, forecast: dict, measured: dict) -> None:
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        for uid in LIVE:
            state["plan_snapshot"]["units"][uid]["forecast_minutes"] = forecast.get(uid)
            actual = state["unit_actuals"].setdefault(uid, {})
            actual["minutes"] = measured.get(uid)
            actual.pop("spans", None)
        state.pop(sr.run_state.DELEGATED, None)
        path.write_text(json.dumps(state), encoding="utf-8")

    def _minutes(self) -> dict:
        rep = sr.build_report(self.root, lean.RETRO)
        rows = {r["est_measure"]["value"]: r for r in lean._sections(rep)["estimates"]["rows"]}
        return rows["Minutes"]["est_actual"]

    def test_the_reason_names_the_missing_pair(self) -> None:
        """AC1. MUTANT: HEAD's single reason, which says no unit carries a measured time while
        US0001 and US0002 carry 70 and 30 measured minutes. The second case is the control the
        criterion names: with no measured minutes at all the old reason still stands, so a
        mutant that always names the pair is caught."""
        self._set(forecast={}, measured={"US0001": 70.0, "US0002": 30.0})
        actual = self._minutes()
        self.assertEqual(sr.NOT_MEASURED, actual["value"], actual)
        self.assertIn(PAIR, actual.get("reason", ""), actual)
        self.assertNotIn(NONE, actual.get("reason", ""), actual)

        self._set(forecast={"US0001": 40.0, "US0002": 30.0}, measured={})
        actual = self._minutes()
        self.assertEqual(sr.NOT_MEASURED, actual["value"], actual)
        self.assertIn(NONE, actual.get("reason", ""), actual)
        self.assertNotIn(PAIR, actual.get("reason", ""), actual)

    def test_a_unit_with_both_shows_a_figure(self) -> None:
        """Control. MUTANT: a reason chosen on measured minutes alone that also blanks the
        figure - US0001 carries both, so the actual is its 70 measured minutes."""
        self._set(forecast={"US0001": 40.0}, measured={"US0001": 70.0, "US0002": 30.0})
        actual = self._minutes()
        self.assertEqual(70.0, actual["value"], actual)


if __name__ == "__main__":
    unittest.main()
