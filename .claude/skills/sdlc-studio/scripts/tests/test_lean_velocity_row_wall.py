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

    def test_a_run_with_one_unmeasured_unit_records_no_wall(self) -> None:
        """BG0907 round 1. MUTANT: `return None` -> `continue` in `_run_active_seconds` for a
        unit with no time, which writes the measured unit's 720 s as the Wall of a run whose
        other delivered unit was never measured. The control: both units timed, 12 + 9 min."""
        rid = self._run(5)
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        (self.root / "sdlc-studio" / "stories" / "US0206-x.md").write_text(
            "# US0206: x\n\n> **Status:** Done\n> **Points:** 3\n", encoding="utf-8")
        retro_md = next((self.root / "sdlc-studio" / "retros").glob(f"{rid}-*.md"))
        retro_md.write_text(retro_md.read_text(encoding="utf-8")
                            .replace("> **Batch:** US0105", "> **Batch:** US0105, US0206"),
                            encoding="utf-8")
        span = {"started_at": "2026-10-05T09:05:00Z", "start_tokens": 0, "tokens": 1000,
                "open": False}
        for actuals, wall in (({"US0105": {**span, "minutes": 12.0}}, None),
                              ({"US0105": {**span, "minutes": 12.0},
                                "US0206": {**span, "minutes": 9.0}}, 1260)):
            state = json.loads(path.read_text(encoding="utf-8"))
            state.update(batch=["US0105", "US0206"], unit_actuals=actuals)
            path.write_text(json.dumps(state), encoding="utf-8")
            self._close(rid)
            row = self._row(rid)
            self.assertEqual((2, 6), (row["units"], row["points"]), "premise: two units")
            self.assertEqual(wall, row["wall_time_s"], sorted(actuals))

    def test_the_capacity_floor_reads_no_whole_sprint_wall(self) -> None:
        """BG0907 round 1, the regression. MUTANT: the base floor, which sums every row's
        Wall (s) over the summed Measured, so the three close rows' 2,160 s (Measured 0) enter
        with no unit and lift the floor from 21.3 to 33.3 min/unit. The control: a runner row
        (Measured 3, 3,840 s) still sets it."""
        sprint, retro = _live("sprint"), _live("retro")
        retro.record_velocity(self.root, {     # a runner row: three measured units
            "id": "RETRO0009", "date": "2026-07-15", "n_units": 3, "n_measured": 3,
            "n_forecast": 3, "models": [OTHER], "constants": None, "sample": "-",
            "batch": {"delivered_points": 10, "actual_tokens": 564_066, "ratio": None,
                      "wall_time_s": 3840}})
        self.assertEqual(21.3, sprint._unit_wall_minutes(sprint._velocity_rows(self.root)))
        for n, minutes in ((1, 12.0), (2, 9.0), (3, 15.0)):
            rid = self._run(n)
            self._span(n, minutes)
            self._close(rid)
            self.assertEqual((0, minutes * 60), (self._row(rid)["measured"],
                                                 self._row(rid)["wall_time_s"]), "premise")
        self.assertEqual(21.3, sprint._unit_wall_minutes(sprint._velocity_rows(self.root)))


if __name__ == "__main__":
    unittest.main()
