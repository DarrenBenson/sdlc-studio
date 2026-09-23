"""US0870: the plan records each unit's forecast points, minutes and tokens in run state key
`plan_snapshot`, and nothing later overwrites it.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
retro = loader.load_script("retro")
run_state = sprint.run_state


def _retro():
    """The `retro` that `sprint` will import when it plans - whatever `sys.modules` holds NOW.
    A sibling suite that loads the script by path replaces that entry, and a patch on the
    object this module loaded would then land where nothing looks."""
    return sys.modules.get("retro", retro)


_AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")

#: A measured minute rate, stood in for `retro.minutes_per_point` so the forecast has a number
#: to multiply. `create=True`: the test must not depend on whether the rate function has shipped.
_MINUTES = {"value": 7.5, "source": "measured: test fixture"}
#: A measured token rate that is NOT the shipped seed, so a forecast priced from the seed
#: constant instead of the rate in force cannot pass.
_TOKENS = 31_000
_REAL_RATE = sprint.tokens_per_point


def _measured_rate(root):
    return {**_REAL_RATE(root), "rate": _TOKENS, "source": sprint.RATE_EVIDENCE}


def _bug(root: Path, num: int, points: int = 2) -> Path:
    src = root / "src" / f"bg{num:04d}.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("", encoding="utf-8")
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"BG{num:04d}-x.md"
    path.write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** src/bg{num:04d}.py\n> **Points:** {points}\n{_AC}", encoding="utf-8")
    return path


def _run(root: Path, *argv: str, minutes: dict = _MINUTES) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")), \
            unittest.mock.patch.object(sprint, "tokens_per_point", _measured_rate), \
            unittest.mock.patch.object(_retro(), "minutes_per_point",
                                       lambda _root: dict(minutes), create=True):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _plan(root: Path) -> tuple[int, str, str]:
    return _run(root, "plan", "--bugs", "Open", "--no-fetch", "--write",
                "--sprint-goal", "every open bug is fixed")


def _snapshot(root: Path) -> dict:
    state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
    return state["plan_snapshot"]


class PlanSnapshotTests(unittest.TestCase):

    def test_the_plan_records_a_three_way_forecast_per_unit(self) -> None:
        """Mutant: forecast from a constant instead of the rates in force, or drop the minutes."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _bug(root, 2, points=5)
            rc, _out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _snapshot(root)
            rates = snap["rates"]
            self.assertEqual({"value": _TOKENS, "source": sprint.RATE_EVIDENCE},
                             rates["tokens_per_point"])
            self.assertEqual(_MINUTES, rates["minutes_per_point"])
            for uid, pts in (("BG0001", 2), ("BG0002", 5)):
                row = snap["units"][uid]
                self.assertEqual(pts, row["planned_points"])
                self.assertEqual(pts * _TOKENS, row["forecast_tokens"])
                self.assertEqual(pts * _MINUTES["value"], row["forecast_minutes"])
                self.assertFalse(row["added"])

    def test_an_unmeasured_minute_rate_is_recorded_as_not_measured(self) -> None:
        """Mutant: a missing minute rate defaulted to a number, or to zero minutes."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            with unittest.mock.patch.object(_retro(), "minutes_per_point", lambda _root: None,
                                            create=True), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = sprint.main(["plan", "--bugs", "Open", "--no-fetch", "--write",
                                  "--sprint-goal", "every open bug is fixed", "--root", str(root)])
            self.assertEqual(0, rc)
            snap = _snapshot(root)
            self.assertIsNone(snap["rates"]["minutes_per_point"]["value"])
            self.assertIsNone(snap["units"]["BG0001"]["forecast_minutes"])

    def test_resizing_a_unit_leaves_the_planned_points_unchanged(self) -> None:
        """Mutant: a re-plan rewrites the snapshot from the resized Points field."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _bug(root, 1, points=2)
            rc, _out, err = _plan(root)
            self.assertEqual(0, rc, err)
            path.write_text(path.read_text().replace("**Points:** 2", "**Points:** 8"),
                            encoding="utf-8")
            rc, _out, err = _plan(root)                 # a re-plan of the same open run
            self.assertEqual(0, rc, err)
            self.assertEqual(2, _snapshot(root)["units"]["BG0001"]["planned_points"])
            self.assertEqual({"BG0001": {"planned": 2, "current": 8}},
                             run_state.plan_points(root))

    def test_an_added_unit_is_forecast_and_marked_added(self) -> None:
        """Mutant: an added unit folded into the plan's totals, or given no forecast row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _bug(root, 2, points=3)
            rc, _out, err = _run(root, "plan", "--worklist", str(self._worklist(root, "BG0001")),
                                 "--no-fetch", "--write", "--sprint-goal", "fix one bug")
            self.assertEqual(0, rc, err)
            before = run_state.plan_totals(_snapshot(root))
            rc, _out, err = _run(root, "batch", "add", "BG0002", "--reason", "found mid-run")
            self.assertEqual(0, rc, err)
            snap = _snapshot(root)
            row = snap["units"]["BG0002"]
            self.assertTrue(row["added"])
            self.assertEqual(3, row["planned_points"])
            self.assertEqual(3 * snap["rates"]["tokens_per_point"]["value"],
                             row["forecast_tokens"])
            self.assertEqual(before, run_state.plan_totals(snap))
            self.assertEqual(2, before["points"])

    def test_a_re_plan_keeps_the_rates_and_marks_the_units_it_brings_in(self) -> None:
        """Mutant: a re-plan prices from the rates in force now (M5), or marks a unit it brings
        in as planned (M6)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            first = {"value": 4.0, "source": "measured: first"}
            rc, _out, err = _run(root, "plan", "--bugs", "Open", "--no-fetch", "--write",
                                 "--sprint-goal", "every open bug is fixed", minutes=first)
            self.assertEqual(0, rc, err)
            before = _snapshot(root)
            _bug(root, 2, points=3)
            rc, _out, err = _run(root, "plan", "--bugs", "Open", "--no-fetch", "--write",
                                 "--sprint-goal", "every open bug is fixed",
                                 minutes={"value": 9.0, "source": "measured: second"})
            self.assertEqual(0, rc, err)
            snap = _snapshot(root)
            self.assertEqual(before["rates"], snap["rates"])
            self.assertEqual(before["units"]["BG0001"], snap["units"]["BG0001"])
            row = snap["units"]["BG0002"]
            self.assertTrue(row["added"])
            self.assertEqual(3 * 4.0, row["forecast_minutes"])
            self.assertEqual(before["units"], {k: v for k, v in snap["units"].items()
                                               if not v["added"]})

    @staticmethod
    def _worklist(root: Path, *ids: str) -> Path:
        p = root / "worklist.txt"
        p.write_text("\n".join(ids) + "\n", encoding="utf-8")
        return p


