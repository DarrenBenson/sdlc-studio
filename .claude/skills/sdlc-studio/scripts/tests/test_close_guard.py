"""The Stop-hook close guard (US0166): remind the agent of an owed close before a turn ends.

The load-bearing property is DEFAULT-ALLOW: a hook that blocks a turn on its own bug (bad stdin,
unbaselined project, detector crash) is worse than a missed reminder, so every doubt exits allow.
It blocks only on the one true positive - a delivery unit terminal since the baseline that no retro
accounts for - and never re-blocks a turn it already blocked.
"""
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "hooks"))
import close_guard  # noqa: E402
import close_owed  # noqa: E402


def _story(root: Path, sid: str, st: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}-s.md").write_text(f"# {sid}: s\n\n> **Status:** {st}\n> **Points:** 2\n",
                                   encoding="utf-8")


class CloseGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def _make_owed(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _story(self.root, "US0005", "Done")  # later, no retro -> owed

    def test_blocks_when_a_close_is_owed(self) -> None:
        self._make_owed()
        decision = close_guard.decide({"cwd": str(self.root)})
        self.assertIsNotNone(decision)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("US0005", decision["reason"])

    def test_allows_when_stop_hook_active(self) -> None:
        self._make_owed()
        self.assertIsNone(close_guard.decide({"cwd": str(self.root), "stop_hook_active": True}))

    def test_allows_when_covered_by_a_retro(self) -> None:
        self._make_owed()
        (self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md").write_text(
            "# RETRO-0002: s\n\n> **Batch:** US0005\n\n## Delivered\n- x\n", encoding="utf-8")
        self.assertIsNone(close_guard.decide({"cwd": str(self.root)}))

    def test_allows_when_unbaselined(self) -> None:
        _story(self.root, "US0005", "Done")  # uncovered but no baseline stamped
        self.assertIsNone(close_guard.decide({"cwd": str(self.root)}))

    def test_empty_event_falls_back_to_cwd_and_does_not_block_on_its_own(self) -> None:
        # A malformed event parses to {} (no cwd), so the hook falls back to the process cwd. It
        # must not block on ITS OWN bug: run it with cwd pointed at a baseline-less tree and assert
        # allow. (The hook legitimately blocks if the real cwd genuinely owes a close - that is the
        # feature, not a bug - so the tested invariant is "never block on a parse error", not
        # "never block".)
        import os
        from unittest import mock
        with mock.patch.object(os, "getcwd", return_value=str(self.root)):
            self.assertIsNone(close_guard.decide({}))  # {} -> cwd=self.root (unbaselined) -> allow

    def test_blocks_on_a_corrupt_baseline(self) -> None:
        # BG0155: a corrupt baseline silently disarms the close-down, so this is the one non-owed
        # case that must BLOCK - and direct a repair, never a re-stamp.
        _story(self.root, "US0005", "Done")
        (self.root / close_owed.BASELINE_FILE).write_text('["US0005"]', encoding="utf-8")
        decision = close_guard.decide({"cwd": str(self.root)})
        self.assertIsNotNone(decision)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("corrupt", decision["reason"].lower())
        self.assertIn("restore", decision["reason"].lower())  # directs a repair, not a re-stamp

    def test_block_reason_names_a_retro_missing_its_velocity_row(self) -> None:
        """US0288 AC4: the unit half being clean is not the whole close. A retro that never
        wrote its velocity row is an unfinished close, and the hook must say so rather than
        reporting nothing because no unit is uncovered."""
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-07-16")
        (self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md").write_text(
            "# RETRO-0002: s\n\n> **Date:** 2026-07-20\n> **Batch:** US0001\n\n"
            "## Delivered\n- x\n", encoding="utf-8")
        decision = close_guard.decide({"cwd": str(self.root)})
        self.assertIsNotNone(decision, "a close with no velocity row is still owed")
        self.assertEqual(decision["decision"], "block")
        self.assertIn("RETRO0002", decision["reason"])
        self.assertIn("VELOCITY", decision["reason"].upper())
        self.assertIn("accuracy", decision["reason"])

    def test_a_retro_with_its_row_written_does_not_block(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-07-16")
        (self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md").write_text(
            "# RETRO-0002: s\n\n> **Date:** 2026-07-20\n> **Batch:** US0001\n\n"
            "## Delivered\n- x\n", encoding="utf-8")
        (self.root / "sdlc-studio" / "retros" / "VELOCITY.md").write_text(
            "# Velocity history\n\n"
            "| Retro | Date | Units | Measured | Forecast | Points | Estimate | Actual | "
            "Ratio | Tokens/pt | Oversized | Wall | Constants | Sample | Model | Note | "
            "Source |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | "
            "--- | --- | --- | --- | --- | --- |\n"
            "| RETRO0002 | 2026-07-20 | 1 | 0 | 0 | 2 | - | - | - | - | 0 | - | - | "
            "unforecast | - | not attributable | - |\n", encoding="utf-8")
        self.assertIsNone(close_guard.decide({"cwd": str(self.root)}))

    def test_read_event_tolerates_garbage(self) -> None:
        import io
        from unittest import mock
        with mock.patch.object(sys, "stdin", io.StringIO("not json{{")):
            self.assertEqual(close_guard._read_event(), {})


if __name__ == "__main__":
    unittest.main()
