"""BG1698: a unit carried at the review cap and then approved by the reviewer who rejected it, in
the run that carried it, stayed dropped from that run's batch, so the close, the retro and the
report never credited a unit delivered in the run. `critic.py record` now returns it to the
carrying run's batch when it writes the discharging APPROVE, the add's reason naming the carry
bug and any ruling, and says the carry bug is still Open and how it is closed. An APPROVE in a
later run that already holds the unit, or with no open run, changes no batch.

Each case records through `critic.py record`'s entry point in a throwaway workspace, its runs
opened and closed through `run_state`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
from lib import run_state  # noqa: E402

UNIT, OTHER = "US0101", "US0102"
REVIEWER = "rev-a"
REJOINS = "rejoins the carrying run's batch"


def _workspace(root: Path) -> None:
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    for uid in (UNIT, OTHER):
        (stories / f"{uid}-unit.md").write_text(
            f"# {uid}: unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 2\n"
            f"> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n"
            f"- [ ] **AC1** the unit works\n  - **Verify:** shell true\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")


def _record(root: Path, verdict: str, *extra: str) -> str:
    issues = "[new] the unit drops a row" if verdict == "reject" else "none"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = critic.main(["record", "--unit", UNIT, "--verdict", verdict, "--reviewer", REVIEWER,
                          "--author", "builder", "--issues", issues, *extra,
                          "--root", str(root)])
    assert rc == 0, buf.getvalue()
    return buf.getvalue()


def _close(root: Path) -> None:
    """Close the open run and archive it, as a close does."""
    state = run_state.read(root)
    state["outcome"] = run_state.GOAL_REACHED
    run_state.write(root, state)
    run_state.archive(root, state)


class CarryDischargeRejoinsBatchTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _workspace(self.root)
        saved = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"
        self.addCleanup(lambda: os.environ.__setitem__(run_state.TRANSCRIPTS_ENV, saved)
                        if saved is not None else os.environ.pop(run_state.TRANSCRIPTS_ENV, None))

    def _carry(self) -> str:
        """Carry UNIT at the cap in an open run; the carry bug's id."""
        run_state.open_run(self.root, batch=[UNIT, OTHER], goal="g")
        _record(self.root, "reject")
        _record(self.root, "reject")
        bug = critic.carried_by(self.root, UNIT)
        self.assertTrue(bug, "premise: the second REJECT carried nothing")
        self.assertEqual([OTHER], run_state.read(self.root)["batch"], "premise: no drop")
        return bug

    def _rejoined(self, bug: str, *named: str) -> dict:
        state = run_state.read(self.root)
        self.assertIn(UNIT, state["batch"], "the discharged unit did not rejoin the batch")
        last = state["batch_changes"][-1]
        self.assertEqual(("add", UNIT), (last["action"], last["id"]))
        for name in (bug, *named):
            self.assertIn(name, last.get("reason", ""), f"the add's reason does not name {name}")
        return state

    def test_the_discharging_approve_returns_the_unit_to_the_batch(self) -> None:
        """AC1. Mutant: nothing in the record's path adds the unit back."""
        bug = self._carry()
        _record(self.root, "approve")
        self._rejoined(bug)

    def test_a_ruled_approve_returns_the_unit_to_the_batch(self) -> None:
        """AC2: a round a decision authorises past the cap discharges the carry too, and the
        add names the ruling. Mutant: the ruling left out of the add's reason."""
        bug = self._carry()
        (self.root / "sdlc-studio" / "decisions.md").write_text(
            "# Decisions\n\n| ID | Decision | Rationale | Status | Supersedes | Date |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            f"| D0001 | {UNIT} gets a third review round past the cap. | Specified. | accepted | "
            f"-- | 2026-11-24 |\n", encoding="utf-8")
        _record(self.root, "approve", "--ruling", "D0001")
        self.assertEqual("D0001", critic.read_round_rulings(self.root)[-1]["ruling"],
                         "premise: the round was not the ruled one")
        self._rejoined(bug, "D0001")

    def test_no_add_outside_the_carrying_run(self) -> None:
        """AC3, the guards. Mutants: an add on every APPROVE of a once-carried unit, writing a
        duplicate entry into a later run that holds it, or into the carrying run once the unit
        is added back by hand, or into a closed run's state, or a run state where none is open;
        a REJECT read as a discharge; a hand drop after the carry undone."""
        self._carry()
        _close(self.root)
        run_state.open_run(self.root, batch=[UNIT], goal="g2")
        before = run_state.read(self.root)
        _record(self.root, "approve")
        after = run_state.read(self.root)
        self.assertEqual(([UNIT], before["batch_changes"]),
                         (after["batch"], after["batch_changes"]))
        for unlinked in (False, True):
            with self.subTest(run_state_file=not unlinked), tempfile.TemporaryDirectory() as d:
                self.root = Path(d)
                _workspace(self.root)
                self._carry()
                _close(self.root)
                if unlinked:
                    run_state.path(self.root).unlink()
                before = run_state.read(self.root)
                out = _record(self.root, "approve")
                self.assertEqual(before, run_state.read(self.root), "a closed run was changed")
                self.assertNotIn(REJOINS, out)
                self.assertNotIn("WARNING", out)
        with tempfile.TemporaryDirectory() as d:
            self.root = Path(d)
            _workspace(self.root)
            self._carry()
            run_state.add_to_batch(self.root, UNIT, "re-added by hand")
            before = run_state.read(self.root)
            out = _record(self.root, "approve")
            self.assertEqual(before, run_state.read(self.root),
                             "a unit the carrying run already holds again was added twice")
            self.assertNotIn(REJOINS, out)
            self.assertNotIn("WARNING", out)
        with tempfile.TemporaryDirectory() as d:
            self.root = Path(d)
            _workspace(self.root)
            self._carry()
            run_state.add_to_batch(self.root, UNIT, "re-added by hand")
            run_state.drop_from_batch(self.root, UNIT, "held back by the operator")
            before = run_state.read(self.root)["batch_changes"]
            self.assertNotIn(REJOINS, _record(self.root, "approve"))
            self.assertEqual(before, run_state.read(self.root)["batch_changes"])

    def test_another_units_later_drop_does_not_hide_the_carry(self) -> None:
        """The carry is read from the unit's own latest drop, not the batch's: OTHER dropped by
        hand after UNIT's carry leaves UNIT's discharge to rejoin. Mutant: the drop's unit id
        unread, so OTHER's hand drop is taken for UNIT's latest and nothing rejoins."""
        bug = self._carry()
        run_state.drop_from_batch(self.root, OTHER, "held back by the operator")
        _record(self.root, "approve")
        self._rejoined(bug)

    def test_the_library_writer_prints_the_rejoin(self) -> None:
        """`record_verdict`, the writer other commands call, returns the unit too and prints the
        notice on stderr. Mutant: the notice dropped from its loop."""
        bug = self._carry()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            critic.record_verdict(self.root, UNIT, "approve", REVIEWER, "builder", "none")
        self._rejoined(bug)
        self.assertIn(f"{UNIT} {REJOINS}", err.getvalue())

    def test_the_output_and_the_review_reference_name_the_rejoin(self) -> None:
        """AC4. Mutants: the output saying only that the APPROVE was recorded; the carry bug,
        or the command that closes it, left out; the page naming no rejoin."""
        bug = self._carry()
        out = _record(self.root, "approve")
        self.assertIn(f"{UNIT} {REJOINS}", out)
        self.assertIn(f"{bug}, which holds the carried findings, is still Open", out)
        self.assertIn(f"transition.py set --id {bug} --status Fixed", out)
        page = " ".join((SKILL / "reference-review.md").read_text(encoding="utf-8").split())
        start = page.index("**carries the unit**")
        paragraph = page[start:page.index("A licence for the census", start)]
        self.assertIn(REJOINS, paragraph, "the carry and discharge paragraph names no rejoin")
        self.assertIn("still Open", paragraph)

    def test_a_rejoin_that_cannot_be_written_is_named_with_its_remedy(self) -> None:
        """The APPROVE row stands when the add fails, and the output names the command that adds
        the unit back by hand. Mutant: the failure escaping as a crash after the row."""
        bug = self._carry()
        with unittest.mock.patch.object(run_state, "add_to_batch",
                                        side_effect=run_state.RunStateError("locked")):
            out = _record(self.root, "approve")
        self.assertEqual("APPROVE", critic.read_verdicts(self.root)[-1]["verdict"])
        self.assertIn(f"sprint.py batch add {UNIT}", out)
        self.assertIn("locked", out)
        self.assertIn(bug, out)


if __name__ == "__main__":
    unittest.main()
