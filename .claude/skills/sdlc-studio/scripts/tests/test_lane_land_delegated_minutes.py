"""`sprint lane land` records each landed unit's minutes from its builder's transcript.

The land prices each unit's return from the builder's own transcript, split by points between
the lane's units. It now records the builder's minutes beside those tokens, taken from the
transcript's first and last message times and split by points as the tokens are, so a unit
whose repair round was landed too reads its minutes rather than NOT MEASURED on the report the
close files. A `lane return` or `lane accept --agent` that prices the transcript again reads
its minutes the same way, so it keeps the minutes the land recorded. The cases drive `sprint.py
lane land`, `lane return` and `lane accept` through their entry point against the throwaway
repository of `test_lane_land`, with HOME, CLAUDE_CONFIG_DIR and XDG_DATA_HOME on a temporary
harness store, never the operator's, and the report is built by `sprint_report`; two cases call
`sprint._lane_transcript_minutes` on a transcript file directly, for the lines it passes over
and the files it cannot read.
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
import loader  # noqa: E402
import test_lane_land as base  # noqa: E402

A, B, LANE, meter = base.A, base.B, base.LANE, base.meter
run_state = base.run_state
RETRO = "RETRO0001"
#: when each builder's first message was written
T0 = datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 11, 20, 11, 0, tzinfo=timezone.utc)
REJECT = ("VERDICT: REJECT\nISSUES: [new] a is not two enough\n"
          "BLOCKING: [new] a is not two enough\n")


def _sprint():
    """The sprint script, loaded once, for the function the land reads minutes with."""
    return loader.load_script("sprint")


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

    def _land_round_and_repair(self) -> None:
        """Round one's builder works 20 minutes and lands, the REJECT is recorded, and the
        repair's builder works 10 more in a fresh worktree and lands."""
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

    def test_a_repaired_unit_reads_both_builders_minutes(self) -> None:
        """Both landings record their builder's minutes, so the unit reads 30 agent minutes.
        MUTANT: the land passes no minutes, as it did, so the cell reads NOT MEASURED with `0
        of its 2 tagged agent(s) reported minutes`."""
        self._land_round_and_repair()
        self._minutes_are([20.0, 10.0], self._returns())
        cell = self._minutes_cell(A)
        self.assertEqual(30.0, cell["value"], json.dumps(cell))
        self.assertEqual("agent minutes", cell.get("label"))

    def _approve(self, unit: str, *extra: str) -> subprocess.CompletedProcess:
        """`sprint.py lane accept` of the round-1 reviewer's APPROVE for `unit`, `extra` handed
        through to the return it ends with."""
        verdict = Path(self._tmp.name) / f"{unit}-approve.txt"
        verdict.write_text("VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n", encoding="utf-8")
        return self._sprint("lane", "accept", "--unit", unit, "--verdict", str(verdict),
                            "--reviewer", f"qa-seat-{unit}-r1", *extra)

    def _sprint(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(base.SPRINT), *args, "--root", str(self.root)],
            capture_output=True, text=True, timeout=600, cwd=str(self.root), env=self._env(),
            check=False)

    def test_the_documented_approve_naming_the_repairer_keeps_both_minutes(self) -> None:
        """The APPROVE accepted with `--agent <the repair's builder>`, as help/sprint.md
        documents, prices that builder's transcript again and reads its minutes with it, so
        the unit still reads 30 agent minutes. MUTANT: minutes read only by the land, as they
        were, so the accept's record replaces the repair's 10 minutes with none and the cell
        reads 20.0."""
        self._land_round_and_repair()
        done = self._approve(A, "--agent", self.REPAIRER)
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        self._minutes_are([20.0, 10.0], self._returns())
        self.assertEqual(30.0, self._minutes_cell(A)["value"])

    def test_a_return_after_the_land_reads_the_transcripts_minutes(self) -> None:
        """A unit landed once and then returned with `lane return --agent <builder>` keeps its
        minutes: the return reads them from the transcript it prices. MUTANT: minutes read only
        by the land, so the cell reads NOT MEASURED, `0 of its 1 tagged agent(s)`."""
        self._builder_works(self.AGENT, self.wt, T0, 20)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        back = self._sprint("lane", "return", "--units", A, "--agent", self.AGENT)
        self._minutes_are([20.0], self._returns())
        self.assertEqual(20.0, self._minutes_cell(A)["value"], back.stdout + back.stderr)

    def test_a_return_of_a_transcript_with_no_times_records_tokens_and_says_nothing(self) -> None:
        """A return reading a transcript whose messages carry no time records its tokens and no
        minutes, and says nothing of them, as before it read the span: only the land, where no
        --minutes can be given, says why. MUTANT: the land's warning printed by every return."""
        self._builder_says(base.BUILD_1, base.BUILD_2)
        back = self._sprint("lane", "return", "--units", A, "--agent", self.AGENT)
        self.assertEqual(0, back.returncode, back.stdout + back.stderr)
        recs = self._returns()
        self.assertEqual(1, len(recs), back.stdout + back.stderr)
        self.assertNotIn("minutes", recs[0])
        self.assertNotIn("no minutes were recorded", back.stdout + back.stderr)

    def test_minutes_a_return_supplies_are_recorded_over_the_transcripts_span(self) -> None:
        """`--minutes` given beside `--agent` is the figure recorded, not the transcript's span.
        MUTANT: the span read whatever --minutes says, so the 20-minute span is recorded."""
        self._builder_works(self.AGENT, self.wt, T0, 20)
        back = self._sprint("lane", "return", "--units", A, "--agent", self.AGENT,
                            "--minutes", "7")
        recs = self._returns()
        self.assertEqual(1, len(recs), back.stdout + back.stderr)
        self.assertEqual(7.0, recs[0].get("minutes"))

    def test_a_transcript_whose_times_do_not_move_records_tokens_and_no_minutes(self) -> None:
        """Every message of the transcript carries one time, so it spans nothing: the tokens are
        recorded, no minutes, and the land says why. MUTANT: a span of equal times read as 0.0
        minutes, which the record refuses as not a positive number, so the unit's tokens go
        unrecorded too."""
        lines = [*self.tx._records("msg_same_0", base.BUILD_1, T0, str(self.wt)),
                 *self.tx._records("msg_same_1", base.BUILD_2, T0, str(self.wt))]
        stamp = T0.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        lines = [json.dumps({**json.loads(ln), "timestamp": stamp}) for ln in lines]
        meter._Transcripts._append(self.builder, lines)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        recs = self._returns()
        self.assertEqual(1, len(recs), r.stdout + r.stderr)
        self.assertEqual(meter._tokens(meter._sum(base.BUILD_1, base.BUILD_2)), recs[0]["tokens"])
        self.assertNotIn("minutes", recs[0])
        self.assertIn("carries 6 message time(s) and no span between a first and a last",
                      r.stdout + r.stderr)

    def _span(self, *lines: str | bytes) -> tuple:
        """`sprint._lane_transcript_minutes` of a transcript holding `lines`."""
        path = Path(self._tmp.name) / "transcript.jsonl"
        path.write_bytes(b"\n".join(ln if isinstance(ln, bytes) else ln.encode("utf-8")
                                    for ln in lines) + b"\n")
        return _sprint()._lane_transcript_minutes(path), path

    def test_a_line_that_is_not_json_or_not_an_object_is_passed_over(self) -> None:
        """A line that is not JSON, and one that is JSON but not an object, are passed over and
        the times either side still span 20 minutes. MUTANTS: the JSON error re-raised; the
        object guard dropped, so `.get` is called on a list."""
        first = json.dumps({"timestamp": "2026-11-20T09:00:00.000Z"})
        last = json.dumps({"timestamp": "2026-11-20T09:20:00.000Z"})
        for odd in ("{not json", "[1, 2]", '"a string"'):
            with self.subTest(line=odd):
                (minutes, why), _path = self._span(first, odd, last)
                self.assertEqual((20.0, ""), (minutes, why))

    def test_a_transcript_that_cannot_be_read_gives_its_reason(self) -> None:
        """A transcript that is not UTF-8, or is gone, gives no minutes and says why, rather
        than raising. MUTANT: the read error raised, so the land stops on it."""
        (minutes, why), path = self._span(b"\xff\xfe not utf-8", b"\x80")
        self.assertIsNone(minutes)
        self.assertIn(f"the transcript {path} cannot be read for its message times", why)
        path.unlink()
        minutes, why = _sprint()._lane_transcript_minutes(path)
        self.assertIsNone(minutes)
        self.assertIn("cannot be read for its message times", why)

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
