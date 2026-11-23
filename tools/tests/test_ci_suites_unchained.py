"""BG0968: CI ran tools/tests in the same `run:` block as the skill suite, one command after the
other, and the step's shell stops at the first failing command. A red skill suite therefore
hid every tools/tests failure: the second suite never ran, so a second defect survived the fix
of the first.

These tests run the ci job's suite step itself, under the shell GitHub runs an unconfigured
step with (`bash -e`), in a fixture where each suite is a stub that records it ran and exits
with the code the case asks for. Each suite must run whatever the other returned, and the step
must fail when either one does.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

# test-census-subject: .github/workflows/lint.yml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
SKILL_SUITE = "tools/skill-tests.sh"
TOOLS_SUITE = "--run-tests tools/tests/"
GATE_REL = ".claude/skills/sdlc-studio/scripts/gate.py"
#: What GitHub runs a `run:` step with on Linux when the step and the job name no shell.
STEP_SHELL = ("bash", "-e")


def _suite_steps() -> list[dict]:
    """The ci job's steps whose script runs either suite."""
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["ci"]["steps"]
    return [s for s in steps if SKILL_SUITE in str(s.get("run", ""))
            or TOOLS_SUITE in str(s.get("run", ""))]


def _run_step(step: dict, skill_exit: int, tools_exit: int) -> subprocess.CompletedProcess:
    """Run `step`'s script in a fixture whose two suites are stubs exiting as asked."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tools").mkdir()
        (root / SKILL_SUITE).write_text(f"echo SKILL-SUITE-RAN\nexit {skill_exit}\n",
                                        encoding="utf-8")
        gate = root / GATE_REL
        gate.parent.mkdir(parents=True)
        gate.write_text(f"import sys\nprint('TOOLS-SUITE-RAN')\nsys.exit({tools_exit})\n",
                        encoding="utf-8")
        script = root / "step.sh"
        script.write_text(step["run"], encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("SDLC_", "SKILL_"))}
        return subprocess.run([*STEP_SHELL, str(script)], cwd=root, env=env,
                              capture_output=True, text=True, timeout=60)


class SuitesUnchainedTests(unittest.TestCase):

    def setUp(self) -> None:
        steps = _suite_steps()
        self.assertEqual(1, len(steps), "one ci step runs the two suites; split across steps, "
                                        "this test must be taught the steps' `if:` conditions")
        self.step = steps[0]
        self.assertNotIn("shell", self.step, "the step's shell is the default this test runs")
        self.assertIn(SKILL_SUITE, self.step["run"])
        self.assertIn(TOOLS_SUITE, self.step["run"])

    def test_tools_tests_run_when_the_skill_suite_fails_and_both_results_are_reported(self):
        """AC1. MUTANT: the two commands put back one after the other with nothing holding the
        first one's failure, which stops the step before tools/tests runs."""
        r = _run_step(self.step, skill_exit=1, tools_exit=0)
        self.assertIn("SKILL-SUITE-RAN", r.stdout, r.stderr)
        self.assertIn("TOOLS-SUITE-RAN", r.stdout, "tools/tests did not run after the skill "
                                                   f"suite failed:\n{r.stdout}{r.stderr}")
        self.assertNotEqual(0, r.returncode, "the skill suite's failure was not reported")

    def test_the_suites_are_not_chained_whichever_one_fails(self):
        """AC2. Every combination of results: both suites always run, and the step fails
        exactly when one of them does. MUTANTS: the first suite's failure swallowed (the step
        green on a red skill suite); the step failing on a green pair; either suite dropped."""
        for skill_exit, tools_exit in ((0, 0), (1, 0), (0, 1), (1, 1), (3, 0)):
            with self.subTest(skill=skill_exit, tools=tools_exit):
                r = _run_step(self.step, skill_exit, tools_exit)
                self.assertIn("SKILL-SUITE-RAN", r.stdout, r.stderr)
                self.assertIn("TOOLS-SUITE-RAN", r.stdout, r.stderr)
                self.assertEqual(bool(skill_exit or tools_exit), r.returncode != 0,
                                 f"exit {r.returncode}:\n{r.stdout}{r.stderr}")


if __name__ == "__main__":
    unittest.main()
