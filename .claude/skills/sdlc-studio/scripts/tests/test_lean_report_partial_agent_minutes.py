"""BG0901: a unit's supplied agent minutes win over its span when another agent gave none.

`sprint_report` read a unit's agent minutes only when every agent total tagged to it carried
minutes, so a builder's 40-minute total beside a second total with no minutes made the unit
read its 7-minute lane span, unlabelled, beside tokens labelled as the agents'. The supplied
agent minutes now count, labelled as agent minutes over the agents that supplied them, and the
span is the fallback only when no agent supplied minutes. A page filed before the rule carries
no mark and re-derives as it was signed.

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


class PartialAgentMinutesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = lane._Workspace(self._tmp.name)
        env = unittest.mock.patch.dict(
            os.environ, {lane._live("lib.run_state").TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def test_supplied_agent_minutes_win_when_one_agent_gave_none(self) -> None:
        """AC1. MUTANT: HEAD, which reads agent minutes only when every tagged agent supplied
        them (`timed == agents`), so US0101 reads its 7-minute span unlabelled. The controls: a
        unit no agent timed still reads its span, unlabelled; and a page filed before the rule
        re-derives the span it was signed with."""
        ws, sr = self.ws, lane._live("sprint_report")
        rs = lane._live("lib.run_state")
        ws.deliver("US0101", "--tokens", "250000", "--minutes", "40", minutes=7)
        rs.record_delegated_tokens(ws.root, 50_000, agent="reviewer", unit="US0101")
        ws.deliver("US0102", "--tokens", "90000", minutes=9)          # no agent minutes
        rows = ws.unit_rows(ws.page())
        mins = rows["US0101"]["eu_minutes"]
        self.assertEqual(40.0, mins["value"])
        self.assertIn("agent minutes", mins.get("label", ""))
        self.assertIn("1 of 2", mins["label"])
        self.assertEqual(300_000, rows["US0101"]["eu_tokens"]["value"])
        span = rows["US0102"]["eu_minutes"]
        self.assertEqual(9.0, span["value"])
        self.assertNotIn("label", span)
        before = ws.unit_rows(sr.build_report(ws.root, lane.RETRO, agent_minutes_rule=False))
        self.assertEqual(7.0, before["US0101"]["eu_minutes"]["value"])
        self.assertNotIn("label", before["US0101"]["eu_minutes"])


if __name__ == "__main__":
    unittest.main()
