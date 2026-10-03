"""BG0938: the last lows the v6.1 reviews raised (D0334).

The changelog cut places a `####` block cleanly in any section, not only the last, and folds two
fragments carrying the same `####` heading in one section under one heading; a fields-file
`seats` value that is not a list is named as such; and the goal-note parser is linear on a
whitespace-free run of repeated measure names. Each is driven through its shipped entry point:
`release_cut.py changelog-cut`, `sprint.py goal-review record` and the real `sprint close`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/changelog.py
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_goal_note_ratio_numeric as numeric  # noqa: E402 - by module, not re-collected
import test_lean_retired_handoff_surface as cut  # noqa: E402 - the cut fixture, shared
import test_lean_v61_review_residue as residue  # noqa: E402 - the goal-review recorder, shared
from lib import retired_surface  # noqa: E402

_TABLE_HEAD = ("#### Retired flags\n"
               "\n"
               "| Before (v6.0) | After (v6.1) | Migration |\n"
               "| --- | --- | --- |\n")

#: Fragment file -> text, in the order the cut folds them (by name). BG0001 makes `### Fixed`
#: first, so every later block in Added or Changed sits above a following `###` heading. CR0001
#: opens Changed with a block and no bullet, CR0002 then puts a bullet on top of that block and
#: a second `#### Retired flags` in the same section, and US0001 closes Added with a block.
_FRAGMENTS = {
    "BG0001.md": "<!-- section: Fixed -->\n\n- A fix (BG0001).\n",
    "CR0001.md": ("<!-- section: Changed -->\n\n" + _TABLE_HEAD
                  + "| `a.py --old-a` | Removed (argparse error) | drop it |\n"),
    "CR0002.md": ("<!-- section: Changed -->\n\n- A change (CR0002).\n\n" + _TABLE_HEAD
                  + "| `b.py --old-b` | Removed (argparse error) | drop it |\n"),
    "US0001.md": ("<!-- section: Added -->\n\n- A new thing (US0001).\n\n" + _TABLE_HEAD
                  + "| `c.py --old-c` | Removed (argparse error) | drop it |\n"),
}


def _release(text: str) -> list[str]:
    """The cut 6.1.0 section's lines."""
    return text.split("## [6.1.0]", 1)[1].split("## [6.0.0]", 1)[0].splitlines()


