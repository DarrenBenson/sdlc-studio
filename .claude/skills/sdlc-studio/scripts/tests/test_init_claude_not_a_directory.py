"""BG1260: `init run` and `init guided` finish a project whose `.claude` is a regular file.

Drafting the subagent definitions creates `.claude/agents/`, and where `.claude` is a regular
file that raised NotADirectoryError out of both entry points, exiting 1 with the tree half
written. Each definition is now skipped with its OSError reason and the rest of the project is
written. A definition that cannot be read is not an instruction file: it neither earns the
"so the doctrine check can read it" directive nor hides the doctrine offer.

Every test drives the shipped CLI in a throwaway project. Unreadable is made without chmod (root
ignores mode bits): a directory stands at the file's path, which every host refuses to read.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/init.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
INIT = SCR / "init.py"
DEFINITIONS = (".claude/agents/sdlc-builder.md", ".claude/agents/sdlc-reviewer.md")
DIRECTIVE = "so the doctrine check can read it"
DOCTRINE_OFFER = "AGENTS.md carries no lifecycle doctrine"
BOILERPLATE = "# AGENTS.md\n\nThis is an Astro site. Run `npm run dev` to start it.\n"


def _init(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(INIT), *args, "--root", str(root)],
                          capture_output=True, text=True, cwd=root, timeout=120)


def _project(d: str, claude_is_a_file: bool = True) -> Path:
    root = Path(d) / "proj"
    root.mkdir()
    if claude_is_a_file:
        (root / ".claude").write_text("", encoding="utf-8")
    return root


class ClaudeIsAFileTests(unittest.TestCase):

    def _assert_each_definition_skipped(self, out: str) -> None:
        for rel in DEFINITIONS:
            lines = [line for line in out.splitlines() if rel in line]
            self.assertEqual(len(lines), 1, f"{rel} is not named once:\n{out}")
            self.assertIn("skipped", lines[0])
            self.assertIn("NotADirectoryError", lines[0], f"{rel} names no OSError reason")

    def test_init_run_finishes_and_names_each_skipped_definition(self) -> None:
        """AC1. MUTANTS: the per-definition OSError guard removed (exit 1, decisions log
        unwritten); the reason dropped from the skip line."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            r = _init(root, "run")
            self.assertEqual(r.returncode, 0, r.stderr)
            for rel in ("AGENTS.md", "CLAUDE.md", "sdlc-studio/decisions.md",
                        "sdlc-studio/definition-of-ready.md", "sdlc-studio/definition-of-done.md"):
                self.assertTrue((root / rel).is_file(), f"{rel} was not written")
            self.assertTrue((root / ".claude").is_file(), "the project's .claude was replaced")
            self._assert_each_definition_skipped(r.stdout)
            for rel in DEFINITIONS:
                self.assertNotIn(f"+ {rel}", r.stdout, f"{rel} reported created")

        # The JSON report names each with its reason; nothing reports it created.
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            r = _init(root, "run", "--format", "json")
            self.assertEqual(r.returncode, 0, r.stderr)
            report = json.loads(r.stdout)
            unwritable = {u["path"]: u["reason"] for u in report["unwritable"]}
            self.assertEqual(sorted(unwritable), sorted(DEFINITIONS))
            for reason in unwritable.values():
                self.assertIn("NotADirectoryError", reason)
            self.assertFalse(set(DEFINITIONS) & set(report["created"]))

        # The control: with no .claude at all, both definitions are written.
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, claude_is_a_file=False)
            r = _init(root, "run")
            self.assertEqual(r.returncode, 0, r.stderr)
            for rel in DEFINITIONS:
                self.assertTrue((root / rel).is_file(), f"{rel} was not written")
            self.assertNotIn("NotADirectoryError", r.stdout)

    def test_init_guided_agents_stage_finishes(self) -> None:
        """AC2. MUTANT: stage_agents' unguarded mkdir and write restored (exit 1)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            r = _init(root, "guided")
            self.assertEqual(r.returncode, 0, r.stderr)
            for rel in ("AGENTS.md", "CLAUDE.md"):
                self.assertTrue((root / rel).is_file(), f"{rel} was not written")
            self._assert_each_definition_skipped(r.stdout)

        # The control: with .claude absent, the stage writes both definitions.
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, claude_is_a_file=False)
            r = _init(root, "guided")
            self.assertEqual(r.returncode, 0, r.stderr)
            for rel in DEFINITIONS:
                self.assertTrue((root / rel).is_file(), f"{rel} was not written")
                self.assertIn(f"drafted {rel}", r.stdout)
            self.assertNotIn("NotADirectoryError", r.stdout)

    def test_an_unreadable_definition_neither_misdirects_nor_hides_the_doctrine_offer(self) -> None:
        """AC3. MUTANT: the unreadable-file check widened from INSTRUCTION_FILES to AGENT_FILES
        (the directive then names the definition and the doctrine offer is hidden)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, claude_is_a_file=False)
            (root / "AGENTS.md").write_text(BOILERPLATE, encoding="utf-8")
            (root / DEFINITIONS[0]).mkdir(parents=True)  # unreadable: a directory at its path
            r = _init(root, "guided")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn(DIRECTIVE, r.stdout)
            self.assertIn(DOCTRINE_OFFER, r.stdout)

        # The control, so the absence above is not vacuous: an unreadable INSTRUCTION file does
        # draw the directive, in the words this test looks for.
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, claude_is_a_file=False)
            (root / "AGENTS.md").mkdir()
            r = _init(root, "guided")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("AGENTS.md cannot be read", r.stdout)
            self.assertIn(DIRECTIVE, r.stdout)


if __name__ == "__main__":
    unittest.main()
