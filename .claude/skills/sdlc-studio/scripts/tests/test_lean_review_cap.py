"""US0872: one reviewer, at most two rounds - a fixed unit clears and a non-converging unit is
carried as a known issue so the run keeps going.

Every test drives `critic.py record` through `critic.main`, the surface an agent invokes, in a
throwaway workspace. Nothing reads this repository's own config, ledgers or `.local` state.
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import transition  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

UNIT = "US0001"


def _workspace(d: str, max_rounds: int | None = None) -> Path:
    root = Path(d)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/unit.py\n\n"
        "## Acceptance Criteria\n\n- **AC1:** the unit behaves\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
    cfg = "review:\n  require_brief_provenance: false\n"
    if max_rounds is not None:
        cfg += f"  max_rounds: {max_rounds}\n"
    (root / "sdlc-studio" / ".config.yaml").write_text(cfg, encoding="utf-8")
    return root


def _record(root: Path, verdict: str, reviewer: str, issues: str = "") -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    argv = ["record", "--unit", UNIT, "--verdict", verdict, "--reviewer", reviewer,
            "--author", "builder", "--root", str(root)]
    if issues:
        argv += ["--issues", issues]
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _rows(root: Path) -> list[dict]:
    return [r for r in critic.read_verdicts(root) if sdlc_md.norm_id(r["unit"]) == UNIT]


class ReviewRoundTests(unittest.TestCase):
    def setUp(self) -> None:
        # The token meter is read when a run opens; point it at nothing so no test reads the
        # operator's real transcripts.
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def test_each_verdict_carries_its_round_and_is_kept(self) -> None:
        """AC1. MUTANTS: number rows per ledger rather than per unit; keep only the latest row
        per unit; count the rows of every unit in `review_rounds`. Each misreads the second
        unit's row or the count."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            self.assertEqual(critic.review_rounds(root, UNIT), 0)
            critic.record_verdict(root, "US0099", "APPROVE", "someone", "builder")
            rc, out, err = _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            self.assertEqual(rc, 0, err)
            self.assertIn("round 1", out)
            rc, out, err = _record(root, "APPROVE", "rev-a")
            self.assertEqual(rc, 0, err)
            self.assertIn("round 2", out)
            rows = _rows(root)
            self.assertEqual([(r["verdict"], r["round"]) for r in rows],
                             [("REJECT", 1), ("APPROVE", 2)])
            self.assertEqual(critic.review_rounds(root, UNIT), 2)
            self.assertEqual(critic.review_rounds(root, "US0099"), 1)

    def test_a_round_two_approve_clears_the_reject(self) -> None:
        """AC2. MUTANT: retire a REJECT only on a matching brief fingerprint (the old rule, under
        which a re-review's rejoinder brief never matches), so the unit keeps an unanswered
        REJECT and the Done gate refuses it."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            # the positive control: the gate names the REJECT before round 2
            self.assertIn(transition.UNANSWERED_REJECT,
                          transition._unanswered_delivery_reject(root, UNIT) or "")
            rc, _out, err = _record(root, "APPROVE", "rev-a")
            self.assertEqual(rc, 0, err)
            self.assertEqual(critic.repairs_for(root, UNIT), [], "premise: no repair record")
            self.assertEqual(critic.verdict_for(root, UNIT)["verdict"], "APPROVE")
            self.assertIsNone(transition._unanswered_delivery_reject(root, UNIT))
            try:
                transition.transition(root, UNIT, "Done", dry_run=True)
            except ValueError as exc:
                self.assertNotIn(transition.UNANSWERED_REJECT, str(exc))

    def test_round_two_from_another_reviewer_is_refused(self) -> None:
        """AC3. MUTANT: drop the same-reviewer check, so B's row is written as round 2."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            rc, _out, err = _record(root, "APPROVE", "rev-b")
            self.assertEqual(rc, 2)
            self.assertIn("rev-a", err)
            self.assertEqual(len(_rows(root)), 1, "the refused round wrote a row")
            # the control: the round-1 reviewer is accepted
            self.assertEqual(_record(root, "APPROVE", "rev-a")[0], 0)

    def test_a_round_two_reject_carries_the_unit_as_a_known_issue(self) -> None:
        """AC4. MUTANTS: skip the filing; skip the batch drop; exit non-zero on the carry. Each
        leaves no bug, the unit still in the batch, or a run that stops."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            rc, out, err = _record(root, "REJECT", "rev-a",
                                   "[new] the parser still drops the last row")
            self.assertEqual(rc, 0, err)
            bugs = list((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(len(bugs), 1, f"expected one filed bug: {bugs}")
            bug_id = sdlc_md.extract_record_id(bugs[0].stem)
            text = bugs[0].read_text(encoding="utf-8")
            self.assertIn("the parser still drops the last row", text)
            self.assertIn(UNIT, text)
            state = run_state.read(root)
            self.assertEqual(state["batch"], ["US0002"])
            drop = state["batch_changes"][-1]
            self.assertEqual((drop["action"], drop["id"], drop["reason"]),
                             ("drop", UNIT, f"carried at the review cap: {bug_id}"))
            self.assertIn(bug_id, out)

    def test_a_third_round_is_refused(self) -> None:
        """AC5. MUTANTS: default the cap to 3; compare with `>` rather than `>=`; ignore
        `review.max_rounds`. Each lets the third row through or refuses the configured one."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            _record(root, "APPROVE", "rev-a")
            rc, _out, err = _record(root, "APPROVE", "rev-a")
            self.assertEqual(rc, 2)
            self.assertIn("review.max_rounds", err)
            self.assertIn("cap of 2", err)
            self.assertEqual(len(_rows(root)), 2, "the refused third round wrote a row")
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d, max_rounds=3)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            self.assertEqual(_record(root, "APPROVE", "rev-a")[0], 0,
                             "a configured cap of 3 refused round 3")
            self.assertEqual(_record(root, "APPROVE", "rev-a")[0], 2)


