"""BG1108: a carried unit's redelivery brief diffs from the commit its capping REJECT judged.

`critic.py brief` scoped a unit's diff to the base of the run that holds it. A unit carried at
the review cap whose repair landed before the next run opened had an empty diff there: the
next run's base is after the repair, so every finding on it read as pre-existing and the
redelivery review could not block. The carry now records the commit the capping REJECT judged
(the commit its brief was cut at, else the commit at the carry) on the batch drop, and the
brief of the carry bug, or of the carried unit delivered again, diffs from it.

The carry is made for real: two REJECTs recorded at the cap with `critic.py record` in an open
run, each against a brief `critic.py brief` cut, before a repair lands and a later run opens.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo
import loader  # noqa: E402

critic = loader.load_script("critic")
run_state = sys.modules["lib.run_state"]
UNIT = "US0001"
REJECT = "VERDICT: REJECT\nISSUES: [new] a is wrong\nBLOCKING: [new] a is wrong\n"
REVIEWER, AUTHOR = "qa-seat-r1", "builder-agent"


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _commit(root: Path, message: str, body: str) -> str:
    _write(root, "src/a.py", body)
    gitutil.git(["commit", "-q", "--no-verify", "-am", message], root)
    return gitutil.git(["rev-parse", "--short=12", "HEAD"], root, text=True).stdout.strip()


def _cli(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class CarriedReviewBaseTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = root = Path(tmp.name)
        env = unittest.mock.patch.dict(os.environ, {
            **gitutil.git_env(), run_state.TRANSCRIPTS_ENV: str(root / "no-transcripts")})
        env.start()
        self.addCleanup(env.stop)
        _write(root, "src/a.py", "a = 1\n")
        _write(root, ".gitignore", "sdlc-studio/.local/\n")
        _write(root, f"sdlc-studio/stories/{UNIT}-the-widget.md",
               f"# {UNIT}: the widget\n\n> **Status:** Review\n> **Points:** 2\n"
               f"> **Epic:** EP0001\n> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
               f"### AC1: works\n- **Verify:** shell true\n")
        gitutil.git(["init", "-q"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "--no-verify", "-m", "chore: the fixture"], root)

    def _round(self, n: int, elsewhere: bool = False) -> str:
        """A brief of the unit cut now, and a REJECT recorded against it; the brief's commit.
        With `elsewhere`, another unit's commit to another file lands between the two, so the
        commit at the record is not the one the brief was cut at."""
        rc, out, err = _cli(self.root, "brief", "--unit", UNIT, "--seat", "qa",
                            "--tier", "light")
        self.assertEqual(0, rc, err)
        fp = critic._noted_row(self.root, UNIT)["fp"]
        if elsewhere:
            _write(self.root, "src/z.py", "z = 1\n")
            gitutil.git(["add", "-A"], self.root)
            gitutil.git(["commit", "-q", "--no-verify", "-m", "feat(US0002): z"], self.root)
        path = _write(self.root, f"verdicts/{UNIT}-{n}.txt", REJECT)
        rc, out, err = _cli(self.root, "record", "--unit", UNIT, "--from-verdict", str(path),
                            "--reviewer", REVIEWER, "--author", AUTHOR, "--brief", fp,
                            "--tier", "light")
        self.assertEqual(0, rc, out + err)
        return critic._noted_row(self.root, UNIT, fp)["commit"]

    def _carry(self) -> tuple[str, str, str]:
        """The unit built, rejected, repaired, rejected at the cap and so carried, then repaired
        again on main before a later run opens with the carry bug in its batch. Returns the
        commit the capping REJECT judged, the late repair's commit and the carry bug."""
        run_state.open_run(self.root, batch=[UNIT], goal="g")
        _commit(self.root, f"feat({UNIT}): a", "a = 2\n")
        self._round(1)
        _commit(self.root, f"fix({UNIT}): round one", "a = 2\nb = 1\n")
        judged = self._round(2, elsewhere=True)
        self.assertNotEqual(judged, critic._head_commit(self.root),
                            "premise: the carry's commit is not the one its brief was cut at")
        bug = critic.carried_by(self.root, UNIT)
        self.assertIsNotNone(bug, "premise: the round-2 REJECT carried the unit")
        repair = _commit(self.root, f"fix({UNIT}): the carried findings",
                         "a = 2\nb = 1\nrepaired = True\n")
        run_state.update(self.root, outcome="partial")
        run_state.open_run(self.root, batch=[bug], goal="g2")
        self.assertEqual(repair, run_state.base_ref(self.root)[:12],
                         "premise: the later run's base is after the repair")
        return judged, repair, bug

    def test_a_carried_units_brief_diffs_from_the_commit_its_capping_reject_judged(self) -> None:
        """AC1. Mutants: the brief diffing from the later run's base, so the repair's diff is
        empty; the carry recording no commit; the commit at the carry taken over the brief's;
        the carry bug's brief not reading the carried unit's record; the carried unit's own
        redelivery brief not reading it."""
        judged, repair, bug = self._carry()
        drop = [c for c in run_state.archived(self.root)[-1]["batch_changes"]
                if c.get("action") == "drop"][-1]
        self.assertEqual(judged, drop["review_base"], "the carry did not record the commit")
        for uid in (bug, UNIT):
            if uid == UNIT:
                run_state.add_to_batch(self.root, UNIT, "delivered again")
            text = critic.brief(self.root, uid, "qa", "light")
            self.assertIn(f"--- UNIT DIFF (git diff {judged} HEAD -- src/a.py) ---", text, uid)
            self.assertIn("+repaired = True", text, f"{uid}: the repair is not in the diff")
            self.assertNotIn("+b = 1", text, f"{uid}: the diff reaches past the judged commit")
            self.assertIn(f"Diff against the commit {UNIT}'s capping REJECT judged "
                          f"(it was carried at the review cap): git diff {judged} -- src/a.py",
                          text, uid)
        # an open run's record that cannot be read leaves the archived carry to answer
        (self.root / run_state.REL).write_text("{not json", encoding="utf-8")
        self.assertEqual((judged, UNIT), critic.carried_review_base(self.root, bug))

    def test_a_carry_with_no_noted_brief_records_the_commit_at_the_carry(self) -> None:
        """The fallback. Mutant: no commit recorded when the REJECT's brief left no note (the
        notes are runtime files a clean checkout lacks); a unit no drop names read as carried."""
        root = self.root
        run_state.open_run(root, batch=[UNIT], goal="g")
        _commit(root, f"feat({UNIT}): a", "a = 2\n")
        self._round(1)
        head = _commit(root, f"fix({UNIT}): round one", "a = 2\nb = 1\n")
        (root / critic.BRIEF_NOTES_REL).unlink()
        self._round_without_note()
        drop = [c for c in run_state.read(root)["batch_changes"] if c.get("action") == "drop"]
        self.assertEqual(head, drop[-1]["review_base"])
        self.assertEqual((head, UNIT), critic.carried_review_base(root, UNIT))
        self.assertEqual(("", ""), critic.carried_review_base(root, "US0009"))

    def test_the_capping_reject_reads_its_own_briefs_commit_not_the_units_latest_note(self):
        """A round of a high-risk unit briefs two seats, and they need not share a commit: the
        qa seat is briefed, the unit's file moves, and a second seat is briefed after it. The
        qa REJECT recorded at the cap judged the qa brief's commit. Mutant: the unit's latest
        note read whatever brief cut it, so the second seat's later commit is recorded and the
        redelivery's diff hides the commit between them."""
        root = self.root
        run_state.open_run(root, batch=[UNIT], goal="g")
        _commit(root, f"feat({UNIT}): a", "a = 2\n")
        self._round(1)
        rc, _out, err = _cli(root, "brief", "--unit", UNIT, "--seat", "qa", "--tier", "light")
        self.assertEqual(0, rc, err)
        qa = critic._noted_row(root, UNIT)
        _commit(root, f"fix({UNIT}): between the seats", "a = 2\nbetween = 1\n")
        rc, _out, err = _cli(root, "brief", "--unit", UNIT, "--seat", "product",
                             "--tier", "light")
        self.assertEqual(0, rc, err)
        self.assertNotEqual(qa["commit"], critic._noted_row(root, UNIT)["commit"],
                            "premise: the second seat's brief was cut at a later commit")
        path = _write(root, f"verdicts/{UNIT}-2.txt", REJECT)
        rc, out, err = _cli(root, "record", "--unit", UNIT, "--from-verdict", str(path),
                            "--reviewer", REVIEWER, "--author", AUTHOR, "--brief", qa["fp"],
                            "--tier", "light")
        self.assertEqual(0, rc, out + err)
        self.assertEqual((qa["commit"], UNIT), critic.carried_review_base(root, UNIT))

    def test_a_carried_unit_is_found_by_its_id_in_lower_case(self) -> None:
        """The briefed id is folded before it is compared, as every other id read here is, so
        a lower-case id briefed through the shipped CLI finds the carry. Mutant: the id compared
        as typed, so `bg0001` reads as never carried and its brief diffs from the run's base,
        the empty diff this repair exists to replace."""
        judged, _repair, bug = self._carry()
        for typed in (bug.lower(), UNIT.lower()):
            self.assertEqual((judged, UNIT), critic.carried_review_base(self.root, typed), typed)
        rc, out, err = _cli(self.root, "brief", "--unit", bug.lower(), "--seat", "qa",
                            "--tier", "light")
        self.assertEqual(0, rc, err)
        self.assertIn(f"--- UNIT DIFF (git diff {judged} HEAD -- src/a.py) ---", out)
        self.assertNotIn("Diff against the run's base commit", out)

    def test_a_note_that_records_no_commit_carries_at_the_commit_checked_out(self) -> None:
        """The second fallback the docstring and the changelog name: a note that names the
        REJECT's fingerprint but records no commit, as every note cut before notes recorded one
        does, so a run open across the upgrade carries at the commit checked out at the carry.
        Mutant: such a note read as recording an empty commit, so the drop records none."""
        root = self.root
        run_state.open_run(root, batch=[UNIT], goal="g")
        _commit(root, f"feat({UNIT}): a", "a = 2\n")
        self._round(1)
        rc, _out, err = _cli(root, "brief", "--unit", UNIT, "--seat", "qa", "--tier", "light")
        self.assertEqual(0, rc, err)
        notes = root / critic.BRIEF_NOTES_REL
        rows = [json.loads(line) for line in notes.read_text(encoding="utf-8").splitlines()]
        notes.write_text("".join(json.dumps({k: v for k, v in r.items() if k != "commit"}) + "\n"
                                 for r in rows), encoding="utf-8")
        fp = rows[-1]["fp"]
        self.assertNotIn("commit", critic._noted_row(root, UNIT, fp), "premise: no commit noted")
        head = _commit(root, f"fix({UNIT}): after the brief", "a = 2\nlate = 1\n")
        path = _write(root, f"verdicts/{UNIT}-2.txt", REJECT)
        rc, out, err = _cli(root, "record", "--unit", UNIT, "--from-verdict", str(path),
                            "--reviewer", REVIEWER, "--author", AUTHOR, "--brief", fp,
                            "--tier", "light")
        self.assertEqual(0, rc, out + err)
        self.assertEqual((head, UNIT), critic.carried_review_base(root, UNIT))

    def test_the_latest_carry_wins_and_a_plain_drop_records_none(self) -> None:
        """Mutants: the first carry's commit kept over a later one's; a later drop recording no
        commit (a hand drop, or one carried by no REJECT) read as erasing the carry's."""
        root = self.root
        reason = f"{critic.CARRIED_REASON}: BG0001"
        run_state.open_run(root, batch=[UNIT], goal="g")
        run_state.drop_from_batch(root, UNIT, reason, review_base="aaa111")
        run_state.update(root, outcome="partial")
        run_state.open_run(root, batch=[UNIT], goal="g2")
        run_state.drop_from_batch(root, UNIT, reason, review_base="bbb222")
        run_state.add_to_batch(root, UNIT, "back again")
        run_state.drop_from_batch(root, UNIT, "pulled by hand")
        self.assertEqual(("bbb222", UNIT), critic.carried_review_base(root, UNIT))

    def _round_without_note(self) -> None:
        path = _write(self.root, f"verdicts/{UNIT}-2.txt", REJECT)
        rc, out, err = _cli(self.root, "record", "--unit", UNIT, "--from-verdict", str(path),
                            "--reviewer", REVIEWER, "--author", AUTHOR, "--brief", "0" * 12,
                            "--tier", "light")
        self.assertEqual(0, rc, out + err)


if __name__ == "__main__":
    unittest.main()
