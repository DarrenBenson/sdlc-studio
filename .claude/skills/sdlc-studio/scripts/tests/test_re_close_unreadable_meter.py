"""A re-close after `sprint reopen` whose meter cannot be read keeps the first window.

The close after a reopen re-reads the meter and measures the page to itself. When that reading
cannot be had, the page keeps the window it filed before the reopen, rather than stretching it
to a close it holds no reading for, and its Priced cost row says the second reading is missing.
Each test runs the real `sprint.py close` through the reopened-run fixture.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_sprint_report as tsr  # noqa: E402 - the reopened-run close fixture

MISSING = "the second reading is missing"


class ReCloseUnreadableMeterTests(unittest.TestCase):
    # The fixture's methods, borrowed rather than inherited (or held at module level) so its
    # own tests are not collected and run a second time here.
    _R = tsr.ReopenedRunCostTests
    FIRST, REOPEN, SECOND, THIRD = _R.FIRST, _R.REOPEN, _R.SECOND, _R.THIRD
    setUp, spend, at, close_at, reopen_at = _R.setUp, _R.spend, _R.at, _R.close_at, _R.reopen_at
    priced = staticmethod(_R.priced)
    del _R

    def _second_close_unread(self, unread) -> tuple[dict, dict]:
        """Close, reopen, spend, then close again with the meter made unreadable by `unread`."""
        first = self.close_at(self.FIRST)
        self.reopen_at(self.REOPEN)
        self.spend(9000)                                 # the reopened unit's work
        with unread:
            again = self.close_at(self.SECOND)
        return first, again

    def _gone(self):
        return mock.patch.dict(os.environ, {self.rs.TRANSCRIPTS_ENV: str(self.root / "gone")})

    def _assert_kept(self, unread, why: str) -> None:
        first, again = self._second_close_unread(unread)
        self.assertEqual(self.FIRST, again["window_end"], "the first window is kept")
        self.assertEqual(self.FIRST, self.lean._read(self.root)["report_window_end"])
        self.assertEqual(self.priced(first)["est_actual"]["value"],
                         self.priced(again)["est_actual"]["value"])
        basis = self.priced(again)["est_basis"]["value"]
        for said in (MISSING, f"reopened at {self.REOPEN}", why, f"runs to {self.FIRST}"):
            self.assertIn(said, basis)
        self.assertNotIn("re-read at the close", basis)
        sr = self.lean._live("sprint_report")
        self.assertIn(MISSING, sr.render_markdown(again))
        # LC-017: the page re-derives from the record as filed.
        check = sr.revalidate(self.root, again["report_id"])
        self.assertTrue(check["valid"], check.get("changes"))

    def test_a_meter_with_no_reading_keeps_the_first_window_and_says_so(self) -> None:
        """AC1. MUTANTS: HEAD, which stretches the window to the second close and says nothing;
        the window kept with no word on the page; the word on the page with the window
        stretched; the reason or the kept window's end left out of the word."""
        self._assert_kept(self._gone(), "the meter returned no reading")

    def test_a_meter_that_raises_keeps_the_first_window_and_names_why(self) -> None:
        """AC1 over a reading that raises. MUTANT: the raise swallowed with the generic reason."""
        self._assert_kept(mock.patch.object(self.rs, "stamp_tokens", side_effect=OSError(
            "the transcript is locked")), "the meter could not be read: the transcript is locked")

    def test_a_later_reopen_that_reads_the_meter_replaces_the_missing_word(self) -> None:
        """MUTANT: the missing record kept after a later close re-reads, so the page says both."""
        self._second_close_unread(self._gone())
        self.reopen_at("2026-09-23T07:30:00Z")
        third = self.close_at(self.THIRD)
        self.assertEqual(self.THIRD, third["window_end"])
        basis = self.priced(third)["est_basis"]["value"]
        self.assertIn(f"re-read at the close of {self.THIRD}", basis)
        self.assertNotIn(MISSING, basis)

    def test_a_re_close_with_no_reopen_says_nothing_of_a_reading(self) -> None:
        """The control: an unreadable meter on a re-close with no reopen since keeps the window
        as it always did, and the page says nothing about a re-read or a missing one."""
        self.close_at(self.FIRST)
        with self._gone():
            again = self.close_at(self.SECOND)
        self.assertEqual(self.FIRST, again["window_end"])
        basis = self.priced(again)["est_basis"]["value"]
        self.assertNotIn(MISSING, basis)
        self.assertNotIn("reopen", basis)


if __name__ == "__main__":
    unittest.main()
