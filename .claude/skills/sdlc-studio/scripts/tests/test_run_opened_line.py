"""US0387: the run-opened confirmation line names the Sprint Goal and the `--goal` ladder rung
distinctly, so `rung=done` is never misread as the Sprint Goal failing to take."""
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


APPETITE = {"minutes": 240.0, "units": 8}


def _state(goal_rung="done", sprint_goal=None):
    return {"run_id": "RUN-01KABCD", "goal": goal_rung, "sprint_goal": sprint_goal}


class RunOpenedLine(unittest.TestCase):
    def test_names_sprint_goal_and_rung_distinctly(self) -> None:
        line = _load().run_opened_line(_state(sprint_goal="ship the widget"), APPETITE)
        self.assertIn("rung=done", line)               # the ladder rung, labelled
        self.assertIn("sprint-goal=", line)            # the Sprint Goal, distinctly labelled
        # neither field is the bare `goal=` that read as either
        self.assertNotIn("goal=done", line.replace("sprint-goal=", ""))

    def test_supplied_sprint_goal_shown_as_set(self) -> None:
        line = _load().run_opened_line(_state(sprint_goal="ship the widget"), APPETITE)
        self.assertIn("ship the widget", line)
        self.assertNotIn("sprint-goal=unset", line)

    def test_absent_sprint_goal_stated(self) -> None:
        line = _load().run_opened_line(_state(sprint_goal=None), APPETITE)
        self.assertIn("sprint-goal=unset", line)

    def test_the_two_cases_cannot_render_identically(self) -> None:
        """AC4. Set and unset must differ, so a regression cannot collapse them."""
        mod = _load()
        with_goal = mod.run_opened_line(_state(sprint_goal="ship it"), APPETITE)
        without = mod.run_opened_line(_state(sprint_goal=None), APPETITE)
        self.assertNotEqual(with_goal, without)


if __name__ == "__main__":
    unittest.main()
