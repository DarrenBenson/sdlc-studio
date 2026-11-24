"""`goal-review brief --seat <role>` briefs one seat through its own review card.

A seat a card fills is named with the card it adopts, so two seats over one batch and goal read
different briefs; a seat no card fills is refused naming the seats that have one, and no brief is
printed; and the unframed brief ends by naming the review seats and the form that frames one.

Driven through `sprint.main`, the shipped entry point, in throwaway trees built on the goal-trace
fixture.

BG1658: the no-current-batch answer names a command that runs, a seat's brief opens with its
framing, and an unknown seat is refused before the stale-plan check, with no plan written.
"""
from __future__ import annotations

import contextlib
import io
import re
import shlex
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")
critic = loader.load_script("critic")
persona_resolve = loader.load_script("persona_resolve")

_GOAL = "every open bug is fixed"
_SEAT = ("<!-- role: {role} -->\n# {name} - {title} seat\n\n## Lens\n\n- {lens}\n\n"
         "## Pushes Back When\n\n- the goal is vague\n\n## Shadow\n\nReads too much in.\n")
_CARDS = (("qa", "Quinn Abara", "QA", "Can the goal be shown false?"),
          ("sre", "Sol Reyes", "SRE", "Who is paged when it breaks?"))
#: The roster the fixture's seats make: the shipped seats, then the project's declared roles.
_ROSTER = ["engineering", "qa", "product", "sre"]


def _fixture(root: Path) -> dict[str, Path]:
    """S1's plannable project (BG0001) with a qa and an sre seat card, keyed by role."""
    s1._project(root)
    sdir = root / "sdlc-studio" / "personas" / "seats"
    sdir.mkdir(parents=True)
    cards = {}
    for role, name, title, lens in _CARDS:
        card = sdir / f"{name.lower().replace(' ', '-')}.md"
        card.write_text(_SEAT.format(role=role, name=name, title=title, lens=lens),
                        encoding="utf-8")
        cards[role] = card
    return cards


