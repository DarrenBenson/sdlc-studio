"""`sprint lane run` refuses a unit whose lane is the main checkout.

A unit declaring `> **Isolation:** home` sets a temporary HOME in its tests, which a
worktree-isolated agent's command check refuses, so its brief says to build it in the main
checkout. `lane run` always runs its CLI in a worktree, so it now refuses such a unit before the
CLI starts, naming the main checkout, and the field is read exactly: `no home` is not `home`.

Every lane run case drives `sprint.py lane run` through `sprint.main` against `test_lane_run`'s
throwaway repository, under its confined PATH of fake CLIs; no real harness CLI is ever called.
The shape list reads each value through `lane_home_isolated` itself, the reader `lane run` uses.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_run as base  # noqa: E402

UNIT, sprint, lanes = base.UNIT, base.sprint, base.lanes


class HomeIsolationLaneRunTests(base._LaneCase):

    def _isolation(self, value: str) -> None:
        """Declare `value` as the unit's Isolation, committed, so a worktree carries it."""
        path = self.root / f"sdlc-studio/stories/{UNIT}-lane.md"
        text = path.read_text(encoding="utf-8").replace(
            "> **Epic:** EP0001\n", f"> **Epic:** EP0001\n> **Isolation:** {value}\n")
        path.write_text(text, encoding="utf-8")
        base.gitutil.git(["commit", "-q", "-am", f"chore: isolation {value}"], self.root)

    def test_a_home_isolated_unit_is_refused_before_the_cli_runs(self) -> None:
        """MUTANT: no refusal, so the CLI runs in a worktree the unit's tests cannot run in."""
        self._isolation("home")
        self._open_run()
        rc, out = self._run("claude")
        self.assertEqual(2, rc, out)
        self.assertIn("Isolation: home", out)
        self.assertIn("main checkout", out)
        self.assertFalse((self.log / "claude.json").exists(), "the CLI was run")
        self.assertEqual([], self._records(), "a lane record was written")
        self.assertFalse((self.root / lanes.RUN_WORKTREES).exists(), "a worktree was created")
        rs = base._rs()
        self.assertEqual([], rs.lanes_in_flight(self.root), "a lane was left in flight")

    def test_no_home_is_not_home(self) -> None:
        """MUTANT: the old word search, which reads `no home` as home and refuses the run."""
        self._isolation("no home")
        rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        self.assertEqual(1, len(self._records()))
        self.assertNotEqual(self.root.resolve(),
                            Path(self._called("claude")["cwd"]).resolve())

    def test_a_value_opening_with_home_is_not_home(self) -> None:
        """MUTANT: the value's first word read, so `home only` refuses the run as home."""
        self._isolation("home only")
        rc, out = self._run("claude")
        self.assertEqual(0, rc, out)
        self.assertNotIn("main checkout", out)
        self.assertEqual(1, len(self._records()))
        self.assertNotEqual(self.root.resolve(),
                            Path(self._called("claude")["cwd"]).resolve())

    def test_the_field_is_read_exactly(self) -> None:
        """The value itself decides: `home` in any case or in backticks is home; a sentence
        that holds the word is not, wherever the word stands in it. MUTANTS: the first word
        read, so a value opening with `home` and saying more is home; the value compared with
        its case, its backticks or the spaces inside them."""
        for value, home in (("home", True), ("Home", True), ("`home`", True),
                            ("` home `", True), ("no home", False), ("not home", False),
                            ("homework", False), ("home only", False),
                            ("home (its tests set HOME)", False), ("home worktree", False),
                            ("home, then worktree", False), ("worktree", False), ("", False)):
            with self.subTest(value=value):
                text = f"# {UNIT}: x\n\n> **Isolation:** {value}\n"
                self.assertEqual(home, sprint.lane_home_isolated(text))
        self.assertFalse(sprint.lane_home_isolated(f"# {UNIT}: x\n"))


if __name__ == "__main__":
    unittest.main()
