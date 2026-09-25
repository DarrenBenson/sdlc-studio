"""US0928: the seat reviewing a Sprint Goal is shown the PRD outcomes and the personas' End goals,
and the plan's own goal trace - reading, never a refusal (D0266, LC-008).

Driven through `sprint.main`, the shipped entry point, in throwaway project trees built on
US0927's fixture (S1).
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_lean_goal_trace as s1  # noqa: E402 - S1's fixture: the PRD and the plannable project

sprint = loader.load_script("sprint")

_MAYA_GOALS = ("Ship real features through a disciplined lifecycle, not ad-hoc edits",
               "Never lose the thread - know the true state of the work after any reset",
               "Drive a whole batch to done autonomously, pausing only when a decision is hers")
_JONAH_GOALS = ("Get a validated specification out of the existing code",
                "Adopt the lifecycle incrementally")
_TREVOR_GOALS = ("Drive delivery from a rich GUI with boards and swimlanes",)
_CARD = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
         "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n\n## {heading}\n\n"
         "*Most important first.*\n\n{goals}\n\n## Experience Goals\n\n- calm\n")
_LESSON = {"id": "LC-001", "class": "repair breaks its neighbour",
           "rule": "A repair masks the defect beside it.", "behaviour": "Re-check the neighbour.",
           "inject": ["review"], "hits": [], "state": "active", "recorded_run": "R"}


def _cards(root: Path) -> None:
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    for name, role, heading, goals in (
            ("Maya Okafor", "Primary", "End Goals", _MAYA_GOALS),
            ("Jonah Reyes", "Secondary", "End Goals", _JONAH_GOALS),
            ("Trevor Hale", "Negative", "End Goals (stated to exclude)", _TREVOR_GOALS)):
        listed = "\n".join(f"{i}. {g}" for i, g in enumerate(goals, 1))
        (pdir / f"{name.lower().replace(' ', '-')}.md").write_text(
            _CARD.format(name=name, role=role, heading=heading, goals=listed), encoding="utf-8")


def _fixture(root: Path, *, prd: str | None = s1._PRD, cards: bool = True) -> Path:
    """S1's plannable project, its persona cards carrying End goals, and one active lesson."""
    worklist = s1._project(root, prd=prd, personas=())
    if cards:
        _cards(root)
    (root / "sdlc-studio" / "lessons.jsonl").write_text(json.dumps(_LESSON) + "\n",
                                                        encoding="utf-8")
    return worklist


def _brief(root: Path, goal: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main(["goal-review", "brief", "--goal", goal, "--brief-worklist",
                          str(root / "worklist.txt"), "--root", str(root)])
    assert rc == 0, err.getvalue()
    return out.getvalue()


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines()]


