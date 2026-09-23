"""US0868: a sprint goal is one memorable sentence, and its seat read advises rather than blocks.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

_AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")


def _bug(root: Path, num: int) -> None:
    """A groomed open bug: Points, a resolvable Affects path and one criterion."""
    src = root / "src" / f"bg{num:04d}.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("", encoding="utf-8")
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** src/bg{num:04d}.py\n> **Points:** 2\n{_AC}", encoding="utf-8")


def _seats(root: Path) -> None:
    d = root / "sdlc-studio" / "personas" / "seats"
    d.mkdir(parents=True, exist_ok=True)
    for role in ("product", "engineering"):
        (d / f"{role}.md").write_text(
            f"# Sam - {role} seat\n\n<!-- role: {role} -->\n\n## Lens\nx\n", encoding="utf-8")


def _run(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _plan(root: Path, goal: str) -> tuple[int, str, str]:
    return _run(root, "plan", "--bugs", "Open", "--no-fetch", "--write", "--sprint-goal", goal)


def _state(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


def _words(n: int) -> str:
    return " ".join(f"w{i}" for i in range(n))


class GoalLengthTests(unittest.TestCase):

    def test_a_goal_over_twenty_words_is_refused(self) -> None:
        """Mutant: drop the word-count check, so a 21-word goal opens a run."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, _out, err = _plan(root, _words(21))
            self.assertEqual(2, rc, err)
            self.assertIn("21 words", err)
            self.assertIn("limit is 20", err)
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists(),
                             "the refusal still opened a run")

    def test_a_twenty_word_goal_plans(self) -> None:
        """Mutant: `<` for `<=` in the limit, or a gate that refuses every goal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            goal = _words(20)
            rc, _out, err = _plan(root, goal)
            self.assertEqual(0, rc, err)
            self.assertEqual(goal, _state(root)["sprint_goal"])

    def test_a_spaced_hyphen_is_not_a_word(self) -> None:
        """Mutant: count every whitespace token, so a goal of 20 words with a spaced hyphen reads
        as 21 and is refused."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            goal = _words(10) + " - " + " ".join(f"x{i}" for i in range(10))
            rc, _out, err = _plan(root, goal)
            self.assertEqual(0, rc, err)
            self.assertEqual(goal, _state(root)["sprint_goal"])
        # the control: a 21st real word is still refused, and the count names it
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            rc, _out, err = _plan(root, goal + " y0")
            self.assertEqual(2, rc, err)
            self.assertIn("21 words", err)

    def test_an_open_run_with_a_long_goal_can_change_its_batch(self) -> None:
        """Mutant: the limit enforced wherever a recorded goal is read, not where it is authored."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for n in (1, 2, 3):
                _bug(root, n)
            rc, _out, err = _run(root, "plan", "--bugs", "Open", "--no-fetch", "--write",
                                 "--sprint-goal", "fix the bugs")
            self.assertEqual(0, rc, err)
            state = _state(root)
            state["sprint_goal"] = _words(40)          # a run recorded before the limit existed
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps(state), encoding="utf-8")
            rc, _out, err = _run(root, "batch", "drop", "BG0002", "--reason", "not needed")
            self.assertEqual(0, rc, err)
            rc, _out, err = _run(root, "batch", "add", "BG0002")
            self.assertEqual(0, rc, err)
            self.assertIn("BG0002", _state(root)["batch"])


class GoalSeatReadTests(unittest.TestCase):

    def test_an_objecting_seat_advises_and_does_not_refuse(self) -> None:
        """Mutant: restore the refusal on an objection, or drop the note from the plan output."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            goal = "every open bug is fixed"
            rc, _out, err = _run(root, "goal-review", "record", "--goal", goal, "--seat",
                                 "engineering|no|every bug Fixed|yes|the appetite is too small")
            self.assertEqual(0, rc, err)
            rc, out, err = _plan(root, goal)
            self.assertEqual(0, rc, err)
            self.assertTrue((root / "sdlc-studio" / ".local" / "run-state.json").exists())
            advice = [ln for ln in out.splitlines() if "advice" in ln.lower()]
            self.assertTrue(advice, out)
            self.assertIn("the appetite is too small", advice[0])
            self.assertIn("engineering", advice[0])

    def test_an_unread_goal_does_not_refuse_the_close(self) -> None:
        """The review's point 4, with US0876 in. Mutant: the close's checklist holds the
        `goal-seat-reviewed` row again, so a goal no seat read refuses the close.

        The row's window is `sprint plan`, so at the close it is past its window: named on the
        close's output as advice, like the seat read itself, and never a refusal."""
        import test_lean_close as lean  # noqa: PLC0415 - the close fixture, shared
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            rc, out, err = lean._close(root, real=("checklist",))
            self.assertEqual(0, rc, err)
            self.assertIn("goal-seat-reviewed", out + err)
            self.assertNotIn("goal-seat-reviewed",
                             " ".join(i["detail"] for i in lean._read(root)["close_known_issues"]))

    def test_a_missing_seat_read_is_recorded_as_not_read(self) -> None:
        """Mutant: record an unread goal as reviewed, or refuse the plan for want of a read."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1)
            _seats(root)
            rc, _out, err = _plan(root, "every open bug is fixed")
            self.assertEqual(0, rc, err)
            review = _state(root)["sprint_goal_review"]
            self.assertEqual("not read", review["status"])
            self.assertFalse(review["reviewed"])


if __name__ == "__main__":
    unittest.main()
