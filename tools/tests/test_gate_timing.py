"""Unit tests for tools/gate_timing.py - the pre-commit suite's runtime history (US0219).

The measurement is advisory: it exists so a 2.5-minute run is expected rather than
mistaken for a hang. That makes its failure modes the interesting part - it must never
fail a commit, and must never print a number it cannot support.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "gate_timing.py"


def _load():
    spec = importlib.util.spec_from_file_location("gate_timing", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gate_timing"] = mod
    spec.loader.exec_module(mod)
    return mod


gt = _load()


class RecordTests(unittest.TestCase):
    """AC1: durations accumulate to a bounded per-suite history."""

    def test_record_creates_and_appends(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "skill-tests", 12.3)
            gt.record(root, "skill-tests", 14.1)
            data = json.loads((root / gt.REL).read_text(encoding="utf-8"))
            self.assertEqual(data["skill-tests"], [12.3, 14.1])

    def test_history_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for i in range(gt.HISTORY + 5):
                gt.record(root, "skill-tests", float(i))
            runs = json.loads((root / gt.REL).read_text(encoding="utf-8"))["skill-tests"]
            self.assertEqual(len(runs), gt.HISTORY)
            self.assertEqual(runs[-1], float(gt.HISTORY + 4))   # newest kept
            self.assertNotIn(0.0, runs)                          # oldest dropped

    def test_suites_are_tracked_separately(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "skill-tests", 100.0)
            gt.record(root, "tool-tests", 2.0)
            self.assertEqual(gt.expected(root, "skill-tests"), 100.0)
            self.assertEqual(gt.expected(root, "tool-tests"), 2.0)


class EstimateTests(unittest.TestCase):
    """AC2: a long expected run is announced before it is paid for."""

    def _estimate(self, root, warn):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = gt.main(["--root", str(root), "estimate",
                          "--suite", "skill-tests", "--warn-seconds", str(warn)])
        return rc, buf.getvalue()

    def test_warns_above_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for _ in range(3):
                gt.record(root, "skill-tests", 150.0)
            rc, out = self._estimate(root, 30)
            self.assertEqual(rc, 0)
            self.assertIn("~150s", out)
            self.assertIn("timeout", out)

    def test_silent_below_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "skill-tests", 3.0)
            rc, out = self._estimate(root, 30)
            self.assertEqual(rc, 0)
            self.assertEqual(out, "")


class DegradeTests(unittest.TestCase):
    """AC3: no history and a corrupt file both degrade to silence, not to a wrong number."""

    def _estimate(self, root):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = gt.main(["--root", str(root), "estimate", "--suite", "skill-tests"])
        return rc, buf.getvalue()

    def test_no_history_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out = self._estimate(Path(d))
            self.assertEqual(rc, 0)
            self.assertEqual(out, "")

    def test_corrupt_history_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / gt.REL
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{not json", encoding="utf-8")
            rc, out = self._estimate(root)
            self.assertEqual(rc, 0)          # never fails a commit
            self.assertEqual(out, "")        # never invents a figure

    def test_non_numeric_entries_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / gt.REL
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"skill-tests": ["bogus", None, 10.0]}), encoding="utf-8")
            self.assertEqual(gt.expected(root, "skill-tests"), 10.0)

    def test_record_over_corrupt_file_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / gt.REL
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("garbage", encoding="utf-8")
            gt.record(root, "skill-tests", 5.0)
            self.assertEqual(gt.expected(root, "skill-tests"), 5.0)


class MedianTests(unittest.TestCase):
    """AC4: one pathological run must not inflate every later estimate."""

    def test_outlier_does_not_dominate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for s in (100.0, 102.0, 98.0, 101.0, 900.0):   # one cold-cache run
                gt.record(root, "skill-tests", s)
            exp = gt.expected(root, "skill-tests")
            self.assertLess(exp, 150.0)      # a mean would be ~260
            self.assertGreater(exp, 90.0)


class BudgetLaneTests(unittest.TestCase):
    """RFC0048 D6: a per-commit gate budget, declared against a measured baseline, reported as a
    TREND and never blocking."""

    def _project(self, root: Path, body: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def setUp(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - the budget block cannot be read")

    def test_budget_config_carries_its_baseline(self) -> None:
        """A ceiling recorded without the measurement it was chosen against cannot be reviewed
        later - 'is 120s still right?' is unanswerable without knowing what it was 29% above."""
        repo = Path(__file__).resolve().parents[2]
        block = gt.budget_config(repo)
        self.assertIsNotNone(block, "this repo declares no gate_budget")
        self.assertIn("seconds", block)
        self.assertIn("baseline_seconds", block)
        self.assertIn("baseline_date", block)

    def test_over_budget_warns_and_never_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "gate_budget:\n  seconds: 100\n"
                                "  baseline_seconds: 90\n  baseline_date: 2026-07-21\n")
            gt.record(root, "total", 250.0)                 # far over
            rep = gt.budget_report(root)
            self.assertTrue(rep["over"])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = gt.main(["--root", str(root), "budget"])
            self.assertEqual(rc, 0)                          # ...and STILL exits clean
            self.assertIn("OVER", out.getvalue())

    def test_the_report_names_the_baseline_and_the_drift(self) -> None:
        """Reporting only 'under budget' is how test_gate.py grew 28% unnoticed: it was under
        every ceiling the whole time. The drift is the signal, not the verdict."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "gate_budget:\n  seconds: 200\n"
                                "  baseline_seconds: 100\n  baseline_date: 2026-07-21\n")
            gt.record(root, "total", 128.0)                  # under budget, but +28% on baseline
            rep = gt.budget_report(root)
            self.assertFalse(rep["over"])
            self.assertIn("2026-07-21", rep["detail"])
            self.assertIn("+28%", rep["detail"])

    def test_the_budget_reads_the_latest_run_not_the_median(self) -> None:
        """A median over a ten-run window lags a step change: when the suite went 153s -> 79s the
        median still read ~152s. A budget built on it would report a number true of no run that
        had happened."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "gate_budget:\n  seconds: 120\n"
                                "  baseline_seconds: 93.1\n  baseline_date: 2026-07-21\n")
            for s in (153.0, 152.0, 154.0, 153.0, 155.0, 152.0, 159.0, 161.0, 109.0, 79.0):
                gt.record(root, "total", s)
            self.assertEqual(gt.latest(root, "total"), 79.0)
            self.assertGreater(gt.expected(root, "total"), 140.0)   # the median still says ~153
            self.assertEqual(gt.budget_report(root)["measured"], 79.0)

    def test_no_budget_or_no_history_is_silent(self) -> None:
        """Silence, never a guessed number - the same rule `estimate` follows."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total", 50.0)
            self.assertIsNone(gt.budget_report(root))        # recorded, but no budget declared
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, "gate_budget:\n  seconds: 100\n")
            self.assertIsNone(gt.budget_report(root))        # declared, but nothing recorded


