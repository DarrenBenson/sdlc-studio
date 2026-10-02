"""BG0890: a unit carried at the review cap and discharged inside the same run is delivered.

A REJECT at the cap carries a unit: its findings are filed as a bug and the unit is dropped from
the batch with the reason `carried at the review cap: <bug>`. The rejecting reviewer's APPROVE
answers that REJECT and discharges the carry, and the unit then moves terminal. RPT0014 read six
such units as `dropped - carried at the review cap`, left their points out of Delivered and the
Estimates points row, and the velocity row (RETRO0129) left them out too.

Every test builds a lean run in a throwaway workspace, derives the page through
`sprint_report.build_report` and records the velocity row through `retro.py accuracy --write`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

RETRO = "RETRO0001"
AS_OF = "2026-09-23T12:00:00Z"
DAY = "2026-09-23"
LEDGER_HEAD = ("# Critic Verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
REVIEWER = "qa-rev; agent; v1"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


class DischargedCarryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _run(self, carried_status: str = "Done", rows: list[tuple] | None = None) -> None:
        """US0101 (2 points) delivered; US0102 (3 points) carried at the cap by `REVIEWER`'s
        round-2 REJECT, then answered by `rows` (default: that reviewer's APPROVE) and left at
        `carried_status`. The retro names the batch as the close scaffolds it, after the drop."""
        root = self.root
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid, pts, status in (("US0101", 2, "Done"), ("US0102", 3, carried_status)):
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** {status}\n> **Points:** {pts}\n\n"
                "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** shell true\n",
                encoding="utf-8")
        rows = rows if rows is not None else [("APPROVE", REVIEWER)]
        ledger = [("US0101", "APPROVE", REVIEWER), ("US0102", "REJECT", REVIEWER),
                  ("US0102", "REJECT", REVIEWER), *(("US0102", v, r) for v, r in rows)]
        reviews = root / "sdlc-studio" / "reviews"
        reviews.mkdir(parents=True)
        (reviews / "critic-verdicts.md").write_text(LEDGER_HEAD + "".join(
            f"| {u} | {v} | {r} | dev | {DAY} | abcdef012345 | full | [new] a finding |\n"
            for u, v, r in ledger), encoding="utf-8")
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-lean.md").write_text(
            f"# RETRO-0001: lean\n\n> **Date:** {DAY}\n> **Batch:** US0101\n\n"
            "## Lessons\n\n- learned a thing\n", encoding="utf-8")
        state = {
            "schema": 1, "run_id": "RUN-LEAN0001", "started_at": "2026-09-23T00:00:00Z",
            "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
            "sprint_goal": "deliver both", "ci_runs": {"source": "gh run list", "runs": []},
            "plan_snapshot": {"units": {
                "US0101": {"planned_points": 2, "forecast_minutes": 20.0, "added": False},
                "US0102": {"planned_points": 3, "forecast_minutes": 30.0, "added": False}}},
            "batch_changes": [{"action": "drop", "id": "US0102",
                               "reason": "carried at the review cap: BG0201",
                               "at": "2026-09-23T06:00:00Z"}]}
        p = root / "sdlc-studio" / ".local" / "run-state.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps(state), encoding="utf-8")

    def _page(self, **build) -> dict:
        return _live("sprint_report").build_report(self.root, RETRO, as_of=AS_OF, **build)

    @staticmethod
    def _section(page: dict, key: str) -> dict:
        return next(s for s in page["sections"] if s["key"] == key)

    def _carried_outcome(self, page: dict) -> str:
        rows = self._section(page, "delivered")["rows"]
        return next(r["unit_outcome"]["value"] for r in rows
                    if r["unit_id"]["value"] == "US0102")

    def test_a_discharged_carry_counts_as_delivered(self) -> None:
        """AC1. MUTANT: HEAD, which reads every drop as dropped, so US0102 reads `dropped -
        carried at the review cap: BG0201`, Delivered of the plan is 1 unit and 2 points, the
        Estimates points row reads 2 of 2, and Dropped is 1 unit and 3 points."""
        self._run()
        page = self._page()
        self.assertEqual("delivered - discharged after it was carried at the review cap: "
                         "BG0201", self._carried_outcome(page))
        figs = self._section(page, "delivered")["figures"]
        self.assertEqual((2, 5), (figs["plan_delivered_units"]["value"],
                                  figs["plan_delivered_points"]["value"]))
        self.assertEqual((0, 0), (figs["dropped_units"]["value"],
                                  figs["dropped_points"]["value"]))
        self.assertEqual(5, figs["points_delivered"]["value"])
        pts = next(r for r in self._section(page, "estimates")["rows"]
                   if r["est_measure"]["value"] == "Points")
        self.assertEqual((5, 5), (pts["est_forecast"]["value"], pts["est_actual"]["value"]))
        issues = [r["issue_id"]["value"] for r in self._section(page, "known_issues")["rows"]]
        self.assertNotIn("US0102", issues)

    def test_a_carry_not_discharged_stays_dropped(self) -> None:
        """The controls. MUTANTS: count every carry as delivered once the unit is terminal (a
        carry the cap left standing, then moved by hand); accept any reviewer's APPROVE (not the
        one whose REJECT carried it); count a discharged unit not yet terminal."""
        for name, status, rows in (("still rejected", "Done", []),
                                   ("another reviewer", "Done", [("APPROVE", "other; agent; v1")]),
                                   ("not terminal", "Review", None)):
            with self.subTest(name):
                self._tmp.cleanup()
                self.root.mkdir(parents=True, exist_ok=True)
                self._run(carried_status=status, rows=rows)
                page = self._page()
                self.assertEqual("dropped - carried at the review cap: BG0201",
                                 self._carried_outcome(page))
                figs = self._section(page, "delivered")["figures"]
                self.assertEqual(1, figs["dropped_units"]["value"])

    def test_the_velocity_row_counts_a_discharged_carry(self) -> None:
        """AC2. MUTANT: HEAD, whose row counts the retro's Batch field alone - the batch after
        the carry dropped US0102 - so it reads 1 unit and 2 points for a run that delivered
        2 units and 5 points."""
        self._run()
        retro = _live("retro")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = retro.main(["--root", str(self.root), "accuracy", "--id", RETRO, "--write"])
        self.assertEqual(0, rc, out.getvalue())
        row = next(r for r in retro.velocity_history(self.root) if r.get("id") == RETRO)
        self.assertEqual((2, 5), (row["units"], row["points"]), row)

    def _prepare(self) -> str:
        """What PREPARE records before it files the page - the units whose terminal gate cleared
        (`report_gate_clear`, here US0101) and the ledger rows and discharges it freezes
        (`freeze_review_rows`) - then the page filed as the close files it. Returns its id."""
        sr = _live("sprint_report")
        _live("lib.run_state").update(self.root, report_gate_clear=["US0101"])
        sr.freeze_review_rows(self.root)
        return sr.file_report(self.root, self._page())

    def _set_status(self, uid: str, status: str) -> None:
        p = self.root / "sdlc-studio" / "stories" / f"{uid}-x.md"
        text = p.read_text(encoding="utf-8")
        old = next(ln for ln in text.splitlines() if ln.startswith("> **Status:**"))
        p.write_text(text.replace(old, f"> **Status:** {status}"), encoding="utf-8")

    def test_a_unit_moved_by_hand_after_filing_does_not_move_the_page(self) -> None:
        """BG0890 round 1, the reviewer's repro. The page is filed with the carried unit at
        Review (answered, not yet terminal), then both units are set Done by hand - the seal
        moves only batch units, so a dropped one is moved by hand. MUTANT: read the discharge's
        terminal status live, as round 1 did, so the re-derived page reads US0102 delivered
        and revalidate reads INVALID."""
        self._run(carried_status="Review")
        self._set_status("US0101", "Review")
        sr = _live("sprint_report")
        rid = self._prepare()
        self.assertEqual("dropped - carried at the review cap: BG0201",
                         self._carried_outcome(sr.read_report(self.root, rid)))
        self._set_status("US0101", "Done")
        self._set_status("US0102", "Done")
        check = sr.revalidate(self.root, rid)
        self.assertTrue(check["valid"], check["changes"])

    def test_the_frozen_review_rows_path_reads_the_discharge(self) -> None:
        """The path real runs take: PREPARE froze `REVIEW_ROWS` and the discharges with them.
        MUTANTS: the frozen-rows branch of `_run_rows` reading nothing, so PREPARE freezes no
        discharge and US0102 reads dropped; a frozen discharge list the page ignores in favour
        of a live reading (killed by the repro above)."""
        self._run()
        rid = self._prepare()
        state = _live("lib.run_state").read(self.root)
        sr = _live("sprint_report")
        self.assertIn("US0102", state[sr.REVIEW_ROWS], "premise: PREPARE froze the rows")
        self.assertEqual(["US0102"], state[sr.DISCHARGED])
        self.assertEqual("delivered - discharged after it was carried at the review cap: "
                         "BG0201", self._carried_outcome(sr.read_report(self.root, rid)))
        self.assertTrue(sr.revalidate(self.root, rid)["valid"])

    def test_a_page_filed_before_the_fix_re_derives_as_signed(self) -> None:
        """RPT0014 was signed with six discharged carries read as dropped. MUTANTS: apply the
        rule to a page that carries no mark of it, so the signed page reads INVALIDATED; leave
        the mark off a new page."""
        self._run()
        sr = _live("sprint_report")
        before = self._page(discharge_rule=False)
        self.assertEqual("dropped - carried at the review cap: BG0201", self._carried_outcome(before))
        self.assertNotIn(sr.DISCHARGE_RULE, before)
        check = sr.revalidate(self.root, sr.file_report(self.root, before))
        self.assertTrue(check["valid"], check["changes"])
        after = self._page()
        self.assertEqual(sr.DISCHARGE_DELIVERED, after.get(sr.DISCHARGE_RULE))
        check = sr.revalidate(self.root, sr.file_report(self.root, after))
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
