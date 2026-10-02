"""BG0905: a delivered unit with no span and no agent total withholds the tokens ratio.

`_tokens_ratio_withheld` withholds the Estimates tokens ratio when any live unit that did work
- delivered, or carrying a span - supplied no agent total. Every earlier test delivered through
a lane, which opens a span, so a check over spanned units alone survived them all while a unit
moved to Done without a brief would then print a ratio over a partial actual. This pins the
delivered half.

Drives `sprint.py lane` in-process against the throwaway workspace of
`test_lean_lane_delegated_tokens`, and derives the page through `sprint_report.build_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_lane_delegated_tokens as lane  # noqa: E402 - the lane workspace, shared


class RatioWithheldDeliveredTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = lane._Workspace(self._tmp.name)
        env = unittest.mock.patch.dict(
            os.environ, {lane._live("lib.run_state").TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def test_a_delivered_unit_with_no_span_withholds_the_ratio(self) -> None:
        """AC1. MUTANT: check spanned units only (`u["spanned"]` for `u["delivered"] or
        u["spanned"]`), so US0102, moved to Done with no brief, owes nothing and the page prints
        a ratio over US0101's total alone. The control: once US0102's agent total is recorded,
        the ratio is stated."""
        ws, sr = self.ws, lane._live("sprint_report")
        ws.deliver("US0101", "--tokens", "250000")
        p = ws.root / "sdlc-studio" / "stories" / "US0102-x.md"
        p.write_text(p.read_text(encoding="utf-8").replace("Ready", "Done"), encoding="utf-8")
        row = ws.tokens_row(ws.page())
        self.assertEqual(sr.NOT_MEASURED, row["est_ratio"]["value"])
        reason = row["est_ratio"]["reason"]
        self.assertIn("US0102 supplied no agent total", reason)
        self.assertNotIn("US0101", reason)
        lane._live("lib.run_state").record_delegated_tokens(ws.root, 150_000, unit="US0102")
        self.assertRegex(ws.tokens_row(ws.page())["est_ratio"]["value"], r"^\d+(\.\d+)?x$")


if __name__ == "__main__":
    unittest.main()
