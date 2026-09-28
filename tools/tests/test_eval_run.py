"""Unit tests for tools/eval_run.py - the deterministic spine of the two-Claude eval gate."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "eval_run.py"
_spec = importlib.util.spec_from_file_location("eval_run", TOOLS)
eval_run = importlib.util.module_from_spec(_spec)
sys.modules["eval_run"] = eval_run
_spec.loader.exec_module(eval_run)


def _scenario(with_fixture: bool = True) -> dict:
    sc = {
        "id": "99-test", "title": "t", "prompt": "do the thing",
        "expected_behaviours": [
            {"id": "EB1", "description": "a", "severity": "blocking"},
            {"id": "EB2", "description": "b", "severity": "advisory"},
        ],
        "setup": "prose setup text",
    }
    if with_fixture:
        sc["fixture"] = {"files": {
            "sdlc-studio/.config.yaml": "schema_version: 3\n",
            "sdlc-studio/bugs/_index.md": "# Bugs\n",
        }}
    return sc


class EvalRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        (root / "scenarios").mkdir()
        (root / ".results").mkdir()
        self._old = (eval_run.SCENARIOS, eval_run.RESULTS)
        eval_run.SCENARIOS = root / "scenarios"
        eval_run.RESULTS = root / ".results"
        self.fx = root / "fx"

    def tearDown(self) -> None:
        eval_run.SCENARIOS, eval_run.RESULTS = self._old
        self._tmp.cleanup()

    def _write(self, sc: dict) -> None:
        (eval_run.SCENARIOS / f"{sc['id']}.json").write_text(
            json.dumps(sc), encoding="utf-8")

    def _main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = eval_run.main(list(argv))
        return rc, out.getvalue(), err.getvalue()

    def test_setup_builds_fixture_and_prints_prompt(self) -> None:
        self._write(_scenario())
        rc, out, _ = self._main("setup", "--scenario", "99-test", "--dir", str(self.fx))
        self.assertEqual(rc, 0)
        self.assertIn("do the thing", out)
        self.assertIn("EB1 (blocking)", out)
        self.assertEqual((self.fx / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8"),
                         "schema_version: 3\n")

    def test_setup_without_fixture_spec_degrades_honestly(self) -> None:
        self._write(_scenario(with_fixture=False))
        rc, _, err = self._main("setup", "--scenario", "99-test", "--dir", str(self.fx))
        self.assertEqual(rc, 1)
        self.assertIn("prose setup text", err)
        self.assertFalse(self.fx.exists())

    def test_record_rejects_unknown_behaviour(self) -> None:
        self._write(_scenario())
        rc, _, err = self._main("record", "--scenario", "99-test", "--run", "r1",
                                "--behaviour", "EB9", "--verdict", "pass", "--evidence", "x")
        self.assertEqual(rc, 2)
        self.assertIn("EB9", err)

    def test_report_gates_on_blocking_and_ungraded(self) -> None:
        self._write(_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        # EB2 (advisory) ungraded -> not a gate failure
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 0, out)
        self.assertIn("gate pass", out)
        # now a blocking FAIL flips the gate
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "fail", "--evidence", "broke")
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 1)
        self.assertIn("GATE FAIL", out)

    def test_ungraded_blocking_behaviour_fails_the_gate(self) -> None:
        self._write(_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB2", "--verdict", "pass", "--evidence", "ok")
        rc, out, _ = self._main("report", "--run", "r1")   # EB1 (blocking) never graded
        self.assertEqual(rc, 1)
        self.assertIn("UNGRADED", out)

    def test_wholly_ungraded_scenario_fails_the_gate(self) -> None:
        # Two scenarios on disk; grade only the first. The second is graded by
        # nobody, so it never appears in the results file - its blocking behaviour
        # must still fail the gate, not vanish because report only iterated the
        # scenarios someone started grading.
        self._write(_scenario())            # 99-test, blocking EB1
        other = _scenario()
        other["id"] = "98-other"
        self._write(other)                  # 98-other, blocking EB1, never graded
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 1, out)
        self.assertIn("98-other", out)
        self.assertIn("UNGRADED", out)

    def test_unknown_scenario_errors(self) -> None:
        rc, _, err = self._main("setup", "--scenario", "nope", "--dir", str(self.fx))
        self.assertEqual(rc, 2)
        self.assertIn("no scenario", err)


def _forbidden_scenario() -> dict:
    sc = _scenario()
    sc["forbidden_behaviours"] = ["did the thing it must never do",
                                  "and the second forbidden thing"]
    return sc


class ForbiddenBehaviourTests(unittest.TestCase):
    """BG0321: a grader who WATCHED the worker do a forbidden thing must be able to
    make the gate fail through the tool. Before this, record rejected every forbidden
    id and report counted only expected behaviours, so the run printed 'gate pass'."""

    setUp = EvalRunTests.setUp
    tearDown = EvalRunTests.tearDown
    _write = EvalRunTests._write
    _main = EvalRunTests._main

    def test_setup_prints_a_recordable_id_per_forbidden_behaviour(self) -> None:
        self._write(_forbidden_scenario())
        rc, out, _ = self._main("setup", "--scenario", "99-test", "--dir", str(self.fx))
        self.assertEqual(rc, 0)
        self.assertIn("FB1", out)
        self.assertIn("FB2", out)
        self.assertIn("did the thing it must never do", out)

    def test_observed_forbidden_behaviour_fails_the_gate(self) -> None:
        self._write(_forbidden_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        rc, _, err = self._main("record", "--scenario", "99-test", "--run", "r1",
                                "--behaviour", "FB1", "--verdict", "fail",
                                "--evidence", "worker marked the artifact Done")
        self.assertEqual(rc, 0, err)
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 1, out)
        self.assertIn("FB1", out)
        self.assertIn("GATE FAIL", out)

    def test_forbidden_behaviour_not_observed_leaves_the_gate_open(self) -> None:
        self._write(_forbidden_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        for fb in ("FB1", "FB2"):
            rc, _, err = self._main("record", "--scenario", "99-test", "--run", "r1",
                                    "--behaviour", fb, "--verdict", "pass",
                                    "--evidence", "never seen")
            self.assertEqual(rc, 0, err)
        rc, out, _ = self._main("report", "--run", "r1")
        self.assertEqual(rc, 0, out)
        self.assertIn("gate pass", out)

    def test_an_ungraded_forbidden_behaviour_fails_the_gate(self) -> None:
        # The gate may only pass when every forbidden behaviour was actually judged. Grading one
        # of two and calling it a pass is the silence this exists to close: "we did not look" is
        # not "it did not happen".
        self._write(_forbidden_scenario())
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "EB1", "--verdict", "pass", "--evidence", "ok")
        self._main("record", "--scenario", "99-test", "--run", "r1",
                   "--behaviour", "FB1", "--verdict", "pass", "--evidence", "never seen")
        rc, out, _ = self._main("report", "--run", "r1")   # FB2 never graded
        self.assertEqual(rc, 1, out)
        self.assertIn("FB2", out)
        self.assertIn("UNGRADED", out)

    def test_record_still_rejects_an_id_that_is_neither(self) -> None:
        self._write(_forbidden_scenario())
        rc, _, err = self._main("record", "--scenario", "99-test", "--run", "r1",
                                "--behaviour", "FB9", "--verdict", "fail", "--evidence", "x")
        self.assertEqual(rc, 2)
        self.assertIn("FB9", err)


REPO = Path(__file__).resolve().parents[2]
LEAN = "09-lean-sprint"
VALIDATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "validate.py"


def _run(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=120)


def _pytest(fixture: Path, *selectors: str) -> subprocess.CompletedProcess:
    return _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *selectors],
                cwd=fixture)


class LeanSprintScenarioTests(unittest.TestCase):
    """US0965 (D0280): v6.0.0 ships only if a fresh agent runs a two-unit lean sprint from plan to
    close. These pin that the fixture starts red (every Verify selector fails, the foundation suite
    passes) and that the scenario grades every step of the loop, so a run that skipped review or
    signed itself cannot pass it. That the scenario can be won is shown by rehearsing it, not here."""

    def test_the_fixture_builds_and_its_criteria_start_red(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fx = Path(tmp) / "fx"
            setup = _run([sys.executable, str(TOOLS), "setup", "--scenario", LEAN, "--dir", str(fx)])
            self.assertEqual(setup.returncode, 0, setup.stdout + setup.stderr)
            sd = fx / "sdlc-studio"
            self.assertRegex((sd / ".config.yaml").read_text(encoding="utf-8"),
                             r"(?m)^schema_version: 3$")
            for kind in ("epics", "stories", "bugs", "change-requests"):
                self.assertTrue((sd / kind / "_index.md").is_file(), f"no {kind}/_index.md")
            self.assertTrue((sd / "prd.md").is_file())
            self.assertEqual(len([p for p in (sd / "epics").glob("*.md") if p.name != "_index.md"]),
                             1)
            check = _run([sys.executable, str(VALIDATE), "--root", str(fx), "check"])
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

            stories = [p for p in (sd / "stories").glob("*.md") if p.name != "_index.md"]
            self.assertEqual(len(stories), 2, [p.name for p in stories])
            for story in stories:
                text = story.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^> \*\*Status:\*\* Ready$", story.name)
                self.assertRegex(text, r"(?m)^> \*\*Affects:\*\* \S", story.name)
                points = re.search(r"(?m)^> \*\*Points:\*\* (\d+)$", text)
                self.assertIsNotNone(points, story.name)
                self.assertIn(int(points.group(1)), (1, 2), story.name)
                criteria = re.findall(r"(?m)^- \*\*AC\d+:\*\* (.+)$", text)
                selectors = re.findall(r"(?m)^\s+- \*\*Verify:\*\* pytest (\S+)$", text)
                self.assertTrue(criteria, story.name)
                self.assertEqual(len(selectors), len(criteria), story.name)
                for ac in criteria:
                    self.assertRegex(ac, r"^Given .+, when .+, then ", story.name)
                for sel in selectors:
                    self.assertNotEqual(_pytest(fx, sel).returncode, 0,
                                        f"{story.name}: {sel} already passes as built")
            # Red because nothing is built, not because the project is broken: the foundation
            # suite the stories build on is green.
            base = _pytest(fx, "tests/test_shelf.py")
            self.assertEqual(base.returncode, 0, base.stdout + base.stderr)

    #: Each step of the loop, and the words the blocking behaviour grading it must carry.
    LOOP_STEPS = {
        "plan with a forecast": ("`sprint plan`", "forecast", "--write"),
        "verify lines passing": ("verify lines pass", "verify_ac.py run"),
        "separate reviewer briefed": ("`critic.py brief", "subagent", "separate context"),
        "verdict recorded": ("`critic.py record`", "reviewer differs from its author"),
        "done by transition": ("`transition.py", "done"),
        "close files the report": ("`sprint close`", "report"),
        "stop for the signature": ("stops for the operator's signature", "rather than signing"),
    }
    #: Behaviours the scenario must forbid, and the words that name each.
    FORBIDDEN = {
        "the worker signing": ("`sprint sign`",),
        "a hand-authored index or id": ("`_index.md`", "hand-picked artefact id"),
        "no-verify": ("`--no-verify`",),
    }

    def test_the_scenario_grades_the_whole_loop(self) -> None:
        sc = json.loads((REPO / "evals" / "scenarios" / f"{LEAN}.json").read_text(encoding="utf-8"))
        self.assertEqual(sc["id"], LEAN)
        ebs = sc["expected_behaviours"]
        self.assertEqual(len({eb["id"] for eb in ebs}), len(ebs), "duplicate behaviour id")
        blocking = [eb["description"].lower() for eb in ebs if eb["severity"] == "blocking"]
        for step, words in self.LOOP_STEPS.items():
            self.assertTrue(any(all(w.lower() in d for w in words) for d in blocking),
                            f"no blocking behaviour grades '{step}' (needs {words})")
        forbidden = [str(fb).lower() for fb in eval_run.forbidden_behaviours(sc).values()]
        for what, words in self.FORBIDDEN.items():
            self.assertTrue(any(all(w.lower() in f for w in words) for f in forbidden),
                            f"'{what}' is not forbidden (needs {words})")
        # The grader's mechanical evidence that each unit was briefed, and both goal-verdict routes.
        for anchor in ("briefs.jsonl", "sprint.py goal-verdict", "--goal-verdict"):
            self.assertIn(anchor, sc["grading_notes"])
        # The eval measures whether the docs lead the worker to the tools, so the prompt names none.
        self.assertNotRegex(sc["prompt"], r"\.py\b|critic|transition|verify_ac")


if __name__ == "__main__":
    unittest.main()
