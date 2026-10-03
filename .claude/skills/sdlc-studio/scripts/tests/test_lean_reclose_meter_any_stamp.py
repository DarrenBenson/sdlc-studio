"""BG0916: a meter stamp taken after the first close does not move a re-filed page's tokens.

BG0913 stopped a re-close taking a new report-time reading, but the main-thread tokens are the
spread of EVERY stamp on the run, so a stamp taken after the first close for another reason (a
unit moved In Progress, a span settled by the re-close) still moved the re-filed page: the
reviewer saw 13,000 where the first close read 4,000. The page now counts only the stamps taken
inside its window, so a re-close, and any re-derivation of the page, reads what the first close
read.

Each test runs the real `sprint.py close` (every chain step stubbed green, see
`test_lean_close._close`) against a transcript directory and clock it controls.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

T = "2026-09-23T06:00:00Z"
BETWEEN = "2026-09-23T06:30:00Z"
LATER = "2026-09-23T07:00:00Z"


class RecloseMeterAnyStampTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self.transcripts = Path(self._tmp.name) / "transcripts"
        self.transcripts.mkdir()
        self.rs = lean._live("lib.run_state")
        env = unittest.mock.patch.dict(os.environ,
                                       {self.rs.TRANSCRIPTS_ENV: str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        lean._fixture(self.root)
        self.spend(1000)
        with self.clock("2026-09-23T00:00:00Z"):
            self.rs.stamp_tokens(self.root, "open")      # the meter's opening reading
        self.spend(4000)                                 # the run's own main-thread work

    def spend(self, tokens: int) -> None:
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    @contextlib.contextmanager
    def clock(self, at: str):
        mods = {id(m): m for m in (lean._live("lib.sdlc_md"), lean._live("sprint").sdlc_md,
                                   lean._live("sprint_report").sdlc_md, self.rs.sdlc_md)}
        with contextlib.ExitStack() as stack:
            for m in mods.values():
                stack.enter_context(unittest.mock.patch.object(m, "now_iso8601", lambda: at))
            yield

    def close_at(self, at: str) -> dict:
        """Close at `at`, returning the page the close filed."""
        with self.clock(at):
            rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        state = lean._read(self.root)
        return lean._live("sprint_report").read_report(self.root, state["report"])

    @staticmethod
    def main_thread(page: dict) -> int:
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        return sum(r["model_tokens"]["value"] for r in cost["rows"])

    @staticmethod
    def tokens_total(page: dict) -> int:
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        return cost["figures"]["tokens_total"]["value"]

    def test_a_later_stamp_does_not_move_the_meter(self) -> None:
        """AC1. MUTANTS: HEAD, which counts every stamp on the run, so the later stamp moves the
        re-filed page to 13,000; and the half-fix that filters only the per-model cost rows,
        leaving the page's token total at 13,000."""
        first = self.close_at(T)
        self.assertEqual((4000, 4000), (self.main_thread(first), self.tokens_total(first)),
                         "premise: the first close read 4,000, nothing delegated")
        self.spend(9000)                                 # post-close paperwork
        with self.clock(BETWEEN):
            stamp = self.rs.stamp_tokens(self.root, "unit-start")
        self.assertEqual(("unit-start", 14000), (stamp["kind"], stamp["tokens"]),
                         "premise: a later, non-report stamp is on the run")
        again = self.close_at(LATER)
        self.assertEqual(4000, self.main_thread(again))
        self.assertEqual(4000, self.tokens_total(again))

    def test_a_stamp_inside_the_window_still_counts(self) -> None:
        """The control: the bound is the window's end, not the report stamp. A unit stamp taken
        before the first close counts. MUTANT: count only the open and report stamps."""
        self.spend(2000)
        with self.clock("2026-09-23T05:00:00Z"):
            self.rs.stamp_tokens(self.root, "unit-end")
        self.spend(3000)
        page = self.close_at(T)
        self.assertEqual(9000, self.main_thread(page))


if __name__ == "__main__":
    unittest.main()
