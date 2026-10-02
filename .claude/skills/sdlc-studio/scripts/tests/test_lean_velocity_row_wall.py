"""BG0907: the close records the run's active minutes on the velocity row, so the minutes rate
measures on the run's own model.

`retro.minutes_per_point` reads each VELOCITY row's Wall (s), and only a runner-measured row
(Measured equals Units) carried one: rows the close recorded from RETRO0121 onward carry none, so
even rows naming claude-opus-5-5 left the minutes rate on the fallback, the July RETRO0028 row
of another model. The close now records the run's measured active time - each delivered unit's
agent minutes, else its closed span - as the row's Wall (s) when every delivered unit carries
one, and that whole-sprint row counts toward the rate.

Drives `retro.main` as the close's tail runs it, on the workspace of
`test_lean_velocity_row_model`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_velocity_row_model as rowmodel  # noqa: E402 - the close's velocity fixture

MODEL, OTHER, _live = rowmodel.MODEL, rowmodel.OTHER, rowmodel._live


class VelocityRowWallTests(unittest.TestCase):
    _fixture = rowmodel.VelocityRowModelTests      # its workspace, its runs and its close
    setUp = _fixture.setUp
    _transcript, _run, _close, _row = (_fixture._transcript, _fixture._run, _fixture._close,
                                       _fixture._row)

    def _span(self, n: int, minutes: float | None) -> None:
        """Give RUN-n's one unit a closed span of `minutes` (None: no span at all)."""
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        if minutes is not None:
            state["unit_actuals"] = {f"US010{n}": {"started_at": f"2026-10-0{n}T09:05:00Z",
                                                   "start_tokens": 0, "minutes": minutes,
                                                   "tokens": 1000, "open": False}}
        path.write_text(json.dumps(state), encoding="utf-8")

    def test_the_minutes_rate_measures_on_recent_named_rows(self) -> None:
        """AC1. MUTANT: HEAD, whose close-recorded rows carry no Wall (s), so the minutes rate
        falls back to the July row of another model (`fallback: 0 row(s) for
        claude-opus-5-5`). The control: a run whose delivered unit carries no measured time
        records no Wall (s), so a partial time is never divided by every point."""
        retro = _live("retro")
        retro.record_velocity(self.root, {     # the July row of another model, as RETRO0028
            "id": "RETRO0009", "date": "2026-07-15", "n_units": 3, "n_measured": 3,
            "n_forecast": 3, "models": [OTHER], "constants": None, "sample": "-",
            "batch": {"delivered_points": 10, "actual_tokens": 564_066, "ratio": None,
                      "wall_time_s": 3840}})
        self.assertTrue(retro.minutes_per_point(self.root, model=MODEL)["source"]
                        .startswith("fallback"), "premise: the July row is the fallback")
        for n, minutes in ((1, 12.0), (2, 9.0), (3, 15.0)):     # 3-point units: 4, 3, 5 per pt
            rid = self._run(n)
            self._span(n, minutes)
            self._close(rid)
            self.assertEqual(MODEL, self._row(rid)["model"])
        rate = retro.minutes_per_point(self.root)
        self.assertEqual(4.0, rate["value"])
        self.assertEqual(f"measured on {MODEL}: median of RETRO0001, RETRO0002, RETRO0003",
                         rate["source"])
        rid = self._run(4)
        self._span(4, None)                                 # delivered, never measured
        self._close(rid)
        self.assertIsNone(self._row(rid)["wall_time_s"])


if __name__ == "__main__":
    unittest.main()
