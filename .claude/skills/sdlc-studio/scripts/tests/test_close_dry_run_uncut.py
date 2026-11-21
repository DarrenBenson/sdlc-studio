"""BG1051: the close's dry run prints every unit of a long refusal whole.

The known-issues refusal packs every unit the run cannot end over into one line, each with its
status and reason. The dry run's report cut every body and remedy line at 160 characters, so the
cut landed inside the second unit and the operator could not learn from the preview what held
it. Driven through `sprint.main(["close", "--dry-run"])` on the lean close fixture, with the real
checklist step (its compulsory items answered) and the real unanswered-unit hold over three
unfinished stories; every other step is stubbed green and the pre-flight is clean.

MUTANTS, each of which the test fails on: (1) the body line is cut at 160 characters again;
(2) any continuation line of a step's detail is cut; (3) the remedy is cut.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture and its green chain, shared

UNITS = ("US0101", "US0102", "US0103")
#: The checklist with every compulsory item answered, so only the unanswered-unit hold refuses.
ANSWERED = {"items": [{"id": "retro-filed", "title": "the retro is filed", "value": "yes",
                       "detail": ""}],
            "outstanding": [], "expired": [], "stop_ship": [], "pending_in_close": []}


def _stories(root: Path) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    for uid in UNITS:
        (root / "src" / f"{uid.lower()}.py").write_text("x = 1\n", encoding="utf-8")
        (d / f"{uid}-widget.md").write_text(
            f"# {uid}: widget\n\n> **Status:** In Progress\n> **Points:** 3\n"
            f"> **Affects:** src/{uid.lower()}.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
            "- **Verify:** shell true\n", encoding="utf-8")


class DryRunUncutTests(unittest.TestCase):

    def test_every_unit_of_a_long_refusal_is_printed_whole(self) -> None:
        mod = lean._live("sprint")
        report = lean._live("sprint_report")
        pre = {"blockers": [], "ready": True, "gate_ran": True}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root, batch=list(UNITS))
            _stories(root)
            state = mod.run_state.read(root)
            held = mod.unanswered_units(root, state, "RETRO0001")["unanswered"]
            self.assertEqual(list(UNITS), [h["unit"] for h in held],
                             "the fixture must hold all three units, or nothing long is printed")
            line = mod.unanswered_line(held)
            self.assertGreater(len(line), 160, "the refusal must be longer than the old cut")
            out = io.StringIO()
            with lean._green_steps(mod, real=("checklist",)), \
                    unittest.mock.patch.object(mod, "close_preflight", lambda *a, **k: pre), \
                    unittest.mock.patch.object(report, "checklist", lambda *a, **k: ANSWERED), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = mod.main(["close", "--retro", "RETRO0001", "--dry-run", "--root", str(root)])
        text = out.getvalue()
        self.assertEqual(1, rc, text)
        self.assertIn(line, text, f"the known-issues line was cut:\n{text}")
        for h in held:
            self.assertIn(f"{h['unit']} ({h['status']}) - {h['why']} - findings NONE filed",
                          text, f"{h['unit']}'s id, status or reason was not printed whole")
        ways = mod.unanswered_ways_out(held, "RETRO0001", state.get("run_id"))
        for remedy in ways.splitlines():
            self.assertIn(remedy.strip(), text, "a remedy line was cut")

    def test_no_line_of_a_step_is_cut(self) -> None:
        """Every line a step says is printed whole: the first line of its detail, each line after
        it, the first line of its remedy and each line after that."""
        mod = lean._live("sprint")
        pre = {"blockers": [], "ready": True, "gate_ran": True}
        said = {name: f"{name} " + "x" * 170 + " END" for name in
                ("first", "second", "remedy", "remedy-more")}
        step = (False, f"{said['first']}\n{said['second']}",
                f"{said['remedy']}\n{said['remedy-more']}")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            out = io.StringIO()
            with lean._green_steps(mod), \
                    unittest.mock.patch.object(mod, "_close_reconcile", lambda *a, **k: step), \
                    unittest.mock.patch.object(mod, "close_preflight", lambda *a, **k: pre), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = mod.main(["close", "--retro", "RETRO0001", "--dry-run", "--root", str(root)])
        text = out.getvalue()
        self.assertEqual(1, rc, text)
        for name, line in said.items():
            self.assertIn(line, text, f"the {name} line was cut:\n{text}")


if __name__ == "__main__":
    unittest.main()
