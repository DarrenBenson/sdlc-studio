"""BG0900: the delegated token total counts in the run's actual when the session meter reads 0.

`sprint_report._run_tokens_actual` added the delegated agents' totals only when the main-thread
meter read a non-zero spend, so a run whose meter read 0 reported no token actual at all though
a lane return had recorded its builder's total. The delegated total now counts whatever the
meter reads, and a meter of 0 is named as unread in the basis. A page filed before the rule
carries no mark and re-derives as it was signed.

Drives `sprint.py lane` in-process against the throwaway workspace of
`test_lean_lane_delegated_tokens`, and derives the page through `sprint_report.build_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_lane_delegated_tokens as lane  # noqa: E402 - the lane workspace, shared


class MeterZeroDelegatedTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = lane._Workspace(self._tmp.name)
        env = unittest.mock.patch.dict(
            os.environ, {lane._live("lib.run_state").TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def test_delegated_tokens_count_when_the_meter_reads_zero(self) -> None:
        """AC1. MUTANT: HEAD, which adds the delegated total only beside a non-zero meter, so
        the 250,000 the lane return recorded is dropped and the actual reads NOT MEASURED. The
        controls: a meter that read spend still adds the total, and a page filed before the
        rule re-derives the actual it was signed with."""
        ws, sr = self.ws, lane._live("sprint_report")
        ws.deliver("US0101", "--tokens", "250000")        # no spend after the open: meter 0
        row = ws.tokens_row(ws.page())
        self.assertEqual(250_000, row["est_actual"]["value"])
        self.assertIn("1 delegated agent", row["est_basis"]["value"])
        self.assertIn("unread", row["est_basis"]["value"])
        before = ws.tokens_row(sr.build_report(ws.root, lane.RETRO, delegated_rule=False))
        self.assertEqual(sr.NOT_MEASURED, before["est_actual"]["value"])
        ws.spend(5000)                                     # the meter now reads 5,000
        lane._live("lib.run_state").stamp_tokens(ws.root, "report", ws.transcripts)
        row = ws.tokens_row(ws.page())
        self.assertEqual(255_000, row["est_actual"]["value"])
        self.assertNotIn("unread", row["est_basis"]["value"])

    def test_a_filed_page_re_derives_under_its_own_mark(self) -> None:
        """BG0900 round 1. MUTANTS: drop the DELEGATED_RULE mark from the envelope, so a page
        filed with the 250,000 re-derives with the rule off (NOT MEASURED) and reads
        INVALIDATED; hard-wire `delegated_rule=True` in revalidate, so a page filed before the
        rule re-derives 250,000 against its NOT MEASURED. Each filing is the other's control."""
        ws, sr = self.ws, lane._live("sprint_report")
        ws.deliver("US0101", "--tokens", "250000")        # no spend after the open: meter 0
        for rule, actual in ((True, 250_000), (False, sr.NOT_MEASURED)):
            page = sr.build_report(ws.root, lane.RETRO, delegated_rule=rule)
            self.assertEqual(actual, ws.tokens_row(page)["est_actual"]["value"], "premise")
            check = sr.revalidate(ws.root, sr.file_report(ws.root, page))
            self.assertTrue(check["valid"], (rule, check["changes"]))


if __name__ == "__main__":
    unittest.main()
