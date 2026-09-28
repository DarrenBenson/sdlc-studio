"""BG0820: a unit whose only owed step is the signature awaits it at any pre-terminal status.

The close judged "awaiting the signature" only for a unit at Review, while `sprint sign` seals any
batch unit that meets the review bar (`seal_bar_unmet`). A unit the loop left at Ready or In
Progress with an independent delivery APPROVE was therefore handed over as an unanswered known
issue by the close and then moved to Done by the signature: two bars for one unit. The fix judges
the case by the seal's own bar at every pre-terminal status, and the loop's Build step names the
move to Review.

AC1 drives the close's reader in a throwaway workspace. AC2 reads the shipped loop doc.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import re
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
                _unit(root, uid, status, approved=True)
                state = _state(root, [uid])
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
            _unit(root, "US0101", "Ready", approved=False)
            state = _state(root, ["US0101"])
            held = [h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]]
            self.assertEqual(["US0101"], held)
            hold = [h for h in sprint._report_holds(root, state)
                    if h["hold"] == "unanswered-review"]
            self.assertTrue(hold and "US0101: Ready" in hold[0]["detail"], hold)
        # THE KIND CONTROL: an approved CR short of Review meets the bar, but `sign` moves only
        # stories and bugs, so the close still holds it rather than pass what the seal leaves.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _unit(root, "CR0105", "In Progress", approved=True)
            state = _state(root, ["CR0105"])
            self.assertEqual([], sprint.seal_bar_unmet(root, "CR0105"))
            self.assertNotIn(sprint.sdlc_md.find_by_id(root, "CR0105")[1],
                             sprint._SIGNOFF_TERMINAL)
            held = [h["unit"] for h in sprint.unanswered_units(root, state)["unanswered"]]
            self.assertEqual(["CR0105"], held)
            holds = [h["hold"] for h in sprint._report_holds(root, state)]
            self.assertIn("unanswered-review", holds)

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
