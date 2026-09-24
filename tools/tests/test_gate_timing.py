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

    def test_a_SELECTED_run_is_not_judged_against_the_full_peak(self) -> None:
        """Selection and this floor were in direct conflict the moment selection began working.
        A selected run legitimately runs a fraction of the suite, so the peak comparison cannot
        tell it from the truncated run the floor exists to catch - and the first selected commit
        reported `total NOT recorded - 1171 tests against a peak of 6174`. Left there, the budget
        series would have stopped being written at exactly the moment the gate got cheaper."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 6174)
            self.assertFalse(gt.scope_ok(root, "total", 1171)["ok"],
                             "a truncated FULL run must still be refused")
            v = gt.scope_ok(root, "total", 1171, selected=True)
            self.assertTrue(v["ok"], "a selected run is refused, so the budget stops recording")
            self.assertIn("SELECTED", v["why"])

    def test_a_selected_run_with_a_loader_error_is_still_refused(self) -> None:
        """Selection relaxes the THRESHOLD, never the fact. A selected run whose module failed to
        import is exactly as broken as a full one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 6174)
            self.assertFalse(
                gt.scope_ok(root, "total", 1171, loader_error=True, selected=True)["ok"])

    def test_a_selected_count_is_recorded_in_its_OWN_series(self) -> None:
        """The peak is a `max`, so one selected count mixed in is harmless today. The history is
        a rolling window, though, so a stretch of selected commits evicts every full count and
        the peak collapses to a subset's - the floor then judging full runs against a fraction.
        Separated at the source rather than relying on the window never filling."""
        import argparse
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 6174)
            gt.cmd_scope(argparse.Namespace(root=str(root), suite="total", tests=1171,
                                            loader_error=False, selected=True))
            data = gt._load(root)
            self.assertIn("total.selected.tests", data)
            self.assertNotIn(1171, data.get("total.tests", []),
                             "a selected count landed in the full series and will erode the peak")

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
        the counts that would rebuild it are exactly the ones being thrown away.

        Exercised with a DRIFT (2000 of 3400 - under the 0.8 floor, above the collapse
        threshold), so this stays a test about exit 1 declining a recording. The collapse path
        records its count too; that is asserted in ScopeCollapseTests.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            with contextlib.redirect_stdout(io.StringIO()):   # captured: a green run is silent
                rc = gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "2000"])
            self.assertEqual(rc, 1)
            data = json.loads((root / gt.REL).read_text(encoding="utf-8"))
            self.assertEqual(data["total.tests"], [3400, 2000])

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


