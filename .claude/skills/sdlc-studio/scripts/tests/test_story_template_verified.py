"""A criterion copied from the shipped story template closes its verify loop.

A bare `- **Verified:** no` under a criterion is an authored miss: a passing selector does not
overwrite it and the run fails. The story template shipped that line under every criterion and
two reference pages told authors to write it until reconcile ran, so every template-authored
story failed its verify run until its author deleted the line the template had asked for. A new
criterion carries no Verified line; the runner adds one. A hand-written bare no on an existing
criterion stays sticky.

Each criterion is cut from the template as it ships, its placeholders filled here, and run
through the shipped `verify_ac.py` entry point.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/core/story.md
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
TEMPLATE = SKILL / "templates" / "core" / "story.md"
SCRIPT = SKILL / "scripts" / "verify_ac.py"
REFERENCES = (SKILL / "reference-story.md", SKILL / "reference-verify.md")
CRITERIA = ("AC1", "AC2", "AC3")


def _criterion(ac: str) -> str:
    """The template's `ac` block as shipped, its Verify placeholder `shell true` and every other
    placeholder filled with plain words."""
    text = TEMPLATE.read_text(encoding="utf-8")
    block = re.search(rf"(?ms)^### {ac}: .*?(?=^### |^> |^## )", text)
    if block is None:
        raise AssertionError(f"the template carries no {ac} block")
    n = ac[2:]
    filled = block.group(0).replace(f"{{{{ac{n}_verify}}}}", "shell true")
    return re.sub(r"\{\{\w+\}\}", "a plain value", filled).strip()


class StoryTemplateVerifiedTests(unittest.TestCase):
    def story(self, criterion: str, status: str) -> tuple[Path, Path]:
        d = Path(tempfile.mkdtemp(prefix="template_verified_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        path = d / "sdlc-studio" / "stories" / "US9100-probe.md"
        path.write_text(
            f"# US9100: probe\n\n> **Status:** {status}\n> **Affects:** a.py\n\n"
            f"## Acceptance Criteria\n\n{criterion}\n\n## Revision History\n\n"
            "| Date | Author | Change |\n| --- | --- | --- |\n| 2026-11-15 | probe | created |\n",
            encoding="utf-8")
        return d, path

    @staticmethod
    def run_verify(root: Path) -> str:
        out = subprocess.run([sys.executable, "-B", str(SCRIPT), "run", "--id", "US9100",
                              "--root", str(root)], capture_output=True, text=True, check=False)
        return out.stdout + out.stderr

    @staticmethod
    def verified(path: Path) -> list[str]:
        return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
                if "**Verified:**" in ln]

    def test_a_criterion_copied_from_the_template_is_stamped_yes(self) -> None:
        """AC1. MUTANT: the template still ships a bare `- **Verified:** no` under any one of its
        three criteria - that criterion's run reads fail=1 and its line stays no."""
        for ac in CRITERIA:
            with self.subTest(criterion=ac):
                root, path = self.story(_criterion(ac), "Draft")
                out = self.run_verify(root)
                self.assertIn("pass=1", out)
                self.assertIn("fail=0", out)
                lines = self.verified(path)
                self.assertEqual(1, len(lines), lines)
                self.assertTrue(lines[0].startswith("- **Verified:** yes"), lines)

    def test_the_references_say_a_new_criterion_carries_no_verified_line(self) -> None:
        """AC2. MUTANTS: either page still tells an author to write `Verified: no` until
        reconcile runs; either page drops the sentence that a new criterion carries no Verified
        line, or that `Verified: no` is a recorded miss the runner does not overwrite."""
        for page in REFERENCES:
            with self.subTest(page=page.name):
                flat = " ".join(page.read_text(encoding="utf-8").split())
                self.assertNotRegex(flat, r"Verified: no`?[^.]*until reconcile runs")
                self.assertNotRegex(flat, r"(?i)mark `Verified: no` on every")
                self.assertIn("A new criterion carries no `Verified:` line", flat)
                self.assertIn("`Verified: no` is a recorded miss the runner does not overwrite",
                              flat)

    def test_a_hand_written_bare_no_stays_sticky(self) -> None:
        """AC3. MUTANT: the fix made in verify_ac.py instead of the template - a passing selector
        overwrites a hand-written bare no with yes, or the run counts it as a pass."""
        root, path = self.story(f"{_criterion('AC1')}\n- **Verified:** no", "In Progress")
        out = self.run_verify(root)
        self.assertIn("fail=1", out)
        self.assertIn("pass=0", out)
        self.assertEqual(["- **Verified:** no"], self.verified(path))


if __name__ == "__main__":
    unittest.main()
