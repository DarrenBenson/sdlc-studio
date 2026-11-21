"""BG1107: an End goal written across several lines reaches every reader whole.

A persona card wraps a long End goal onto an indented next line. The reader kept the numbered
line and dropped the rest, so the goal-review brief handed the seats half a sentence ending in a
comma. These read a card whose End goals wrap through `sprint._end_goals` and `persona_cards`, and
drive `sprint.py goal-review brief` through `sprint.main` on the goal-trace fixture.

MUTANTS, each of which a test here fails on: (1) the continuation lines are dropped, as before;
(2) a nested `Verify` line is joined into the goal's text; (3) a blank line no longer ends the
goal, so the paragraph after the list is read into its last goal; (4) a new numbered line is
joined into the goal above it; (5) a heading deeper than `##`, which leaves the End Goals
section open, and the lines under it are joined into the goal above it; (6) any `#`-led line is
taken for a heading, so a goal wrapping onto `#123 before the tag is cut` is cut off before it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_goal_review_testable_goals as tg  # noqa: E402 - the brief runner
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")

_FIRST = ("A push is judged against exactly the commit pushed in about the ten minutes a gate "
          "host takes, not the hour it took on a workstation shared with agent sessions")
_SECOND = ("A fix landed here is in force in the installed copy the same day, so no fix is "
           "believed shipped while it runs nowhere")
_THIRD = "Main is never left red and unread"

_CARD = (
    "# Rowan Vale\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
    "| **Cast role** | Primary |\n\n## Who They Are\n\nSomebody.\n\n## End Goals\n\n"
    "*What they are trying to accomplish, most important first.*\n\n"
    "1. A push is judged against exactly the commit pushed in about the ten minutes a gate host\n"
    "   takes,\n"
    "   not the hour it took on a workstation shared with agent sessions\n"
    "2. A fix landed here is in force in the installed copy the same day, so no fix is\n"
    "believed shipped while it runs nowhere\n"
    "   - **Verify:** pytest tests/test_fixed.py::FixedTests::test_closed\n"
    "3. Main is never left red and unread\n\n"
    "A paragraph after the list that belongs to no goal.\n\n## Experience Goals\n\n- calm\n")


class EndGoalsWrapTests(unittest.TestCase):

    def test_a_wrapped_end_goal_is_returned_whole(self) -> None:
        goals = sprint._end_goals(_CARD)
        self.assertEqual([("1", _FIRST), ("2", _SECOND), ("3", _THIRD)], goals,
                         "a wrapped End goal lost its continuation lines, or a line that is no "
                         "part of it (a Verify, the paragraph after the list) was joined in")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root, personas=())
            (root / "sdlc-studio" / "personas").mkdir(parents=True)
            (root / "sdlc-studio" / "personas" / "rowan-vale.md").write_text(_CARD,
                                                                             encoding="utf-8")
            card = next(c for c in sprint.persona_cards(root) if c["name"] == "Rowan Vale")
            self.assertEqual([_FIRST, _SECOND, _THIRD], [g.text for g in card["goals"]],
                             "the card's goals carry the cut text the brief and the trace read")
            self.assertEqual("pytest tests/test_fixed.py::FixedTests::test_closed",
                             card["goals"][1].verify,
                             "joining the wrapped line lost the goal's own Verify")
            rc, out, err = tg._run(root, "goal-review", "brief", "--goal",
                                   "Rowan Vale ships the fix", "--brief-worklist",
                                   str(root / "worklist.txt"))
        self.assertEqual(0, rc, err)
        self.assertIn(f"1. {_FIRST}", out, out)
        self.assertIn(f"2. {_SECOND}", out, out)
        self.assertNotIn("gate host\n", out, "the brief still cuts the goal at the card's wrap")

    def test_a_deeper_heading_ends_the_goal_above_it(self) -> None:
        """A `###` or `####` heading does not end the End Goals section, so the goal after it
        is still read, but it ends the wrapped goal above it: neither it nor its lines join. A
        line led by `#` and no space, such as an issue number, is no heading and is joined."""
        card = ("# X\n\n## End Goals\n\n1. Close every bug the release names in\n"
                "#123 before the tag is cut\n### Detail\nmore\n"
                "2. Goal two wraps\n   onto there\n#### Deeper\nstill more\n")
        self.assertEqual([("1", "Close every bug the release names in #123 before the tag is cut"),
                          ("2", "Goal two wraps onto there")],
                         sprint._end_goals(card),
                         "a heading, or a line under it, was read into the goal above it, or a "
                         "`#`-led line that is no heading was cut off as one")


if __name__ == "__main__":
    unittest.main()
