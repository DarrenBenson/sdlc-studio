#!/usr/bin/env python3
"""The shipped testing practice states the entry-point rule.

A rule that lives only in a reviewer's head is one that gets skipped, and this particular one
cost a review round: a criterion describing a command, verified through the library, passes
forever while the command does nothing.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import best_practice_rules as bpr  # noqa: E402

PRACTICE = REPO / bpr.PRACTICE_REL

class TestingPracticeTests(unittest.TestCase):

    def test_the_entry_point_rule_is_stated(self) -> None:
        """MUTANT: delete the section from best-practices/testing.md."""
        missing = bpr.missing_claims(PRACTICE.read_text(encoding="utf-8"))
        self.assertEqual([], missing, f"the practice never states {missing}")

    def test_deleting_the_passage_reddens_the_guard(self) -> None:
        """The guard must not be satisfiable by prose ABOUT the change.

        Builds the adversarial case: the section removed, a Revision History row describing it
        left behind. A whole-file substring check goes green on that row; this must not.
        """
        text = PRACTICE.read_text(encoding="utf-8")
        gutted = text.replace(bpr.section(text), "")
        gutted += ("\n## Revision History\n\n| Date | Change |\n| --- | --- |\n"
                   "| 2026-08-02 | State the entry point rule: name the entry point before "
                   "writing the test; a library import is not evidence for a command. |\n")
        self.assertEqual("", bpr.section(gutted),
                         "the guard finds the rule outside its own section - a Revision "
                         "History row would turn it green")
    def test_the_command_exits_non_zero_when_the_rule_is_absent(self) -> None:
        """The rule is a runnable CHECK, not only a test. MUTANT: return 0 unconditionally."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / bpr.PRACTICE_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("## Something else\n\nNothing about doors.\n", encoding="utf-8")
            self.assertEqual(1, bpr.main(["--root", str(root)]),
                             "a practice missing the rule exited zero")
            target.write_text(PRACTICE.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(0, bpr.main(["--root", str(root)]),
                             "the shipped practice was refused by its own guard")




class AnAbsentPracticeFileRefusesTests(unittest.TestCase):
    """BG0493: `best_practice_rules.py` returned 0 when its practice file was absent, so the one
    input that silenced the check completely was the easiest to produce - and nothing ran it at
    all, so it guarded nothing either way."""

    REPO = Path(__file__).resolve().parents[2]
    SRC = REPO / "tools" / "best_practice_rules.py"

    def test_a_missing_file_is_not_an_exemption(self) -> None:
        """MUTANT: swap the refusal on a missing practice file for a zero return.

        An exemption reachable by deleting a file is the shape US0608 AC4 exists to prevent."""
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, str(self.SRC), "--root", d],
                               capture_output=True, text=True, timeout=60)
            self.assertNotEqual(0, r.returncode,
                                f"an absent practice file was treated as nothing to check:\n"
                                f"{r.stdout}{r.stderr}")
            self.assertIn("absence is a broken tree", r.stdout + r.stderr)

    def test_a_present_practice_still_passes(self) -> None:
        """The paired control: a checker that refuses every root satisfies the row above."""
        r = subprocess.run([sys.executable, str(self.SRC), "--root", str(self.REPO)],
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
