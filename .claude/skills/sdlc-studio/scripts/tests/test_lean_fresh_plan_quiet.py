"""US0971: a fresh project's first plan is quiet.

The first `sprint plan` on a freshly initialised project told the operator that no seat could
review the goal (the shipped seats can), reported a TSD the operator chose to skip as
UNAVAILABLE and the absent commit hook as a policy DIVERGENCE, proposed retired units from the
blocker sweep, and carried a seat's NOT-achievable verdict onto the wording that seat asked
for. Every case runs the shipped CLI in a temporary project.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SPRINT = _SCRIPTS / "sprint.py"


def _cli(root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(_SCRIPTS / script), *argv, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300)


def _project(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True,
                   capture_output=True)
    r = _cli(root, "init.py", "run")
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return root


def _plan(root: Path, *argv: str) -> str:
    r = _cli(root, "sprint.py", "plan", "--stories", "Ready", "--no-fetch", *argv)
    if r.returncode != 0:
        raise AssertionError(f"plan exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
    return r.stdout + r.stderr


def _story(root: Path, sid: str, status: str, extra: str = "") -> None:
    d = root / "sdlc-studio" / "stories"
    (d / f"{sid}-s.md").write_text(
        f"# {sid}: s\n\n> **Status:** {status}\n> **Epic:** EP0001\n{extra}\n"
        "## Acceptance Criteria\n\n### AC1: works\n\n- **Verify:** shell true\n",
        encoding="utf-8")


class FreshPlanQuietTests(unittest.TestCase):

    def test_a_fresh_project_is_offered_the_shipped_seats(self) -> None:
        """AC1. MUTANTS: (1) HEAD's project-seats-only offer - `no seat can review it`;
        (2) the shipped seats offered but not named on the line."""
        with tempfile.TemporaryDirectory() as d:
            out = _plan(_project(Path(d)), "--sprint-goal", "ship the thing")
        line = next(ln for ln in out.splitlines() if "goal review:" in ln)
        self.assertNotIn("no seat can review it", out)
        for seat in ("engineering", "product", "qa"):
            self.assertIn(seat, line)

    def test_init_chosen_states_are_not_reported_as_divergence(self) -> None:
        """AC2. MUTANTS: (1) a skipped TSD reported UNAVAILABLE; (2) a project with no hook and
        no declared per-commit mode told the policy DIVERGES; (3) a hook that IS installed and
        disagrees no longer reported (the positive control)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            for _stage in ("agents", "prd", "trd", "tsd"):
                r = _cli(root, "init.py", "guided", "--skip")
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            out = _plan(root)
            self.assertNotIn("test strategy: UNAVAILABLE", out)
            self.assertNotIn("execution policy DIVERGES", out)
            hook = root / ".githooks" / "pre-commit"
            hook.parent.mkdir()
            hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            self.assertIn("execution policy DIVERGES", _plan(root))

    def test_the_blocker_sweep_skips_terminal_units(self) -> None:
        """AC3. MUTANT: HEAD's sweep with no terminal check - the Superseded story is
        proposed."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            _story(root, "US0001", "Done")
            _story(root, "US0002", "Superseded", "> **Blocked by:** US0001\n")
            _story(root, "US0003", "Blocked", "> **Blocked by:** US0001\n")
            out = _plan(root)
        line = next(ln for ln in out.splitlines() if "blocker sweep:" in ln)
        self.assertIn("US0003", line)
        self.assertNotIn("US0002", line)

    def test_the_requesting_seats_verdict_is_discharged_by_its_amendment(self) -> None:
        """AC4. MUTANTS: (1) HEAD - engineering's carried NOT-achievable verdict printed as
        advice on the wording it asked for; (2) every carried or fresh objection discharged -
        qa's fresh objection to the amended goal goes unprinted (the positive control)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _cli(root, "sprint.py", "goal-review", "record", "--goal", "ship everything",
                     "--seat", "engineering|no|all of it|yes|too large for one sprint")
            self.assertEqual(0, r.returncode, r.stderr)
            r = _cli(root, "sprint.py", "goal-review", "record", "--goal", "ship the core",
                     "--amend-from", "ship everything", "--requesting-seat", "engineering",
                     "--seat", "qa|no|the core|yes|no test plan yet")
            self.assertEqual(0, r.returncode, r.stderr)
            out = _plan(root, "--sprint-goal", "ship the core", "--write")
        advice = [ln for ln in out.splitlines() if "judged the goal NOT achievable" in ln]
        self.assertEqual(1, len(advice), advice)
        self.assertIn("qa", advice[0])


    def test_an_installed_hook_that_cannot_be_read_still_diverges(self) -> None:
        """US0971 round 1. A hook that exists but is not read at the fixed paths still runs.
        MUTANT: the suppression keyed on `not hook["read"]` - a husky hook under
        `core.hooksPath`, and a non-UTF-8 `.githooks/pre-commit`, go silent."""
        for case in ("husky", "non-utf8"):
            with self.subTest(case), tempfile.TemporaryDirectory() as d:
                root = _project(Path(d))
                if case == "husky":
                    hook = root / ".husky" / "pre-commit"
                    subprocess.run(["git", "config", "core.hooksPath", ".husky"], cwd=root,
                                   env=gitutil.git_env(), check=True)
                    hook.parent.mkdir()
                    hook.write_text("#!/bin/sh\nnpm test\n", encoding="utf-8")
                else:
                    hook = root / ".githooks" / "pre-commit"
                    hook.parent.mkdir()
                    hook.write_bytes(b"#!/bin/sh\n\xff\xfe pytest\n")
                self.assertIn("execution policy DIVERGES", _plan(root))

    def test_a_hook_git_resolves_elsewhere_still_diverges(self) -> None:
        """US0971 round 2. The hooks directory is the one git resolves, not a fixed path.
        MUTANTS: read `core.hooksPath` as a plain string and the hook paths relative to the root
        - (a) in a linked worktree, where `.git` is a file and the hooks live in the common
        dir, and (b) under `core.hooksPath = ~`, which git expands, the hook goes silent."""
        with tempfile.TemporaryDirectory() as d:
            main = _project(Path(d) / "main")
            gitutil.git(["add", "-A"], main)
            gitutil.git(["commit", "-qm", "base"], main)
            hook = main / ".git" / "hooks" / "pre-commit"     # after the commit it would run on
            hook.write_text("#!/bin/sh\npytest\n", encoding="utf-8")
            hook.chmod(0o755)
            gitutil.git(["worktree", "add", "-q", str(Path(d) / "wt")], main)
            wt = Path(d) / "wt"
            self.assertTrue((wt / ".git").is_file(), "the fixture is not a linked worktree")
            self.assertIn("execution policy DIVERGES", _plan(wt))
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d) / "p")
            home = Path(d) / "home"
            home.mkdir()
            (home / "pre-commit").write_text("#!/bin/sh\npytest\n", encoding="utf-8")
            gitutil.git(["config", "core.hooksPath", "~"], root)
            # a `commit-msg` alone is a hook too. MUTANT: look for `pre-commit` only.
            for name in ("pre-commit", "commit-msg"):
                if name == "commit-msg":
                    (home / "pre-commit").rename(home / "commit-msg")
                r = subprocess.run(
                    [sys.executable, str(SPRINT), "plan", "--stories", "Ready", "--no-fetch",
                     "--root", str(root)], cwd=root, env=gitutil.git_env(HOME=str(home)),
                    capture_output=True, text=True, timeout=300)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn("execution policy DIVERGES", r.stdout + r.stderr, name)
        # the negative control: a plain project with no hook anywhere stays quiet
        with tempfile.TemporaryDirectory() as d:
            self.assertNotIn("execution policy DIVERGES", _plan(_project(Path(d))))

    def test_a_hooks_git_dir_does_not_answer_for_the_root(self) -> None:
        """Run from inside another repository's hook, `GIT_DIR` names that repository; git must
        still answer for `root`. MUTANT: pass the environment through - the other repository's
        hook is read as this project's."""
        import loader  # noqa: PLC0415 - the module under test, in process for the env patch
        sprint = loader.load_script("sprint")
        with tempfile.TemporaryDirectory() as d:
            other = _project(Path(d) / "other")
            hook = other / ".git" / "hooks" / "pre-commit"
            hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            root = _project(Path(d) / "root")
            with mock.patch.dict(os.environ, {"GIT_DIR": str(other / ".git")}):
                self.assertFalse(sprint._hook_installed(root))
            self.assertTrue(sprint._hook_installed(other))

    def test_the_requesting_seats_fresh_objection_stays_visible(self) -> None:
        """US0971 round 1. Only a CARRIED verdict is discharged. MUTANT: `discharged` ignoring
        `carried_from` - the requesting seat's fresh NO on the amended goal is hidden."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _cli(root, "sprint.py", "goal-review", "record", "--goal", "ship everything",
                     "--seat", "engineering|no|all of it|yes|too large for one sprint")
            self.assertEqual(0, r.returncode, r.stderr)
            r = _cli(root, "sprint.py", "goal-review", "record", "--goal", "ship the core",
                     "--amend-from", "ship everything", "--requesting-seat", "engineering",
                     "--seat", "engineering|no|the core|yes|still too large")
            self.assertEqual(0, r.returncode, r.stderr)
            out = _plan(root, "--sprint-goal", "ship the core", "--write")
        advice = [ln for ln in out.splitlines() if "judged the goal NOT achievable" in ln]
        self.assertEqual(1, len(advice), advice)
        self.assertIn("engineering", advice[0])
        self.assertIn("still too large", advice[0])


if __name__ == "__main__":
    unittest.main()
