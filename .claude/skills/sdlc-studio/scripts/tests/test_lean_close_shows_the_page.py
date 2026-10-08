"""BG0912: the close puts the readable page in front of the operator before asking for a signature.

`sprint close` ended with `sign it with: sprint.py sign --report RPTxxxx` and named neither the
page nor a rendering of it, so the operator was asked to sign a report they had not been shown.
The close now writes the HTML page to the ignored `sdlc-studio/.local/reports/` (D2a, D0315: no
rendered page churns in git, and a tracked file written after the close would make `sprint sign`
refuse the tree as changed) and names the Markdown page and the HTML page above the sign command.

Each test runs the real `sprint.py close` with every chain step stubbed green
(`test_lean_close._close`).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared


class CloseShowsThePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean._fixture(self.root)
        self.reports = self.root / "sdlc-studio" / "reports"
        self.local_reports = self.root / "sdlc-studio" / ".local" / "reports"

    def test_the_close_names_the_page_and_its_html_twin(self) -> None:
        """AC1. MUTANTS: writing the HTML into the tracked reports/ folder (01fea1ac, which
        breaks D2a); writing no HTML and printing only the sign command; naming the paths after
        the sign command, so the last line is no longer the one action left."""
        before = set(self.reports.iterdir()) if self.reports.is_dir() else set()
        rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        self.assertEqual("RPT0001", lean._read(self.root)["report"])
        html = self.local_reports / "RPT0001.html"
        self.assertTrue(html.is_file(), "no HTML page under sdlc-studio/.local/reports/")
        self.assertIn("<h2>Goal</h2>", html.read_text(encoding="utf-8"))
        md = next(self.reports.glob("RPT0001-*.md"))
        # Nothing under the tracked reports/ folder but the filed page itself: its record, its
        # Markdown twin, the derived index, and the run's record awaiting its signature, so
        # every checkout sees the run is open (BG0993).
        filed = {self.reports / "RPT0001.json", md, self.reports / "_index.md",
                 self.reports / "runs"}
        self.assertEqual(filed, set(self.reports.iterdir()) - before)
        self.assertEqual([self.reports / "runs" / f"{lean._read(self.root)['run_id']}.json"],
                         list((self.reports / "runs").iterdir()))
        self.assertEqual([], list(self.reports.rglob("*.html")))
        lines = out.splitlines()
        sign = next(i for i, ln in enumerate(lines) if ln.startswith("sign it with:"))
        named_md = [i for i, ln in enumerate(lines) if md.name in ln]
        named_html = [i for i, ln in enumerate(lines)
                      if "sdlc-studio/.local/reports/RPT0001.html" in ln]
        self.assertTrue(named_md and named_html, out)
        self.assertLess(max(named_md + named_html), sign, out)
        self.assertEqual(sign, max(i for i, ln in enumerate(lines) if ln.strip()),
                         "the sign command is no longer the last line")

    def test_a_close_that_files_no_report_names_no_page(self) -> None:
        """The control. MUTANT: write or name an HTML twin whether or not a page was filed."""
        sr = lean._live("sprint_report")

        def refuse(*_a, **_k):
            raise sr.ReportError("the run cannot be reported")

        with unittest.mock.patch.object(sr, "build_report", refuse):
            rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        self.assertEqual([], list(self.root.rglob("*.html")))
        self.assertNotIn(".html", out + err)
        self.assertNotIn("sign it with:", out)


if __name__ == "__main__":
    unittest.main()
