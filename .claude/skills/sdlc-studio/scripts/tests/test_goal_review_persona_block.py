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
_JONAH = "sdlc-studio/personas/jonah-reyes.md"
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

    def test_a_card_that_is_not_utf8_is_named_and_nothing_tracebacks(self) -> None:
        """Mutants: the strict UTF-8 read reached again from the brief or the plan (a
        UnicodeDecodeError traceback); the unreadable card judged by no rule, so the plan names
        nothing; its line without the remedy that saves it as UTF-8."""
        runs = {}
        with tempfile.TemporaryDirectory() as d:
            for name in ("utf-8", "cp1252"):
                root = Path(d) / name
                root.mkdir()
                _project(root)
                if name == "cp1252":
                    card = root / _JONAH
                    card.write_bytes(card.read_bytes().replace(b"Somebody.", b"Jos\xe9."))
                runs[name] = {
                    "brief": _brief(root, _MAYA_GOAL),
                    "plan": _plan(root, _MAYA_GOAL, "--format", "json"),
                    "text": _plan(root, _MAYA_GOAL),
                    "skip": _plan(root, _MAYA_GOAL, "--skip-personas"),
                }
        ok, bad = runs["utf-8"], runs["cp1252"]
        # The UTF-8 control briefs and plans; the same tree with one cp1252 byte does too.
        for key in ("brief", "plan", "text", "skip"):
            with self.subTest(run=key):
                self.assertEqual(0, ok[key][0], ok[key][2])
                self.assertEqual(0, bad[key][0], bad[key][2])
                self.assertNotIn("Traceback", bad[key][1] + bad[key][2])
        self.assertIn(_MAYA_GOALS[0], bad["brief"][1])
        self.assertEqual([u["id"] for u in json.loads(ok["plan"][1])["batch"]],
                         [u["id"] for u in json.loads(bad["plan"][1])["batch"]])
        # The plan names the card it cannot read, the byte's line and how to fix it.
        named = [ln for ln in (bad["text"][1] + bad["text"][2]).splitlines() if _JONAH in ln]
        self.assertEqual(1, len(named), bad["text"][1] + bad["text"][2])
        self.assertTrue(named[0].startswith(f"persona card blocked: {_JONAH} breaks the "
                                            "persona standard - card-not-utf8 (line "), named[0])
        self.assertIn("0xe9", named[0])
        self.assertIn(f"Run next: save {_JONAH} as UTF-8", named[0])
        self.assertEqual([], [ln for ln in (ok["text"][1] + ok["text"][2]).splitlines()
                              if ln.startswith("persona card blocked:")])

    def test_a_goal_naming_a_held_card_and_a_passing_one_is_refused(self) -> None:
        """Mutant: refuse only when no traced persona is left to read (`and "end_goals" not in
        trace`), so a goal naming Maya beside a passing Jonah is briefed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            _record(root, "sdlc-studio/personas/jonah-reyes.md", "pass")
            _record(root, _MAYA, "fail", "persona-evidence")
            rc, out, err = _brief(root, "Maya Okafor and Jonah Reyes upgrade without a surprise")
        self.assertEqual(2, rc, out)
        self.assertEqual("", out)
        self.assertIn(f"traces to Maya Okafor, whose card the persona standard refuses", err)
        self.assertNotIn("traces to Jonah Reyes", err)

    def test_a_card_the_registry_contradicts_is_refused_without_a_fail(self) -> None:
        """Mutant: the refusal reads only the ledger (no blocking findings passed to
        `held_cards`), so a card breaking a blocking rule frames the brief."""
        registry = ("# Persona Index\n\n## Primary\n\n- [Maya Okafor](maya-okafor.md) - x\n\n"
                    "## {role}\n\n- [Jonah Reyes](jonah-reyes.md) - y\n")
        results = {}
        with tempfile.TemporaryDirectory() as d:
            for role in ("Secondary", "Primary"):
                root = Path(d) / role
                root.mkdir()
                _project(root)
                (root / "sdlc-studio" / "personas" / "index.md").write_text(
                    registry.format(role=role), encoding="utf-8")
                results[role] = _brief(root, _JONAH_GOAL)
        # Positive control: the registry agreeing with Jonah's card, the goal is briefed.
        self.assertEqual(0, results["Secondary"][0], results["Secondary"][2])
        rc, out, err = results["Primary"]
        self.assertEqual(2, rc, out)
        self.assertEqual("", out)
        self.assertIn(_JONAH, err)
        self.assertIn("persona-registry-role", err)


if __name__ == "__main__":
    unittest.main()