def _run(module, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = module.main(argv)
    return rc, buf.getvalue()


def _status(root: Path) -> str:
    text = (root / "sdlc-studio" / "stories" / f"{UNIT}-a-unit.md").read_text(encoding="utf-8")
    return sdlc_md.extract_field(text, "Status") or ""


class _NoTranscripts(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env


class RoundRulesHoldForEveryWriterTests(_NoTranscripts):
    """The round rules and the cap carry live in `critic.record_verdict`, so `artifact.py close`
    and `transition.py set --verdict` are held to them exactly as `critic.py record` is."""

    def test_the_other_writers_refuse_a_round_two_from_another_reviewer(self) -> None:
        """MUTANT: enforce the round rules only in `critic.py record` (their old home), so the
        one-call closes write round 2 for a reviewer who did not reject. Nothing is written by
        a refused close: no row, no status change."""
        import artifact  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            story = root / "sdlc-studio" / "stories" / f"{UNIT}-a-unit.md"
            before = story.read_bytes()
            rc, out = _run(artifact, ["close", "--id", UNIT,
                                      "--verdict", "APPROVE", "--reviewer", "rev-b",
                                      "--author", "builder", "--root", str(root)])
            self.assertEqual(rc, 2, out)
            self.assertIn("rev-a", out)
            rc, out = _run(transition, ["set", "--id", UNIT, "--status", "In Progress",
                                        "--verdict", "APPROVE", "--reviewer", "rev-c",
                                        "--author", "builder", "--root", str(root)])
            self.assertNotEqual(rc, 0, out)
            self.assertIn("rev-a", out)
            self.assertEqual(len(_rows(root)), 1, "a refused close wrote a row")
            self.assertEqual(story.read_bytes(), before, "a refused close wrote the unit")

    def test_the_other_writers_refuse_a_round_past_the_cap(self) -> None:
        """MUTANT: as above - the cap held only by `critic.py record`."""
        import artifact  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            _record(root, "APPROVE", "rev-a")
            rc, out = _run(artifact, ["close", "--id", UNIT, "--verdict", "APPROVE",
                                      "--reviewer", "rev-a", "--author", "builder",
                                      "--root", str(root)])
            self.assertEqual(rc, 2, out)
            self.assertIn("cap of 2", out)
            self.assertEqual(len(_rows(root)), 2)

    def test_a_round_two_reject_through_transition_is_carried(self) -> None:
        """MUTANT: carry only from `critic.py record`, so a round-2 REJECT recorded by the
        one-call close leaves the unit in the batch with nothing filed."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            rc, out = _run(transition, ["set", "--id", UNIT, "--status", "In Progress",
                                        "--verdict", "REJECT", "--reviewer", "rev-a",
                                        "--author", "builder", "--root", str(root)])
            self.assertEqual(rc, 0, out)
            self.assertEqual(_status(root), "In Progress")
            bugs = list((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(len(bugs), 1, out)
            self.assertIn(UNIT, bugs[0].read_text(encoding="utf-8"))
            self.assertEqual(run_state.read(root)["batch"], ["US0002"])

    def test_a_failed_carry_says_the_reject_was_written(self) -> None:
        """MUTANT: let the carry's failure reach the batch runner as a refusal, which reports
        `0 unit(s) written` while the REJECT row is on the ledger. The filer refuses a bug it
        cannot size, so a unit with no Points cannot be carried."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            story = root / "sdlc-studio" / "stories" / f"{UNIT}-a-unit.md"
            story.write_text(story.read_text(encoding="utf-8").replace("> **Points:** 2\n", ""),
                             encoding="utf-8")
            run_state.open_run(root, batch=[UNIT], goal="g")
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            rc, out, err = _record(root, "REJECT", "rev-a", "[new] still drops it")
            self.assertEqual(rc, 1, out + err)
            self.assertEqual(len(_rows(root)), 2, "premise: the round-2 REJECT row is written")
            self.assertIn("1 unit(s) written", out)
            self.assertIn("WAS written", err)
            self.assertIn("carrying it at the review cap failed", err)
            self.assertEqual(run_state.read(root)["batch"], [UNIT], "premise: not carried")


class PerDeliveryRoundTests(_NoTranscripts):
    """Rounds are counted per DELIVERY, never over the unit's whole ledger history: in an open
    run holding the unit, only the rows written since the run first reviewed it; outside one,
    the rows since the APPROVE that closed the unit's previous delivery."""

    def test_a_carried_unit_is_reviewed_afresh_in_a_later_run(self) -> None:
        """MUTANT: count rounds over the whole ledger, so the carried unit's two rows hold it
        at the cap forever and the bug's advice to deliver it again in a later run cannot be
        followed. On the same day, as a real re-run would be, so a date cannot tell them apart."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
            _record(root, "REJECT", "rev-a", "[new] the parser drops a row")
            self.assertEqual(_record(root, "REJECT", "rev-a", "[new] still drops it")[0], 0)
            self.assertEqual(critic.review_rounds(root, UNIT), 2)
            run_state.update(root, outcome="goal-reached")
            run_state.open_run(root, batch=[UNIT], goal="g2")
            self.assertEqual(critic.review_rounds(root, UNIT), 0)
            rc, out, err = _record(root, "REJECT", "rev-b", "[new] a third finding")
            self.assertEqual(rc, 0, err)
            self.assertIn("round 1", out)
            self.assertEqual(critic.review_rounds(root, UNIT), 1)
            self.assertEqual(_record(root, "APPROVE", "rev-c")[0], 2, "round 2 is rev-b's")
            rc, out, err = _record(root, "APPROVE", "rev-b")
            self.assertEqual(rc, 0, err)
            self.assertIn("round 2", out)
            self.assertEqual(critic.review_rounds(root, UNIT), 2)
            self.assertEqual(len(_rows(root)), 4, "every row is kept")

    def test_outside_a_run_a_closed_delivery_is_not_counted(self) -> None:
        """MUTANT: as above. A history written before the round rules (two reviewers on one
        unit) holds a delivery an APPROVE closed; the REJECT after it is round 1 of the next,
        which its own reviewer may re-check and no other reviewer may answer."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d, max_rounds=9)      # the history predates the cap
            _record(root, "REJECT", "rev-a", "[new] a")
            _record(root, "APPROVE", "rev-a")
            _record(root, "REJECT", "rev-b", "[new] b")
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  require_brief_provenance: false\n", encoding="utf-8")
            self.assertEqual(len(_rows(root)), 3, "premise: the history was written")
            self.assertEqual(critic.review_rounds(root, UNIT), 1)
            self.assertEqual(_record(root, "APPROVE", "rev-a")[0], 2, "round 2 is rev-b's")
            rc, out, err = _record(root, "APPROVE", "rev-b")
            self.assertEqual(rc, 0, err)
            self.assertIn("round 2", out)
            self.assertEqual(critic.review_rounds(root, UNIT), 2)
            self.assertEqual(_record(root, "APPROVE", "rev-b")[0], 2, "a third round")

    def test_an_earlier_approve_does_not_answer_a_later_reject(self) -> None:
        """MUTANT: let an APPROVE anywhere in the unit's rows answer a REJECT (`rows` for
        `rows[i + 1:]`), so the reviewer's own earlier APPROVE retires the REJECT it later
        recorded and the Done gate passes a rejected unit. The REJECT must not be the latest
        row, or it stands whether answered or not: a later APPROVE by another seat, which does
        not answer it, follows - history written before the round rules, which refuse it now."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _record(root, "APPROVE", "rev-a")
            self.assertEqual(_record(root, "REJECT", "rev-a", "[new] found late")[0], 0)
            with mock.patch.object(critic, "round_refusal", lambda *a, **k: None):
                critic.record_verdict(root, UNIT, "APPROVE", "rev-b", "builder")
            self.assertEqual([r["reviewer"] for r in _rows(root)], ["rev-a", "rev-a", "rev-b"])
            self.assertEqual(critic.verdict_for(root, UNIT)["verdict"], "REJECT")
            self.assertIn(transition.UNANSWERED_REJECT,
                          transition._unanswered_delivery_reject(root, UNIT) or "")


if __name__ == "__main__":
    unittest.main()
