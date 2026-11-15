"""US1150: the plan records a priced, a dollar and a wall-clock forecast beside its tokens and
minutes, each its points times a rate measured from this project's own record, and names every
row it cannot forecast.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import statistics
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
prices = run_state.prices


def _retro():
    """The `retro` that `sprint` imports when it plans (whatever `sys.modules` holds now)."""
    return sys.modules.get("retro", retro)


_AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")
_MINUTES = {"value": 7.5, "source": "measured: test fixture"}
_TOKENS = 31_000
_REAL_RATE = sprint.tokens_per_point
_HEADER = ("| Retro | Date | Units | Measured | Forecast | Points | Actual (tokens) | Model | Source "
           "| Priced/pt |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
#: Five priced runs: median 1,000,000, mean 1,360,000, so a mean cannot pass for the median.
_PRICED = {"RETRO0001": "800,000", "RETRO0002": "3,000,000", "RETRO0003": "900,000",
           "RETRO0004": "1,000,000", "RETRO0005": "1,100,000"}
#: Three signed runs, points per elapsed hour 5.0, 6.0 and 2.0: median 5.0, mean 4.33.
_SIGNED = {"RPT0001": (20, "4.0h"), "RPT0002": (30, "5.0h"), "RPT0003": (10, "5.0h")}
_MODEL = "claude-fixture-1"
#: A configured price whose date is not the table's newest, so the two dates tell apart.
_CONFIG = (f"pricing:\n  models:\n    {_MODEL}:\n      input: 7.0\n      output: 35.0\n"
           f"      cache_read: 0.7\n      cache_write_5m: 8.75\n      cache_write_1h: 14.0\n"
           f"      effective: 2020-01-02\n      source: the test fixture\n")


def _measured_rate(root):
    return {**_REAL_RATE(root), "rate": _TOKENS, "source": sprint.RATE_EVIDENCE}


def _bug(root: Path, num: int, points: int = 2) -> None:
    src = root / "src" / f"bg{num:04d}.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("", encoding="utf-8")
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** src/bg{num:04d}.py\n> **Points:** {points}\n{_AC}", encoding="utf-8")


def _velocity(root: Path, priced: dict, model: str = _MODEL) -> None:
    path = root / "sdlc-studio" / "retros" / "VELOCITY.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(f"| {rid} | 2026-10-0{i + 1} | 3 | 0 | 3 | 6 | 600,000 | {model} | harness "
                   f"| {pp} |\n" for i, (rid, pp) in enumerate(priced.items()))
    path.write_text("# Velocity\n\n" + _HEADER + rows, encoding="utf-8")


def _report(root: Path, rid: str, points: int, hours: str, signed: bool = True) -> None:
    d = root / "sdlc-studio" / "reports"
    d.mkdir(parents=True, exist_ok=True)
    page = {"report_id": rid, "sections": [
        {"key": "goal", "figures": {"duration_hours": {"key": "duration_hours", "value": hours}}},
        {"key": "estimates", "rows": [
            {"est_measure": {"key": "est_measure", "value": "Points"},
             "est_actual": {"key": "est_actual", "value": points}}]}]}
    if signed:
        page["signature"] = {"principal": "operator", "signed_at": "2026-11-01T00:00:00Z"}
    (d / f"{rid}.json").write_text(json.dumps(page), encoding="utf-8")


def _run(root: Path, *argv: str, minutes=_MINUTES) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")), \
            unittest.mock.patch.object(sprint, "tokens_per_point", _measured_rate), \
            unittest.mock.patch.object(_retro(), "minutes_per_point",
                                       lambda _root: minutes, create=True):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _plan(root: Path, write: bool = True, **kw) -> tuple[int, str, str]:
    return _run(root, "plan", "--bugs", "Open", "--no-fetch",
                *(["--write"] if write else []), "--sprint-goal", "every open bug is fixed", **kw)


def _state(root: Path) -> dict:
    path = root / "sdlc-studio" / ".local" / "run-state.json"
    return json.loads(path.read_text()) if path.is_file() else {}


class PlanPricedRateTests(unittest.TestCase):

    def test_plan_write_records_priced_rate_with_source(self) -> None:
        """Mutants: a mean for the rolling median; the rate without its source or runs; a
        preview that writes the snapshot; unit rows carrying only tokens and minutes."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _bug(root, 2, points=3)
            _velocity(root, _PRICED)
            rc, _out, err = _plan(root, write=False)
            self.assertEqual(0, rc, err)
            self.assertNotIn("plan_snapshot", _state(root), "a preview wrote the snapshot")
            rc, _out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _state(root)["plan_snapshot"]
            rate = snap["rates"]["priced_per_point"]
            self.assertEqual(1_000_000, rate["value"])
            self.assertNotEqual(statistics.mean([800_000, 3_000_000, 900_000, 1_000_000,
                                                 1_100_000]), rate["value"])
            self.assertEqual(sorted(_PRICED), rate["retros"])
            for rid in _PRICED:
                self.assertIn(rid, rate["source"])
            for uid, pts in (("BG0001", 2), ("BG0002", 3)):
                self.assertEqual(pts * 1_000_000, snap["units"][uid]["forecast_priced"])

    def test_fewer_than_three_priced_runs_record_no_rate(self) -> None:
        """Mutant: two runs' median taken as the rate, or an unmeasured rate read as 0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _velocity(root, {"RETRO0001": "800,000", "RETRO0002": "900,000"})
            rc, _out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _state(root)["plan_snapshot"]
            self.assertIsNone(snap["rates"]["priced_per_point"]["value"])
            self.assertIn("2 priced run(s)", snap["rates"]["priced_per_point"]["source"])
            self.assertIsNone(snap["units"]["BG0001"]["forecast_priced"])


class PlanDollarForecastTests(unittest.TestCase):

    def test_dollar_forecast_names_model_and_effective_date(self) -> None:
        """Mutants: a hard-coded price; the effective date dropped; the entry's date given as
        the table's; a model the table does not list priced as $0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _velocity(root, _PRICED)
            (root / "sdlc-studio" / ".config.yaml").write_text(_CONFIG, encoding="utf-8")
            table = prices.load(root)
            rc, _out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _state(root)["plan_snapshot"]
            rate = snap["rates"]["usd_per_million"]
            self.assertEqual(7.0, rate["value"])
            self.assertEqual(_MODEL, rate["model"])
            self.assertEqual(table.newest_effective.isoformat(), rate["effective"])
            self.assertEqual("2020-01-02", rate["price_effective"])
            self.assertIn(rate["effective"], rate["source"])
            self.assertAlmostEqual(2_000_000 * 7.0 / 1_000_000,
                                   snap["units"]["BG0001"]["forecast_usd"])

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            _velocity(root, _PRICED, model="claude-absent-9")
            rc, out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _state(root)["plan_snapshot"]
            self.assertIsNone(snap["rates"]["usd_per_million"]["value"])
            self.assertIn("claude-absent-9", snap["rates"]["usd_per_million"]["source"])
            self.assertIsNone(snap["units"]["BG0001"]["forecast_usd"])
            self.assertEqual(2_000_000, snap["units"]["BG0001"]["forecast_priced"])
            self.assertRegex(out, r"Dollar cost: not forecast: \S.*claude-absent-9")


