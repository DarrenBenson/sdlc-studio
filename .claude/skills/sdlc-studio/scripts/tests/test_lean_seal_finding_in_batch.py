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

import json
import os
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

    def __init__(self, d: str, outside: bool = False) -> None:
        super().__init__(d)
        self.outside = outside

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

    def test_a_page_filed_before_the_fix_re_derives_as_signed(self) -> None:
        """RPT0013 listed a batch finding. MUTANTS: apply the rule to a page that carries no
        mark of it, so RPT0013 reads INVALIDATED; leave the mark off a new page."""
        root = Path(self._tmpdir())
        lean._fixture(root, batch=["BG0101"], ci_runs={"source": "gh run list", "runs": []})
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
