"""US0947: the files the close writes pass markdownlint without a hand fix.

Two writers the close runs left their output for a human to trim before the paperwork commit
could pass the repo's markdownlint: the lesson-graduation CR put its `Hits:` list straight under
the label (MD032, a list needs a blank line above it), and the retro's accuracy block, written
under an `## Estimate vs actual` heading at the foot of the file, left a trailing blank line
(MD012). The tests assert the structure markdownlint checks rather than run a node binary, so
they run without npm. Each is driven through the writer the close calls, in a throwaway tree.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

lessons = loader.load_script("lessons")
retro = loader.load_script("retro")

CR_INDEX = ("# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 0 |\n"
            "| **Total** | **0** |\n\n## All\n\n"
            "| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n")


def _accuracy_res(path: Path) -> dict:
    """The smallest result `write_accuracy` renders: one measured unit and its batch line."""
    unit = {"id": "US0001", "points": 2, "state": "measured", "estimate": 50000,
            "actual_tokens": 40000, "ratio": 1.25, "tokens_per_point": 20000,
            "oversized": False, "wall_time_s": 60, "model": "m"}
    batch = {"points": 2, "estimate": 50000, "actual_tokens": 40000, "ratio": 1.25,
             "tokens_per_point": 20000, "wall_time_s": 60, "oversized": [],
             "tokens_per_point_within": 20000, "split_above": 8}
    return {"path": str(path), "batch": batch, "units": [unit], "n_units": 1,
            "n_measured": 1, "n_forecast": 1, "n_sized": 1, "unmeasured": [], "unforecast": [],
            "models": ["m"], "constants": None, "sample": None}


class CloseWritersLintTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_a_graduation_cr_has_a_blank_line_before_its_list(self) -> None:
        """AC1. A class recorded in RUN-0 and repeated in RUN-1 and RUN-2 graduates at the
        close of RUN-3, which files its CR. MUTANT: HEAD's `Hits:\\n- ...` - the first item
        sits directly under the label and markdownlint refuses it as MD032."""
        crs = self.root / "sdlc-studio" / "change-requests"
        crs.mkdir(parents=True)
        (crs / "_index.md").write_text(CR_INDEX, encoding="utf-8")
        row = {"id": "LC-001", "class": "stale read", "rule": "Read before you write.",
               "behaviour": "Re-read the file first.", "inject": ["build"], "state": "active",
               "recorded_run": "RUN-0",
               "hits": [{"run": "RUN-1", "unit": "US0001", "source": "critic:RUN-1",
                         "finding": "the file was written from a stale read"},
                        {"run": "RUN-2", "unit": "US0002", "source": "critic:RUN-2"}]}
        store = self.root / lessons.STORE_FILE
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(row) + "\n", encoding="utf-8")

        res = lessons.close_pass(self.root, "RUN-3", {})

        self.assertEqual([], res["errors"])
        self.assertEqual(1, len(res["graduating"]), res)
        [cr] = sorted(crs.glob("CR*.md"))
        lines = cr.read_text(encoding="utf-8").splitlines()
        at = lines.index("Hits:")
        first = next(i for i in range(at + 1, len(lines)) if lines[i].startswith("- "))
        self.assertEqual("", lines[first - 1],
                         f"no blank line above the Hits list:\n{lines[at:first + 1]}")
        self.assertIn("RUN-1 on US0001", lines[first])

    def _retro(self, text: str) -> Path:
        path = self.root / "RETRO0001-a-sprint.md"
        path.write_text(text, encoding="utf-8")
        retro.write_accuracy(self.root, _accuracy_res(path))
        return path

    def test_accuracy_write_at_the_foot_ends_with_one_newline(self) -> None:
        """AC2. MUTANT: HEAD, which appends `block + "\\n\\n"` under a heading at the foot and
        leaves a trailing blank line (MD012)."""
        path = self._retro("# RETRO-0001: a sprint\n\n## Keep\n\n- small units\n\n"
                           f"## {retro.ACCURACY_SECTION}\n")
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.endswith(retro.ACCURACY_END + "\n"), repr(text[-60:]))
        self.assertFalse(text.endswith("\n\n"), repr(text[-60:]))

    def test_accuracy_write_mid_file_keeps_one_blank_line(self) -> None:
        """AC3. MUTANT: strip every trailing newline from the block - it then joins the next
        heading with no blank line between them."""
        path = self._retro("# RETRO-0001: a sprint\n\n## Keep\n\n- small units\n\n"
                           f"## {retro.ACCURACY_SECTION}\n\n## Actions raised\n\n- none\n")
        text = path.read_text(encoding="utf-8")
        self.assertIn(retro.ACCURACY_END + "\n\n## Actions raised\n", text)
        self.assertNotIn(retro.ACCURACY_END + "\n\n\n", text)
        self.assertTrue(text.endswith("- none\n"), repr(text[-40:]))


if __name__ == "__main__":
    unittest.main()
