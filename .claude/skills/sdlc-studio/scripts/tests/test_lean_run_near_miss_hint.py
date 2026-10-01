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
          "- [ ] **AC1** Given a, when b, then c\n  - **Verify:** {verify}\n{verified}")


def _run(verify: str, verified: str = "", *extra: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tests").mkdir()
        (root / "tests" / "test_probe.py").write_text(_TESTS, encoding="utf-8")
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        story = stories / "US0001-probe.md"
        story.write_text(_STORY.format(verify=verify, verified=verified), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run", "--story", str(story),
             "--dry-run", "--root", str(root), *extra],
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

    def test_a_recorded_reason_saying_not_found_gets_no_hint(self) -> None:
        """Round-1 repro. A passing node under `Verified: no ... - device not found in lab` FAILs
        as recorded-not-verified, and its text is the author's reason. MUTANT: read `not found`
        from any FAIL's text, not only a pytest FAIL's - the near-miss reader then answers the
        real `ProbeTests::test_alpha` with itself. MUTANT: read pytest's `not found` line from
        any FAIL - a reason that quotes one, as an author pasting a lab log does, is then read
        as this run's pytest output."""
        for reason in ("device not found in lab",
                       "the lab log said ERROR: not found: "
                       "tests/test_probe.py::ProbeTests::test_alpha"):
            with self.subTest(reason=reason):
                proc = _run("pytest tests/test_probe.py::ProbeTests::test_alpha",
                            f"  - **Verified:** no (2026-09-01) - {reason}\n")
                out = proc.stdout + proc.stderr
                self.assertEqual(1, proc.returncode, out)
                self.assertIn(reason[:20], proc.stdout, "the recorded-not-verified FAIL was "
                                                        "not the one reached")
                self.assertNotIn("hint:", out)

    def test_a_multi_node_selector_hints_about_the_missing_node(self) -> None:
        """Round-1 repro. MUTANT: hint about the selector's first `::` argument, which here is
        the real `ProbeTests::test_alpha` - the hint then names test_alpha, not the missing
        `ProbTests::test_beta`."""
        proc = _run("pytest tests/test_probe.py::ProbeTests::test_alpha "
                    "tests/test_probe.py::ProbTests::test_beta")
        out = proc.stdout + proc.stderr
        self.assertEqual(1, proc.returncode, out)
        hints = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip().startswith("hint:")]
        self.assertEqual(["hint: did you mean tests/test_probe.py::ProbeTests::test_beta"], hints,
                         out)

    def test_the_hint_names_the_path_as_written(self) -> None:
        """pytest's `not found` line carries an absolute path; the hint names the file as the
        Verify line does. MUTANT: pass pytest's absolute path through - the close-name arm then
        prints the throwaway tree's absolute path."""
        proc = _run("pytest tests/test_probe.py::ProbeTests::test_alpah")
        self.assertIn("hint: no `test_alpah` in tests/test_probe.py::ProbeTests; "
                      "did you mean `test_alpha`", proc.stdout, proc.stdout + proc.stderr)

    def test_the_batch_run_hints_too(self) -> None:
        """`--batch` reports a missing node as `no such test node`, not pytest's line. MUTANT:
        read only pytest's `ERROR: not found:` line - the batch FAIL then gets no hint."""
        proc = _run("pytest tests/test_probe.py::ProbTests::test_alpha", "", "--batch")
        self.assertIn("no such test node", proc.stdout, proc.stdout + proc.stderr)
        self.assertIn("hint: did you mean tests/test_probe.py::ProbeTests::test_alpha",
                      proc.stdout)


if __name__ == "__main__":
    unittest.main()
