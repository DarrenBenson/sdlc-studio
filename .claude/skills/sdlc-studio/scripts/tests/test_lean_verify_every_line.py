"""BG0687: every `Verify:` line under a criterion runs, and the criterion passes only when all do.

Each test drives the shipped `verify_ac.py run --id` as a subprocess against a throwaway
workspace holding one bug whose single criterion carries two `Verify:` lines. Nothing reads
this repository's own artefacts, config or `.local` state.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_PASS = "shell test -d /"
_FAIL = "shell test -d /nonexistent-bg0687"

_BUG = ("# BG0001: a bug\n\n> **Status:** In Progress\n> **Severity:** medium\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c in both environments\n"
        "  - **Verify:** {first}\n  - **Verify:** {second}\n")


def _run_unit(first: str, second: str) -> tuple[subprocess.CompletedProcess, str]:
    """Run the unit's criteria through the shipped CLI; return the process and the file after."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        path = bugs / "BG0001-a-bug.md"
        path.write_text(_BUG.format(first=first, second=second), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", "--id", "BG0001",
             "--root", str(root)],
            capture_output=True, text=True, check=False, timeout=300)
        return proc, path.read_text(encoding="utf-8")


class VerifyEveryLineTests(unittest.TestCase):
    def test_a_failing_second_line_fails_the_criterion(self) -> None:
        """AC1. MUTANT: HEAD, which runs only the first line and reports `pass=1`."""
        proc, body = _run_unit(_PASS, _FAIL)
        out = proc.stdout + proc.stderr
        self.assertIn("pass=0 fail=1", out, out)
        self.assertIn(f"FAIL AC1: {_FAIL}", out, "the failing line is not named:\n" + out)
        self.assertNotIn("**Verified:** yes", body)

    def test_a_failing_first_line_fails_the_criterion(self) -> None:
        """AC2. MUTANT: run only the last line, which passes here."""
        proc, body = _run_unit(_FAIL, _PASS)
        out = proc.stdout + proc.stderr
        self.assertIn("pass=0 fail=1", out, out)
        self.assertIn(f"FAIL AC1: {_FAIL}", out, "the failing line is not named:\n" + out)
        self.assertNotIn("**Verified:** yes", body)

    def test_two_passing_lines_pass_once(self) -> None:
        """AC3. MUTANTS: refuse or fail every second line, so a both-environments criterion can
        never pass; and stamp once per line, so the criterion carries two verdicts."""
        proc, body = _run_unit(_PASS, "shell test -e /")
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("ac=1 pass=1 fail=0", out, out)
        self.assertEqual(1, body.count("**Verified:**"), body)
        self.assertIn("**Verified:** yes", body)


if __name__ == "__main__":
    unittest.main()
