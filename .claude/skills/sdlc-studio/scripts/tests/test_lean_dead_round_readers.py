"""BG0783: the run-state review-round ledger lost its only writer when US0918 retired
`critic.py sprint-review`, so every reader of it read an empty list. The readers are deleted rather
than re-pointed at the per-unit verdict ledger, and the goal verdict stops refusing a note against
a count that was always 0.

The goal verdict is driven through `sprint.py goal-verdict`, the surface an agent invokes, in a
throwaway workspace. The census test reads this repository's production scripts and writes nothing.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import sprint  # noqa: E402
from lib import run_state  # noqa: E402

#: The ledger, its writer and every reader of it that US0918 left behind.
DEAD_NAMES = ("REVIEW_ROUNDS", "CEILING_OVERRIDES", "record_review_round", "review_round_count",
              "review_round_guard", "next_round_offer", "round_cost_report", "classify_finding",
              "escalation_for")


def _production_modules() -> list[Path]:
    return sorted(p for p in SCRIPTS.rglob("*.py")
                  if "tests" not in p.relative_to(SCRIPTS).parts
                  and "__pycache__" not in p.parts)


class DeadRoundReaderTests(unittest.TestCase):
    def test_a_goal_verdict_note_naming_rounds_is_recorded(self) -> None:
        """AC1. MUTANT: keep `record_goal_verdict` checking the note against
        `len(review_rounds)` - the note is refused against a ledger that is always empty. MUTANT:
        keep stamping `rounds` - every verdict carries a count read from a dead ledger."""
        note = "two rounds of review converged"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            run_state.open_run(root, batch=["US0001"], goal="ship the widget")
            run_state.update(root, sprint_goal="ship the widget")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sprint.main(["goal-verdict", "--verdict", "achieved", "--note", note,
                                  "--root", str(root)])
            self.assertEqual(rc, 0, err.getvalue())
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual(state["sprint_goal_verdict"], {"verdict": "achieved", "note": note})

    def test_no_run_state_round_reader_survives(self) -> None:
        """AC2. MUTANT: delete the tests of a reader and leave the reader - US0918 left eight."""
        modules = _production_modules()
        self.assertIn(SCRIPTS / "critic.py", modules, "the census read no production script")
        self.assertIn(SCRIPTS / "lib" / "run_state.py", modules)
        found = []
        for path in modules:
            text = path.read_text(encoding="utf-8")
            for name in DEAD_NAMES:
                for m in re.finditer(rf"\b{name}\b", text):
                    line = text.count("\n", 0, m.start()) + 1
                    found.append(f"{path.relative_to(SCRIPTS)}:{line}: {name}")
        self.assertEqual(found, [], "a run-state review-round reader survives")


if __name__ == "__main__":
    unittest.main()