class ScopeCollapseTests(unittest.TestCase):
    """BG0413: a suite that stops running most of itself must REFUSE, not decline a timing.

    `scope_ok`'s generous 0.8 floor is right for its own purpose - tests are legitimately
    deleted, and a floor that fires on real deletions trains people to ignore it. But it was
    the only thing in the repo that could notice a suite had silently stopped running, and its
    entire consequence was that a number did not reach a JSON file. RUN-01KYNKDP deleted eight
    test classes, the suite reported 510 passing against a peak of 5,645, and the commit landed.
    """

    def test_a_collapsed_count_refuses_the_commit_not_merely_the_recording(self) -> None:
        """The filed reproduction, at its filed magnitude: 510 against a peak of 5,645."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            v = gt.scope_ok(root, "total", 510)
            self.assertFalse(v["ok"])
            self.assertTrue(v["collapsed"],
                            "a 91% loss is graded the same as a noisy timing, so the commit lands")

    def test_a_drift_inside_the_generous_floor_is_not_a_collapse(self) -> None:
        """AC3: the 0.8 floor keeps its own behaviour. A legitimate deletion must still only
        decline the recording, or the blocking event trains the bypass it exists to prevent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 1000)
            v = gt.scope_ok(root, "total", 700)          # under the 0.8 floor, far above collapse
            self.assertFalse(v["ok"], "the existing floor stopped judging this a short run")
            self.assertFalse(v["collapsed"], "an ordinary deletion now BLOCKS a commit")

    def test_the_collapse_boundary_is_bracketed_two_sided(self) -> None:
        """Behavioural, not a constant assertion: moving the threshold fails here rather than
        silently widening what counts as survivable."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 1000)
            self.assertFalse(gt.scope_ok(root, "total", 500)["collapsed"])  # at the threshold
            self.assertTrue(gt.scope_ok(root, "total", 499)["collapsed"])   # one below it

    def test_the_refusal_names_the_count_the_peak_and_the_drop(self) -> None:
        """AC2. The old message named neither number, so a reader who saw it could not tell a
        rounding wobble from a suite that had stopped running."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            why = gt.scope_ok(root, "total", 510)["why"]
            self.assertIn("510", why)
            self.assertIn("5645", why)
            self.assertIn("91%", why, "the drop is not stated, only the two counts")

    def test_a_collapsed_run_exits_distinctly_from_a_declined_recording(self) -> None:
        """The hook branches on this: exit 1 declines a timing and proceeds, exit 3 blocks.

        THREE, not two - python itself exits 2 for an argparse error and for a missing
        script file, so a hook reading 2 as `collapsed` refuses every commit on which the
        tool is absent or mis-invoked. This docstring said 2 while the assertion below
        pinned 3."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "510"])
            self.assertEqual(rc, 3, "a collapse exits as an ordinary declined recording")
            self.assertIn("BLOCKED", buf.getvalue())

    def test_a_selected_run_is_never_judged_a_collapse(self) -> None:
        """A selected run legitimately runs a fraction of the suite. Judging it a collapse would
        block every selected commit - the same conflict the 0.8 floor already had to resolve."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 6174)
            self.assertFalse(gt.scope_ok(root, "total", 510, selected=True)["collapsed"])

    def test_no_history_cannot_manufacture_a_collapse(self) -> None:
        """A fresh clone has no peak. Comparing against a peak that does not exist is how a first
        commit gets blocked by a guard about regressions."""
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(gt.scope_ok(Path(d), "total", 3)["collapsed"])

    def test_an_acked_bulk_removal_is_allowed_and_states_itself(self) -> None:
        """AC4: a deliberate bulk removal is recorded, not waved through by a generous threshold."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(
                json.dumps({"tests": 510, "reason": "the legacy suite was split out to its own "
                                                    "package under US1234"}), encoding="utf-8")
            v = gt.scope_ok(root, "total", 510)
            self.assertFalse(v["collapsed"])
            self.assertIn("acknowledged", v["why"])

    def test_an_ack_for_a_different_count_does_not_license_this_collapse(self) -> None:
        """An ack is spent on the removal it describes. A stale one left in the tree would license
        every future collapse silently - the fail-open this escape would otherwise introduce."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(
                json.dumps({"tests": 510, "reason": "the legacy suite moved out"}),
                encoding="utf-8")
            self.assertTrue(gt.scope_ok(root, "total", 120)["collapsed"],
                            "a stale ack licensed a collapse it does not describe")

    def test_a_reasonless_ack_is_not_an_ack(self) -> None:
        """An absence stated is evidence; an empty field is the gap this escape would open."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(
                json.dumps({"tests": 510, "reason": "  "}), encoding="utf-8")
            self.assertTrue(gt.scope_ok(root, "total", 510)["collapsed"])

    def test_an_unreadable_ack_never_reports_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text("{not json", encoding="utf-8")
            self.assertTrue(gt.scope_ok(root, "total", 510)["collapsed"])

    def test_a_loader_error_still_only_declines_the_recording(self) -> None:
        """The loader-error branch is a different fact with a different consequence, and it is
        checked first. Grading it a collapse would block every import failure, which is a build
        problem the author already sees.

        The count must be BELOW the collapse threshold, or the `not loader_error` term is never
        reached and the test passes whether that term is present or absent. An independent
        review mutated the term away and this test survived - a vacuous test, in the sprint that
        shipped the rule against them."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            v = gt.scope_ok(root, "total", 100, loader_error=True)
            self.assertFalse(v["ok"])
            self.assertFalse(v["collapsed"],
                             "a loader error at a collapsed count is graded a collapse, so "
                             "every import failure now blocks the commit")

    def test_a_zero_count_is_a_collapse_and_says_which_fault_it_is(self) -> None:
        """`suite_tests` is parsed out of the runner's output, so a changed output format yields
        0 and blocks every commit. That is the right verdict - nobody can tell "ran nothing" from
        "counted nothing", and neither shows the scope ran - but the two have different fixes, so
        the message must not send a reader chasing a deleted test that does not exist."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            v = gt.scope_ok(root, "total", 0)
            self.assertTrue(v["collapsed"])
            self.assertIn("output format", v["why"])
            self.assertNotIn("100% drop", v["why"])

    def test_a_collapsed_count_is_NOT_recorded_so_retries_cannot_evict_the_peak(self) -> None:
        """The refusal text says "commit again" and the history is a rolling window of 10, so
        recording the collapsed count meant ten retries evicted every real count and left the
        peak at the collapsed value - the guard then permanently off. With a zero count it took
        the 0.8 floor down too, since nothing is below `0 * 0.8`. Found by an independent
        review driving the documented retry loop."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            for _ in range(12):
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = gt.main(["--root", str(root), "scope", "--suite", "total",
                                  "--tests", "510"])
                self.assertEqual(rc, 3, "the guard stopped blocking an identical collapsed run")
            self.assertEqual(json.loads((root / gt.REL).read_text(encoding="utf-8"))["total.tests"],
                             [5645], "a collapsed count entered the series and evicted the peak")

    def test_a_DRIFTING_count_is_still_recorded_so_the_peak_can_recover(self) -> None:
        """The control for the rule above: a drift must still record, or one short run poisons
        the series permanently - the counts that would rebuild the peak are the ones being
        thrown away."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 3400)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "2000"])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads((root / gt.REL).read_text(encoding="utf-8"))["total.tests"],
                             [3400, 2000])

    def test_an_acked_shrink_still_declines_the_timing(self) -> None:
        """The ack clears the COLLAPSE grade and nothing else. Setting `ok = True` let a 1-test
        run's duration into the budget series, where it read as a 100% improvement - BG0239's
        exact regression, reintroduced through the new escape. Found by independent review,
        end-to-end through the real hook."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(
                json.dumps({"tests": 510, "reason": "the legacy suite moved out"}),
                encoding="utf-8")
            v = gt.scope_ok(root, "total", 510)
            self.assertFalse(v["collapsed"], "the acknowledged shrink still blocks")
            self.assertFalse(v["ok"],
                             "an acknowledged shrink is recorded as comparable, so its duration "
                             "enters the budget series and reads as an improvement")

    def test_the_acknowledged_escape_is_said_out_loud(self) -> None:
        """An escape taken silently is indistinguishable from a guard that never fired, which
        is what the ack's own criterion forbids."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gt.record(root, "total.tests", 5645)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(
                json.dumps({"tests": 510, "reason": "the legacy suite moved out"}),
                encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                gt.main(["--root", str(root), "scope", "--suite", "total", "--tests", "510"])
            self.assertIn("acknowledged", buf.getvalue())

    def test_a_non_object_ack_is_not_an_ack(self) -> None:
        """Mutation found the `isinstance` guard unheld: a JSON list or string parses fine and
        must not license a collapse."""
        for payload in ("[1, 2, 3]", '"just a string"', "42"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                gt.record(root, "total.tests", 5645)
                (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
                (root / "sdlc-studio" / gt.COLLAPSE_ACK).write_text(payload, encoding="utf-8")
                self.assertTrue(gt.scope_ok(root, "total", 510)["collapsed"],
                                f"{payload} was accepted as an acknowledgement")


if __name__ == "__main__":
    unittest.main()
