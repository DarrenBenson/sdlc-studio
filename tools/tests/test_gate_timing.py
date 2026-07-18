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


if __name__ == "__main__":
    unittest.main()
