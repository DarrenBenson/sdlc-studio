"""BG0920: the close checklist's cost row reads the same window as the re-filed page.

After BG0913 and BG0916 a re-close re-files a page whose main-thread tokens keep the first
close's reading (4,000), but the checklist's cost row read every meter stamp on the run, so after
a later stamp it printed 13,000 "as the report's Estimates section states it" beside a page
stating 4,000. The row now counts only the stamps inside the window the first filed page ended
at, as the page does.

Each test runs the real `sprint.py close` (every chain step stubbed green, see
`test_lean_close._close`) against a transcript directory and clock it controls, then prints the
checklist through `sprint_report.py checklist`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import io
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
RETRO = "RETRO0001"                       # the retro `lean._close` names


class RecloseChecklistCostTests(unittest.TestCase):
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
        # The checklist joins the run to the retro by the units its Batch field names.
        retro = self.root / "sdlc-studio" / "retros" / "RETRO0001-lean.md"
        retro.write_text(retro.read_text(encoding="utf-8").replace(
            "> **Date:** 2026-09-23\n", "> **Date:** 2026-09-23\n> **Batch:** US0101\n"),
            encoding="utf-8")
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
    def tokens_total(page: dict) -> int:
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        return cost["figures"]["tokens_total"]["value"]

    def cost_row(self) -> str:
        """The checklist's cost row as `sprint_report.py checklist` prints it."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            lean._live("sprint_report").main(["--root", str(self.root), "checklist", "--id",
                                              RETRO, "--format", "json"])
        items = json.loads(out.getvalue())["items"]
        return next(r for r in items if r["id"] == "cost")["value"]

    def test_the_checklist_cost_row_matches_the_page(self) -> None:
        """AC1. MUTANT: HEAD, whose cost row reads every stamp on the run, so the later stamp
        moves it to 13,000 while the re-filed page reads 4,000."""
        self.close_at(T)
        self.spend(9000)                                 # post-close paperwork
        with self.clock(BETWEEN):
            self.rs.stamp_tokens(self.root, "unit-start")
        again = self.close_at(LATER)
        self.assertEqual(4000, self.tokens_total(again), "premise: the re-filed page reads 4,000")
        self.assertEqual("4,000 tokens, measured", self.cost_row())

    def test_before_any_page_the_row_reads_every_stamp(self) -> None:
        """The control: a run that has filed no page has no window end, so the row counts every
        stamp, a unit stamp included. MUTANT: count only the open and report stamps, so the unit
        stamp drops and the row reads no measured total."""
        self.spend(9000)
        with self.clock(BETWEEN):
            self.rs.stamp_tokens(self.root, "unit-start")
        self.assertIsNone(lean._read(self.root).get("report"), "premise: no page filed")
        self.assertEqual("13,000 tokens, measured", self.cost_row())


if __name__ == "__main__":
    unittest.main()
