"""A pytest Verify that runs some of its tests and skips the rest is not a pass.

An all-skipped run was already refused as vacuous; a run printing "1 passed, 1 skipped" was
stamped `Verified: yes` although the skipped test, the one carrying the criterion's behaviour,
never ran where the gate runs. Both routes are driven through `verify_ac.py run`: the per-AC
subprocess, and `--batch`, which reads a JUnit report and hands a partly skipped target back to
that subprocess. Each refusal sits beside a positive control that is stamped, so a change that
fails every pytest run cannot pass.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

MIXED = '''import pytest


class TestPartial:
    def test_partial_structure(self):
        assert True

    def test_partial_render(self):
        pytest.importorskip("no_such_module_for_bg_partial_skip")
        assert True

    @pytest.mark.skip(reason="not on this platform")
    def test_partial_marked(self):
        assert True


class TestGreen:
    def test_green_one(self):
        assert True

    def test_green_two(self):
        assert True
'''

CLASS_SKIP = '''import pytest


def test_cls_runs():
    assert True


@pytest.mark.skip(reason="class off")
class TestOff:
    def test_off_one(self):
        assert True

    def test_off_two(self):
        assert True


@pytest.mark.skip("other")
class TestAlso:
    def test_also(self):
        assert True
'''

MODULE_SKIP = '''import pytest

pytestmark = pytest.mark.skip(reason="module off")


def test_mod_one():
    assert True
'''

HEAD = "# {uid}: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n## Acceptance Criteria\n\n"


class PartialSkipTests(unittest.TestCase):
    def _project(self, root: Path, units: dict[str, str]) -> None:
        (root / "tests").mkdir()
        (root / "tests" / "test_mixed.py").write_text(MIXED, encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        for uid, verify in units.items():
            (bugs / f"{uid}-x.md").write_text(
                HEAD.format(uid=uid) + f"- [ ] **AC1** it holds\n  - **Verify:** {verify}\n",
                encoding="utf-8")

    def _run(self, root: Path, uid: str, *extra: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(["run", "--ids" if "," in uid else "--id", uid,
                                 "--root", str(root), *extra])
        return rc, out.getvalue() + err.getvalue()

    def _stamped(self, root: Path, uid: str) -> bool:
        text = (root / "sdlc-studio" / "bugs" / f"{uid}-x.md").read_text(encoding="utf-8")
        return "Verified:** yes" in text

    def _assert_names_each_skip(self, text: str) -> None:
        self.assertIn("test_partial_render", text)
        self.assertIn("no_such_module_for_bg_partial_skip", text, "the skip's reason is named")
        self.assertIn("test_partial_marked", text)
        self.assertIn("not on this platform", text, "the skip's reason is named")
        self.assertNotIn("test_partial_structure", text, "a test that ran is not called skipped")

    def test_a_partly_skipped_run_is_not_verified(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9001": "pytest tests/test_mixed.py -k partial",
                                 "BG9002": "pytest tests/test_mixed.py -k green"})
            rc, text = self._run(root, "BG9001")
            self.assertNotEqual(rc, 0, text)
            self.assertIn("fail=1", text)
            self.assertFalse(self._stamped(root, "BG9001"), "a partly skipped run was stamped")
            self._assert_names_each_skip(text)
            # Positive control: the same file, a selector whose tests all run, is stamped.
            rc, text = self._run(root, "BG9002")
            self.assertEqual(rc, 0, text)
            self.assertTrue(self._stamped(root, "BG9002"), text)

    def test_the_junit_path_reads_a_partial_skip_as_unverified(self):
        report = ('<testsuites><testsuite>'
                  '<testcase classname="tests.test_mixed.TestPartial" name="test_partial_structure"/>'
                  '<testcase classname="tests.test_mixed.TestPartial" name="test_partial_render">'
                  '<skipped message="could not import"/></testcase>'
                  '</testsuite></testsuites>')
        nodes = verify_ac._parse_junit_xml(report, ["tests/test_mixed.py"])
        cached = verify_ac.resolve_pytest_from_cache("pytest tests/test_mixed.py::TestPartial", nodes)
        self.assertFalse(cached is not None and cached.ok, "the JUnit cache passed a partial skip")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9001": "pytest tests/test_mixed.py::TestPartial",
                                 "BG9002": "pytest tests/test_mixed.py::TestGreen"})
            # One serial batch answers both: the parallel phase decides no verdict, only speed.
            with unittest.mock.patch.object(verify_ac, "_xdist_args", return_value=None):
                rc, text = self._run(root, "BG9001,BG9002", "--batch")
            self.assertIn("batch: cached 5 pytest node(s)", text, "the batch never ran")
            self.assertNotEqual(rc, 0, text)
            self.assertFalse(self._stamped(root, "BG9001"), "the batch route stamped a partial skip")
            self._assert_names_each_skip(text)
            self.assertTrue(self._stamped(root, "BG9002"), text)

    def test_a_class_or_module_skip_mark_is_named(self):
        # pytest folds a skip mark on a class or a module with no line number.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9001": "pytest tests/test_cls.py tests/test_mod.py",
                                 "BG9002": "pytest tests/test_cls.py::test_cls_runs"})
            (root / "tests" / "test_cls.py").write_text(CLASS_SKIP, encoding="utf-8")
            (root / "tests" / "test_mod.py").write_text(MODULE_SKIP, encoding="utf-8")
            rc, text = self._run(root, "BG9001")
            self.assertNotEqual(rc, 0, text)
            self.assertFalse(self._stamped(root, "BG9001"), "a partly skipped run was stamped")
            self.assertIn("SKIPPED 4 selected", text)
            # Each fold is tied to its class by the reason its mark gives.
            self.assertIn("tests/test_cls.py::TestOff x2 (class off)", text)
            self.assertIn("tests/test_cls.py::TestAlso (other)", text)
            self.assertIn("tests/test_mod.py (module off)", text)
            self.assertNotIn("add -rs", text, "the command already asks for the skip report")
            self.assertNotIn("test_cls_runs", text, "a test that ran is not called skipped")
            rc, text = self._run(root, "BG9002")
            self.assertEqual(rc, 0, text)
            self.assertTrue(self._stamped(root, "BG9002"), text)


class PartialSkipNamingTests(unittest.TestCase):
    """The verdict's edges: what names a skip when pytest's report folds it, and what is judged."""

    def test_a_module_level_skip_is_named_by_its_location(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_m.py").write_text("import pytest\nX = 1\n\n\ndef test_a():\n    pass\n",
                                               encoding="utf-8")
            msg = verify_ac._pytest_partial_skips(
                "SKIPPED [3] test_m.py:2: no module\n1 passed, 3 skipped in 0.1s", "", Path(d))
        self.assertIn("SKIPPED 3 selected", msg)
        self.assertIn("test_m.py:2 x3 (no module)", msg)

    def test_a_skip_the_report_does_not_list_still_counts(self):
        msg = verify_ac._pytest_partial_skips("2 passed, 1 skipped in 0.1s", "", Path.cwd())
        self.assertIn("SKIPPED 1 selected", msg)
        self.assertEqual("", verify_ac._pytest_partial_skips("2 passed in 0.1s", "", Path.cwd()))

    def test_only_the_pytest_verb_is_judged(self):
        # A `shell` line running a whole suite keeps its own verdict; its skips are its own.
        r = verify_ac.run_verifier("shell printf '%s\\n' '3 passed, 1 skipped in 0.04s'", 30, Path.cwd())
        self.assertTrue(r.ok, r.stderr)


if __name__ == "__main__":
    unittest.main()
