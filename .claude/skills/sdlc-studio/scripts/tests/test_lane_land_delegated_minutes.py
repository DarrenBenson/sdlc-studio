"""`sprint lane land` records each landed unit's minutes from its builder's transcript.

The land prices each unit's return from the builder's own transcript, split by points between
the lane's units. It now records the builder's minutes beside those tokens, taken from the
transcript's first and last message times and split by points as the tokens are, so a unit
whose repair round was landed too reads its minutes rather than NOT MEASURED on the report the
close files. Every case drives `sprint.py lane land` through its entry point against the
throwaway repository of `test_lane_land`, with HOME, CLAUDE_CONFIG_DIR and XDG_DATA_HOME on a
temporary harness store, never the operator's; the report is built by `sprint_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import importlib
import json
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_land as base  # noqa: E402

A, B, LANE, meter = base.A, base.B, base.LANE, base.meter
run_state = base.run_state
RETRO = "RETRO0001"
#: when each builder's first message was written
T0 = datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 11, 20, 11, 0, tzinfo=timezone.utc)
REJECT = ("VERDICT: REJECT\nISSUES: [new] a is not two enough\n"
          "BLOCKING: [new] a is not two enough\n")


class LaneLandRecordsMinutesTests(base._PricedFixture):
    """BG1629: a landed unit's minutes come from its builder's transcript."""

    REPAIRER = "0fedcba98765"

    def setUp(self) -> None:
        super().setUp()
        retros = self.root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-a-sprint.md").write_text(
            f"# {RETRO}: a sprint\n\n> **Batch:** {A}, {B}\n", encoding="utf-8")

    def _builder_works(self, agent: str, wt: Path, start: datetime, minutes: int) -> None:
        """Builder `agent` writes two messages in `wt`, `minutes` apart from `start`."""
        lines = [*self.tx._records(f"msg_{agent}_0", base.BUILD_1, start, str(wt)),
                 *self.tx._records(f"msg_{agent}_1", base.BUILD_2,
                                   start + timedelta(minutes=minutes), str(wt))]
        meter._Transcripts._append(self.tx.subagents / f"agent-{agent}.jsonl", lines)

    def _minutes_are(self, expected: list[float], recs: list[dict]) -> None:
        """Each record's minutes, to the second: the fixture's messages are written a
        millisecond apart per content block, so a span reads a few milliseconds long."""
        got = [rec.get("minutes") for rec in recs]
        self.assertEqual(len(expected), len(got), got)
        for want, have in zip(expected, got):
            self.assertIsNotNone(have, got)
            self.assertAlmostEqual(want, have, delta=1 / 60, msg=got)

    def _minutes_cell(self, unit: str) -> dict:
        """The unit's Minutes cell on the report the close files."""
        sr = importlib.import_module("sprint_report")
        rep = sr.build_report(self.root, RETRO)
        section = next(s for s in rep["sections"] if s["key"] == "estimates")
        rows = {r["unit_id"]["value"]: r for r in section["unit_rows"]}
        return rows[unit]["eu_minutes"]

    def _reject(self, unit: str) -> None:
        verdict = Path(self._tmp.name) / f"{unit}-reject.txt"
        verdict.write_text(REJECT, encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-B", str(base.SPRINT), "lane", "accept", "--unit", unit,
             "--verdict", str(verdict), "--reviewer", f"qa-seat-{unit}-r1",
             "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root), env=self._env(),
            check=False)
        self.assertEqual(1, done.returncode, done.stdout + done.stderr)
        self.assertIn("REJECT recorded", done.stdout)

    def test_a_repaired_unit_reads_both_builders_minutes(self) -> None:
        """Round one's builder works 20 minutes, the REJECT is recorded, the repair's builder
        works 10 more in a fresh worktree, and both landings record their builder's minutes,
        so the unit reads 30 agent minutes. MUTANT: the land passes no minutes, as it did, so
        the cell reads NOT MEASURED with `0 of its 2 tagged agent(s) reported minutes`."""
        self._builder_works(self.AGENT, self.wt, T0, 20)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self._minutes_are([20.0], self._returns())
        self.assertIn("20.0 minutes", r.stdout)
        self._reject(A)
        repair = Path(self._tmp.name).resolve() / f"agent-{self.REPAIRER}"
        gitutil.git(["worktree", "add", "-q", "-b", "repair-us0101", str(repair), "main"],
                    self.root)
        self._builder_works(self.REPAIRER, repair, T1, 10)
        first, self.wt = self.wt, repair
        try:
            self._stage("src/a.py", "A = 22\n")
            self._hand_in(message=f"fix({A}): a is two enough")
            r = self._land(A)
        finally:
            self.wt = first
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self._minutes_are([20.0, 10.0], self._returns())
        cell = self._minutes_cell(A)
        self.assertEqual(30.0, cell["value"], json.dumps(cell))
        self.assertEqual("agent minutes", cell.get("label"))

    def test_a_lane_of_two_units_splits_its_minutes_by_points(self) -> None:
        """One 20-minute transcript for a lane of two 2-point units: each unit reads 10 minutes,
        marked split. MUTANT: the whole 20 minutes given to each unit."""
        self._builder_works(self.AGENT, self.wt, T0, 20)
        for rel, body in (("src/a.py", "A = 2\n"), (f"changelog.d/{A}.md", "a is two\n"),
                          ("src/b.py", "B = 2\n"), (f"changelog.d/{B}.md", "b is two\n")):
            self._stage(rel, body)
        self._hand_in(units=(A, B), message=f"feat({A}): a and b are two")
        r = self._land(A, B)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        for unit in (A, B):
            with self.subTest(unit=unit):
                self._minutes_are([10.0], self._returns(unit))
                cell = self._minutes_cell(unit)
                self.assertEqual((10.0, "agent minutes, split by points"),
                                 (cell["value"], cell.get("label")))

    def test_a_transcript_with_no_times_records_tokens_and_says_so(self) -> None:
        """A transcript whose messages carry no timestamp gives no span: the tokens are still
        recorded, no minutes are invented, and the land says why. MUTANT: a missing time read
        as 0, which the record refuses, so the unit is left unpriced."""
        self._builder_says(base.BUILD_1, base.BUILD_2)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        recs = self._returns()
        self.assertEqual(1, len(recs), r.stdout + r.stderr)
        self.assertNotIn("minutes", recs[0])
        self.assertIn("no minutes", r.stdout)


if __name__ == "__main__":
    unittest.main()
