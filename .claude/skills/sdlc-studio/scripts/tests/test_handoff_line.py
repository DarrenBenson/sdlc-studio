"""US0386: the plan's handoff line states nothing carried over for a zero-remaining handoff, and
is unchanged for a non-zero one. The boundary between the two is pinned two-sided so a future
change cannot make the zero case reappear as a false action item or suppress the non-zero one."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


def _pending(remaining: int):
    return {"id": "HO-0025", "worklist": "sdlc-studio/.local/wl.txt",
            "plannable": remaining, "remaining": remaining, "outcome": "goal-reached"}


class HandoffLine(unittest.TestCase):
    def test_zero_remaining_states_nothing_carried_over(self) -> None:
        line = _load().handoff_line(_pending(0))
        self.assertIn("nothing carried over", line)
        self.assertNotIn("--worklist", line)          # no false action item
        self.assertNotIn("remaining item", line)

    def test_nonzero_remaining_names_count_and_worklist(self) -> None:
        line = _load().handoff_line(_pending(3))
        self.assertIn("3 remaining item(s)", line)     # the count, verbatim
        self.assertIn("--worklist sdlc-studio/.local/wl.txt", line)
        self.assertNotIn("nothing carried over", line)

    def test_boundary_pinned_both_sides(self) -> None:
        """One test holds both sides: zero suppresses the worklist, one keeps it - so a change
        cannot silently flip either without failing here."""
        mod = _load()
        zero, one = mod.handoff_line(_pending(0)), mod.handoff_line(_pending(1))
        self.assertNotIn("--worklist", zero)
        self.assertIn("--worklist", one)
        self.assertIn("nothing carried over", zero)
        self.assertNotIn("nothing carried over", one)
        self.assertIn("1 remaining item(s)", one)


if __name__ == "__main__":
    unittest.main()
