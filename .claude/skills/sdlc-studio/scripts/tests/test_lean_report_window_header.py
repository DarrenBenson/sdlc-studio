"""BG0893: the report header names the end of the window the page measured to, never 'open'.

The close derives the page while the run is still open (the seal writes `ended_at` after it),
so RPT0014's header read `2026-10-01T10:19:17Z to open (9.6h)` though the page records its
`window_end` and its duration already ran to it. The header's end is now that window end.

The page is derived through `sprint_report.build_report` on a lean run still open, rendered in
both twins, and then judged by `revalidate` once the run is sealed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import test_lean_close as lean  # noqa: E402 - the lean run fixture, shared

RETRO = "RETRO0001"
STARTED = "2026-10-01T10:19:17Z"
WINDOW_END = "2026-10-01T19:54:55Z"
SEALED = "2026-10-01T20:30:00Z"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


class ReportWindowHeaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        # Open: no `ended_at` yet. The window's CI runs frozen (none), so no forge is read.
        lean._fixture(self.root, started_at=STARTED, ci_runs={"source": "gh run list",
                                                              "runs": []})

    def test_the_header_names_the_window_end(self) -> None:
        """AC1. MUTANTS: HEAD, which renders `ended_at` as `open` until the seal writes it;
        reading the end from the record's `ended_at` (still None at the close, so `open`
        again)."""
        sr = _live("sprint_report")
        page = sr.build_report(self.root, RETRO, as_of=WINDOW_END)   # derived at the close
        self.assertEqual(WINDOW_END, page["window_end"], "premise: the page's window")
        md, html = sr.render_markdown(page), sr.render_html(page)
        self.assertIn(f"> **Run:** {STARTED} to {WINDOW_END} (9.6h)", md)
        self.assertIn(f"Run {STARTED} &rarr; {WINDOW_END} (9.6h)", html)
        for label, text in (("markdown", md), ("html", html)):
            self.assertNotIn("to open", text, label)
            self.assertNotIn("&rarr; open", text, label)

    def test_a_sealed_page_still_checks_valid(self) -> None:
        """The end is outside the digest and judged against the run record instead
        (`_lifecycle_edits`). MUTANT: read the header's end from the record's `ended_at` once
        the seal writes it, so a re-derivation of the filed page names the seal's moment and
        the check reads the page as edited."""
        sr = _live("sprint_report")
        rid = sr.file_report(self.root, sr.build_report(self.root, RETRO, as_of=WINDOW_END))
        rs = _live("lib.run_state")
        rs.update(self.root, ended_at=SEALED, outcome="goal-reached")
        check = sr.revalidate(self.root, rid)
        self.assertTrue(check["valid"], (check["changes"], check["edited"]))
        self.assertEqual([], check["edited"])

    def test_a_page_derived_after_the_seal_names_the_run_s_end(self) -> None:
        """The window ends at the earlier of the run's end and the page's generation. MUTANT:
        name the generation time, so a page derived an hour after the seal claims the run
        went on to it."""
        sr = _live("sprint_report")
        _live("lib.run_state").update(self.root, ended_at=SEALED, outcome="goal-reached")
        page = sr.build_report(self.root, RETRO, as_of="2026-10-01T21:30:00Z")
        self.assertIn(f"> **Run:** {STARTED} to {SEALED} (10.2h)", sr.render_markdown(page))


if __name__ == "__main__":
    unittest.main()
