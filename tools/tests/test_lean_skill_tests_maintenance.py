"""BG0782: `tools/skill-tests.sh` turns git's automatic maintenance off for its unittest run.

The repository-root conftest.py turns it off for pytest, and unittest never loads a conftest, so
the script has to do it too, appending to any `GIT_CONFIG_*` entries its caller made rather than
replacing them. Both runs below start with exactly one entry of the caller's own.

Not named after the skill module it runs: both test trees are packages called `tests`, so two
modules of one basename are one module to a pytest session over both trees, and the second is
never collected.
"""
# test-census-subject: tools/skill-tests.sh
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
MODULE = SKILL / "tests" / "test_lean_git_maintenance_off.py"
sys.path.insert(0, str(MODULE.parent))
from test_lean_git_maintenance_off import PROBE, with_one_callers_entry  # noqa: E402


def _skill_tests(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(REPO / "tools" / "skill-tests.sh"), *args], cwd=REPO,
                          env=with_one_callers_entry(os.environ), capture_output=True, text=True,
                          timeout=600)


class SkillTestsMaintenanceTests(unittest.TestCase):

    def test_skill_tests_turns_maintenance_off_and_keeps_existing_config(self) -> None:
        """AC2. The skill module runs green through the script, and a probe run through it reads
        both the script's setting and the caller's entry. MUTANTS: set it only in conftest.py
        (the module's first half goes red under unittest); `export GIT_CONFIG_COUNT=1` over the
        caller's entry (the probe loses `sdlc.kept`)."""
        proc = _skill_tests(str(SKILL), str(MODULE))
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("Ran 1 test", out)

        with tempfile.TemporaryDirectory() as root:
            tests = Path(root) / "tests"
            tests.mkdir()
            (tests / "test_maintenance_probe.py").write_text(PROBE, encoding="utf-8")
            proc = _skill_tests(root)
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("Ran 1 test", out)


if __name__ == "__main__":
    unittest.main()
