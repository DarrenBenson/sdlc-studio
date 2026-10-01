"""US0966: `verify_ac.py run` names the near-miss node under a FAIL whose node was not found.

`selector_near_miss` already answers "which collected node did this selector mean"; only
`file_finding` asked it, so a mistyped class in a Verify line printed pytest's `not found` lines
and sent the author to grep. Each test drives the shipped CLI as a subprocess against a
throwaway workspace holding one test file and one story; nothing reads this repository.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_TESTS = ("import unittest\n\n\nclass ProbeTests(unittest.TestCase):\n"
          "    def test_alpha(self):\n        self.assertTrue(True)\n\n"
          "    def test_beta(self):\n        self.assertEqual(1, 2)\n")

_STORY = ("# US0001: a probe\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
          "- [ ] **AC1** Given a, when b, then c\n  - **Verify:** {verify}\n")


def _run(verify: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tests").mkdir()
        (root / "tests" / "test_probe.py").write_text(_TESTS, encoding="utf-8")
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        story = stories / "US0001-probe.md"
        story.write_text(_STORY.format(verify=verify), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", "--story", str(story),
             "--dry-run", "--root", str(root)],
            capture_output=True, text=True, check=False, timeout=300)


def _fail_block(out: str) -> str:
    """The lines from AC1's FAIL line to the next non-indented line."""
    lines = out.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip().startswith("FAIL AC1:"))
    block = [lines[start]]
    for ln in lines[start + 1:]:
        if not ln.startswith("          "):
            break
        block.append(ln)
    return "\n".join(block)


class RunNearMissHintTests(unittest.TestCase):
    def test_a_mistyped_class_names_the_collected_node(self) -> None:
        """AC1. MUTANT: HEAD, which prints pytest's `not found` lines and no hint."""
        proc = _run("pytest tests/test_probe.py::ProbTests::test_alpha")
        out = proc.stdout + proc.stderr
        self.assertEqual(1, proc.returncode, out)
        self.assertIn("did you mean tests/test_probe.py::ProbeTests::test_alpha",
                      _fail_block(proc.stdout), out)

    def test_a_failing_real_node_gets_no_hint(self) -> None:
        """AC2. MUTANT: ask for a hint on every FAIL, not only one whose node was not found.
        Asked about the real `ProbeTests::test_beta`, the near-miss reader's close-name arm
        answers `did you mean test_beta` - the node itself - so the guard must be the
        `not found` read, not the reader returning None."""
        proc = _run("pytest tests/test_probe.py::ProbeTests::test_beta")
        out = proc.stdout + proc.stderr
        self.assertEqual(1, proc.returncode, out)
        self.assertIn("FAIL AC1:", proc.stdout, out)
        self.assertNotIn("did you mean", out)


if __name__ == "__main__":
    unittest.main()
