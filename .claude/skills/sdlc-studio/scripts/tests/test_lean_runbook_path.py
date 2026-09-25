"""US0943: `sprint plan` finds the toolchain runbook beside the skill, not in the project.

In a consuming project the skill is installed under ~/.claude/skills, so a runbook path joined to
the project root never resolves and every plan printed TOOLCHAIN RUNBOOK MISSING. Driven through
`sprint.main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

_SKILL = Path(__file__).resolve().parents[2]


def _project(root: Path) -> None:
    """A plannable project holding no `.claude/skills/` of its own."""
    (root / "src").mkdir(parents=True)
    (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / "US0001-x.md").write_text(
        "# US0001: a unit\n\n> **Status:** Ready\n> **Points:** 3\n"
        "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
        "### AC1: it behaves\n\n- **Then** it behaves\n- **Verify:** shell true\n",
        encoding="utf-8")


def _plan(root: Path) -> tuple[int, str]:
    """Run from inside the project, as its owner would, so a cwd-relative lookup finds no skill."""
    out, cwd = io.StringIO(), os.getcwd()
    os.chdir(root)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()), \
                unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
            rc = sprint.main(["plan", "--stories", "Ready", "--no-fetch", "--root", str(root)])
    finally:
        os.chdir(cwd)
    return rc, out.getvalue()


class RunbookTests(unittest.TestCase):

    def test_consuming_project_finds_runbook(self) -> None:
        """MUTANT: resolve the runbook under the project root (HEAD's `Path(root) / RUNBOOK_REL`)."""
        runbook = (_SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        steps = [ln[3:].strip() for ln in runbook.splitlines()
                 if ln.startswith("## ") and not ln[3:].startswith("When a")]
        self.assertTrue(steps, "the shipped runbook carries no step headings to look for")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            self.assertFalse((root / ".claude").exists())
            rc, out = _plan(root)
        self.assertEqual(0, rc, f"the plan did not run:\n{out}")
        self.assertNotIn("TOOLCHAIN RUNBOOK MISSING", out,
                         "the plan looked for the runbook in the project, not beside the skill")
        for step in steps:
            self.assertIn(step, out, f"the runbook step {step!r} was not printed")

    def test_absent_runbook_still_reported(self) -> None:
        """MUTANT: return [] when the runbook cannot be read."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as s:
            root = Path(d)
            _project(root)
            with unittest.mock.patch.object(sprint, "SKILL_ROOT", Path(s)):
                rc, out = _plan(root)
        self.assertEqual(0, rc, f"the plan did not run:\n{out}")
        self.assertIn("TOOLCHAIN RUNBOOK MISSING", out,
                      "a skill tree with no runbook produced no absence report")


if __name__ == "__main__":
    unittest.main()