def _brief(root: Path, *extra: str) -> tuple[int, str, str]:
    """`goal-review brief` over the fixture's worklist and the one goal, with `extra` flags."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main(["goal-review", "brief", "--goal", _GOAL, "--brief-worklist",
                          str(root / "worklist.txt"), *extra, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class GoalReviewSeatBriefTests(unittest.TestCase):

    def test_each_seat_is_briefed_through_its_own_card(self) -> None:
        """Mutants: the brief ignores --seat; it names the seat but not its card; every seat
        resolves to one card."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cards = _fixture(root)
            briefs = {}
            for role in ("qa", "sre"):
                rc, out, err = _brief(root, "--seat", role)
                self.assertEqual(rc, 0, err)
                briefs[role] = out
        for role, other in (("qa", "sre"), ("sre", "qa")):
            with self.subTest(role=role):
                self.assertIn(f"You are the {role} review seat.", briefs[role])
                self.assertIn(f"{cards[role]} (the review render)", briefs[role])
                self.assertNotIn(str(cards[other]), briefs[role])
                self.assertNotIn(f"the {other} review seat", briefs[role])
                # Framing a seat leaves the goal's brief under it: the goal and the batch.
                self.assertIn(f"Sprint Goal: {_GOAL}", briefs[role])
                self.assertRegex(briefs[role], r"(?m)^Batch: 1 unit\(s\), ")
        self.assertNotEqual(briefs["qa"], briefs["sre"])

    def test_an_unknown_seat_is_refused_naming_the_roster(self) -> None:
        """Mutant: an unresolvable seat falls back to the unframed brief with exit 0."""
        # The skill carries no security card, so neither home fills the seat.
        self.assertIsNone(persona_resolve.default_card("security"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            rc, out, err = _brief(root, "--seat", "security")
            # Positive control: a shipped seat with no project card is briefed on the shipped one.
            ok_rc, ok_out, ok_err = _brief(root, "--seat", "engineering")
        self.assertEqual(rc, 2, out)
        self.assertEqual(out, "")
        self.assertIn("'security'", err)
        roster = re.search(r"\(seats: ([^)]*)\)", err)
        self.assertIsNotNone(roster, err)
        self.assertEqual(roster.group(1).split(", "), _ROSTER)
        self.assertEqual(ok_rc, 0, ok_err)
        self.assertIn(f"{persona_resolve.default_card('engineering')} (the review render)",
                      ok_out)

    def test_the_unframed_brief_names_the_per_seat_form(self) -> None:
        """Mutant: the unframed brief carries no pointer to the per-seat form, so an orchestrator
        hands every seat the same text."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            rc, out, err = _brief(root)
            _rc, framed, _err = _brief(root, "--seat", "qa")
        self.assertEqual(rc, 0, err)
        last = out.rstrip("\n").splitlines()[-1]
        named = re.match(r"Review seats: (.*?) - ", last)
        self.assertIsNotNone(named, last)
        self.assertEqual(named.group(1).split(", "), _ROSTER)
        self.assertIn("`sprint.py goal-review brief --seat <role>`", last)
        self.assertNotIn("review seat.", out)
        # The framed brief is the one seat's, so it carries no pointer to the others.
        self.assertNotIn(last, framed)

    def test_the_review_brief_adopts_the_same_card(self) -> None:
        """Mutant: `critic.py brief` resolves a seat's card by a path of its own, so the unit
        review and the goal review frame one seat through two cards."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cards = _fixture(root)
            for role in ("qa", "sre", "engineering"):
                with self.subTest(role=role):
                    card = cards.get(role) or persona_resolve.default_card(role)
                    _rc, goal_brief, _err = _brief(root, "--seat", role)
                    unit_brief = critic.brief(root, "BG0001", role, "light")
                    for text in (goal_brief, unit_brief):
                        self.assertIn(f"You are the {role} review seat.", text)
                        self.assertIn(f"{card} (the review render)", text)
            with self.assertRaisesRegex(ValueError, r"\(seats: engineering, qa, product, sre\)"):
                critic.brief(root, "BG0001", "security", "light")

    def test_a_stale_plan_answer_frames_no_seat(self) -> None:
        """Mutant: the answer that there is no current batch is framed as a seat's brief."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            for argv in ((), ("--seat", "qa")):
                with self.subTest(argv=argv):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        rc = sprint.main(["goal-review", "brief", *argv, "--root", str(root)])
                    self.assertEqual(rc, 0, err.getvalue())
                    self.assertTrue(out.getvalue().startswith("NO CURRENT BATCH TO BRIEF: "),
                                    out.getvalue())
                    self.assertNotIn("review seat", out.getvalue())
                    self.assertNotIn("Review seats:", out.getvalue())

    def test_one_role_per_brief(self) -> None:
        """Mutants: a second --seat is dropped silently; a record spec is looked up as a role."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            for argv in (("--seat", "qa", "--seat", "sre"), ("--seat", "qa|yes|done|yes")):
                with self.subTest(argv=argv):
                    rc, out, err = _brief(root, *argv)
                    self.assertEqual(rc, 2, out)
                    self.assertEqual(out, "")
                    self.assertIn("one role per brief", err)

    @staticmethod
    def _bare(root: Path, *argv: str) -> tuple[int, str, str]:
        """`goal-review brief` with only `argv`: no worklist and no goal unless named."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["goal-review", "brief", *argv, "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()

    def test_the_stale_plan_answer_names_a_command_that_runs(self) -> None:
        """BG1658 AC1. The answer's command, run as written with the fixture's worklist in
        place of `<file>`, exits 0 with a brief. MUTANT: the answer naming `--worklist`, which
        argparse refuses as an unrecognised argument."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            rc, out, err = self._bare(root)
            self.assertEqual(0, rc, err)
            self.assertTrue(out.startswith("NO CURRENT BATCH TO BRIEF: "), out)
            named = re.search(r"`(sprint\.py )?(goal-review brief [^`]*)`", out)
            self.assertIsNotNone(named, out)
            argv = shlex.split(named.group(2).replace("<file>", str(root / "worklist.txt")))
            rc, brief, err = self._bare(root, *argv[2:])
        self.assertEqual(0, rc, err)
        self.assertNotIn("NO CURRENT BATCH", brief)
        self.assertRegex(brief, r"(?m)^Batch: 1 unit\(s\), ")

    def test_a_framed_brief_opens_with_its_seat(self) -> None:
        """BG1658 AC2. MUTANT: the seat framing appended after the body, not opening it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            rc, framed, err = _brief(root, "--seat", "qa")
            _rc, unframed, _err = _brief(root)
        self.assertEqual(0, rc, err)
        opening = "You are the qa review seat. Read and adopt the charter at"
        self.assertEqual(opening, framed.splitlines()[0])
        self.assertFalse(unframed.startswith("You are the"), unframed.splitlines()[0])

    def test_an_unknown_seat_with_no_plan_is_refused(self) -> None:
        """BG1658 AC3. No plan written and no worklist: a seat no card fills is refused naming
        the roster, nothing on stdout and no plan written; `--seat qa` there gets the
        no-current-batch answer. MUTANT: the card resolved after the stale-plan check."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            plan = root / "sdlc-studio" / ".local" / "sprint-plan.json"
            self.assertFalse(plan.exists())
            rc, out, err = self._bare(root, "--seat", "security")
            self.assertEqual(2, rc, out)
            self.assertEqual("", out)
            self.assertIn("'security'", err)
            self.assertIn("(seats: engineering, qa, product, sre)", err)
            self.assertFalse(plan.exists(), "the refused brief wrote a plan")
            rc, out, err = self._bare(root, "--seat", "qa")
            self.assertEqual(0, rc, err)
            self.assertTrue(out.startswith("NO CURRENT BATCH TO BRIEF: "), out)


if __name__ == "__main__":
    unittest.main()
