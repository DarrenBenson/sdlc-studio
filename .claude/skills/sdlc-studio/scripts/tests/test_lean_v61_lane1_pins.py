"""BG0931: four lane-1 fixes of the v6.1 run, each correct by execution but unpinned.

The reviews approved BG0924, BG0926, BG0927 and BG0930 and each named a mutant its own tests
let through. Each pin here drives the fix's own fixture (borrowed from the unit's test module,
so the two cannot drift) through the case that mutant gets wrong, beside a control.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_lean_appetite_sealed_run as appetite  # noqa: E402
import test_lean_closed_run_late_total as late  # noqa: E402
import test_lean_minutes_reason_true as minutes  # noqa: E402
import test_lean_sign as signing  # noqa: E402
import test_lean_transcript_scan_dangling as dangling  # noqa: E402
from lib import run_state  # noqa: E402


class V61Lane1PinsTests(unittest.TestCase):
    _ws = appetite.AppetiteSealedRunTests._ws
    _set = appetite.AppetiteSealedRunTests._set

    def _borrow(self, case: type[unittest.TestCase]) -> unittest.TestCase:
        """`case`'s fixture, set up for this test and torn down with it."""
        h = case("run")
        h.setUp()
        self.addCleanup(h.doCleanups)
        return h

    def test_a_split_forecast_names_the_missing_pair(self) -> None:
        """BG0924, AC1. MUTANT: the reason chosen on there being no forecast anywhere, which
        reads "no unit carries a measured time" here, where US0001 carries the forecast and
        US0002 the 30 measured minutes. The control: with no measured minutes at all the old
        reason stands, so a mutant that always names the pair is caught."""
        h = self._borrow(minutes.MinutesReasonTrueTests)
        h._set(forecast={"US0001": 40.0}, measured={"US0002": 30.0})
        actual = h._minutes()
        self.assertEqual(minutes.sr.NOT_MEASURED, actual["value"], actual)
        self.assertIn(minutes.PAIR, actual.get("reason", ""), actual)
        self.assertNotIn(minutes.NONE, actual.get("reason", ""), actual)

        h._set(forecast={"US0001": 40.0}, measured={})
        actual = h._minutes()
        self.assertIn(minutes.NONE, actual.get("reason", ""), actual)
        self.assertNotIn(minutes.PAIR, actual.get("reason", ""), actual)

    def test_a_reopened_re_close_records_no_late_total(self) -> None:
        """BG0926, AC2. MUTANTS: `return not reopens`, which counts a run reopened once as open
        for good, so the return after the re-close lands and RPT0002 reads INVALIDATED; and
        `reopens[0]`, which compares the page against the FIRST reopen, so after a second
        reopen the run still reads as filed and the total that reopen exists to let in is lost.
        The control is RPT0002 itself, VALID before the return."""
        h = self._borrow(late.ClosedRunLateTotalTests)

        def check(report: str) -> tuple[int, str]:
            import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = sprint_report.main(["--root", str(h.root), "check", "--report", report])
            return rc, out.getvalue()

        def seal_and_reopen(report: str) -> None:
            rc, _out, err = signing._sign(h.root, report)
            self.assertEqual(0, rc, err)
            h._commit("seal")
            rc, said = h._run("reopen", "--reason", "a late review belongs to this run")
            self.assertEqual(0, rc, said)

        h._close()
        seal_and_reopen("RPT0001")
        h._close()
        state = run_state.read(h.root)
        self.assertEqual("RPT0002", state.get("report"), "premise: the re-close filed RPT0002")
        rc, out = check("RPT0002")
        self.assertEqual(0, rc, f"premise: the re-filed page checks VALID\n{out}")
        before = h._delegated()

        _rc, said = h._run("lane", "return", "--units", "US0101", "--tokens", "7000")

        self.assertEqual(before, h._delegated(),
                         f"the late total was recorded into the re-closed run:\n{said}")
        rc, out = check("RPT0002")
        self.assertEqual(0, rc, f"the late return moved the re-filed page:\n{out}")
        self.assertNotIn("INVALIDATED", out)

        seal_and_reopen("RPT0002")
        _rc, said = h._run("lane", "return", "--units", "US0101", "--tokens", "7000")
        self.assertEqual(7000, (h._delegated() or [{}])[-1].get("tokens"),
                         f"a second reopen refused the total it exists to let in:\n{said}")

    def test_the_newest_transcript_is_read(self) -> None:
        """BG0927, AC3. MUTANT: an oldest-first pick in `_newest_transcript`, which reads the
        older transcript - it records another project's `cwd`, so the long-path scan misses
        this repo's folder and the meter reads nothing. The newer one records this repo, and
        its 5 tokens are the ones read."""
        h = self._borrow(dangling.TranscriptScanDanglingTests)
        root = h.base / ("a" * 70) / ("b" * 70) / ("c" * 70)
        root.mkdir(parents=True)
        slug = run_state.harness_project_slug(root)
        self.assertGreater(len(slug), 200, "premise: a slug the harness truncates")
        match = h.projects / (slug[:200] + "-1abc2d")
        match.mkdir(parents=True)
        now = time.time()
        for name, cwd, tokens, mtime in (("old.jsonl", "/somewhere/else", 3, now - 100),
                                         ("new.jsonl", str(root), 5, now)):
            f = match / name
            f.write_text(json.dumps({"cwd": cwd, "message": {"usage": {"input_tokens": tokens}}})
                         + "\n", encoding="utf-8")
            os.utime(f, (mtime, mtime))

        self.assertEqual(match, run_state._harness_transcript_dir(root))
        got = run_state.session_tokens(root)
        self.assertEqual(5, got.get("tokens"), got)

    def test_a_partial_run_spends_no_appetite(self) -> None:
        """BG0930, AC4. MUTANT: a skip for `goal-reached` only, which warns APPETITE SPENT
        against a signed partial run - the outcome of the web run that raised BG0930 - and
        every other closed outcome. The control: the same run open still warns."""
        for outcome in (run_state.PARTIAL,
                        *[o for o in run_state.CLOSED if o != run_state.PARTIAL]):
            with self.subTest(outcome=outcome):
                signed = self._ws(outcome, ended_at="2026-08-14T02:00:00Z",
                                  signature={"principal": "Darren", "report": "RPT0001"})
                said = self._set(signed, "BG9101")
                self.assertNotIn("APPETITE SPENT", said, said)

        said = self._set(self._ws(run_state.RUNNING), "BG9101")
        self.assertIn("APPETITE SPENT", said, said)


if __name__ == "__main__":
    unittest.main()