class GoalSeatPrdTests(unittest.TestCase):

    def test_the_brief_carries_outcomes_and_end_goals(self) -> None:
        """Mutants: list outcome ids without their text; leave out the End goals; renumber
        them; list the Negative persona's goals as ones to serve."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            lines = _lines(_brief(root, "every open bug is fixed"))
        for oid, text in (("O1", s1._O1), ("O2", s1._O2)):
            self.assertIn(f"{oid} - {text}", lines)
        self.assertNotIn("O7", "\n".join(lines))      # a later section is not an outcome
        for name, role, goals in (("Maya Okafor", "Primary", _MAYA_GOALS),
                                  ("Jonah Reyes", "Secondary", _JONAH_GOALS)):
            head = lines.index(f"{name} ({role}):")
            self.assertEqual([f"{i}. {g}" for i, g in enumerate(goals, 1)],
                             lines[head + 1:head + 1 + len(goals)], name)
        declined = [ln for ln in lines if "Trevor Hale" in ln]
        self.assertEqual(1, len(declined), declined)
        self.assertIn("declined", declined[0])
        self.assertIn("Negative", declined[0])
        for goal in _TREVOR_GOALS:
            self.assertFalse(any(goal in ln for ln in lines), goal)

    def test_the_brief_states_the_plans_own_trace(self) -> None:
        """Mutants: a second matcher inside the brief (replacing `goal_trace` would not change
        it); a goal serving none rendered without asking the seat to name the outcome."""
        goal = "every open bug is fixed, advancing O2"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            # the plan's own trace of the same goal
            rc, out, err = s1._plan(root, goal, "--format", "json")
            self.assertEqual(0, rc, err)
            planned = json.loads(out)["goal_trace"]
            self.assertEqual([{"kind": "outcome", "id": "O2", "text": s1._O2}],
                             planned["serves"])
            traced = [ln for ln in _lines(_brief(root, goal)) if ln.startswith("Goal serves")]
            self.assertEqual([f"Goal serves (the plan's own trace): O2 - {s1._O2}"], traced)
            # replacing the plan's function changes the brief: there is no second matcher
            calls = []

            def fake(root_arg, goal_arg, serves=None):
                calls.append(goal_arg)
                return {"goal": goal_arg, "serves": [{"kind": "outcome", "id": "O1",
                                                      "text": "SENTINEL"}],
                        "unknown": [], "flagged": False,
                        "could_serve": {"outcomes": ["O1", "O2"], "personas": []}}

            with unittest.mock.patch.object(sprint, "goal_trace", fake):
                faked = _lines(_brief(root, goal))
            self.assertEqual([goal], calls)
            self.assertIn("Goal serves (the plan's own trace): O1 - SENTINEL", faked)
            self.assertFalse(any(s1._O2 in ln and ln.startswith("Goal serves") for ln in faked))
            # a goal that traces to none: said, and the seat is asked to name what it serves
            none = [ln for ln in _lines(_brief(root, "every open bug is fixed"))
                    if ln.startswith("Goal serves")]
            self.assertEqual(1, len(none), none)
            self.assertTrue(none[0].startswith("Goal serves: NONE"), none[0])
            for word in ("done_means", "note", "O1", "O2", "Maya Okafor"):
                self.assertIn(word, none[0])
            self.assertNotIn("Trevor Hale", none[0])

    def test_no_prd_says_so_and_keeps_the_brief(self) -> None:
        """Mutants: print nothing, or print the empty outcome and persona sections; drop or
        reword the batch, grooming or lessons lines."""
        goal = "every open bug is fixed"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            worklist = _fixture(root, prd="# PRD\n\n## 1. Project Overview\n\nNo outcomes.\n",
                                cards=False)
            lines = _brief(root, goal).rstrip("\n").split("\n")
            plan = sprint.build_plan(root, worklist=str(worklist), skip_personas=True)
            before = sprint._compose_seat_brief(
                plan, goal, sprint.lessons.phase_digest(root, "review")).split("\n")
        said = [ln for ln in lines if "nothing to trace" in ln]
        self.assertEqual(1, len(said), lines)
        self.assertIn("PRD outcomes", said[0])
        self.assertIn("persona", said[0])
        self.assertEqual(before, [ln for ln in lines if ln not in said])
        for expected in (f"Sprint Goal: {goal}", "Placeholder/ungroomed ACs: none - every unit "
                         "is groomed", "Shared-file clusters: none", "    Behaviour: Re-check "
                         "the neighbour."):
            self.assertIn(expected, lines)
        self.assertTrue(any(ln.startswith("Batch: 1 unit(s)") for ln in lines), lines)
        self.assertTrue(any(ln.startswith("Reachable end state: ") for ln in lines), lines)
        self.assertTrue(any(ln.startswith("  LC-001 ") for ln in lines), lines)
        self.assertFalse(any(ln.startswith("Goal serves") for ln in lines), lines)
        # half the context degrades to what is there, and says what is not
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, prd="# PRD\n\nNo outcomes.\n")
            lines = _lines(_brief(root, "Maya's open bugs are fixed"))
        self.assertTrue(any(ln.startswith("PRD outcomes: none") for ln in lines), lines)
        self.assertIn("Maya Okafor (Primary):", lines)
        self.assertIn("Goal serves (the plan's own trace): Maya Okafor (Primary)", lines)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root, cards=False)
            lines = _lines(_brief(root, "every open bug is fixed"))
        self.assertIn(f"O1 - {s1._O1}", lines)
        self.assertTrue(any(ln.startswith("Personas: none") for ln in lines), lines)

    def test_record_adds_no_required_field(self) -> None:
        """Mutant: `goal-review record` demands a `serves` answer once the PRD is read."""
        goal = "every open bug is fixed"
        three = {"achievable": "yes", "done_means": "every bug Fixed", "one_increment": "yes"}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            fields = root / "fields.json"
            fields.write_text(json.dumps({"goal": goal, "seats": [{"seat": "qa", **three}]}),
                              encoding="utf-8")
            for argv in (["--seat", "product|yes|every bug Fixed|yes"],
                         ["--fields-file", str(fields)]):
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                    rc = sprint.main(["goal-review", "record", "--goal", goal, *argv,
                                      "--root", str(root)])
                self.assertEqual(0, rc, out.getvalue())
            rounds = json.loads((root / "sdlc-studio" / ".local" / "goal-review.json")
                                .read_text(encoding="utf-8"))["rounds"]
        self.assertEqual([[{"seat": "product", **three}], [{"seat": "qa", **three}]],
                         [r["seats"] for r in rounds])


if __name__ == "__main__":
    unittest.main()
