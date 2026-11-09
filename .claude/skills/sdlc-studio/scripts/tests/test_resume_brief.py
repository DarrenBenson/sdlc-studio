"""US1140: the run's next action and a resume brief of at most 8k tokens, derived from disk alone.

Each fixture is a throwaway workspace holding only what the module may read: the run state and
the sprint plan under `sdlc-studio/.local/`, the QA briefs `sprint lane land` writes beside them,
the delivery verdict ledger `critic.py record` appends to, and the artefacts themselves.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py -q
"""
from __future__ import annotations

import inspect
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import critic  # noqa: E402
import file_finding  # noqa: E402
import sprint_report  # noqa: E402
from lib import resume_brief, sdlc_md  # noqa: E402
from tests import quiet  # noqa: E402

RUN = "RUN-01TESTRUN"
#: Every lane in these fixtures was briefed at this moment, so a QA brief written as the fixture
#: runs is one its landing wrote, and a brief dated before it is a stale one from an earlier run.
STARTED = "2026-01-01T00:00:00Z"
STARTED_EPOCH = 1767225600  # STARTED as seconds since the epoch
BEFORE_STARTED = STARTED_EPOCH - 86400
#: The `Raised-in-batch` stamp `file_finding` writes on a finding filed while a run is open: the
#: absence of a batch, then the moment of filing as its last token. A run's own close is the only
#: writer that names the run (`<run id> close, <moment>`). `KnownIssuesTests` pins MID_RUN against
#: a real filing, so no fixture here carries a stamp no tool writes.
MID_RUN = "none open - raised outside a delivery batch, {}"
#: Before the fixture run's start.
PRE_RUN = "2025-12-31T23:59:59Z"
DIRS = {"US": "stories", "BG": "bugs", "CR": "change-requests"}
TERMINAL = {"US": "Done", "BG": "Fixed", "CR": "Complete"}
OPEN = {"US": "Ready", "BG": "Open", "CR": "Approved"}
LEDGER_HEAD = ("# Critic verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


class Tree:
    """A run in a temporary workspace, shaped through the files the shipped tools write."""

    def __init__(self, tmp: str, batch, waves=None, goal="Ship the resume brief", rulings=()):
        self.root = Path(tmp)
        self.local = self.root / "sdlc-studio" / ".local"
        self.local.mkdir(parents=True)
        self.state = {"schema": 1, "run_id": RUN, "started_at": STARTED, "outcome": "running",
                      "goal": "done",
                      "batch": list(batch), "sprint_goal": goal, "rulings": list(rulings),
                      "lanes_in_flight": [], "plan": "sdlc-studio/.local/sprint-plan.json"}
        plan = {"waves": [list(w) for w in (waves or [batch])]}
        (self.local / "sprint-plan.json").write_text(json.dumps(plan), encoding="utf-8")
        self.briefs: dict[str, str] = {}
        for uid in batch:
            self.artefact(uid, OPEN[uid[:2]])
        self.save()

    def save(self) -> None:
        (self.local / "run-state.json").write_text(json.dumps(self.state), encoding="utf-8")

    def artefact(self, uid: str, status: str, title: str | None = None, extra: str = "") -> None:
        folder = self.root / "sdlc-studio" / DIRS[uid[:2]]
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob(f"{uid}-*.md"):
            old.unlink()
        (folder / f"{uid}-fixture.md").write_text(
            f"# {uid}: {title or 'Fixture unit ' + uid}\n\n> **Status:** {status}\n{extra}\n",
            encoding="utf-8")

    def fly(self, uid: str, started: str = STARTED) -> None:
        """What `sprint.py lane brief` records: the unit under `lanes_in_flight`, id normalised."""
        rows = [r for r in self.state["lanes_in_flight"] if r["unit"] != sdlc_md.norm_id(uid)]
        self.state["lanes_in_flight"] = rows + [{"unit": sdlc_md.norm_id(uid),
                                                 "started_at": started}]
        self.save()

    def land(self, uid: str, stale: bool = False) -> str:
        """What `sprint lane land` writes: the unit's QA brief under `sdlc-studio/.local/briefs/`."""
        rel = f"sdlc-studio/.local/briefs/{uid}-qa.txt"
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        text = f"QA brief for {uid}, landing {len(self.briefs) + 1}\n"
        path.write_text(text, encoding="utf-8")
        if stale:
            os.utime(path, (BEFORE_STARTED, BEFORE_STARTED))
        self.briefs[uid] = text
        return rel

    def verdict(self, uid: str, verdict: str) -> None:
        """What `critic.py record` appends: a row against the fingerprint of the unit's brief."""
        ledger = self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        head = ledger.read_text(encoding="utf-8") if ledger.exists() else LEDGER_HEAD
        fp = critic.brief_fingerprint(self.briefs[uid])
        ledger.write_text(head + f"| {uid} | {verdict} | qa-seat | builder | 2026-01-02 | {fp} "
                                 f"| full | none |\n", encoding="utf-8")

    def finish(self, uid: str) -> None:
        """An APPROVE moved by `sprint lane accept`: the unit terminal and its lane returned."""
        self.artefact(uid, TERMINAL[uid[:2]])
        self.state["lanes_in_flight"] = [r for r in self.state["lanes_in_flight"]
                                         if r["unit"] != sdlc_md.norm_id(uid)]
        self.save()

    def accept(self, uid: str) -> None:
        self.fly(uid)
        self.land(uid)
        self.verdict(uid, "APPROVE")
        self.finish(uid)


class NextActionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def tree(self, batch, waves=None, **kw) -> Tree:
        return Tree(self._tmp.name, batch, waves, **kw)

    def test_each_fixture_state_yields_its_rung_of_the_ladder(self):
        t = self.tree(["US0001", "US0002", "US0003", "BG0004", "US0005"],
                      [["US0001", "US0002"], ["US0003", "BG0004"], ["US0005"]])
        # state 1: a lane in flight, while a landed unit owes its review and two later waves
        # are unbriefed - rungs 2 and 3 both hold, and the in-flight lane still wins
        t.fly("US0001")
        t.fly("US0002")
        t.land("US0002")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (1, "await", ("US0001",)))
        self.assertIn("US0001", step.text)
        # two calls on one tree return the same step; a changed tree changes it, so nothing is
        # carried between calls in the process
        self.assertEqual(resume_brief.next_action(t.root), step)

        # state 2: a landed unit with a QA brief and no APPROVE (US0002, none at all; US0001,
        # a REJECT), with the later waves still unbriefed
        t.land("US0001")
        t.verdict("US0001", "REJECT")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind), (2, "review"))
        self.assertEqual(set(step.units), {"US0001", "US0002"})
        self.assertIn("sdlc-studio/.local/briefs/US0002-qa.txt", step.text)
        self.assertIn("sprint.py lane accept --unit US0002", step.text)
        self.assertIn("sprint.py lane brief --units US0001", step.text)
        # with the review answered, the REJECT alone is a repair on the same rung
        t.verdict("US0002", "APPROVE")
        t.finish("US0002")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (2, "repair", ("US0001",)))
        self.assertIn("sprint.py lane brief --units US0001", step.text)
        # an APPROVE against an EARLIER brief does not answer the brief this landing wrote
        t.verdict("US0001", "APPROVE")
        t.land("US0001")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (2, "review", ("US0001",)))
        # a repair lane briefed again after the REJECT is in flight, not a repair owed: the
        # brief on disk predates the lane's start, so no landing of this lane wrote it
        t.verdict("US0001", "REJECT")
        os.utime(t.root / "sdlc-studio/.local/briefs/US0001-qa.txt",
                 (BEFORE_STARTED, BEFORE_STARTED))
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (1, "await", ("US0001",)))
        # a brief written in the very second the lane started is this lane's
        os.utime(t.root / "sdlc-studio/.local/briefs/US0001-qa.txt",
                 (STARTED_EPOCH, STARTED_EPOCH))
        self.assertEqual(resume_brief.next_action(t.root).kind, "repair")

        # state 3: every landed unit approved, a later wave unbriefed: brief THAT wave only
        t.land("US0001")
        t.verdict("US0001", "APPROVE")
        t.finish("US0001")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (3, "brief", ("US0003", "BG0004")))
        self.assertIn("sprint.py lane brief --units US0003 BG0004", step.text)
        self.assertNotIn("US0005", step.text)
        # a wave part briefed names only its unbriefed ids
        t.accept("US0003")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.units), (3, ("BG0004",)))

        # an APPROVE that did not move its unit leaves that unit owing its finish, and the
        # close is not named while it is not terminal
        t.accept("BG0004")
        t.accept("US0005")
        t.artefact("US0005", "Ready")
        t.fly("US0005")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (2, "finish", ("US0005",)))
        self.assertNotIn("sprint.py close", step.text)

        # state 4: every batch unit terminal
        t.finish("US0005")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (4, "close", ()))
        self.assertIn("`sprint.py close`", step.text)
        self.assertIn("fresh session", step.text)
        # one unit back out of terminal and the close is withdrawn
        t.artefact("BG0004", "Open")
        self.assertEqual(resume_brief.next_action(t.root).rung, 3)
        # a lane state no lower rung catches is refused rather than closed over
        stray = resume_brief.Lane("US0001", 1, "parked", None, "")
        with self.assertRaises(resume_brief.ResumeError) as caught:
            resume_brief._ladder([stray])
        self.assertIn("US0001 is not terminal", str(caught.exception))

    def test_the_wave_boundary_holds_only_with_every_lane_accepted_and_none_in_flight(self):
        t = self.tree(["US0001", "US0002", "US0003"], [["US0001", "US0002"], ["US0003"]])
        # nothing briefed yet: no lane is open, so the run stands between waves
        self.assertTrue(resume_brief.at_wave_boundary(t.root))
        t.fly("US0001")
        t.fly("US0002")
        b = resume_brief.at_wave_boundary(t.root)
        self.assertIs(bool(b), False)
        self.assertEqual(b.blocking, "US0001")
        self.assertIn("in flight", b.reason)
        # one lane landed and awaiting its verdict, the other still in flight
        t.land("US0001")
        self.assertEqual(resume_brief.at_wave_boundary(t.root).blocking, "US0001")
        t.verdict("US0001", "APPROVE")
        t.finish("US0001")
        b = resume_brief.at_wave_boundary(t.root)
        self.assertEqual((bool(b), b.blocking), (False, "US0002"))
        # landed, no verdict: still not a boundary
        t.land("US0002")
        b = resume_brief.at_wave_boundary(t.root)
        self.assertEqual((bool(b), b.blocking), (False, "US0002"))
        self.assertIn("verdict", b.reason)
        # REJECTed: not a boundary either
        t.verdict("US0002", "REJECT")
        b = resume_brief.at_wave_boundary(t.root)
        self.assertEqual((bool(b), b.blocking), (False, "US0002"))
        # APPROVEd and not yet moved: every lane is accepted and none in flight
        t.verdict("US0002", "APPROVE")
        b = resume_brief.at_wave_boundary(t.root)
        self.assertIs(bool(b), True)
        self.assertIsNone(b.blocking)
        t.finish("US0002")
        self.assertTrue(resume_brief.at_wave_boundary(t.root))
        # a lane of the next wave in flight ends the boundary again
        t.fly("US0003", started=None)
        b = resume_brief.at_wave_boundary(t.root)
        self.assertEqual((bool(b), b.blocking), (False, "US0003"))
        self.assertIn("in flight", b.reason)
        # a lane record with no start: any brief on disk is taken as this lane's landing
        t.land("US0003")
        self.assertIn("verdict", resume_brief.at_wave_boundary(t.root).reason)


