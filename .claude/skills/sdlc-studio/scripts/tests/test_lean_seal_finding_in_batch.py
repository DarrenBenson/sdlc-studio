"""BG0895: a finding the run filed and took into its batch does not move the signed page.

BG0876 and BG0877 were filed inside RUN-01M3VF2J and added to its batch. The close listed them as
open findings raised in the run; `sprint sign` moved them to Fixed, the re-derivation no longer
found them open, and the page read INVALIDATED in the rehearsal (BG0848's lineage: the sign
moved something the page had read). A batch unit is on the page as a unit, delivered or carried,
so the open-findings scan leaves the batch out; a finding outside the batch is still listed.

AC1 and AC2 run the real `sprint close`, `sprint sign` and `revalidate` on BG0848's sign fixture
(`test_lean_sign._SignMovesRun`), with the bug stamped as raised inside the open run.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - BG0848's close-and-sign fixture, shared

RETRO = "RETRO0001"


def _raise_in_run(path: Path, at: str) -> None:
    """Stamp a bug as raised at `at`, inside the run, as `file_finding` stamps one."""
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("> **Severity:** Medium\n", "> **Severity:** Medium\n"
                                 "> **Raised-in-batch:** none open - raised outside a delivery "
                                 f"batch, {at}\n", 1), encoding="utf-8")


class _FindingRun(signing._SignMovesRun):
    """BG0848's run, with BG0101 filed inside it (its stamp at the run's own start) and, with
    `outside`, a second bug BG0102 filed inside it and never taken into the batch."""

    def __init__(self, d: str, outside: bool = False, carried: bool = False) -> None:
        super().__init__(d)
        self.outside, self.carried = outside, carried

    def _cli(self, name: str, *argv: str, **kw) -> str:
        """With `carried`, BG0101's criterion is red when it is verified and nobody approves it,
        so its terminal gate refuses at PREPARE and the page carries it undelivered."""
        if self.carried and "BG0101" in argv:
            if name == "critic":
                return ""
            if name == "verify_ac":
                path = self.root / "sdlc-studio" / "bugs" / "BG0101-x.md"
                path.write_text(path.read_text(encoding="utf-8").replace(
                    "shell true", "shell false"), encoding="utf-8")
                return self._verify_red()
        return super()._cli(name, *argv, **kw)

    def _verify_red(self) -> str:
        """`verify_ac run --id BG0101`, which exits non-zero on the red criterion it records."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            lean._live("verify_ac").main(["run", "--id", "BG0101", "--root", str(self.root)])
        return out.getvalue()

    def build(self) -> None:
        rs = lean._live("lib.run_state")
        real_open = rs.open_run

        def open_run(root, *a, **k):
            state = real_open(root, *a, **k)
            bugs = Path(root) / "sdlc-studio" / "bugs"
            _raise_in_run(bugs / "BG0101-x.md", state["started_at"])
            if self.outside:
                (bugs / "BG0102-y.md").write_text(
                    "# BG0102: found mid-run\n\n> **Status:** Open\n> **Severity:** Medium\n"
                    "> **Points:** 1\n\n## Acceptance Criteria\n\n- [ ] **AC1** it holds\n"
                    "  - **Verify:** shell true\n", encoding="utf-8")
                _raise_in_run(bugs / "BG0102-y.md", state["started_at"])
            return state
        with unittest.mock.patch.object(signing.run_state, "open_run", open_run):
            super().build()
        time.sleep(1.1)        # the close's window ends a second after the stamps, never on them


def _criterion(run: "_FindingRun", green: bool) -> None:
    """Turn BG0101's criterion green or red and record the run of it, as a lane would, so its
    terminal gate clears or refuses; the tree is committed so the close takes it."""
    path = run.root / "sdlc-studio" / "bugs" / "BG0101-x.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("shell false", "shell true") if green
                    else text.replace("shell true", "shell false"), encoding="utf-8")
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        lean._live("verify_ac").main(["run", "--id", "BG0101", "--root", str(run.root)])
    for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "BG0101 moved"]):
        subprocess.run(["git", "-C", str(run.root), *argv], env=run.env, check=True,
                       capture_output=True)


def _rule(root: Path, *rulings: tuple[str, str]) -> None:
    """The retro's `## Known issues carried` table, ruling each `(id, ruling)` - none given,
    an empty table, so the checklist reads the table rather than finding none."""
    path = root / "sdlc-studio" / "retros" / f"{RETRO}-lean.md"
    text = path.read_text(encoding="utf-8").replace(   # the batch, so the checklist finds the run
        "> **Date:** 2026-09-23\n", "> **Date:** 2026-09-23\n> **Batch:** US0101, BG0101\n", 1)
    path.write_text(text + "\n## Known issues carried\n\n"
                    "| ID | Ruling | Ruled by | Date |\n| --- | --- | --- | --- |\n"
                    + "".join(f"| {uid} | {ruling} | Maya | 2026-09-30 |\n"
                              for uid, ruling in rulings), encoding="utf-8")


