"""BG0913: a re-close keeps the first close's window end and main-thread meter reading.

Every `sprint close` re-run on a closed run re-filed the page with its window ended at the
re-close and took another meter reading, so the orchestrator's post-close paperwork counted as
the run's cost: RUN-01M3Y7DP's main-thread tokens read 0.64M at the first close and 3.47M after
four re-closes. The first close that files a page now records its window end on the run, and a
re-close re-derives against it and takes no new reading, so only artefact changes move a
re-filed page.

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
LATER = "2026-09-23T07:00:00Z"


class RecloseKeepsWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self.transcripts = Path(self._tmp.name) / "transcripts"
        self.transcripts.mkdir()
        rs = lean._live("lib.run_state")
        env = unittest.mock.patch.dict(os.environ, {rs.TRANSCRIPTS_ENV: str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        lean._fixture(self.root)
        self.spend(1000)
        with unittest.mock.patch.object(rs.sdlc_md, "now_iso8601",
                                        lambda: "2026-09-23T00:00:00Z"):
            rs.stamp_tokens(self.root, "open")           # the meter's opening reading
        self.spend(4000)                                 # the run's own main-thread work

    def spend(self, tokens: int) -> None:
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def close_at(self, at: str) -> dict:
        """Close at `at`, returning the page the close filed."""
        mods = {id(m): m for m in (lean._live("lib.sdlc_md"), lean._live("sprint").sdlc_md,
                                   lean._live("sprint_report").sdlc_md)}
        with contextlib.ExitStack() as stack:
            for m in mods.values():
                stack.enter_context(unittest.mock.patch.object(m, "now_iso8601", lambda: at))
            rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        state = lean._read(self.root)
        return lean._live("sprint_report").read_report(self.root, state["report"])

    @staticmethod
    def main_thread(page: dict) -> int:
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        return sum(r["model_tokens"]["value"] for r in cost["rows"])

    def test_a_re_close_keeps_the_first_close_s_window_and_meter(self) -> None:
        """AC1. MUTANTS: HEAD, which ends a re-close's window at the re-close and stamps the
        meter again (window 07:00, 13,000 tokens); keeping the window but stamping again; or
        stamping nothing but ending the window at the re-close."""
        first = self.close_at(T)
        self.assertEqual((T, 4000), (first["window_end"], self.main_thread(first)),
                         "premise: the first close measures to its own moment")
        self.spend(9000)                                 # an hour of post-close paperwork
        again = self.close_at(LATER)
        self.assertEqual(first["report_id"], again["report_id"])
        self.assertEqual(T, again["window_end"])
        self.assertEqual(4000, self.main_thread(again))

    def test_a_finding_filed_between_the_closes_is_on_the_re_filed_page(self) -> None:
        """D0317: only the cost figures keep the first close's window. A High bug raised at 06:30,
        between a close at 06:00 and a re-close at 07:00, is still open and the close's checklist
        asks for its ruling, so the re-filed page lists it while its cost still reads as at the
        first close. MUTANT: bound the open findings by the first close's window end too."""
        self.close_at(T)
        self.spend(9000)
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / "BG0999-between.md").write_text(
            "# BG0999: raised between the closes\n\n> **Status:** Open\n> **Severity:** High\n"
            "> **Raised-in-batch:** RUN-LEAN0001 close, 2026-09-23T06:30:00Z\n",
            encoding="utf-8")
        again = self.close_at(LATER)
        sec = next(s for s in again["sections"] if s["key"] == "known_issues")
        listed = {lean._live("sprint").sdlc_md.norm_id(r["issue_id"]["value"])
                  for r in sec.get("rows") or []}
        self.assertIn("BG0999", listed)
        self.assertEqual((T, 4000), (again["window_end"], self.main_thread(again)))

    def test_a_close_that_filed_no_page_does_not_fix_the_window(self) -> None:
        """The control. MUTANT: record the window on a close whose page was refused, so the
        first close that does file one is measured to a moment no page was ever filed at."""
        sr = lean._live("sprint_report")
        real = sr.build_report

        def refuse(*_a, **_k):
            raise sr.ReportError("the run cannot be reported")

        with unittest.mock.patch.object(sr, "build_report", refuse):
            rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self.assertIsNone(lean._read(self.root).get("report"))
        self.assertIs(real, sr.build_report)
        self.spend(9000)
        page = self.close_at(LATER)
        self.assertEqual((LATER, 13000), (page["window_end"], self.main_thread(page)))


if __name__ == "__main__":
    unittest.main()
