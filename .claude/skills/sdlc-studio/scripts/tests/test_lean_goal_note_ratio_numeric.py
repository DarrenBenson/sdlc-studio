"""BG0918: the close compares a note's ratio with the page's as a number, not as text.

BG0911's check named every ratio the goal verdict's note quotes that the filed page does not
derive, but compared the two as strings, so a note quoting 1.70x against a page that formats
the same ratio 1.7x was named as a contradiction. The ratios are now compared as numbers at the
page's precision; a ratio the page does contradict is still named.

Each case runs the real `sprint.py close` with every chain step stubbed green
(`test_lean_close._close`) over a run whose Tokens ratio derives to 1.7x.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared


class GoalNoteRatioNumericTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        empty = Path(self._tmp.name) / "transcripts"   # no meter: the close stamps nothing
        empty.mkdir()
        env = unittest.mock.patch.dict(
            os.environ, {lean._live("lib.run_state").TRANSCRIPTS_ENV: str(empty)})
        env.start()
        self.addCleanup(env.stop)

    def _close(self, name: str, note: str) -> tuple[int, list[str], str]:
        """Close a run whose page derives 1.7x: a 100,000 forecast against a meter delta of
        1,000 plus a 169,000 delegated total tagged to the one unit."""
        root = Path(self._tmp.name) / name
        root.mkdir()
        lean._fixture(
            root,
            sprint_goal_verdict={"verdict": "achieved", "note": note},
            plan_snapshot={"units": {"US0101": {"planned_points": 3, "forecast_minutes": 30.0,
                                                "forecast_tokens": 100_000, "added": False}}},
            session_token_stamps=[
                {"tokens": 1000, "source": "s.jsonl", "at": "2026-09-23T00:00:00Z",
                 "kind": "open"},
                {"tokens": 2000, "source": "s.jsonl", "at": "2026-09-23T01:00:00Z",
                 "kind": "report"}],
            delegated_tokens=[{"tokens": 169_000, "agent": "builder", "note": "",
                               "provenance": "supplied", "recorded_at": "2026-09-23T00:30:00Z",
                               "unit": "US0101"}])
        rc, out, err = lean._close(root)
        state = lean._read(root)
        page = lean._live("sprint_report").read_report(root, state["report"])
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        tokens = next(r for r in est["rows"] if r["est_measure"]["value"] == "Tokens")
        return rc, (out + err).splitlines(), tokens["est_ratio"]["value"]

    @staticmethod
    def named(lines: list[str]) -> list[str]:
        return [ln for ln in lines if "goal verdict note" in ln]

    def test_equal_ratios_written_differently_agree(self) -> None:
        """AC1. MUTANT: the text comparison, which names 1.70x against the page's 1.7x. The
        control: a note quoting 1.46x, which the page does contradict, is still named, so a
        check that names nothing also fails."""
        rc, lines, ratio = self._close("same", "tokens at 1.70x, every unit delivered")
        self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
        self.assertEqual(0, rc, "\n".join(lines))
        self.assertEqual([], self.named(lines), lines)

        rc, lines, ratio = self._close("contradicted", "tokens at 1.46x, every unit delivered")
        self.assertEqual("1.7x", ratio)
        self.assertEqual(0, rc, "\n".join(lines))
        named = self.named(lines)
        self.assertEqual(1, len(named), lines)
        self.assertIn("1.46x", named[0])
        self.assertIn("1.7x", named[0])


if __name__ == "__main__":
    unittest.main()
