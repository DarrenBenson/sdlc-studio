"""The scheduled corpus lane prints each red criterion's own verifier output, and `verify_ac run`
takes the per-verifier budget a runner sets from its measured speed.

The weekly lane read two criteria red and its log named them only by id, so the red could not
be read without re-running the criteria on a runner like CI's. `verify_ac run` held every
verifier to a fixed 120 s whatever the runner, so a check that outlives it on a slower machine
read red there and green on the workstation.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_corpus_verify_red_detail.py
"""
# test-census-subject: tools/verify-corpus.sh
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
_spec = importlib.util.spec_from_file_location("verify_ac", SCRIPTS / "verify_ac.py")
assert _spec and _spec.loader
verify_ac = importlib.util.module_from_spec(_spec)
sys.modules["verify_ac"] = verify_ac
_spec.loader.exec_module(verify_ac)
import gate  # noqa: E402 - reachable once verify_ac has put scripts/ on the path

_RUNNER_TEMP = "${{ runner.temp }}"


def _story(root: Path, rec: str, status: str, verify: str, extra: str = "") -> Path:
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    path = stories / f"{rec}-x.md"
    path.write_text(f"# {rec}: s\n\n> **Status:** {status}\n\n## Acceptance Criteria\n\n"
                    f"### AC1: a\n\n- **Given** x\n- **When** y\n- **Then** z\n"
                    f"- **Verify:** {verify}\n{extra}", encoding="utf-8")
    return path


def _env() -> dict:
    return {k: v for k, v in os.environ.items()
            if not k.startswith("GIT_") and k not in (verify_ac.RED_DETAIL_ENV,
                                                       verify_ac.VERIFY_TIMEOUT_ENV)}


def _steps() -> list[dict]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["corpus-verify"]["steps"]


def _step_env(step: dict, temp: Path) -> dict:
    env = {k: str(v).replace(_RUNNER_TEMP, str(temp)) for k, v in (step.get("env") or {}).items()}
    assert not any("${{" in v for v in env.values()), env
    return env


