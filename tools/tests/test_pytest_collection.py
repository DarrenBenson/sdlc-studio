"""One pytest invocation can name tests in BOTH suites.

The repo carries two test packages - `.claude/skills/sdlc-studio/scripts/tests` (the shipped
skill scripts) and `tools/tests` (the repo-only guards). Both directories are called `tests`,
so under pytest's default prepend import mode both resolve to the module name `tests` and the
second one collected raises `ModuleNotFoundError: No module named 'tests.<module>'`. Four
delivery lanes hit it independently: a unit whose change spans the two halves of the gate could
not write a single `Verify:` line that proved it, because no one command could run both.

The fix belongs to the repo's pytest configuration, not to the invocation, so this test runs a
bare cross-package command - no import-mode flag of its own. If it only passed with a flag the
test supplied, every Verify line would still have to remember the flag, which is the same defect
one layer up.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS_TEST = ".claude/skills/sdlc-studio/scripts/tests/test_gate.py"
TOOLS_TEST = "tools/tests/test_doc_claims.py"


class CrossPackageCollectionTests(unittest.TestCase):
    """A node id from each package, in one command."""

    def _collect(self, *targets: str) -> subprocess.CompletedProcess:
        return subprocess.run(  # noqa: S603 - fixed argv, no shell
            [sys.executable, "-m", "pytest", "--collect-only", "-q", *targets],
            cwd=REPO, capture_output=True, text=True, timeout=300)

    def test_both_suites_collect_in_one_invocation(self) -> None:
        # each half collects alone, so a failure below is about the COMBINATION and not
        # about either suite being broken
        for target in (SCRIPTS_TEST, TOOLS_TEST):
            alone = self._collect(target)
            self.assertEqual(alone.returncode, 0, f"{target} does not collect alone:\n"
                                                  f"{alone.stdout}\n{alone.stderr}")
        both = self._collect(SCRIPTS_TEST, TOOLS_TEST)
        self.assertEqual(both.returncode, 0,
                         "one invocation cannot collect both suites, so no Verify line can "
                         f"span them:\n{both.stdout}\n{both.stderr}")
        self.assertNotIn("ModuleNotFoundError", both.stdout + both.stderr)
        # and it collected BOTH, rather than exiting clean having collected one: a run that
        # silently dropped half is the false green this whole project keeps paying for
        self.assertIn("scripts/tests/test_gate.py", both.stdout)
        self.assertIn("tools/tests/test_doc_claims.py", both.stdout)

    def test_a_node_id_from_each_suite_runs_in_one_invocation(self) -> None:
        """Collection is not execution. A Verify line names node ids and RUNS them, so the
        pinned behaviour is a real two-suite run reporting two passes."""
        run = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [sys.executable, "-m", "pytest", "-q",
             f"{SCRIPTS_TEST}::BoundaryPolicyTests::test_an_unknown_boundary_is_refused_not_ignored",
             f"{TOOLS_TEST}::MutationIsolationTests::test_the_isolation_rule_is_documented"],
            cwd=REPO, capture_output=True, text=True, timeout=300)
        self.assertEqual(run.returncode, 0, f"{run.stdout}\n{run.stderr}")
        self.assertIn("2 passed", run.stdout)


if __name__ == "__main__":
    unittest.main()