class V61LastLowsTests(unittest.TestCase):
    setUp = numeric.GoalNoteRatioNumericTests.setUp
    _close = numeric.GoalNoteRatioNumericTests._close
    named = staticmethod(numeric.GoalNoteRatioNumericTests.named)
    _record = residue.V61ReviewResidueTests._record

    def test_the_cut_places_every_hash4_block_cleanly(self) -> None:
        """AC1. MUTANTS: `_append_to_section` dropping the blank line before the next `###`
        heading (the table runs into `### Changed` and `### Fixed`: MD022, MD058); HEAD's
        compose, which gives Changed two sibling `#### Retired flags` headings (MD024) and puts
        CR0002's bullet hard against CR0001's heading (MD022, MD032). The control: every flag
        row is still read off the cut CHANGELOG, so a cut that drops a table also fails."""
        clog, text = cut._cut(self, dict(_FRAGMENTS))
        lines = _release(text)
        for i, line in enumerate(lines):
            if line.startswith("#"):
                with self.subTest(heading=line, at=i):
                    self.assertEqual("", lines[i - 1], f"no blank line above {line!r}\n{text}")
                    self.assertEqual("", lines[i + 1], f"no blank line below {line!r}\n{text}")
        headings = [ln for ln in lines if ln.startswith("#")]
        self.assertEqual(["### Added", "#### Retired flags", "### Changed", "#### Retired flags",
                          "### Fixed"], headings, text)
        changed = "\n".join(lines).split("### Changed", 1)[1].split("### Fixed", 1)[0]
        self.assertIn("- A change (CR0002).\n\n" + _TABLE_HEAD
                      + "| `a.py --old-a` | Removed (argparse error) | drop it |\n"
                      "| `b.py --old-b` | Removed (argparse error) | drop it |\n", changed,
                      "Changed's two tables are not one table under one heading")
        self.assertEqual(["c.py --old-c", "a.py --old-a", "b.py --old-b"],
                         retired_surface.changelog_flags(clog))
        try:
            lint = cut._markdownlint()
        except unittest.SkipTest:          # the structure above is asserted either way
            lint = None
        if lint:
            proc = subprocess.run([lint, "--config", str(cut.REPO / ".markdownlint.json"),
                                   str(clog)], capture_output=True, text=True, check=False,
                                  timeout=120)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr + text)

    def test_a_non_list_seats_value_is_named(self) -> None:
        """AC2. MUTANT: HEAD's loop over the value, which refuses a string by naming its first
        character and an object by naming its first key. The control: a list holding one good
        seat still records."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            for seats in ("qa|yes|x|yes", residue.SEAT):
                with self.subTest(seats=type(seats).__name__):
                    rc, said = self._record(root, {"goal": "one page is signed", "seats": seats})
                    self.assertEqual(2, rc, said)
                    self.assertIn("seats must be a list", said)
                    self.assertIn(type(seats).__name__, said)
                    self.assertNotIn("is not an object", said)
            self.assertFalse((root / "sdlc-studio" / ".local" / "goal-review.json").exists())
            rc, said = self._record(root, {"goal": "one page is signed",
                                           "seats": [residue.SEAT]})
            self.assertEqual(0, rc, said)

    def test_the_note_parser_is_linear_on_repeated_names(self) -> None:
        """AC3. MUTANT: HEAD's scan, which re-tries every measure name in a whitespace-free run
        and runs each attempt to the end of the run, so 20,000 characters of `tokens-` cost
        about 0.8 s. Timed around the close's own check, in the real close. The control: a
        wrong ratio before the run, and a right one after a name inside it, are still read."""
        mod = lean._live("sprint")
        real = mod.goal_note_contradiction
        spent: list[float] = []

        def timed(*a, **k):
            t = time.perf_counter()
            try:
                return real(*a, **k)
            finally:
                spent.append(time.perf_counter() - t)

        for i, unit in enumerate(("tokens-", "Tokens.", "token(")):
            run = (unit * (20_000 // len(unit) + 1))[:20_000]
            with self.subTest(unit=unit), \
                    unittest.mock.patch.object(mod, "goal_note_contradiction", timed):
                spent.clear()
                rc, lines, ratio = self._close(f"names{i}", f"Tokens 1.4x over plan; {run}")
                self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
                self.assertEqual(0, rc, "\n".join(lines))
                self.assertEqual(1, len(spent), "the close did not check the note")
                self.assertLess(spent[0], 0.25, f"the note check took {spent[0]:.2f}s")
                named = self.named(lines)
                self.assertEqual(1, len(named), lines)
                self.assertIn("1.4x", named[0])
        note = "tokens-tokens-tokens=1.46x more"
        self.assertEqual(["1.46x"], mod._note_ratios(note, ["Tokens"]))
        self.assertEqual(["1.46x"], mod._note_ratios(f"{'tokens-' * 50}tokens 1.46x",
                                                     ["Tokens"]))

    def test_a_name_spanning_words_is_tried_inside_a_dead_run(self) -> None:
        """AC3's neighbour. MUTANT: dropping `and not crosses` from the scan's skip, so a
        word-spanning name inside a run a failed one-word name made dead is passed over:
        `tokens-wall-clock span a b c 1.5x` reads [] for ['1.5x'], its ratio lying beyond
        `tokens`'s three-word reach. Driven on the measures the filed page carries, and through
        the real close, which then names nothing. The control: the same note with no `tokens-`
        prefix is read by either scan, so the pin is the skip, not the name."""
        mod = lean._live("sprint")
        note = "Tokens 1.7x over plan; tokens-wall-clock span a b c 1.5x"
        rc, lines, ratio = self._close("spanning", note)
        self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
        self.assertEqual(0, rc, "\n".join(lines))
        root = Path(self._tmp.name) / "spanning"
        page = lean._live("sprint_report").read_report(root, lean._read(root)["report"])
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        measures = [str(r["est_measure"]["value"]) for r in est["rows"]]
        self.assertIn("Wall-clock span", measures, "premise: the page carries the measure")
        named = self.named(lines)
        self.assertEqual(1, len(named), lines)
        self.assertIn("quotes 1.5x, which", named[0])
        self.assertEqual(["1.5x"],
                         mod._note_ratios("tokens-wall-clock span a b c 1.5x", measures))
        self.assertEqual(["1.5x"], mod._note_ratios("wall-clock span a b c 1.5x", measures))


if __name__ == "__main__":
    unittest.main()
