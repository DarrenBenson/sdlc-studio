"""BG1398: a multi-unit lane brief states the lane's total tool-call budget once.

Each unit's brief carries its own `Budget: N tool calls` line, and `sprint lane brief` printed
the briefs one after another with nothing after them, so a builder handed a lane of several
units never saw the sum. These drive `sprint.py lane brief` in-process against
`test_lane_brief_budget`'s throwaway project (two Ready stories of 1 and 5 points in an open
run). MUTANTS, each failed here: no total printed (AC1); a total printed for a lane of one unit
(AC2); a lane holding an unsized unit summed over its sized units alone (AC3).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_brief_budget as budget  # noqa: E402 - the two-story lane project, shared

TOTAL = "Lane total:"


def _brief(root: Path, *uids: str) -> str:
    """`sprint.py lane brief --units <uids>`'s stdout; a refusal fails the test."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = budget._live("sprint").main(["lane", "brief", "--units", *uids,
                                          "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _totals(out: str) -> list[str]:
    return [ln for ln in out.splitlines() if ln.startswith(TOTAL)]


class LaneTotalBudgetTests(unittest.TestCase):

    def _root(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return budget._project(tmp.name)

    def test_a_multi_unit_brief_states_the_lane_total_once(self) -> None:
        """AC1. Two briefs of 38 and 90 calls, then one total line after both, stating 128
        calls over 2 units with each unit's share."""
        out = _brief(self._root(), "US0101", "US0102")
        self.assertEqual(["38", "90"], re.findall(r"Budget: (\d+) tool calls", out), out)
        self.assertEqual(["Lane total: 128 tool calls over 2 units (38 + 90), the sum of the "
                          "per-unit budgets above."], _totals(out), out)
        lines = out.splitlines()
        at = lines.index(_totals(out)[0])
        last_budget = max(i for i, ln in enumerate(lines) if "Budget: " in ln)
        self.assertGreater(at, last_budget, "the total is not stated after both briefs")
        self.assertNotIn("Budget:", _totals(out)[0])

    def test_a_single_unit_brief_states_no_separate_total(self) -> None:
        """AC2. One unit: no total line, and still exactly one `Budget:` line."""
        root = self._root()
        for uid, calls in (("US0101", 38), ("US0102", 90)):
            with self.subTest(uid=uid):
                out = _brief(root, uid)
                self.assertEqual([], _totals(out), out)
                self.assertEqual(calls, budget._budget(out))

    def test_an_unsized_unit_leaves_the_lane_total_underived(self) -> None:
        """AC3. US0102 declares no Points: the total line says none is derived, names it, and
        states no figure; summing the sized unit alone would understate the lane."""
        root = self._root()
        story = root / "sdlc-studio" / "stories" / "US0102-x.md"
        story.write_text(story.read_text(encoding="utf-8").replace("> **Points:** 5\n", ""),
                         encoding="utf-8")
        out = _brief(root, "US0101", "US0102")
        [line] = _totals(out)
        self.assertEqual("Lane total: NONE DERIVED - US0102 declares no Points, so no lane "
                         "total follows; size it before building it.", line)
        self.assertIsNone(re.search(r"\d+ tool calls", line), line)
        self.assertNotIn("38", line)
        story = root / "sdlc-studio" / "stories" / "US0101-x.md"
        story.write_text(story.read_text(encoding="utf-8").replace("> **Points:** 1\n", ""),
                         encoding="utf-8")
        out = _brief(root, "US0101", "US0102")
        self.assertEqual(["Lane total: NONE DERIVED - US0101, US0102 declare no Points, so no "
                          "lane total follows; size them before building them."], _totals(out))


if __name__ == "__main__":
    unittest.main()
