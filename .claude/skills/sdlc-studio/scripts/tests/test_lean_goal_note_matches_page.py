"""BG0911: the close names a ratio the goal verdict's note quotes and the filed page contradicts.

RUN-01M3Y7DP's note quoted 1.46x from a pre-close preview; the filed RPT0015 derived 1.69x, and
the close said nothing, so the operator nearly signed a page whose verdict line disagreed with its
own Estimates table. The close now reads the ratios off the page it filed (what PREPARE froze)
and prints one line naming each quoted ratio the page does not derive. A warning, never a
refusal: the exit code is unchanged.

Each test runs the real `sprint.py close` with every chain step stubbed green
(`test_lean_close._close`) over a run whose Tokens ratio derives to 1.69x.
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


def _run(root: Path, note: str) -> None:
    """The lean close fixture whose page derives a Tokens ratio of 1.69x: a 100,000 forecast
    against a meter delta of 1,000 plus a 168,000 delegated total tagged to the one unit."""
    lean._fixture(
        root,
        sprint_goal_verdict={"verdict": "achieved", "note": note},
        plan_snapshot={"units": {"US0101": {"planned_points": 3, "forecast_minutes": 30.0,
                                            "forecast_tokens": 100_000, "added": False}}},
        session_token_stamps=[
            {"tokens": 1000, "source": "s.jsonl", "at": "2026-09-23T00:00:00Z", "kind": "open"},
            {"tokens": 2000, "source": "s.jsonl", "at": "2026-09-23T01:00:00Z",
             "kind": "report"}],
        delegated_tokens=[{"tokens": 168_000, "agent": "builder", "note": "",
                           "provenance": "supplied", "recorded_at": "2026-09-23T00:30:00Z",
                           "unit": "US0101"}])


class GoalNoteMatchesPageTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        empty = Path(self._tmp.name) / "transcripts"   # no meter: the close stamps nothing
        empty.mkdir()
        env = unittest.mock.patch.dict(
            os.environ, {lean._live("lib.run_state").TRANSCRIPTS_ENV: str(empty)})
        env.start()
        self.addCleanup(env.stop)

    def _close(self, note: str) -> tuple[int, list[str], str]:
        _run(self.root, note)
        rc, out, err = lean._close(self.root)
        state = lean._read(self.root)
        page = lean._live("sprint_report").read_report(self.root, state["report"])
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        tokens = next(r for r in est["rows"] if r["est_measure"]["value"] == "Tokens")
        return rc, (out + err).splitlines(), tokens["est_ratio"]["value"]

    def test_a_note_figure_the_page_contradicts_is_named(self) -> None:
        """AC1. MUTANT: HEAD, which files the page and prints nothing about the note; or a
        check that reads the note against a live re-derivation rather than the filed page."""
        rc, lines, ratio = self._close("tokens 1.87M at 1.46x, every unit delivered")
        self.assertEqual("1.69x", ratio, "premise: the filed page derives 1.69x")
        self.assertEqual(0, rc, "\n".join(lines))
        named = [ln for ln in lines if "1.46x" in ln and "1.69x" in ln]
        self.assertEqual(1, len(named), "\n".join(lines))

    def test_a_note_the_page_agrees_with_is_not_named(self) -> None:
        """The positive control. MUTANT: name every ratio the note quotes, agreeing or not."""
        rc, lines, ratio = self._close("tokens at 1.69x, every unit delivered")
        self.assertEqual("1.69x", ratio)
        self.assertEqual(0, rc, "\n".join(lines))
        self.assertEqual([], [ln for ln in lines if "goal verdict note" in ln], lines)


if __name__ == "__main__":
    unittest.main()