if __name__ == "__main__":
    unittest.main()


class ScopeTests(unittest.TestCase):
    """BG0239: a lane that was INVOKED is not a lane that RAN.

    The budget series is only comparable between runs that did the same work, so a run that
    covered a fraction of its scope must stay out of it rather than read as a speed-up.
    """

    def test_no_history_starts_the_series(self) -> None:
        # A fresh clone has no peak to judge against. Refusing to record until a baseline exists
        # would mean never recording one.
        with tempfile.TemporaryDirectory() as d:
            v = gt.scope_ok(Path(d), "total", 3400)
            self.assertTrue(v["ok"])
            self.assertIsNone(v["peak"])

    def test_a_full_run_against_an_established_peak_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            self.assertTrue(gt.scope_ok(root, "total", 3400)["ok"])

    def test_a_loader_error_is_refused_even_at_a_full_count(self) -> None:
        """The filed reproduction. A module that fails to import is a FACT, not a threshold, so it
        is refused regardless of how many tests the remaining modules managed to run - and with no
        history at all, where every count-based rule is blind."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            v = gt.scope_ok(root, "total", 3400, loader_error=True)
            self.assertFalse(v["ok"])
            self.assertIn("failed to import", v["why"])
            # ...and with no history, where the count floor cannot fire at all
            with tempfile.TemporaryDirectory() as d2:
                self.assertFalse(gt.scope_ok(Path(d2), "total", 3400, loader_error=True)["ok"])

    def test_a_truncated_count_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            v = gt.scope_ok(root, "total", 1000)
            self.assertFalse(v["ok"])
            self.assertIn("3400", v["why"])

    def test_the_floor_brackets_the_boundary_two_sided(self) -> None:
        """Pins the value of SCOPE_FLOOR behaviourally, so moving it fails rather than silently
        widening what counts as a full run."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 1000)
            self.assertTrue(gt.scope_ok(root, "total", 800)["ok"])    # exactly at the floor
            self.assertFalse(gt.scope_ok(root, "total", 799)["ok"])   # one below it

    def test_a_real_speedup_is_never_refused(self) -> None:
        """The trap the count-based rule exists to avoid. EP0093 took a commit from 196.7s to 99s;
        any plausibility band over DURATION history would have rejected that as implausible and
        discarded the improvement. Scope is judged on tests, not seconds, so a run that got twice
        as fast while running MORE tests is recorded."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for s in (196.7, 190.0, 193.0):
                gt.record(root, "total", s)
            gt.record(root, "total.tests", 3409)
            self.assertTrue(gt.scope_ok(root, "total", 3422)["ok"])

    def test_the_count_is_recorded_even_when_the_run_is_refused(self) -> None:
        """Otherwise one truncated run poisons the series: the peak could never recover, because
        the counts that would rebuild it are exactly the ones being thrown away."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            with contextlib.redirect_stdout(io.StringIO()):   # captured: a green run is silent
                rc = gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "10"])
            self.assertEqual(rc, 1)
            data = json.loads((root / gt.REL).read_text(encoding="utf-8"))
            self.assertEqual(data["total.tests"], [3400, 10])

    def test_the_refusal_is_said_out_loud_and_never_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = gt.main(["--root", str(root), "scope", "--suite", "total",
                              "--tests", "3400", "--loader-error"])
            self.assertEqual(rc, 1)
            self.assertIn("NOT recorded", buf.getvalue())

    def test_a_full_run_prints_nothing_and_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "3400"])
            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue(), "")
