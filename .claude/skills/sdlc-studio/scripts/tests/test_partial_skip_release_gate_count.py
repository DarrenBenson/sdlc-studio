"""The release gate counts its partial skips apart from its other failures.

A criterion whose pytest target runs only in part fails, and before this it was counted inside
`fail=` alone, so a gate reading a red corpus could not say how many of its reds were partial
skips. `verify_ac.py run` and `verify_ac.py report` now print `partly_skipped=N` on each
story's line and on the total line, and the total line names each partly skipped criterion.
An all-skipped target keeps its own vacuous verdict and a clean one adds nothing.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

TARGET = '''import pytest


class TestPartial:
    def test_runs(self):
        assert True

    @pytest.mark.skip(reason="off on this host")
    def test_skip_me(self):
        assert True


class TestFails:
    def test_red(self):
        assert False


class TestAllSkip:
    @pytest.mark.skip(reason="all off")
    def test_only(self):
        assert True


class TestClean:
    def test_clean(self):
        assert True
'''

HEAD = "# {uid}: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n## Acceptance Criteria\n\n"
REPORT = "sdlc-studio/.local/verify-report.json"


class PartialSkipReleaseGateCountTests(unittest.TestCase):
    def _project(self, root: Path, units: dict[str, str]) -> None:
        (root / "tests").mkdir()
        (root / "tests" / "test_g.py").write_text(TARGET, encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        for uid, verify in units.items():
            (bugs / f"{uid}-x.md").write_text(
                HEAD.format(uid=uid) + f"- [ ] **AC1** it holds\n  - **Verify:** {verify}\n",
                encoding="utf-8")

    def _main(self, argv: list[str]) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(argv)
        return rc, out.getvalue() + err.getvalue()

    def _run_and_report(self, root: Path, ids: str) -> tuple[str, str]:
        _, ran = self._main(["run", "--ids", ids, "--root", str(root)])
        _, reported = self._main(["report", "--report", str(root / REPORT)])
        return ran, reported

    def _story(self, text: str, uid: str) -> str:
        found = re.search(rf"^.*\b{uid}-x(?:\.md)?: ac=.*$", text, re.M)
        self.assertIsNotNone(found, f"no summary line for {uid}:\n{text}")
        return found.group(0)

    def _total(self, text: str) -> str:
        found = re.search(r"^total: .*$", text, re.M)
        self.assertIsNotNone(found, f"no total line:\n{text}")
        return found.group(0)

    def test_the_summary_counts_partial_skips_apart_from_other_failures(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9201": "pytest tests/test_g.py::TestPartial",
                                 "BG9202": "pytest tests/test_g.py::TestFails"})
            for name, text in zip(("run", "report"), self._run_and_report(root, "BG9201,BG9202")):
                with self.subTest(name):
                    self.assertIn(" fail=1 partly_skipped=1 ", self._story(text, "BG9201"))
                    self.assertIn(" fail=1 partly_skipped=0 ", self._story(text, "BG9202"))
                    total = self._total(text)
                    self.assertIn(" fail=2 partly_skipped=1 ", total)
                    self.assertIn("(partly skipped: BG9201 AC1)", total)
                    self.assertNotIn("BG9202", total, "an outright failure is not a partial skip")

    def test_an_all_skipped_or_clean_target_is_not_counted(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root, {"BG9203": "pytest tests/test_g.py::TestAllSkip",
                                 "BG9204": "pytest tests/test_g.py::TestClean",
                                 "BG9201": "pytest tests/test_g.py::TestPartial"})
            ran, reported = self._run_and_report(root, "BG9203,BG9204,BG9201")
            self.assertIn("every selected test was SKIPPED", ran, "the all-skipped verdict is kept")
            for name, text in (("run", ran), ("report", reported)):
                with self.subTest(name):
                    self.assertIn(" fail=1 partly_skipped=0 ", self._story(text, "BG9203"))
                    self.assertIn(" pass=1 fail=0 partly_skipped=0 ", self._story(text, "BG9204"))
                    # Positive control: the partial skip beside them is the one counted.
                    total = self._total(text)
                    self.assertIn(" fail=2 partly_skipped=1 ", total)
                    self.assertIn("(partly skipped: BG9201 AC1)", total)
            data = json.loads((root / REPORT).read_text(encoding="utf-8"))
            failure = data["stories"]["BG9203-x"]["failures"][0]
            self.assertTrue(failure["vacuous"], failure)
            self.assertFalse(failure["partly_skipped"], failure)


if __name__ == "__main__":
    unittest.main()