class CorpusVerifyRedDetailTests(unittest.TestCase):
    """AC1: a red criterion is printed in the job's log with its verifier's own output."""

    RED = "shell echo red-out-marker; echo red-err-marker >&2; echo run >> runs.txt; exit 3"

    def _verify(self, root: Path, path: Path, log: Path | None, **kw) -> verify_ac.StoryReport:
        env = {**_env(), **({verify_ac.RED_DETAIL_ENV: str(log)} if log else {})}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            return verify_ac.verify_story(path, dry_run=True, timeout=60, repo_root=root, **kw)

    def test_the_job_prints_each_red_criterion_with_its_verifier_output(self) -> None:
        """Driven as the job runs it: the verification step's own command and environment over a
        corpus holding one red criterion on a Done story, one on a Ready story and one green,
        then the step that runs when it fails."""
        steps = _steps()
        verify = next(s for s in steps if "verify-corpus.sh" in str(s.get("run", "")))
        after = steps[steps.index(verify) + 1:]
        detail = [s for s in after if verify_ac.RED_DETAIL_ENV in str(s.get("run", ""))]
        self.assertEqual(len(detail), 1, "no step after the verification prints the red detail")
        # `failure()` alone is true when any earlier step failed, and that skips the
        # verification: the detail step reads the verification step's own outcome too.
        self.assertTrue(verify.get("id"), "the verification step has no id to read it by")
        self.assertEqual(detail[0].get("if"),
                         f"failure() && steps.{verify['id']}.outcome == 'failure'",
                         "the detail step must run when, and only when, the verification fails")
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = tmp / "corpus"
            _story(root, "US0001", "Done", self.RED)
            _story(root, "US0002", "Ready", "shell echo unbuilt-marker; exit 1")
            _story(root, "US0003", "Done", "shell echo green-marker")
            baseline = tmp / "baseline.txt"
            baseline.write_text("red-criteria|0|r|\ndead-stamps|0|d|\n", encoding="utf-8")
            temp = tmp / "runner-temp"
            temp.mkdir()
            env = {**_env(), **_step_env(verify, temp), "VERIFY_CORPUS_ROOT": str(root),
                   "VERIFY_CORPUS_BASELINE": str(baseline)}
            self.assertEqual(_step_env(detail[0], temp).get(verify_ac.RED_DETAIL_ENV),
                             env.get(verify_ac.RED_DETAIL_ENV),
                             "the two steps name different detail files")
            lane = subprocess.run(["bash", "-e", "-c", verify["run"]], cwd=REPO, env=env,
                                  capture_output=True, text=True, timeout=900, check=False)
            self.assertNotEqual(lane.returncode, 0, lane.stdout + lane.stderr)
            self.assertIn("NEW: US0001::AC1", lane.stderr, lane.stdout + lane.stderr)
            shown = subprocess.run(["bash", "-e", "-c", detail[0]["run"]], cwd=REPO,
                                   env={**_env(), **_step_env(detail[0], temp)},
                                   capture_output=True, text=True, timeout=60, check=False)
        out = shown.stdout + shown.stderr
        self.assertEqual(shown.returncode, 1, "a printed red must leave the step failed, so "
                                              "`gh run view --log-failed` shows it:\n" + out)
        self.assertIn("US0001::AC1", out)
        head = out.index("US0001::AC1")
        for marker in ("red-out-marker", "red-err-marker", "exit 3"):
            self.assertIn(marker, out[head:], f"{marker} is not printed under the red id:\n{out}")
        for absent in ("US0002", "unbuilt-marker", "US0003", "green-marker"):
            self.assertNotIn(absent, out, f"{absent} is printed, but it is no red criterion")

    def test_a_red_on_a_unit_claiming_completion_is_recorded_once_with_its_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "detail.log"
            report = self._verify(root, _story(root, "US0001", "Done", self.RED), log)
            self.assertEqual(report.failed, 1)
            self.assertEqual((root / "runs.txt").read_text(encoding="utf-8"), "run\n",
                             "the verifier ran other than once")
            self._verify(root, _story(root, "US0005", "Done", "shell exit 4"), log)
            text = log.read_text(encoding="utf-8")
        # Each block in full: the id and verifier, the exit, then only the streams that printed;
        # the second is appended after the first.
        self.assertRegex(text, r"\Ared: US0001::AC1 - " + re.escape(self.RED)
                         + r"\nexit 3 after \d+ ms\n--- stdout\nred-out-marker\n"
                           r"--- stderr\nred-err-marker\n\n"
                           r"red: US0005::AC1 - shell exit 4\nexit 4 after \d+ ms\n\n\Z")

    def test_nothing_is_recorded_for_a_green_an_unbuilt_unit_or_an_unset_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "detail.log"
            self._verify(root, _story(root, "US0002", "Ready", self.RED), log)
            self._verify(root, _story(root, "US0003", "Done", "shell echo ok"), log)
            self.assertFalse(log.exists(), "a criterion that is not red on finished work was "
                                           "recorded")
            self._verify(root, _story(root, "US0004", "Done", self.RED), None)
            self.assertFalse(log.exists())
            self.assertFalse(any(root.glob("*.log")))

    def test_a_detail_file_that_cannot_be_opened_is_named_and_the_verdict_stands(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "missing" / "detail.log"
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                report = self._verify(root, _story(root, "US0001", "Done", self.RED), log)
            self.assertEqual((report.failed, report.failures[0]["exit_code"]), (1, 3))
            self.assertFalse(log.parent.exists())
        self.assertIn(f"{verify_ac.RED_DETAIL_ENV} names {log}, which cannot be opened",
                      err.getvalue())
        self.assertIn("US0001::AC1's output is not recorded", err.getvalue())

    def test_a_red_the_batch_answered_is_run_alone_for_its_output(self) -> None:
        """The pytest batch records only pass or not-pass, so its red carries no output; the
        verifier is run alone for the record, and the record says the batch answered it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tests").mkdir()
            (root / "tests" / "test_x.py").write_text(
                "class TestT:\n    def test_a(self):\n        assert False, 'rerun-marker'\n",
                encoding="utf-8")
            node = "tests/test_x.py::TestT::test_a"
            log = root / "detail.log"
            report = self._verify(root, _story(root, "US0001", "Done", f"pytest {node}"), log,
                                  pytest_cache={node: False})
            self.assertEqual(report.failures[0]["stderr"],
                             f"cached pytest run for {node} did not pass (failed, errored, or "
                             f"skipped)", "the verdict is no longer the batch's")
            text = log.read_text(encoding="utf-8")
        self.assertIn("red: US0001::AC1 - pytest " + node, text)
        self.assertIn(f"the batch answered: cached pytest run for {node} did not pass", text)
        self.assertIn("rerun-marker", text)

    def test_a_red_line_after_a_green_one_is_the_line_recorded(self) -> None:
        """Every line of a criterion runs until one is red; the record names that line above
        its own output, not the first line, which passed."""
        red = "shell echo bad-marker; exit 5"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "detail.log"
            self._verify(root, _story(root, "US0001", "Done", "shell echo ok-marker",
                                      f"- **Verify:** {red}\n"), log)
            text = log.read_text(encoding="utf-8")
        self.assertRegex(text, r"\Ared: US0001::AC1 - " + re.escape(red)
                         + r"\nexit 5 after \d+ ms\n--- stdout\nbad-marker\n\n\Z")
        self.assertNotIn("ok-marker", text, "the green line is named above the red one's output")

    def test_a_recorded_verdict_over_several_green_lines_names_the_line_it_shows(self) -> None:
        """Every line passed and the author's record is the red: the record shows the last
        line's run, and names that line above it, not the first."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "detail.log"
            self._verify(root, _story(root, "US0001", "Done", "shell echo first-marker",
                                      "- **Verify:** shell echo second-marker\n"
                                      "- **Verified:** no - unread\n"), log)
            text = log.read_text(encoding="utf-8")
        self.assertRegex(text, r"\Ared: US0001::AC1 - shell echo second-marker\n"
                               r"the selector passed, but this criterion records "
                               r"`Verified: no` - unread\nexit 0 after \d+ ms\n"
                               r"--- stdout\nsecond-marker\n\n\Z")
        self.assertNotIn("first-marker", text, "a line is named above another line's output")

    def test_a_recorded_verdict_that_overrides_a_green_is_recorded_with_why(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            log = root / "detail.log"
            self._verify(root, _story(root, "US0001", "Done", "shell echo passed-marker",
                                      "- **Verified:** no - the page is unread\n"), log)
            text = log.read_text(encoding="utf-8")
        self.assertIn("red: US0001::AC1 - shell echo passed-marker", text)
        self.assertIn("records `Verified: no` - the page is unread", text)
        self.assertIn("--- stdout\npassed-marker", text)
        self.assertNotIn("--- stderr", text, "a stream that printed nothing is labelled")


class CorpusVerifyBudgetTests(unittest.TestCase):
    """AC2: `verify_ac run` holds each check to the budget the runner sets from its measured
    speed, the one the release gate and the corpus lane read."""

    SLOW = "shell python3 -c \"import time; time.sleep(2)\""

    def _run(self, budget: str | None, *flags: str) -> dict:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, "US0926", "Done", self.SLOW)
            env = {**_env(), **({verify_ac.VERIFY_TIMEOUT_ENV: budget} if budget else {})}
            out = io.StringIO()
            with unittest.mock.patch.dict(os.environ, env, clear=True), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = verify_ac.main(["--root", str(root), "run", "--id", "US0926", "--dry-run",
                                     *flags])
        return {"rc": rc, "timeout": "timeout" in out.getvalue()}

    def test_the_runner_budget_sets_the_ceiling_a_check_is_held_to(self) -> None:
        self.assertEqual(self._run("1"), {"rc": 1, "timeout": True},
                         "a 1 s runner budget did not stop a 2 s check")
        self.assertEqual(self._run("30"), {"rc": 0, "timeout": False},
                         "a 30 s runner budget did not let a 2 s check pass")

    def test_an_explicit_timeout_wins_and_a_bad_budget_falls_back(self) -> None:
        self.assertEqual(self._run("1", "--timeout", "30"), {"rc": 0, "timeout": False})
        self.assertEqual(self._run("30", "--timeout", "1"), {"rc": 1, "timeout": True})
        for bad in ("0", "-5", "soon"):
            with self.subTest(budget=bad), unittest.mock.patch.object(
                    verify_ac, "verify_story", wraps=verify_ac.verify_story) as spy:
                self._run(bad)
                self.assertEqual(spy.call_args.args[2], 120)
        with unittest.mock.patch.object(verify_ac, "verify_story",
                                        wraps=verify_ac.verify_story) as spy:
            self._run(None)
            self.assertEqual(spy.call_args.args[2], 120, "the default without a budget moved")

    def test_the_budget_is_the_variable_the_gate_and_the_corpus_job_set(self) -> None:
        self.assertEqual(verify_ac.VERIFY_TIMEOUT_ENV, gate.VERIFY_TIMEOUT_ENV)
        verify = next(s for s in _steps() if "verify-corpus.sh" in str(s.get("run", "")))
        self.assertGreater(int(verify["env"][verify_ac.VERIFY_TIMEOUT_ENV]), 120)


if __name__ == "__main__":
    unittest.main()
