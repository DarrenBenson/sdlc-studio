"""BG0765: the goal trace reports a `--serves` value even with nothing on disk to trace against,
reads no unfilled template placeholder as an outcome, persona or End goal, and bounds outcomes
to the `## Outcomes` section - advice, never a refusal (D0266, LC-008).

Driven through `sprint.main`, the shipped entry point, in throwaway project trees built on
US0927's fixture (S1) and US0928's brief helper.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_lean_goal_seat_prd as s2  # noqa: E402 - US0928's goal-review brief helper
import test_lean_goal_trace as s1  # noqa: E402 - US0927's plannable project and PRD

sprint = loader.load_script("sprint")

_TEMPLATES = Path(sprint.__file__).resolve().parent.parent / "templates"
_NO_OUTCOMES = "# PRD\n\n## 1. Project Overview\n\nNo outcomes here.\n"


def _written(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json")
                      .read_text(encoding="utf-8").replace(str(root), "<root>"))


class GoalTraceFollowupTests(unittest.TestCase):

    def test_serves_is_reported_with_nothing_to_trace_against(self) -> None:
        """Mutant: return before reading --serves when the PRD lists no outcomes and there are
        no persona cards (the value is then dropped silently)."""
        plans = {}
        for label, extra in (("bare", ()), ("serves", ("--serves", "O1,Maya"))):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                s1._project(root, prd=_NO_OUTCOMES, personas=())
                rc, out, err = s1._plan(root, "every open bug is fixed", *extra, "--write")
                plans[label] = (rc, out, err, _written(root))
        rc, out, err, written = plans["serves"]
        self.assertEqual(0, rc, err)
        self.assertEqual(plans["bare"][0], rc)
        self.assertEqual(plans["bare"][3]["batch"], written["batch"])
        self.assertEqual(["O1", "Maya"], written["goal_trace"]["unknown"])
        lines = [ln.strip() for ln in out.splitlines()]
        self.assertIn("--serves O1: the PRD lists no outcome O1", lines)
        self.assertIn("--serves Maya: no persona card is named Maya", lines)
        # without --serves such a project still gets no line (US0927 AC5)
        self.assertEqual([], s1._serves_lines(plans["bare"][1]))
        self.assertNotIn("--serves", plans["bare"][1])

    def test_unfilled_placeholders_are_not_outcomes_or_personas(self) -> None:
        """Mutants: read a `{{...}}` outcome, persona heading or End goal as a real one."""
        prd = (_TEMPLATES / "core" / "prd.md").read_text(encoding="utf-8")
        card = (_TEMPLATES / "personas" / "persona-template.md").read_text(encoding="utf-8")
        # a card named and cast, its End goals left as the template's placeholders
        half = card.replace("{{full_name}}", "Maya Okafor", 1)
        half = re.sub(r"(\|\s*\*\*Cast role\*\*\s*\|)[^|]*\|", r"\1 Primary |", half, count=1)
        self.assertIn("1. {{", half)
        # an outcome partly filled - the claim written, the persona and End goal left as
        # placeholders - is still not one (LC-002: `"{{" not in text` catches this; a filter
        # that only checks the text does not START with `{{` would let it through)
        prd_half_outcome = prd.replace(
            "- **O1:** {{outcome_1}} ({{persona_name}}, End goal {{end_goal_number}})",
            "- **O1:** Ship the deploy pipeline ({{persona_name}}, End goal {{end_goal_number}})",
        )
        self.assertIn("- **O1:** Ship the deploy pipeline ({{persona_name}}", prd_half_outcome)
        with tempfile.TemporaryDirectory() as d0:
            root0 = Path(d0)
            s1._project(root0, prd=prd_half_outcome, personas=())
            self.assertNotIn("O1", sprint.prd_outcomes(root0))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root, prd=prd, personas=())
            pdir = root / "sdlc-studio" / "personas"
            pdir.mkdir()
            (pdir / "unfilled.md").write_text(card, encoding="utf-8")
            (pdir / "maya-okafor.md").write_text(half, encoding="utf-8")
            self.assertEqual({}, sprint.prd_outcomes(root))
            cards = sprint.persona_cards(root)
            self.assertEqual([("Maya Okafor", "primary", [])],
                             [(c["name"], c["role"], c["end_goals"]) for c in cards])
            # traced: --serves O1 names no outcome; offered: nothing holding a placeholder
            trace = s1._json(root, "every open bug is fixed", "--serves", "O1")["goal_trace"]
            self.assertEqual([], trace["serves"])
            self.assertEqual(["O1"], trace["unknown"])
            self.assertEqual({"outcomes": [], "personas": ["Maya Okafor"]}, trace["could_serve"])
            rc, out, err = s1._plan(root, "every open bug is fixed", "--serves", "O1")
            self.assertEqual(0, rc, err)
            self.assertNotIn("{{", "\n".join(s1._serves_lines(out)))
            # shown: the goal-review brief lists no placeholder outcome, persona or End goal
            brief = s2._lines(s2._brief(root, "every open bug is fixed"))
            start = brief.index("PRD outcomes: none - sdlc-studio/prd.md lists no `## Outcomes`")
            served = brief[start:next(i for i, ln in enumerate(brief)
                                      if ln.startswith("Goal serves")) + 1]
            self.assertIn("Maya Okafor (Primary):", served)
            self.assertIn("(no End goals on the card)", served)
            self.assertFalse([ln for ln in served if "{{" in ln], served)

    def test_an_outcome_outside_the_section_is_ignored(self) -> None:
        """Mutant: a parser that ignores the `## Outcomes` section bounds and reads the O7 item
        S1's PRD carries under `## 3. Feature Inventory`."""
        self.assertIn("- **O7:**", s1._PRD)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            self.assertEqual(["O1", "O2"], list(sprint.prd_outcomes(root)))
            trace = s1._json(root, "every open bug is fixed", "--serves", "O7")["goal_trace"]
            self.assertEqual(["O1", "O2"], trace["could_serve"]["outcomes"])
            self.assertEqual(["O7"], trace["unknown"])
            self.assertTrue(trace["flagged"])


if __name__ == "__main__":
    unittest.main()