class SealFindingInBatchTests(unittest.TestCase):
    def _seal(self, outside: bool = False) -> tuple[dict, dict, dict]:
        """Close, read the filed page, sign, check: `(page, check, the run)`."""
        d = self._tmpdir()
        run = _FindingRun(d, outside)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        report = run.close()
        sr = lean._live("sprint_report")
        page = sr.read_report(run.root, report)
        run.sign(report)
        return page, sr.revalidate(run.root, report), run

    def _tmpdir(self) -> str:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name

    @staticmethod
    def _scan(page: dict) -> str:
        sec = next(s for s in page["sections"] if s["key"] == "known_issues")
        return sec["figures"]["findings_scan"]["value"]

    @staticmethod
    def _issues(page: dict) -> list[str]:
        sec = next(s for s in page["sections"] if s["key"] == "known_issues")
        return [r["issue_id"]["value"] for r in sec["rows"]]

    def test_a_batch_finding_does_not_move_the_signed_page(self) -> None:
        """AC1. MUTANT: HEAD, which lists BG0101 - raised in the run, in its batch, In Progress
        at the close - as an open finding; the sign moves it to Fixed and the re-derived page
        drops the row and `findings_scan` reads 0 where 1 was signed: INVALIDATED."""
        page, check, run = self._seal()
        self.assertEqual("Fixed", run.status("BG0101"), "premise: the sign moved it terminal")
        self.assertNotIn("BG0101", self._issues(page))
        self.assertTrue(check["valid"], (check["changes"], check["edited"]))

    def test_a_mid_run_finding_outside_the_batch_stays_listed(self) -> None:
        """AC2, the control. MUTANT: drop every finding raised in the run from the scan, so
        BG0102 - filed in the run, never in the batch, still open - reaches no page."""
        page, check, _run = self._seal(outside=True)
        self.assertIn("BG0102", self._issues(page))
        self.assertNotIn("BG0101", self._issues(page))
        self.assertTrue(check["valid"], (check["changes"], check["edited"]))

    def _close_with_checklist(self, run: _FindingRun) -> tuple[dict, list[dict]]:
        """The real close with its checklist step real: `(filed page, close known issues)`."""
        for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", "the ruling"]):
            subprocess.run(["git", "-C", str(run.root), *argv], env=run.env, check=True,
                           capture_output=True)
        rc, out, err = lean._close(run.root, real=("checklist",))
        self.assertEqual(0, rc, out + err)
        state = lean._read(run.root)
        return (lean._live("sprint_report").read_report(run.root, state["report"]),
                state.get("close_known_issues") or [])

    @staticmethod
    def _finding_rows(page: dict) -> dict:
        sec = next(s for s in page["sections"] if s["key"] == "known_issues")
        return {r["issue_id"]["value"]: r for r in sec["rows"]
                if r["issue_priority"]["value"] not in ("carried unit", "close gap",
                                                          "STOP-SHIP")}

    def test_the_checklist_and_the_page_agree_on_which_findings_need_a_ruling(self) -> None:
        """BG0895 round 1, the reviewer's first repro (D0306). BG0101 in the batch and
        delivered, BG0102 outside it, neither ruled. MUTANT: the checklist reads the unfiltered
        open findings, so its close gap names BG0101 as UNRULED beside a page that lists only
        BG0102."""
        run = _FindingRun(self._tmpdir(), outside=True)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        _rule(run.root)                                    # neither finding ruled
        page, gaps = self._close_with_checklist(run)
        self.assertEqual(["BG0102"], list(self._finding_rows(page)))
        # The close's checklist step ran before PREPARE froze the gate; it asked the gate itself.
        handed = [g["detail"] for g in gaps if g["detail"].startswith("known-issues:")]
        self.assertEqual(1, len(handed), gaps)
        self.assertIn("1 unruled", handed[0])
        # And the checklist read again from the record PREPARE froze names the same one.
        ck = lean._live("sprint_report").checklist(run.root, RETRO)
        row = next(r for r in ck["items"] if r["id"] == "known-issues")
        self.assertIn("UNRULED BG0102", row["detail"])
        self.assertNotIn("BG0101", row["detail"])

    def test_a_carried_batch_finding_keeps_its_severity_and_ruling(self) -> None:
        """BG0895 round 1, the reviewer's second repro (D0306). BG0101 in the batch, never
        approved so carried, and ruled not-stop-ship. MUTANT: round 1's rule, which leaves every
        batch unit out of the scan, so the page shows BG0101 only as a carried unit and loses
        its Medium row and the ruling."""
        run = _FindingRun(self._tmpdir(), carried=True)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        _rule(run.root, ("BG0101", "not-stop-ship"))
        page, gaps = self._close_with_checklist(run)
        row = self._finding_rows(page).get("BG0101")
        self.assertIsNotNone(row, self._issues(page))
        self.assertEqual("Medium", row["issue_priority"]["value"])
        self.assertIn("not-stop-ship, ruled by Maya", row["issue_detail"]["value"])
        self.assertEqual(2, self._issues(page).count("BG0101"), "its finding row and its "
                                                                 "carried-unit row")
        self.assertFalse(any("UNRULED BG0101" in g["detail"] for g in gaps), gaps)

    def _two_closes(self, first_green: bool) -> tuple[_FindingRun, dict, list[dict]]:
        """A re-close (D0308): close once with BG0101's criterion `first_green`, turn it the
        other way, close again. Returns the run, the second attempt's page and its gaps."""
        run = _FindingRun(self._tmpdir(), outside=True)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        _rule(run.root)                                    # neither finding ruled
        if not first_green:
            _criterion(run, green=False)
        self._close_with_checklist(run)
        _criterion(run, green=not first_green)
        return (run, *self._close_with_checklist(run))

    @staticmethod
    def _unruled(gaps: list[dict]) -> str:
        handed = [g["detail"] for g in gaps if g["detail"].startswith("known-issues:")]
        return handed[0] if handed else ""

    def test_a_re_close_red_then_green_judges_the_checklist_by_its_own_gate(self) -> None:
        """BG0909 (BG0895 round 2), red then green. Attempt 1 froze a gate without BG0101;
        attempt 2's gate clears it. MUTANT: the close's checklist reads the frozen verdict, so
        attempt 2 hands over `2 unruled` beside a page listing only BG0102."""
        _run, page, gaps = self._two_closes(first_green=False)
        self.assertEqual(["BG0102"], list(self._finding_rows(page)))
        self.assertIn("1 unruled", self._unruled(gaps))

    def test_a_re_close_green_then_red_judges_the_checklist_by_its_own_gate(self) -> None:
        """BG0909, green then red. Attempt 1 froze a gate clearing BG0101; attempt 2's refuses
        it. MUTANT: the close's checklist reads the frozen verdict, so attempt 2 hands over
        `1 unruled` beside a page listing BG0101 open as well as BG0102."""
        _run, page, gaps = self._two_closes(first_green=True)
        self.assertEqual(["BG0101", "BG0102"], sorted(self._finding_rows(page)))
        self.assertIn("2 unruled", self._unruled(gaps))

    def test_after_the_close_the_checklist_reads_the_filed_page_s_gate(self) -> None:
        """The opposite pin: outside a close attempt the checklist reads the verdict the filed
        page states, so it agrees with that page when a unit moves after filing. MUTANT: delete
        the frozen branch of `delivered_batch`, so BG0101 - delivered on the filed page, its
        criterion since turned red - is demanded a ruling."""
        run = _FindingRun(self._tmpdir(), outside=True)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        _rule(run.root)
        page, _gaps = self._close_with_checklist(run)
        self.assertEqual(["BG0102"], list(self._finding_rows(page)))
        _criterion(run, green=False)
        row = next(r for r in lean._live("sprint_report").checklist(run.root, RETRO)["items"]
                   if r["id"] == "known-issues")
        self.assertIn("UNRULED BG0102", row["detail"])
        self.assertNotIn("BG0101", row["detail"])

    def test_a_page_filed_before_the_fix_re_derives_as_signed(self) -> None:
        """RPT0013 listed a batch finding. MUTANTS: apply the rule to a page that carries no
        mark of it, so RPT0013 reads INVALIDATED; leave the mark off a new page."""
        root = Path(self._tmpdir())
        lean._fixture(root, batch=["BG0101"], ci_runs={"source": "gh run list", "runs": []},
                      report_gate_clear=["BG0101"])     # delivered, as PREPARE froze it
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0101-x.md").write_text(
            "# BG0101: x\n\n> **Status:** In Progress\n> **Severity:** Medium\n"
            "> **Points:** 1\n", encoding="utf-8")
        _raise_in_run(bugs / "BG0101-x.md", "2026-09-23T00:10:00Z")
        sr = lean._live("sprint_report")
        before = sr.build_report(root, RETRO, as_of="2026-09-23T12:00:00Z", findings_rule=False)
        self.assertTrue(self._scan(before).startswith("1 open finding(s)"),
                        "premise: the old scan lists it")
        self.assertNotIn(sr.FINDINGS_RULE, before)
        check = sr.revalidate(root, sr.file_report(root, before))
        self.assertTrue(check["valid"], check["changes"])
        after = sr.build_report(root, RETRO, as_of="2026-09-23T12:00:00Z")
        self.assertTrue(self._scan(after).startswith("0 open finding(s)"), self._scan(after))
        self.assertEqual(sr.FINDINGS_BATCH_EXCLUDED, after.get(sr.FINDINGS_RULE))
        check = sr.revalidate(root, sr.file_report(root, after))
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
