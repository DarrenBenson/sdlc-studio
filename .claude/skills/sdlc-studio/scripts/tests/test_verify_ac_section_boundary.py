"""A criterion ends where its section ends.

A criterion opened under `## Acceptance Criteria` stayed open to the end of the file, so a
`**Verify:**` line in a later section (a `## Closed <date>` record, an update note) was attached
to the last criterion and executed as part of it. Each verifier here leaves a file behind when it
runs, so "not executed" is measured on disk, beside a control that shows the same line executing
from inside the section.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

HEAD = "# BG9001: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n"
CRITERIA = ("## Acceptance Criteria\n\n"
            "- [ ] **AC1** the first holds\n  - **Verify:** file one.txt\n"
            "- [ ] **AC2** the second holds\n  - **Verify:** file two.txt\n{inside}\n")
LATER = ("## Closed 2026-07-23\n\n"
         "**Verify:** shell touch HISTORY_RAN\n\n"
         "## Revision History\n\n| Date | Change |\n| --- | --- |\n")


class SectionBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="section_boundary_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        for name in ("one.txt", "two.txt"):
            (self.root / name).write_text("hello\n", encoding="utf-8")
        self.bugs = self.root / "sdlc-studio" / "bugs"
        self.bugs.mkdir(parents=True)

    def _bug(self, body: str) -> Path:
        path = self.bugs / "BG9001-x.md"
        path.write_text(HEAD + body, encoding="utf-8")
        return path

    def _main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = verify_ac.main(list(args))
        return code, out.getvalue()

    def test_a_verify_in_later_section_not_attached(self):
        text = HEAD + CRITERIA.format(inside="") + LATER
        blocks = verify_ac.parse_story(text)
        self.assertEqual(["AC1", "AC2"], [b.ac_id for b in blocks])
        self.assertEqual(["file two.txt"], blocks[-1].verifiers, "a later line was attached")
        self._bug(CRITERIA.format(inside="") + LATER)
        code, out = self._main("run", "--id", "BG9001", "--root", str(self.root), "--dry-run")
        self.assertIn("ac=2 pass=2 fail=0", out)
        self.assertEqual(0, code, out)
        self.assertFalse((self.root / "HISTORY_RAN").exists(), "a history Verify line was executed")

    def test_the_same_line_inside_the_section_is_executed(self):
        # The control: the instrument sees execution, so its silence above means something.
        self._bug(CRITERIA.format(inside="  - **Verify:** shell touch INSIDE_RAN\n"))
        self._main("run", "--id", "BG9001", "--root", str(self.root), "--dry-run")
        self.assertTrue((self.root / "INSIDE_RAN").exists())

    def test_lint_names_verify_outside_criteria(self):
        path = self._bug(CRITERIA.format(inside="") + LATER)
        _code, out = self._main("lint", "--root", str(self.root), "--story", str(path))
        stray = [ln for ln in out.splitlines() if "outside `## Acceptance Criteria`" in ln]
        self.assertEqual(1, len(stray), out)
        self.assertIn("shell touch HISTORY_RAN", stray[0])
        self.assertIn("Closed 2026-07-23", stray[0])
        self.assertNotIn("file two.txt", "\n".join(stray), "an in-section line was named")

    def test_lint_names_verify_outside_criteria_once_for_a_misplaced_criterion(self):
        # A criterion under another heading is named as misplaced; its line is not named twice.
        misplaced = "## Notes\n\n- [ ] **AC3** stray\n  - **Verify:** shell touch MISPLACED\n"
        path = self._bug(CRITERIA.format(inside="") + misplaced)
        _code, out = self._main("lint", "--root", str(self.root), "--story", str(path))
        self.assertIn("AC3: unreviewable", out)
        self.assertNotIn("MISPLACED' sits under", out)

    def test_lint_names_verify_outside_criteria_and_not_one_inside_before_ac1(self):
        # Inside the section but before its first criterion is not outside it.
        body = CRITERIA.replace("\n\n- [ ] **AC1**", "\n\n**Verify:** shell touch EARLY\n\n- [ ] **AC1**")
        path = self._bug(body.format(inside="") + LATER)
        _code, out = self._main("lint", "--root", str(self.root), "--story", str(path))
        self.assertIn("HISTORY_RAN' sits under", out)
        self.assertNotIn("EARLY' sits under", out)

    def test_lint_names_verify_outside_criteria_but_not_a_fenced_one(self):
        fenced = "## Notes\n\n```text\n**Verify:** shell touch FENCED\n```\n"
        path = self._bug(CRITERIA.format(inside="") + fenced)
        _code, out = self._main("lint", "--root", str(self.root), "--story", str(path))
        self.assertNotIn("FENCED", out, "an illustration inside a fence was named")


if __name__ == "__main__":
    unittest.main()
