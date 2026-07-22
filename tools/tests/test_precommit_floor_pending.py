"""The pre-commit gate's engagement-floor lane over the PENDING commit (BG0251).

The floor evaluates SHIPPED units, and `_git_touched_by_id` derives "shipped" from
`git log --grep` over the history. A unit whose id has never appeared in a commit message
is invisible, so the gate structurally could not detect a floor violation that the very
commit it is gating was about to create: the condition did not exist until after the
commit landed.

Observed during RUN-01KY321Q. The floor reported 0 violations, the gate passed, the
commit landed, and the same check run immediately afterwards reported 2 NEW violations in
files nothing had touched. The gate green-lit a commit that was non-compliant the instant
it existed.

These tests RUN THE REAL HOOK against the REAL `engagement_floor.py` in a throwaway repo,
because the defect is in the joining of the two: the check could always judge a staged
artefact, and the hook never asked it to judge the commit in hand.

What is deliberately NOT claimed: the commit MESSAGE. Git writes `COMMIT_EDITMSG` after
the pre-commit hook runs (verified: at hook time it still holds the previous commit's
message), so a unit this commit names in prose alone, staging no artefact for it, is
still judged one commit later. `test_a_unit_named_only_in_the_message_is_still_not_seen`
holds that limit to a test rather than to a sentence.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"
SKILL_SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

PASS_SH = "#!/usr/bin/env bash\nexit 0\n"
PASS_PY = "import sys\nsys.exit(0)\n"

#: See tools/tests/test_skill_tests_env.py - every fixture module that shells out to git
#: carries this list, and that module holds them all to one definition.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _clean_env() -> dict:
    env = dict(os.environ)
    for var in _GIT_ENV_VARS:
        env.pop(var, None)
    return env


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


class FloorPendingLaneTests(unittest.TestCase):

    def _repo(self, tmp: Path) -> Path:
        """A throwaway repo carrying the REAL engagement_floor.py and stubs for every other
        guard, so the only lane that can refuse is the one under test."""
        root = tmp / "r"
        (root / "tools" / "tests").mkdir(parents=True)
        (root / ".githooks").mkdir(parents=True)
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "src").mkdir(parents=True)

        hook = root / ".githooks" / "pre-commit"
        hook.write_text(HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        hook.chmod(0o755)

        for name in ("lint-style.sh", "check_action_pins.sh", "skill-tests.sh"):
            p = root / "tools" / name
            p.write_text(PASS_SH, encoding="utf-8")
            p.chmod(0o755)
        for name in ("check_links.py", "validate_skill.py", "check_versions.py",
                     "check_budgets.py", "check_neutrality.py", "gate_timing.py"):
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tools" / "tests" / "test_stub.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n", encoding="utf-8")
        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(PASS_SH, encoding="utf-8")
        md.chmod(0o755)

        # The real skill scripts, minus their own test tree: the floor imports siblings.
        dest = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        dest.parent.mkdir(parents=True)
        shutil.copytree(SKILL_SCRIPTS, dest,
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
        # ...but the artefact gate itself is stubbed: this fixture is not a whole project,
        # and a failing gate lane would mask the verdict under test.
        (dest / "gate.py").write_text(PASS_PY, encoding="utf-8")

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _bug(self, root: Path, num: int, *, status: str, affects: str, ac: bool = False) -> Path:
        lines = [f"# BG{num:04d}: sample", "", f"> **Status:** {status}",
                 f"> **Affects:** {affects}", ""]
        if ac:
            lines += ["## Acceptance Criteria", "", "### AC1: works", "- a real criterion", ""]
        path = root / "sdlc-studio" / "bugs" / f"BG{num:04d}-sample.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _commit(self, root: Path, message: str) -> tuple[int, str]:
        _git(root, "add", "-A")
        out = subprocess.run(["git", "-C", str(root), "commit", "-m", message],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr

    def test_a_commit_that_puts_a_unit_below_the_floor_is_refused(self) -> None:
        """BG0251's own guard: an unplanned multi-file unit, staged with the code that
        makes it multi-file. Before this lane the hook passed, because nothing in history
        mentioned the id yet."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, 900, status="Fixed", affects="src/one.py")
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            rc, out = self._commit(root, "fix: three modules\n\nBG0900 spans them")
            self.assertNotEqual(rc, 0, f"the commit was NOT refused:\n{out}")
            self.assertIn("BG0900", out)
            self.assertIn("pending commit", out)
            self.assertEqual(_git(root, "log", "--format=%s").stdout.strip(), "fixture")

    def test_the_refusal_is_the_verdict_the_commit_would_otherwise_have_produced(self) -> None:
        """Not a new rule invented at the hook: bypass the gate for the same commit and the
        standing floor lane, reading history alone, reports the same unit. Without this the
        lane could be refusing commits for reasons the floor never held."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, 900, status="Fixed", affects="src/one.py")
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "--no-verify", "-m",
                 "fix: three modules\n\nBG0900 spans them")
            after = subprocess.run(
                ["python3", ".claude/skills/sdlc-studio/scripts/engagement_floor.py",
                 "check", "--root", "."],
                cwd=root, capture_output=True, text=True, env=_clean_env())
            self.assertEqual(after.returncode, 1, after.stdout + after.stderr)
            self.assertIn("BG0900", after.stdout)

    def test_a_planned_unit_commits_normally(self) -> None:
        """The negative control, and the reason the lane is not simply "refuse everything":
        the same three-file commit, with the unit planned, passes."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, 901, status="Fixed", affects="src/one.py", ac=True)
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            rc, out = self._commit(root, "fix: three modules\n\nBG0901 spans them")
            self.assertEqual(rc, 0, f"a planned unit was refused:\n{out}")
            self.assertIn("ok", out)

    def test_a_unit_named_only_in_the_message_is_still_not_seen(self) -> None:
        """The residual gap, stated as a test so no comment can quietly claim it closed.

        The bug is committed and Fixed already; this commit stages only source files and
        names the unit in its MESSAGE. Git does not give a pre-commit hook the message it
        is gating, so the lane cannot judge this shape - and the check run immediately
        after the commit says the violation is real, which is precisely the "one commit
        behind" behaviour BG0251 describes. Documented, not closed.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, 902, status="Fixed", affects="src/one.py")
            (root / "src" / "one.py").write_text("x = 1\n", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "--no-verify", "-m", "chore: baseline")
            for n in ("two", "three"):
                (root / "src" / f"{n}.py").write_text("y = 2\n", encoding="utf-8")
            rc, out = self._commit(root, "chore: two more modules\n\nper BG0902")
            self.assertEqual(rc, 0, f"the lane claimed a case it cannot see:\n{out}")
            after = subprocess.run(
                ["python3", ".claude/skills/sdlc-studio/scripts/engagement_floor.py",
                 "check", "--root", "."],
                cwd=root, capture_output=True, text=True, env=_clean_env())
            self.assertEqual(after.returncode, 1,
                             "premise: the landed commit DOES create a violation")
            self.assertIn("BG0902", after.stdout)

    def test_the_lane_says_what_it_could_not_see(self) -> None:
        """A lane whose green reads as "this commit is compliant" would be the same
        overclaim BG0251 filed. The scope is printed, not left in a docstring."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, 903, status="Fixed", affects="src/one.py")
            for n in ("one", "two", "three"):
                (root / "src" / f"{n}.py").write_text("x = 1\n", encoding="utf-8")
            _, out = self._commit(root, "fix: three modules\n\nBG0903 spans them")
            self.assertIn("commit message", out.lower())


class LaneWiringTests(unittest.TestCase):
    """The lane has to be invoked by the hook, not merely exist in the script."""

    def test_the_hook_runs_the_floor_over_the_pending_commit(self) -> None:
        text = HOOK.read_text(encoding="utf-8")
        self.assertIn("engagement_floor.py", text)
        self.assertIn("check --pending", text)


if __name__ == "__main__":
    unittest.main()
