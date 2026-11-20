"""BG1096: the TRD's coverage clause says which half does what when `coverage` is absent.

`verify_ac run --coverage` exits 2 naming the module absent, whatever `review.line_coverage`
says; the block/report split belongs to the Done gate in `transition.py`, which refuses under
`block` and reports under `report`. Both halves are driven here with the measurement refusing
as it does when the module is absent, and the clause in the TRD's Script language row is held to what they do.

Run from the repo root:
    python3 -m pytest tools/tests/test_trd_coverage_soft_dependency.py
"""
# test-census-subject: sdlc-studio/trd.md
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
import gitutil  # noqa: E402 - confined git for the fixture repository
import transition  # noqa: E402
import verify_ac  # noqa: E402

UNIT = "US0001"
STORY = (f"# {UNIT}: a story\n\n> **Status:** Ready\n> **Affects:** a.txt\n\n"
         "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file a.txt\n")


def _clause() -> str:
    """The Script language row's text from `coverage` on, whitespace collapsed."""
    body = TRD.read_text(encoding="utf-8").split("\n## Revision History", 1)[0]
    rows = [r for r in body.splitlines() if r.startswith("| Script language |")]
    if len(rows) != 1:
        raise AssertionError(f"{len(rows)} Script language rows, expected one")
    row = " ".join(rows[0].split())
    at = row.find("`coverage`")
    if at < 0:
        raise AssertionError("the Script language row does not name `coverage`")
    return row[at:]


class TrdCoverageSoftDependencyTests(unittest.TestCase):

    def _absent(self) -> contextlib.AbstractContextManager:
        return mock.patch.object(verify_ac, "coverage_report", side_effect=(
            verify_ac.CoverageUnavailable(f"{verify_ac.COVERAGE_ABSENT} on python")))

    def _run_exit(self, mode: str) -> tuple[int, str]:
        """`verify_ac.py run --coverage` on a fixture whose config sets `review.line_coverage`
        to `mode`, with the coverage module absent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.txt").write_text("a\n", encoding="utf-8")
            sd = root / "sdlc-studio"
            (sd / "stories").mkdir(parents=True)
            (sd / "stories" / f"{UNIT}-a.md").write_text(STORY, encoding="utf-8")
            (sd / ".config.yaml").write_text(f"review:\n  line_coverage: {mode}\n",
                                             encoding="utf-8")
            gitutil.git(["init", "-q", "--template="], root)
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-q", "-m", f"fix({UNIT}): a"], root)
            err = io.StringIO()
            with self._absent(), contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(err):
                rc = verify_ac.main(["--root", str(root), "run", "--id", UNIT, "--coverage",
                                     "--dry-run"])
        return rc, err.getvalue()

    def _gate(self, mode: str) -> dict:
        """The Done gate's coverage lane under `mode`, with the coverage module absent."""
        with tempfile.TemporaryDirectory() as d, self._absent(), \
                mock.patch.object(transition, "line_coverage_mode", return_value=mode):
            return transition.line_coverage_lane(d, UNIT, STORY, "story", Path(d) / "s.md",
                                                 base_ref="HEAD")

    def test_the_run_exits_2_and_the_done_gate_splits_block_from_report(self) -> None:
        """Mutants: the clause saying the run refuses under `block` and reports under
        `report`; the clause not naming the run's exit, or not naming the Done gate as the
        split; the run reading `review.line_coverage` (exit 0 under `report`); the gate
        passing an absent module under `block`, or refusing it under `report`."""
        for mode in ("block", "report"):
            with self.subTest(run=mode):
                rc, err = self._run_exit(mode)
                self.assertEqual(2, rc, err)
                self.assertIn(verify_ac.COVERAGE_ABSENT, err)
        block = self._gate("block")
        self.assertTrue(block["blocks"], block)
        self.assertIn(verify_ac.COVERAGE_ABSENT, block["blocks"][0])
        report = self._gate("report")
        self.assertEqual([], report["blocks"])
        self.assertEqual(transition.LINE_COVERAGE_ABSENT_REPORT, report["warning"])
        clause = _clause()
        self.assertNotRegex(clause, r"the run refuses under `block`")
        self.assertRegex(clause, r"`verify_ac run --coverage`[^;]*module absent[^;]*exits 2[^;]*"
                                 r"whatever `review\.line_coverage` says")
        self.assertRegex(clause, r"Done gate[^;)]*`transition\.py`[^;)]*refuses under `block` "
                                 r"and reports under `report`")


if __name__ == "__main__":
    unittest.main()