def _row(text: str, uid: str) -> str:
    rows = [ln for ln in text.splitlines() if ln.startswith(f"| {uid} |")]
    assert len(rows) == 1, (uid, rows)
    return rows[0]


class ResumeBriefTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_the_brief_names_every_unit_and_each_pending_item(self):
        rulings = ["D0435: the human leads the run", "D0442: run nine is a maintenance run"]
        t = Tree(self._tmp.name, ["US0001", "US0002", "US0003", "US0004", "BG0005", "BG0006"],
                 [["US0002", "US0003", "US0004", "BG0005", "BG0006"], ["US0001"]],
                 goal="Waves resume from a short brief", rulings=rulings)
        t.fly("US0002")
        t.fly("US0003")
        brief_path = t.land("US0003")
        t.fly("US0004")
        t.land("US0004")
        t.verdict("US0004", "APPROVE")
        t.accept("BG0005")
        t.fly("BG0006")
        t.land("BG0006")
        t.verdict("BG0006", "REJECT")
        # findings raised in this run, in another run, and in this run but already closed; the
        # other run's close stamped its finding at that run's end, before this one opened
        t.artefact("BG0099", "Open", "Gate host times out",
                   f"> **Raised-in-batch:** {RUN} close, 2026-01-03T00:00:00Z")
        t.artefact("CR0096", "Approved", "Name the agent in the brief",
                   f"> **Raised-in-batch:** {MID_RUN.format('2026-01-02T09:30:00Z')}")
        t.artefact("BG0098", "Fixed", "Already fixed",
                   f"> **Raised-in-batch:** {MID_RUN.format('2026-01-02T10:00:00Z')}")
        t.artefact("CR0097", "Approved", "Another run's finding",
                   "> **Raised-in-batch:** RUN-01OTHERRN close, 2025-12-31T23:00:00Z")

        text = resume_brief.build(t.root, agents={"US0002": "agent-a2e3b739"},
                                  issues=["the push gate is red on main"])
        self.assertIn(RUN, text)
        self.assertIn("Waves resume from a short brief", text)
        read = resume_brief.parse(text)
        self.assertEqual(read["units"], {"US0001": "unbriefed", "US0002": "in flight",
                                         "US0003": "landed awaiting a verdict",
                                         "US0004": "accepted", "BG0005": "terminal",
                                         "BG0006": "rejected"})
        self.assertIn("agent-a2e3b739", _row(text, "US0002"))
        self.assertEqual(read["agents"], {"US0002": "agent-a2e3b739"})
        self.assertIn(brief_path, _row(text, "US0003"))
        pending = text.split("## Pending", 1)[1].split("\n## ", 1)[0]
        self.assertIn(f"QA brief for US0003: `{brief_path}`", pending)
        self.assertIn("Verdict owed on US0003", pending)
        self.assertIn("Repair owed on BG0006", pending)
        self.assertNotIn("US0004", pending)
        for ruling in rulings:
            self.assertIn(f"- {ruling}", text)
        issues = text.split("## Known issues", 1)[1]
        self.assertIn("the push gate is red on main", issues)
        self.assertIn("BG0099", issues)
        self.assertIn("CR0096", issues)
        self.assertNotIn("BG0098", issues)
        self.assertNotIn("CR0097", issues)
        self.assertIs(read["at_wave_boundary"], False)
        self.assertIn("Wave boundary: no (US0002 is in flight)", text)
        step = resume_brief.next_action(t.root)
        self.assertEqual(read["next_action"], step.text)
        self.assertEqual(step.rung, 1)

    def thirty(self, rulings: int = 10) -> Tree:
        ids = [f"US{n:04d}" for n in range(1, 21)] + [f"BG{n:04d}" for n in range(21, 31)]
        t = Tree(self._tmp.name, ids, [ids[:12], ids[12:22], ids[22:]],
                 goal="Abena Osei becomes Primary, Copilot, Grok and Composer runs are priced, "
                      "and waves resume from a short brief",
                 rulings=[f"D{440 + n:04d}: the operator rules that lane {n} carries its own "
                          f"fixtures and lands on main after an independent APPROVE, never "
                          f"before, and the close waits for every lane" for n in range(rulings)])
        for uid in ids:
            t.artefact(uid, OPEN[uid[:2]],
                       f"{uid} derives the run's next step from disk alone, with no session")
        for uid in ids[:6]:
            t.accept(uid)
        for uid in ids[6:12]:
            t.fly(uid)
        for uid in ids[6:9]:
            t.land(uid)
        return t

    def test_an_over_budget_brief_is_refused_and_a_thirty_unit_brief_fits(self):
        self.assertEqual(resume_brief.BUDGET_TOKENS, 8000)
        self.assertEqual([resume_brief.estimate_tokens(s) for s in ("", "abcd", "abcde")],
                         [0, 1, 2])
        t = self.thirty()
        agents = {f"US{n:04d}": f"agent-{n:08d}" for n in range(7, 13)}
        text = resume_brief.build(t.root, agents=agents, issues=["the gate host is slow"])
        self.assertLessEqual(resume_brief.estimate_tokens(text), resume_brief.BUDGET_TOKENS)
        self.assertEqual(len(resume_brief.parse(text)["units"]), 30)
        # the budget is inclusive: a brief at exactly 8,000 tokens is returned whole, one
        # character more is refused, naming the estimate and the budget
        one = resume_brief.build(t.root, agents=agents, issues=["a"])
        fill = 4 * resume_brief.BUDGET_TOKENS - len(one) + 1
        whole = resume_brief.build(t.root, agents=agents, issues=["a" * fill])
        self.assertEqual(resume_brief.estimate_tokens(whole), resume_brief.BUDGET_TOKENS)
        self.assertIn("a" * fill, whole)
        with self.assertRaises(resume_brief.BriefTooLong) as caught:
            resume_brief.build(t.root, agents=agents, issues=["a" * (fill + 1)])
        self.assertEqual(caught.exception.estimate, resume_brief.BUDGET_TOKENS + 1)
        self.assertEqual(caught.exception.budget, resume_brief.BUDGET_TOKENS)
        self.assertIn("8,001", str(caught.exception))
        self.assertIn("8,000", str(caught.exception))
        with self.assertRaises(resume_brief.BriefTooLong) as caught:
            resume_brief.build(t.root, issues=["x" * 40_000])
        self.assertGreater(caught.exception.estimate, 10_000)

    def test_the_brief_round_trips_and_a_schema3_id_is_one_unit(self):
        t = Tree(self._tmp.name, ["US-01M6XQJF", "US0002", "US0003"],
                 [["US-01M6XQJF", "US0002"], ["US0003"]])
        t.artefact("US-01M6XQJF", "Ready", "A schema-3 story")
        # `lane brief` records the unit normalised, the batch keeps the file's spelling
        t.fly("US-01M6XQJF")
        self.assertEqual(t.state["lanes_in_flight"][0]["unit"], "US01M6XQJF")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.units), (1, ("US-01M6XQJF",)))
        # the caller names the lane's agent in the file's spelling, the run state in the other
        text = resume_brief.build(t.root, agents={"US-01M6XQJF": "agent-v3"})
        read = resume_brief.parse(text)
        self.assertEqual(read["run_id"], RUN)
        self.assertEqual((read["next_action"], read["rung"]), (step.text, step.rung))
        self.assertEqual(read["units"], {"US01M6XQJF": "in flight", "US0002": "unbriefed",
                                         "US0003": "unbriefed"})
        self.assertEqual(read["agents"], {"US01M6XQJF": "agent-v3"})
        # an in-flight row kept in the dashed spelling is the same lane
        t.state["lanes_in_flight"][0]["unit"] = "US-01M6XQJF"
        t.save()
        self.assertEqual(resume_brief.next_action(t.root), step)
        # `lane land --units US-01M6XQJF` names the QA brief as typed: still the same unit's
        rel = t.land("US-01M6XQJF")
        self.assertEqual(rel, "sdlc-studio/.local/briefs/US-01M6XQJF-qa.txt")
        step = resume_brief.next_action(t.root)
        self.assertEqual((step.rung, step.kind, step.units), (2, "review", ("US-01M6XQJF",)))
        self.assertIn(rel, step.text)
        t.verdict("US-01M6XQJF", "APPROVE")
        t.finish("US-01M6XQJF")
        t.accept("US0002")
        step = resume_brief.next_action(t.root)
        text = resume_brief.build(t.root)
        read = resume_brief.parse(text)
        self.assertEqual((read["next_action"], read["rung"]), (step.text, 3))
        self.assertIs(read["at_wave_boundary"], True)
        # a hand-kept brief naming the unit in both spellings still reads as one unit
        row = _row(text, "US-01M6XQJF")
        twice = text.replace(row, row + "\n" + row.replace("US-01M6XQJF", "US01M6XQJF"))
        self.assertEqual(len(twice.splitlines()), len(text.splitlines()) + 1)
        self.assertEqual(resume_brief.parse(twice)["units"],
                         {"US01M6XQJF": "terminal", "US0002": "terminal", "US0003": "unbriefed"})