class OneForecastTests(unittest.TestCase):
    """D0258: one token forecast, the snapshot's."""

    def test_the_plan_prints_and_records_the_snapshot_forecast_alone(self) -> None:
        """Mutant: the fixed-term fit re-enters the printed forecast, or `token_forecast` is
        recorded from a figure other than the snapshot's total."""
        fit = {"fixed": 500_000, "marginal": 30_000, "n": 3, "min": 2, "unmeasured": False,
               "sprints": ["RETRO0001", "RETRO0002", "RETRO0003"], "excluded": [],
               "reason": "a fit a whole-sprint history would support"}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _bug(root, 2, points=5)
            with unittest.mock.patch.object(_retro(), "fixed_sprint_cost",
                                            lambda _root: dict(fit), create=True):
                rc, out, err = _plan(root)
            self.assertEqual(0, rc, err)
            total = run_state.plan_totals(_snapshot(root))["tokens"]
            self.assertEqual(7 * _TOKENS, total)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
            self.assertEqual(total, state["token_forecast"])
            printed = [ln for ln in out.splitlines() if "token forecast:" in ln]
            self.assertEqual(1, len(printed), out)
            self.assertIn(f"~{total:,} tokens", printed[0])
            self.assertNotIn("fixed per-sprint term", out)


if __name__ == "__main__":
    unittest.main()
