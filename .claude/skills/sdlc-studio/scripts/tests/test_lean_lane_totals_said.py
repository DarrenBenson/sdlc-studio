"""BG0903: a lane total that is not recorded, or is recorded off the batch, is said.

`sprint lane return --tokens` dropped the total with no word when no run was open, recorded a
total for a unit outside the batch though no per-unit row shows it, and `lane brief --tokens`
was accepted and ignored. Each now prints one line saying so, as `retro.py accuracy` does for
its sibling record; exit codes are unchanged and nothing new is refused.

Driven through `sprint.py lane` in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

UNITS = ("US0101", "US0199")


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


class LaneTotalsSaidTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in UNITS:
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Points:** 1\n> **Affects:** src/a.py\n\n"
                "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n",
                encoding="utf-8")
        self.rs = _live("lib.run_state")

    def lane(self, *argv: str) -> tuple[int, list[str]]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("sprint").main(["lane", *argv, "--root", str(self.root)])
        return rc, out.getvalue().splitlines()

    @staticmethod
    def said(lines: list[str]) -> list[str]:
        return [ln for ln in lines if "--tokens" in ln and ("not recorded" in ln
                                                            or "off the batch" in ln)]

    def test_each_unrecorded_or_off_batch_total_is_said(self) -> None:
        """AC1. MUTANT: HEAD, which says nothing in all three cases. The controls: a total for a
        batch unit of the open run is recorded and says none of it, and each exit code is the
        one the same call gives without `--tokens`."""
        # 1. no open run: nothing to record the total against
        rc_bare, _ = self.lane("return", "--units", "US0101")
        rc, lines = self.lane("return", "--units", "US0101", "--tokens", "9000")
        self.assertEqual((rc_bare, 1), (rc, len(self.said(lines))), lines)
        self.assertIn("no run is open", self.said(lines)[0])
        self.assertEqual([], self.rs.delegated_records(self.rs.read(self.root)))

        self.rs.open_run(self.root, batch=["US0101"], goal="g")
        # 2. a unit outside the batch: recorded, but no per-unit row shows it
        rc_bare, _ = self.lane("return", "--units", "US0199")
        rc, lines = self.lane("return", "--units", "US0199", "--tokens", "9000")
        self.assertEqual((rc_bare, 1), (rc, len(self.said(lines))), lines)
        self.assertIn("US0199", self.said(lines)[0])
        self.assertIn("off the batch", self.said(lines)[0])

        # 3. a brief: it records no total
        rc_bare, _ = self.lane("brief", "--units", "US0101")
        rc, lines = self.lane("brief", "--units", "US0101", "--tokens", "9000")
        self.assertEqual((rc_bare, 1), (rc, len(self.said(lines))), lines)
        self.assertIn("lane return", self.said(lines)[0])

        # the control: a batch unit's total in the open run is recorded, and nothing is said
        rc, lines = self.lane("return", "--units", "US0101", "--tokens", "7000")
        self.assertEqual((0, []), (rc, self.said(lines)), lines)
        self.assertEqual([9000, 7000], [r["tokens"] for r in self.rs.delegated_records(
            self.rs.read(self.root))])


if __name__ == "__main__":
    unittest.main()