class KnownIssuesTests(unittest.TestCase):
    """BG1312: a finding filed while the run is open is the run's by the moment its stamp records,
    placed by the reader `sprint_report` places it with, as well as by a stamp naming the run."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.t = Tree(self._tmp.name, ["US0001"])
        file_finding.ensure_index(self.t.root, "bug", "2026-01-02")

    def file(self, title: str, status: str | None = None,
             moment: str | None = None) -> tuple[str, Path]:
        """File a bug through `file_finding` while the run is open, as a session does mid-run.
        `moment` re-dates the stamp it wrote, keeping its shape; `status` closes the bug."""
        with quiet.diagnostics():
            res = file_finding.file_finding(
                self.t.root, "bug", title,
                {"summary": "s", "severity": "Medium", "steps": "s", "fix": "f",
                 "acs": ["Given x, then y"], "affects": "lib/x.py, tests/test_x.py",
                 "points": "1"}, counted=False)
        path = Path(res["path"])
        text = path.read_text(encoding="utf-8")
        stamp = sdlc_md.extract_field(text, "Raised-in-batch")
        if moment:
            text = text.replace(stamp, MID_RUN.format(moment))
        if status:
            text = text.replace("> **Status:** Open", f"> **Status:** {status}")
        path.write_text(text, encoding="utf-8")
        return res["id"], path

    def known(self) -> str:
        return resume_brief.build(self.t.root).split("## Known issues", 1)[1]

    def test_a_finding_filed_mid_run_is_listed_by_its_moment(self):
        uid, path = self.file("Gate host times out mid-run")
        stamp = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Raised-in-batch")
        self.assertNotIn(RUN, stamp)   # nothing but the moment places it in the run
        known = self.known()
        self.assertIn(f"{uid}: Gate host times out mid-run (Open)", known)
        self.assertNotIn("- none", known)
        # with no recorded start the moment can place nothing, and the section says so
        del self.t.state["started_at"]
        self.t.save()
        known = self.known()
        self.assertNotIn("- none", known)
        self.assertIn("no start time", known)

    def test_pre_run_and_closed_findings_are_left_out_and_a_run_stamp_still_matches(self):
        mid, _ = self.file("Filed inside the run")
        before, _ = self.file("Filed before the run opened", moment=PRE_RUN)
        fixed, _ = self.file("Filed inside the run and already fixed", status="Fixed")
        # the close's stamp names the run, which makes the finding the run's whatever its moment
        self.t.artefact("CR0096", "Approved", "The run's graduation CR",
                        f"> **Raised-in-batch:** {RUN} close, {PRE_RUN}")
        known = self.known()
        self.assertIn(f"{mid}: Filed inside the run (Open)", known)
        self.assertNotIn(before, known)
        self.assertNotIn(fixed, known)
        self.assertIn("CR0096: The run's graduation CR (Approved)", known)

    def test_the_moment_is_read_through_the_report_helper(self):
        uid, path = self.file("Filed inside the run")
        stamp = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Raised-in-batch")
        moment = stamp.rsplit(", ", 1)[-1]
        # the fixtures' stamp is the one `file_finding` writes mid-run, to the character
        self.assertEqual(stamp, MID_RUN.format(moment))
        self.assertIsNotNone(sdlc_md.parse_iso8601(moment))
        self.assertIn(uid, self.known())
        # the brief reads the moment the way the report does: re-read it and the brief follows
        with mock.patch.object(sprint_report, "_stamp_timestamp", return_value=PRE_RUN) as read:
            self.assertNotIn(uid, self.known())
        self.assertIn(stamp, [c.args[0] for c in read.call_args_list])
        # and holds no stamp parser of its own
        source = Path(resume_brief.__file__).read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\\d\{[24]\}")
        self.assertNotIn("re.", inspect.getsource(resume_brief._findings))  # noqa: SLF001


if __name__ == "__main__":
    unittest.main()
