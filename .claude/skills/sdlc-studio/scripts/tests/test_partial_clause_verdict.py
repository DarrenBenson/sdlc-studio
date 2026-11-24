"""BG1673: a seat's `partial` answer reads as partial, not as no answer at all.

`verdict_polarity` knew only yes and no words, so `partial - <reason>` read `unclear`, and
`_recorded_clause_verdicts` dropped it: a clause three seats answered partial reached the close's
goal panel as UNANSWERED. It now reads `partial`, the clause reaches the panel as `partial`, and
a whole-goal `partial` stays what it was to the plan, a hedge and not an objection. These drive
the readers over a goal-review round written as `goal-review record` writes it.

MUTANTS, each failed here: partial words left out of the vocabulary (AC1-AC3); partial mapped to
`missed` or `achieved` on the panel (AC2, AC3); partial mapped to `no`, so a hedge is an
objection (AC4); an unclear answer passed to the panel (AC2).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

A = "persona cards meet an enforced standard"
B = "persona docs match the code"
C = "every seat has a memory file"
D = "the roster is printed at plan"
SEATS = ("engineering", "product", "qa")


def _round(root: Path, seats: list[dict], goal: str) -> None:
    """One goal-review round over `goal`, as `goal-review record` writes it."""
    path = root / "sdlc-studio" / ".local" / "goal-review.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rounds": [{"goal": goal, "seats": seats}]}), encoding="utf-8")


def _seat(role: str, achievable: str = "yes", clauses: dict | None = None) -> dict:
    out = {"seat": role, "achievable": achievable, "done_means": "done", "one_increment": "yes"}
    if clauses is not None:
        out["clauses"] = clauses
    return out


class PartialClauseVerdictTests(unittest.TestCase):

    def test_partial_reads_as_its_own_polarity(self) -> None:
        """AC1, beside the yes, no and unclear answers it must not move."""
        for answer, polarity in (("partial - two cards lack a lens", "partial"),
                                 ("Partly", "partial"), ("partially, see notes", "partial"),
                                 ("yes", "yes"), ("no - not at the stated appetite", "no"),
                                 ("maybe later", "unclear"), ("partials", "unclear")):
            with self.subTest(answer=answer):
                self.assertEqual(polarity, sprint.verdict_polarity(answer))

    def test_a_clause_answered_partial_reaches_the_panel_as_partial(self) -> None:
        """AC2. Three seats answer A partial, B yes and C no; one answers D maybe."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            answers = {A: "partial - two cards lack a lens", B: "yes", C: "no"}
            _round(root, [_seat(r, clauses=dict(answers, **({D: "maybe"} if r == "qa" else {})))
                          for r in SEATS], f"{A}; {B}; {C}; {D}")
            got = sprint._recorded_clause_verdicts(root, [A, B, C, D])
        self.assertEqual({A: dict.fromkeys(SEATS, "partial"), B: dict.fromkeys(SEATS, "achieved"),
                          C: dict.fromkeys(SEATS, "missed")}, got)

    def test_the_close_reports_a_partial_clause_not_unanswered(self) -> None:
        """AC3. A run whose goal is clause A, every seat answering it partial."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _round(root, [_seat(r, clauses={A: "partial - two cards lack a lens"})
                          for r in SEATS], A)
            record: dict = {}
            lines = sprint.close_goal_judgement(
                root, {"sprint_goal": A, "batch": [], "author": "builder"}, record=record)
        text = "\n".join(lines)
        self.assertIn(f"    partial: {A}", lines, text)
        self.assertNotIn("UNANSWERED", text)
        self.assertIn(f"partial: {A}", record["panel"])

    def test_a_whole_goal_partial_is_not_an_objection(self) -> None:
        """AC4. The achievable answer `partial - the appetite is tight` is a hedge; the control,
        `no - the appetite is too small`, is an objection."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _round(root, [_seat("qa", "partial - the appetite is tight"),
                          _seat("product", "no - the appetite is too small")], A)
            status = sprint.goal_review_status(root, A)
        self.assertEqual(["product"], [o["seat"] for o in status["objections"]])


if __name__ == "__main__":
    unittest.main()
