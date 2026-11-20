"""The goal review refuses to brief from a traced persona card the persona standard holds, naming
the card, its failed rules and the remedy, and the plan names that card without listing its End
goals, still planning.

Driven through `sprint.main` and `persona_review.main`, the shipped entry points, in throwaway
trees built on the goal-trace fixture (BG0001; outcomes O1 and O2), with Maya Okafor Primary and
Jonah Reyes Secondary, each card carrying its own End goals.
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
import test_goal_review_testable_goals as tg  # noqa: E402 - the End goal card writer
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")
persona_review = loader.load_script("persona_review")

_MAYA = "sdlc-studio/personas/maya-okafor.md"
_MAYA_GOALS = ("Maya drives the batch to done", "Maya pauses only for her own decisions")
_JONAH_GOALS = ("Jonah upgrades without a surprise",)
_MAYA_GOAL = "Maya Okafor drives the batch to done"
_JONAH_GOAL = "Jonah Reyes upgrades without a surprise"


def _project(root: Path) -> None:
    s1._project(root, personas=())
    (root / "sdlc-studio" / "personas").mkdir(parents=True)
    tg._write_card(root, "Maya Okafor", "Primary",
                   [(_MAYA_GOALS[0], tg._PYTEST), (_MAYA_GOALS[1], None)])
    tg._write_card(root, "Jonah Reyes", "Secondary", [(_JONAH_GOALS[0], tg._HANA_VERIFY)])


def _record(root: Path, card: str, outcome: str, *rules: str) -> None:
    argv = ["record", "--card", card, "--outcome", outcome, "--reviewer", "Rowan Hart (qa)",
            "--run-by", "Tess Moreau", "--root", str(root)]
    for rule in rules:
        argv += ["--rule", rule]
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        rc = persona_review.main(argv)
    assert rc == 0, err.getvalue()


def _brief(root: Path, goal: str) -> tuple[int, str, str]:
    return tg._run(root, "goal-review", "brief", "--goal", goal, "--brief-worklist",
                   str(root / "worklist.txt"))


def _plan(root: Path, goal: str, *extra: str) -> tuple[int, str, str]:
    return tg._run(root, "plan", "--worklist", str(root / "worklist.txt"), "--sprint-goal", goal,
                   "--no-fetch", *extra)


class GoalReviewPersonaBlockTests(unittest.TestCase):

    def test_a_goal_traced_to_a_failed_card_is_not_briefed(self) -> None:
        """Mutants: list the traced End goals without asking `persona_review.blocking`, so the
        FAIL card frames the brief; refuse on any card's FAIL, so a goal naming only Jonah is
        refused for Maya's."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            _record(root, "sdlc-studio/personas/jonah-reyes.md", "pass")
            rc0, before, err0 = _brief(root, _MAYA_GOAL)
            _record(root, _MAYA, "fail", "persona-evidence", "persona-goal-scope")
            rc, out, err = _brief(root, _MAYA_GOAL)
            rc_j, out_j, err_j = _brief(root, _JONAH_GOAL)
        # Positive control: before the FAIL, the same goal is briefed with Maya's End goals.
        self.assertEqual(0, rc0, err0)
        self.assertIn(_MAYA_GOALS[0], before)
        # The FAIL refuses the goal that traces to Maya, with no brief printed.
        self.assertEqual(2, rc, out)
        self.assertEqual("", out)
        self.assertTrue(err.startswith("goal-review brief refused: "), err)
        self.assertIn(_MAYA, err)
        self.assertIn("persona-evidence, persona-goal-scope", err)
        self.assertIn("FAIL by Rowan Hart (qa)", err)
        self.assertIn(f"Run next: python3 {Path(persona_review.__file__).resolve()} brief "
                      f"--card {_MAYA} --seat ", err)
        for text in _MAYA_GOALS:
            self.assertNotIn(text, err)
        # A goal naming only Jonah, whose card passes, is briefed, and reads none of Maya's End
        # goals as sound.
        self.assertEqual(0, rc_j, err_j)
        self.assertIn(f"1. {_JONAH_GOALS[0]} - Verify: {tg._HANA_VERIFY}", out_j)
        for text in _MAYA_GOALS:
            self.assertNotIn(text, out_j)
        self.assertIn(f"Maya Okafor (Primary): refused by the persona standard ({_MAYA})", out_j)

    def test_the_plan_names_the_refused_card_and_still_plans(self) -> None:
        """Mutants: refuse the plan for the FAIL card (advice turned refusal); keep the refused
        card's End goals in the trace; print no line naming the card."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            rc0, out0, err0 = _plan(root, _MAYA_GOAL, "--format", "json")
            text_rc0, text0, text_err0 = _plan(root, _MAYA_GOAL)
            _record(root, _MAYA, "fail", "persona-evidence")
            rc, out, err = _plan(root, _MAYA_GOAL, "--format", "json")
            text_rc, text, text_err = _plan(root, _MAYA_GOAL)
        before, after = json.loads(out0), json.loads(out)
        # Positive control: unrefused, the trace lists Maya's End goals.
        self.assertEqual(0, rc0, err0)
        self.assertEqual(0, text_rc0, text_err0)
        self.assertEqual([_MAYA_GOALS[0], _MAYA_GOALS[1]],
                         [g["text"] for g in before["goal_trace"]["end_goals"]["Maya Okafor"]])
        self.assertNotIn(_MAYA, text0 + text_err0)
        # Refused: the same exit code and batch, one line naming the card, none of its End goals.
        self.assertEqual((rc0, text_rc0), (rc, text_rc), err + text_err)
        self.assertEqual([u["id"] for u in before["batch"]], [u["id"] for u in after["batch"]])
        self.assertEqual(before["count"], after["count"])
        named = [ln for ln in (text + text_err).splitlines() if _MAYA in ln]
        self.assertEqual(1, len(named), text + text_err)
        self.assertIn("refused by the persona standard", named[0])
        self.assertIn("persona-evidence", named[0])
        for text_ in _MAYA_GOALS:
            self.assertNotIn(text_, text + text_err)
            self.assertNotIn(text_, json.dumps(after))
        trace = after["goal_trace"]
        self.assertNotIn("Maya Okafor", trace.get("end_goals", {}))
        self.assertEqual([("Maya Okafor", _MAYA)],
                         [(r["name"], r["card"]) for r in trace["refused"]])
        self.assertEqual(["Maya Okafor (Primary)"],
                         [f"{s['name']} ({s['role'].capitalize()})" for s in trace["serves"]
                          if s["kind"] == "persona"])


if __name__ == "__main__":
    unittest.main()
