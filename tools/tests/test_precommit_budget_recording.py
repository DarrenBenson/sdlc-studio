"""The per-commit gate budget must only ever compare LIKE with LIKE (RFC0048 D6).

Found by the adversarial review of RUN-01KY1WCR. The hook recorded a `total` on every commit,
but it skips the ~85s unit suites on a docs-only commit and on any commit where a cheaper lane
already failed. Those 9-14s runs landed in the same series the budget reads, and because the
budget deliberately reads the LATEST run rather than a median, one docs commit made the next
report say `-85% since`. The gate had not got faster; it had just not run.

That failure is OPEN, which is what makes it worth a test: alternate a docs commit with a code
commit and the ratchet the budget exists to expose is invisible forever.

These tests RUN THE REAL HOOK in a throwaway repo. Round 2 of the same review then killed the
FIRST version of them: the fixture carried only the hook and `gate_timing.py`, so every cheap
guard died on a missing file, `fail` was already 1, and BOTH tests silently exercised the
`elif` (blocked) branch. The docs-only branch - the one that actually produced `-85% since` -
was never executed, and a mutant restoring the original bug for docs-only commits alone kept
them green. The fixture below therefore stubs every guard so the hook reaches `fail=0`, and
each test ASSERTS THE BRANCH MARKER the hook prints, so a test can never again claim a branch
it did not take.

The positive control matters as much as the two negatives: without it, a hook that recorded
nothing at all would pass this file.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"

#: The hook's own branch markers. Asserting on these is what makes each test's coverage claim
#: checkable rather than assumed.
DOCS_ONLY = "no test-relevant file staged"
ALREADY_FAILED = "a cheaper lane already failed"

PASS_SH = "#!/usr/bin/env bash\nexit 0\n"
PASS_PY = "import sys\nsys.exit(0)\n"
FAIL_SH = "#!/usr/bin/env bash\necho 'stub failure'\nexit 1\n"


#: Git hands a pre-commit hook GIT_INDEX_FILE pointing at the OUTER repo's `.git/index.lock`
#: (absolute, under `git commit -a`). Every git call this module makes must therefore run with
#: those variables gone, or the fixture writes ITS tree into the real repo's pending commit -
#: reproduced on three victim repos by the adversarial review, and the same class as the index
#: wipe this repo has already suffered once. `tools/skill-tests.sh` scrubs these for the skill
#: suite; the hook's tool-tests lane now scrubs them too, and this is the second layer.
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


class BudgetRecordingTests(unittest.TestCase):
    """Only a commit that actually paid for the unit suites may enter the budget series."""

    def _repo(self, tmp: Path) -> Path:
        """A throwaway repo whose every guard PASSES, so the hook reaches its real branches."""
        root = tmp / "r"
        (root / "tools" / "tests").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / ".githooks").mkdir(parents=True)
        (root / ".claude" / "skills" / "sdlc-studio" / "scripts").mkdir(parents=True)
        (root / "node_modules" / ".bin").mkdir(parents=True)

        hook = root / ".githooks" / "pre-commit"
        hook.write_text(HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        hook.chmod(0o755)

        for name in ("lint-style.sh", "check_action_pins.sh", "skill-tests.sh"):
            p = root / "tools" / name
            p.write_text(PASS_SH, encoding="utf-8")
            p.chmod(0o755)
        for name in ("check_links.py", "validate_skill.py", "check_versions.py",
                     "check_budgets.py", "check_neutrality.py"):
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        # `gate.py` and the pending-floor lane are stubbed: this fixture is not a whole
        # project, and either failing would send every case down the blocked branch
        # instead of the one under test. Their own behaviour is tested elsewhere
        # (test_precommit_floor_pending.py runs the REAL floor against the real hook).
        for name in ("gate.py", "engagement_floor.py"):
            (scripts / name).write_text(PASS_PY, encoding="utf-8")
        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(PASS_SH, encoding="utf-8")
        md.chmod(0o755)
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        # `unittest discover` over an EMPTY dir exits 1 ("NO TESTS RAN"), which would make the
        # tool-tests lane fail and send every case down the blocked branch.
        (root / "tools" / "tests" / "test_stub.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n", encoding="utf-8")

        # The one real tool: the thing under test.
        (root / "tools" / "gate_timing.py").write_text(
            (REPO / "tools" / "gate_timing.py").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "gate_budget:\n  seconds: 120\n  baseline_seconds: 99\n"
            "  baseline_date: 2026-07-21\n", encoding="utf-8")

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        # Land the scaffolding in a FIRST commit that bypasses the hook. Without this, every
        # test's `git add -A` also stages `tools/*`, which is test-relevant - so even the
        # docs-only case would run the suites and the branch under test would never be reached.
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _totals(self, root: Path) -> list[float]:
        p = root / "sdlc-studio" / ".local" / "gate-timings.json"
        if not p.exists():
            return []
        return json.loads(p.read_text(encoding="utf-8")).get("total", [])

    def _commit(self, root: Path, rel: str, body: str = "x\n") -> str:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        _git(root, "add", "-A")
        out = subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "x"],
                             capture_output=True, text=True, env=_clean_env())
        return out.stdout + out.stderr

    def test_a_docs_only_commit_does_not_enter_the_budget_series(self) -> None:
        """The exact regression: a commit that SKIPPED the suites must not be recorded as this
        gate's cost. Recorded, it made the next report read `-85% since`."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            out = self._commit(root, "README.md")
            self.assertIn(DOCS_ONLY, out, "this test did not reach the docs-only branch")
            self.assertNotIn(ALREADY_FAILED, out)
            self.assertEqual(self._totals(root), [],
                             "a docs-only commit was recorded as a gate cost")
            self.assertNotIn("gate-budget:", out)

    def test_a_commit_blocked_before_the_suites_is_not_recorded_either(self) -> None:
        """The other skip path: a cheap lane failed, so the suites never ran. Its 10s is not
        this gate's cost either."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            (root / "tools" / "lint-style.sh").write_text(FAIL_SH, encoding="utf-8")
            (root / "tools" / "lint-style.sh").chmod(0o755)
            out = self._commit(root, "tools/thing.py")     # test-relevant, so only `fail` skips
            self.assertIn(ALREADY_FAILED, out, "this test did not reach the blocked branch")
            self.assertNotIn(DOCS_ONLY, out)
            self.assertEqual(self._totals(root), [])
            self.assertNotIn("gate-budget:", out)

    def test_a_commit_that_ran_the_suites_IS_recorded(self) -> None:
        """The positive control, and the reason the two tests above are not vacuous: a hook that
        recorded nothing at all would satisfy both of them."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            out = self._commit(root, "tools/thing.py")
            self.assertNotIn(DOCS_ONLY, out)
            self.assertNotIn(ALREADY_FAILED, out)
            self.assertEqual(len(self._totals(root)), 1, "a full-lane commit was not recorded")
            self.assertIn("gate-budget:", out)
            self.assertIn("baseline 99s", out)          # ...against the corrected baseline

    def test_a_suite_that_failed_to_import_is_not_recorded_as_this_commit_s_cost(self) -> None:
        """BG0239: `suites_ran` was set once the lane was INVOKED, not once it ran its scope. A
        module that fails to import takes the same branch, so a run that executed a fraction of
        the tests was recorded as the gate's cost - measured at 73s against a 99s baseline, which
        the budget then reported as `-26% since`. A broken suite reading as an improvement, and
        the same magnitude as the ratchet the lane exists to expose."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            (root / "tools" / "tests" / "test_broken.py").write_text(
                "import nonexistent_module_xyz\n", encoding="utf-8")
            out = self._commit(root, "tools/thing.py")
            self.assertNotIn(DOCS_ONLY, out)
            self.assertNotIn(ALREADY_FAILED, out, "a cheap lane failed - wrong branch")
            self.assertEqual(self._totals(root), [],
                             "a run whose module failed to import was recorded as a gate cost")
            self.assertIn("NOT recorded", out)          # ...and it SAID so rather than going quiet

    def test_a_suite_that_ran_its_scope_and_FAILED_is_still_recorded(self) -> None:
        """The distinction BG0239 turns on, and the reason the test above is not simply 'do not
        record red commits'. A suite that ran everything and reported a failure COST the full
        time, so its total is a true measurement of what this commit paid. Only 'barely ran' is
        excluded."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            (root / "tools" / "tests" / "test_red.py").write_text(
                "import unittest\n\n\nclass T(unittest.TestCase):\n"
                "    def test_red(self):\n        self.fail('deliberate')\n", encoding="utf-8")
            out = self._commit(root, "tools/thing.py")
            self.assertNotIn(DOCS_ONLY, out)
            self.assertNotIn(ALREADY_FAILED, out)
            self.assertEqual(len(self._totals(root)), 1,
                             "a suite that ran its scope and failed should still be recorded")
            self.assertNotIn("NOT recorded", out)


if __name__ == "__main__":
    unittest.main()
