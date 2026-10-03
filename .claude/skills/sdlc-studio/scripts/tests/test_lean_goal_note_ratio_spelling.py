"""BG0922: the goal-note check reads only a ratio beside a measure name, in any spelling.

BG0911's check read every `Nx` token in the goal verdict's note as a ratio, so a note saying the
close ran "10x faster" was named as contradicting the page, and a ratio written 1.4X or with the
multiplication sign was not read at all. A ratio is now read only where it follows one of the
page's Estimates measure names (Tokens, Minutes, ...) within three words, written x, X or the
multiplication sign; the page's own ratios are still read off the page as before.

Each case runs the real `sprint.py close` with every chain step stubbed green
(`test_lean_close._close`) over a run whose Tokens ratio derives to 1.7x.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
from test_lean_goal_note_ratio_numeric import GoalNoteRatioNumericTests  # noqa: E402

TIMES = "×"


class GoalNoteRatioSpellingTests(unittest.TestCase):
    setUp = GoalNoteRatioNumericTests.setUp
    _close = GoalNoteRatioNumericTests._close
    named = staticmethod(GoalNoteRatioNumericTests.named)

    def test_only_measure_ratios_are_read(self) -> None:
        """AC1. MUTANT: HEAD's parser, which reads every `Nx` - the first note names 10x - and
        reads only a lower-case x, so the second note's 1.4X is never named. The page derives
        1.7x, which the first note quotes, so a check naming nothing at all fails the second."""
        rc, lines, ratio = self._close("faster", "tokens at 1.7x, and the close ran 10x faster")
        self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
        self.assertEqual(0, rc, "\n".join(lines))
        self.assertEqual([], self.named(lines), lines)

        rc, lines, ratio = self._close("wrong", "tokens at 1.4X, every unit delivered")
        self.assertEqual("1.7x", ratio)
        self.assertEqual(0, rc, "\n".join(lines))
        named = self.named(lines)
        self.assertEqual(1, len(named), lines)
        self.assertIn("1.4X", named[0])
        self.assertIn("1.7x", named[0])

    def test_each_spelling_of_a_ratio_is_read(self) -> None:
        """The QA seat's controls (D0328). MUTANT: accept X but not the multiplication sign, or
        read a spelling the page's own ratio is not compared in - the page's 1.7x written any
        way names nothing, and a wrong ratio written any way is named."""
        for i, mark in enumerate(("x", "X", TIMES)):
            with self.subTest(mark=mark):
                rc, lines, _ = self._close(f"right{i}", f"Tokens ratio 1.7{mark} as planned")
                self.assertEqual(0, rc, "\n".join(lines))
                self.assertEqual([], self.named(lines), lines)
                rc, lines, _ = self._close(f"wrong{i}", f"Tokens ratio 1.4{mark} as planned")
                named = self.named(lines)
                self.assertEqual(1, len(named), lines)
                self.assertIn(f"1.4{mark}", named[0])

    def test_a_ratio_behind_punctuation_or_a_singular_name_is_read(self) -> None:
        """The engineering seat's regressions (D0331). MUTANT: 9ec3d18d's parser, which needs
        whitespace then a bare number after the name and the name exactly as the page writes
        it, so none of these is named. The control: each written with the page's own 1.7x
        names nothing, so a check that names everything also fails."""
        for i, shape in enumerate(("Tokens ({r}) over plan", "Tokens: ~{r} over plan",
                                   "tokens={r} over plan", "the token ratio was {r}")):
            with self.subTest(shape=shape):
                rc, lines, _ = self._close(f"p-right{i}", shape.format(r="1.7x"))
                self.assertEqual(0, rc, "\n".join(lines))
                self.assertEqual([], self.named(lines), lines)
                rc, lines, _ = self._close(f"p-wrong{i}", shape.format(r="1.4x"))
                named = self.named(lines)
                self.assertEqual(1, len(named), lines)
                self.assertIn("1.4x", named[0])

    def test_the_word_window_is_three(self) -> None:
        """The pin on the window. MUTANT: {0,3} made {0,1}, which no longer reads a wrong
        ratio three words after the name, or {0,10}, which reads one four words after it."""
        rc, lines, _ = self._close("three", "tokens came in at 1.4x")
        named = self.named(lines)
        self.assertEqual(1, len(named), lines)
        self.assertIn("1.4x", named[0])
        rc, lines, _ = self._close("four", "tokens came in well under, 1.4x faster")
        self.assertEqual(0, rc, "\n".join(lines))
        self.assertEqual([], self.named(lines), lines)


if __name__ == "__main__":
    unittest.main()
