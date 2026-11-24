"""BG0820: a unit whose only owed step is the signature awaits it at any pre-terminal status.

The close judged "awaiting the signature" only for a unit at Review, while `sprint sign` seals any
batch unit that meets the review bar (`seal_bar_unmet`). A unit the loop left at Ready or In
Progress with an independent delivery APPROVE was therefore handed over as an unanswered known
issue by the close and then moved to Done by the signature: two bars for one unit. The fix judges
the case by the seal's own bar at every pre-terminal status, and the loop's Build step names the
move to Review.

AC1 drives the close's reader in a throwaway workspace. AC2 reads the shipped loop doc.

US1290 AC4 runs `status.py` over tracked run records awaiting their signatures beside an open run.
BG1583 AC4 reads `status.awaiting_signature_lines` over a tracked record that cannot be parsed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/status.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import sprint  # noqa: E402

RUN = "RUN-LEAN0820"


def _unit(root: Path, uid: str, status: str, *, approved: bool) -> None:
    """A story (or, for a `BG` id, a bug; for a `CR` id, a change request) at `status` with one
    green criterion and, when `approved`, an independent delivery APPROVE."""
    folder = {"BG": "bugs", "CR": "change-requests"}.get(uid[:2], "stories")
    d = root / "sdlc-studio" / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: unit\n\n> **Status:** {status}\n> **Points:** 2\n> **Epic:** EP0001\n\n"
        "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
        encoding="utf-8")
    rp = root / "sdlc-studio" / ".local" / "verify-report.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    report = json.loads(rp.read_text(encoding="utf-8")) if rp.is_file() else {"stories": {}}
    report["stories"][f"{uid}-x"] = {"failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                                     "verified_at": "2099-01-01T00:00:00Z"}
    rp.write_text(json.dumps(report), encoding="utf-8")
    if approved:
        critic.record_verdict(root, uid, "APPROVE", reviewer="qa-seat", author="builder",
                              issues="probed the edges; none blocking")


def _state(root: Path, batch: list[str]) -> dict:
    state = {"schema": 1, "run_id": RUN, "started_at": "2026-09-28T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": batch,
             "handoff": None, "report": "RPT0001", "sprint_goal": "a unit awaits the signature",
             "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}}
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")
    return state


class AwaitingSignatureStatusTests(unittest.TestCase):

    def test_an_approved_ready_unit_awaits_the_signature(self) -> None:
        """AC1. MUTANTS: HEAD's `if critic.is_awaiting_signoff(status):` gate, under which only a
        Review unit can await the signature; a predicate that answers every pre-terminal unit
        whatever its review, so an unreviewed Ready unit is no longer held; one that answers a
        kind `sign` never moves, so an approved CR at In Progress passes the close and the
        signature then seals the run over it where it stands."""
        cases = (("US0101", "Ready"), ("US0102", "In Progress"), ("BG0103", "In Progress"),
                 ("US0104", "Review"))
        for uid, status in cases:
            with self.subTest(unit=uid, status=status), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                state = _state(root, [uid])   # the run opens first: its review is its own
                _unit(root, uid, status, approved=True)
                self.assertEqual([], sprint.seal_bar_unmet(root, uid),
                                 "the fixture does not meet the seal's bar")
                held = sprint.unanswered_units(root, state)["unanswered"]
                self.assertEqual([], held, f"{uid} at {status} held although the seal moves it")
                holds = [h["hold"] for h in sprint._report_holds(root, state)]
                self.assertNotIn("unanswered-review", holds)
        # THE CONTROL: the same Ready unit with no review is still held, by the close's reader
        # and by the report hold, so the close still names the unit `sign` refuses.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _state(root, ["US0101"])
            _unit(root, "US0101", "Ready", approved=False)
            held = [h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]]
            self.assertEqual(["US0101"], held)
            hold = [h for h in sprint._report_holds(root, state)
                    if h["hold"] == "unanswered-review"]
            self.assertTrue(hold and "US0101: Ready" in hold[0]["detail"], hold)
        # THE KIND CONTROL: an approved CR short of Review meets the bar, but `sign` moves only
        # stories and bugs, so the close still holds it rather than pass what the seal leaves.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _state(root, ["CR0105"])
            _unit(root, "CR0105", "In Progress", approved=True)
            self.assertEqual([], sprint.seal_bar_unmet(root, "CR0105"))
            self.assertNotIn(sprint.sdlc_md.find_by_id(root, "CR0105")[1],
                             sprint._SIGNOFF_TERMINAL)
            held = [h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]]
            self.assertEqual(["CR0105"], held)
            holds = [h["hold"] for h in sprint._report_holds(root, state)]
            self.assertIn("unanswered-review", holds)

    def test_status_names_every_run_awaiting_signature(self) -> None:
        """US1290 AC4. Two closed runs await their signatures in their tracked records while a
        third is open; `status.py` names both, each with its run and report, and not the open
        run; a project with none waiting prints no such line. MUTANTS: only the most recent
        waiting run named; the open run counted as waiting; a signed record counted as waiting;
        the line printed with nothing waiting."""
        def record(root: Path, run_id: str, **fields) -> None:
            p = root / "sdlc-studio" / "reports" / "runs" / f"{run_id}.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"schema": 1, "run_id": run_id, **fields}), encoding="utf-8")

        def status(root: Path) -> list[str]:
            r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "status.py"), "pillars",
                                "--root", str(root)], capture_output=True, text=True,
                               timeout=300, check=False)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            return [ln for ln in r.stdout.splitlines() if ln.startswith("Awaiting signature:")]

        with tempfile.TemporaryDirectory() as waiting, tempfile.TemporaryDirectory() as none:
            root = Path(waiting)
            record(root, "RUN-WAIT0001", outcome="running", report="RPT0001")
            record(root, "RUN-WAIT0002", outcome="running", report="RPT0002")
            record(root, "RUN-SIGNED01", outcome="goal-reached", report="RPT0000",
                   signature={"report": "RPT0000"})
            open_run = _state(root, ["US0101"])
            open_run.update(run_id="RUN-OPEN0003", report=None)
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps(open_run), encoding="utf-8")
            lines = status(root)
            self.assertEqual(2, len(lines), lines)
            for run_id, report in (("RUN-WAIT0001", "RPT0001"), ("RUN-WAIT0002", "RPT0002")):
                self.assertTrue(any(run_id in ln and report in ln for ln in lines),
                                f"{run_id} on {report} is not named: {lines}")
            self.assertFalse([ln for ln in lines if "RUN-OPEN0003" in ln or "RUN-SIGNED01" in ln],
                             lines)
            self.assertEqual([], status(Path(none)))

    def test_an_unreadable_record_is_named_not_read_as_none(self) -> None:
        """BG1583 AC4, US1290's third guard. A tracked run record that cannot be parsed reads
        as one `Awaiting signature: UNREADABLE` line naming the record, never as no run
        waiting; a readable record awaiting its page (the control) reads as its sign command.
        MUTANT: `awaiting_signature_lines` returning `[]` for the unreadable record."""
        import status  # noqa: PLC0415 - the reader under test, imported where it is judged

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            runs = root / "sdlc-studio" / "reports" / "runs"
            runs.mkdir(parents=True)
            (runs / "RUN-WAIT0001.json").write_text(
                json.dumps({"schema": 1, "run_id": "RUN-WAIT0001", "outcome": "running",
                            "report": "RPT0001"}), encoding="utf-8")
            self.assertEqual(['Awaiting signature: RUN-WAIT0001 on RPT0001 - sprint.py sign '
                              '--report RPT0001 --principal "<the operator who signs>"'],
                             status.awaiting_signature_lines(root))
            (runs / "RUN-WAIT0002.json").write_text('{"run_id": "RUN-WAIT0002", ',
                                                    encoding="utf-8")
            lines = status.awaiting_signature_lines(root)
            self.assertEqual(1, len(lines), lines)
            self.assertTrue(lines[0].startswith("Awaiting signature: UNREADABLE"), lines)
            self.assertIn("RUN-WAIT0002.json", lines[0])
            self.assertIn("this is not the same as none", lines[0])

    def test_the_loop_moves_a_built_unit_to_review(self) -> None:
        """AC2. MUTANT: the rc.1 and HEAD Build step, which never names the move to Review."""
        text = (SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        loop = text.split("## The loop", 1)[1]
        build = loop.split("2. **Build.**", 1)[1].split("3. **Review.**", 1)[0]
        self.assertRegex(build, r"transition\.py set <id> Review",
                         "the Build step does not name the transition to Review")
        self.assertTrue(re.search(r"moves?\s+to\s+Review", build), build)
        # Said as something the loop DOES: the sentence leading up to the command carries no
        # negation, so "it never moves to Review (`transition.py set <id> Review` is not run)"
        # fails where the positive statement passes.
        lead = re.split(r"(?<=[.;])\s", build.split("`transition.py set <id> Review`", 1)[0])[-1]
        self.assertNotRegex(lead, r"(?i)\b(?:never|not|no|without|nor)\b|n't", lead)


if __name__ == "__main__":
    unittest.main()
