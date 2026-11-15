"""A Verify line's own flags cannot hide pytest's skips from the partial-skip verdict.

A `-q` on the line stacked on the runner's own and took pytest below the level at which it
prints its summary, so a partly skipped target and an entirely skipped one were both stamped.
Under `-s` a test's own output reaches the report, and a passing test that printed a line shaped
like a summary was read as a skip. The verbosity and `-s` cases run through `verify_ac.py run`,
each beside a positive control that is stamped, so a change that fails every such line cannot
pass; the unfolded skip line is read from a report built from pytest's own output.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

TARGET = '''import pytest


class TestMixed:
    def test_runs(self):
        assert True

    @pytest.mark.skip(reason="off on this host")
    def test_skip_me(self):
        assert True


class TestAllSkip:
    @pytest.mark.skip(reason="all off")
    def test_only(self):
        assert True


class TestClean:
    def test_clean(self):
        assert True


class TestPrints:
    def test_prints(self):
        print("1 passed, 1 skipped in 0.01s")


class TestPrintsAllSkipped:
    def test_prints(self):
        print("1 skipped in 0.01s")


class TestPrintsNoTests:
    def test_prints(self):
        print("no tests ran in 0.01s")
'''

HEAD = "# {uid}: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n## Acceptance Criteria\n\n"
NAMED = "tests/test_q.py::TestMixed::test_skip_me (off on this host)"


class QuietFlagSkipReadTests(unittest.TestCase):
    def _project(self, root: Path, units: dict[str, str]) -> None:
        (root / "tests").mkdir()
        (root / "tests" / "test_q.py").write_text(TARGET, encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        for uid, verify in units.items():
            (bugs / f"{uid}-x.md").write_text(
                HEAD.format(uid=uid) + f"- [ ] **AC1** it holds\n  - **Verify:** {verify}\n",
                encoding="utf-8")

    def _run(self, root: Path, uid: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(["run", "--id", uid, "--root", str(root)])
        return rc, out.getvalue() + err.getvalue()

    def _stamped(self, root: Path, uid: str) -> bool:
        text = (root / "sdlc-studio" / "bugs" / f"{uid}-x.md").read_text(encoding="utf-8")
        return "Verified:** yes" in text

    def test_a_q_on_the_verify_line_still_reads_the_skips(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9101": "pytest tests/test_q.py::TestMixed -q",
                                 "BG9102": "pytest tests/test_q.py::TestMixed -qq",
                                 "BG9103": "pytest tests/test_q.py::TestAllSkip -q",
                                 "BG9104": "pytest tests/test_q.py::TestClean -q"})
            for uid in ("BG9101", "BG9102"):
                with self.subTest(uid):
                    rc, text = self._run(root, uid)
                    self.assertNotEqual(rc, 0, text)
                    self.assertFalse(self._stamped(root, uid), "a partly skipped run was stamped")
                    self.assertIn("SKIPPED 1 selected", text)
                    self.assertIn(NAMED, text)
            rc, text = self._run(root, "BG9103")
            self.assertNotEqual(rc, 0, text)
            self.assertFalse(self._stamped(root, "BG9103"), "an all-skipped run was stamped")
            self.assertIn("every selected test was SKIPPED", text)
            # Positive control: a quiet line whose target runs clean is still stamped.
            rc, text = self._run(root, "BG9104")
            self.assertEqual(rc, 0, text)
            self.assertTrue(self._stamped(root, "BG9104"), text)

    def test_a_summary_like_line_under_s_is_not_read_as_a_skip(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9105": "pytest tests/test_q.py::TestPrints -s",
                                 "BG9106": "pytest tests/test_q.py::TestMixed -s"})
            rc, text = self._run(root, "BG9105")
            self.assertEqual(rc, 0, text)
            self.assertTrue(self._stamped(root, "BG9105"), text)
            # Control: under -s a real skip still fails the criterion.
            rc, text = self._run(root, "BG9106")
            self.assertNotEqual(rc, 0, text)
            self.assertFalse(self._stamped(root, "BG9106"), "a partly skipped run was stamped")
            self.assertIn(NAMED, text)
        # pytest's own summary is the last on stdout: a test's earlier line, or one it wrote to
        # stderr, neither adds a skip nor hides one.
        cwd = Path.cwd()
        self.assertEqual("", verify_ac._pytest_partial_skips(
            "1 passed in 0.01s\n", "1 passed, 1 skipped in 0.01s\n", cwd))
        self.assertIn("SKIPPED 1 selected", verify_ac._pytest_partial_skips(
            "2 passed in 0.01s\n.s\n1 passed, 1 skipped in 0.01s\n", "", cwd))

    def test_a_skip_node_line_names_its_test(self):
        # The unfolded form pytest prints under --no-fold-skipped, copied from pytest 9's output.
        report = ("SKIPPED tests/test_q.py::TestMixed::test_skip_me - Skipped: off on this host\n"
                  "SKIPPED tests/test_q.py::TestOther::test_x - not here\n"
                  "1 passed, 2 skipped in 0.01s\n")
        msg = verify_ac._pytest_partial_skips(report, "", Path.cwd())
        self.assertIn("SKIPPED 2 selected", msg)
        self.assertIn(NAMED, msg)
        self.assertIn("tests/test_q.py::TestOther::test_x (not here)", msg)
        self.assertNotIn("add -rs", msg, "the report named its skips")


class AllSkippedReadUnderSTests(unittest.TestCase):
    """The all-skipped and no-tests verdicts read pytest's closing summary only, as the
    partial-skip read does, so a passing test that prints such a line under `-s` passes."""

    _project = QuietFlagSkipReadTests._project
    _run = QuietFlagSkipReadTests._run
    _stamped = QuietFlagSkipReadTests._stamped

    def test_a_printed_all_skipped_or_no_tests_line_under_s_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9111": "pytest tests/test_q.py::TestPrintsAllSkipped -s",
                                 "BG9112": "pytest tests/test_q.py::TestPrintsNoTests -s",
                                 "BG9113": "pytest tests/test_q.py::TestAllSkip -s"})
            for uid in ("BG9111", "BG9112"):
                with self.subTest(uid):
                    rc, text = self._run(root, uid)
                    self.assertEqual(rc, 0, text)
                    self.assertTrue(self._stamped(root, uid), text)
            # Control: under -s a target that really skips everything still fails as all-skipped.
            rc, text = self._run(root, "BG9113")
            self.assertNotEqual(rc, 0, text)
            self.assertFalse(self._stamped(root, "BG9113"), "an all-skipped run was stamped")
            self.assertIn("every selected test was SKIPPED", text)

    def test_the_closing_summary_decides_for_a_pytest_line(self):
        # An earlier summary-shaped line neither makes a run vacuous nor hides that it was.
        self.assertFalse(verify_ac._all_skipped("pytest", "1 skipped in 0.01s\n.\n1 passed in 0.02s\n", ""))
        self.assertTrue(verify_ac._all_skipped("pytest", "1 passed in 0.01s\ns\n1 skipped in 0.02s\n", ""))
        self.assertFalse(verify_ac._ran_no_tests("pytest", "no tests ran in 0.01s\n.\n1 passed in 0.02s\n", ""))
        self.assertTrue(verify_ac._ran_no_tests("pytest", "1 passed in 0.01s\nno tests ran in 0.02s\n", ""))
        # pytest writes its summary to stdout; stderr is read only when stdout holds none.
        self.assertFalse(verify_ac._all_skipped("pytest", "1 passed in 0.01s\n", "1 skipped in 0.01s\n"))
        self.assertTrue(verify_ac._ran_no_tests("pytest", "", "no tests ran in 0.01s\n"))


if __name__ == "__main__":
    unittest.main()
