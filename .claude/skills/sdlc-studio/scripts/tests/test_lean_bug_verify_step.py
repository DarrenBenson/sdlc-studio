"""BG0815: the bug verify and close workflows name the verifier that records a criterion green.

A clean eval run showed an agent following reference-bug.md verify a bug by running its tests by
hand: the verify workflow said "Execute tests listed in Tests Added" and the close workflow's
evidence step said only that `transition.py` reads the criteria. Neither named
`verify_ac.py run --id`, the one command that stamps a criterion `Verified` and writes the
verify-report `transition.py` reads, so the run left nothing behind.

The doc test reads THIS repository's shipped skill, as AC1 names it. The CLI test drives the
shipped `verify_ac.py` and `transition.py` in a temporary workspace, so the guidance's account
of what the verifier records, and what the close refuses, stays true of the tools.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent

VERIFIER = "verify_ac.py run --id"
#: a line telling the agent to run or execute tests; one that does not name the verifier is the
#: hand run the eval caught
RUN_TESTS = re.compile(
    r"\b(?:execute[sd]?|run|runs|running)\b[^.\n]*\btests?\b"
    r"|\btests?\b[^.\n]*\b(?:executed?|ran|run)\b",  # the passive order too
    re.IGNORECASE)


def _section(text: str, start: str, level: str) -> str:
    """The body under the heading line with the word `start`, up to the next heading of `level`."""
    lines = text.splitlines()
    begin = next(i for i, line in enumerate(lines)
                 if line.startswith(level + " ") and start in line.split())
    end = next((j for j in range(begin + 1, len(lines))
                if re.match(rf"#{{1,{len(level)}}} ", lines[j])), len(lines))
    return "\n".join(lines[begin + 1:end])


def _spots() -> dict[str, str]:
    ref = (SKILL / "reference-bug.md").read_text(encoding="utf-8")
    help_ = (SKILL / "help/bug.md").read_text(encoding="utf-8")
    return {
        "reference-bug.md verify workflow": _section(ref, "{#bug-verify-workflow}", "##"),
        "reference-bug.md close workflow": _section(ref, "{#bug-close-workflow}", "##"),
        "help/bug.md verify entry": _section(help_, "verify", "###"),
        "help/bug.md close entry": _section(help_, "close", "###"),
    }


BUG = """# BG0001: login form drops the CSRF token

> **Status:** In Progress
> **Severity:** High
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

The login form drops the CSRF token on resubmit.

## Acceptance Criteria

- [ ] **AC1** Given a resubmit, then the token is kept.
  - **Verify:** pytest tests/test_fix.py::FixTests::test_token_kept

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
"""

TEST = """import unittest
class FixTests(unittest.TestCase):
    def test_token_kept(self):
        self.assertTrue({green})
"""


class BugVerifyStepTests(unittest.TestCase):
    def test_the_verify_and_close_steps_name_the_verifier(self):
        for spot, body in _spots().items():
            with self.subTest(spot=spot):
                named = [line for line in body.splitlines() if VERIFIER in line]
                self.assertTrue(named, f"{spot} never names `{VERIFIER}`")
                self.assertTrue(any("record" in line.lower() for line in named),
                                f"{spot} names the verifier but not that it records the result")
                hand_runs = [line.strip() for line in body.splitlines()
                             if RUN_TESTS.search(line) and "verify_ac" not in line]
                self.assertEqual(hand_runs, [],
                                 f"{spot} tells the agent to run tests without the verifier")

    def _workspace(self, green: bool) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "sdlc-studio/bugs").mkdir(parents=True)
        (root / "sdlc-studio/.config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        (root / "sdlc-studio/bugs/BG0001-csrf.md").write_text(BUG, encoding="utf-8")
        (root / "tests").mkdir()
        (root / "tests/test_fix.py").write_text(TEST.format(green=green), encoding="utf-8")
        return root

    def _run(self, root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=root,
                              capture_output=True, text=True, timeout=120)

    def _close(self, root: Path) -> subprocess.CompletedProcess:
        return self._run(root, "transition.py", "set", "--id", "BG0001", "--status", "Fixed",
                         "--verdict", "approve", "--reviewer", "rev", "--author", "auth",
                         "--brief", "a1b2c3d4e5f6")

    def test_the_verifier_records_what_the_close_reads(self):
        """What the guidance says of the tools: the run stamps and records a green criterion,
        a recorded red refuses Fixed, and a criterion never run is not refused."""
        green = self._workspace(green=True)
        self._run(green, "verify_ac.py", "run", "--id", "BG0001")
        self.assertIn("**Verified:** yes",
                      (green / "sdlc-studio/bugs/BG0001-csrf.md").read_text(encoding="utf-8"))
        self.assertTrue((green / "sdlc-studio/.local/verify-report.json").is_file())
        self.assertEqual(self._close(green).returncode, 0)

        red = self._workspace(green=False)
        self._run(red, "verify_ac.py", "run", "--id", "BG0001")
        refused = self._close(red)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("AC verification is red (AC1)", refused.stdout + refused.stderr)

        unrun = self._workspace(green=False)
        self.assertEqual(self._close(unrun).returncode, 0)


if __name__ == "__main__":
    unittest.main()