class PlanWallClockForecastTests(unittest.TestCase):

    def test_wall_clock_forecast_is_separate_from_active_minutes(self) -> None:
        """Mutants: the span written into `forecast_minutes`, derived from minutes per point, a
        mean for the median, or an unsigned page counted."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, points=2)
            for rid, (pts, hours) in _SIGNED.items():
                _report(root, rid, pts, hours)
            _report(root, "RPT0004", 100, "1.0h", signed=False)
            rc, out, err = _plan(root)
            self.assertEqual(0, rc, err)
            snap = _state(root)["plan_snapshot"]
            rate = snap["rates"]["points_per_elapsed_hour"]
            self.assertEqual(5.0, rate["value"])
            self.assertEqual(sorted(_SIGNED), rate["reports"])
            self.assertNotIn("RPT0004", rate["source"])
            row = snap["units"]["BG0001"]
            self.assertEqual(24.0, row["forecast_span_minutes"])
            self.assertEqual(2 * _MINUTES["value"], row["forecast_minutes"])
            self.assertEqual(24.0, run_state.plan_totals(snap)["span_minutes"])
            self.assertEqual(15.0, run_state.plan_totals(snap)["minutes"])
            self.assertIn("Wall-clock span: ~24.0 minutes", out)


class PlanUnforecastRowTests(unittest.TestCase):

    def test_plan_names_each_row_it_cannot_forecast(self) -> None:
        """Mutants: a bare 'not forecast'; a refusal or non-zero exit on a missing rate; a row
        silently left out of the plan's output."""
        rows = ("Minutes", "Wall-clock span", "Priced cost", "Dollar cost")
        for write in (False, True):
            with self.subTest(write=write), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _bug(root, 1)
                rc, out, err = _plan(root, write=write, minutes=None)
                self.assertEqual(0, rc, err)
                lines = [ln.strip() for ln in out.splitlines() if "not forecast:" in ln]
                self.assertEqual(len(rows), len(lines), out)
                for measure, line in zip(rows, lines):
                    self.assertRegex(line, rf"^{measure}: not forecast: \S")


if __name__ == "__main__":
    unittest.main()
