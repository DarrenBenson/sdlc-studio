"""US1092: the retro's accuracy block and its VELOCITY row carry the priced cost per point under a
named basis, and the forecast names every basis it pooled.

The meter's headline basis changed twice in one run: once per message, then the subagent
transcripts read beside the main thread. A VELOCITY row whose Source said only `harness` could
not tell its basis from an earlier row's, so `sprint.tokens_per_point` pooled rows on different
bases into one rate and called it one figure.

Pinned here: the accuracy block states the priced total and each component on its own line; the
row's Priced/pt cell is a whole number of priced input-equivalent tokens per delivered point,
written `3,846` and read back as an int, under a Source naming the capture's counting basis;
every earlier row keeps its cells; and the rate's basis names every Source among the rows it
pooled.

Run from the repo root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_basis.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_meter_reads_true as meter  # noqa: E402 - the harness transcript fixture, shared

RETRO = "RETRO0003"
UNITS = meter.UNITS            # two stories of 2 points each: 4 delivered points
NEW_BASIS = "harness (main thread and subagents, once per message)"
#: How a page names each component, typed here rather than read from the code under test.
NAMES = {"input": "input", "output": "output", "cache_write_5m": "cache write 5m",
         "cache_write_1h": "cache write 1h", "cache_read": "cache read"}

#: The header VELOCITY.md carried before the Priced/pt column, as the live file still does.
OLD_HEADER = ("| Retro | Date | Units | Measured | Forecast | Points | Written | Estimate (tokens, "
              "plan-time) | Actual (tokens) | Ratio (est/actual) | Tokens/pt | Oversized | Wall "
              "(s) | Overhead | Overhead bound | Constants | Sample | Model | Note | Source |")
#: Two rows recorded on the earlier basis, with the Source every such row carries.
EARLIER = {
    "RETRO0001": "| RETRO0001 | 2026-10-01 | 3 | 0 | 0 | 10 | - | - | 1,500,000 | - | 150,000 | "
                 "0 | - | - | - | - | out-of-sample | claude-opus-5-5 | - | harness |",
    "RETRO0002": "| RETRO0002 | 2026-10-02 | 4 | 0 | 0 | 10 | - | - | 2,000,000 | - | 200,000 | "
                 "0 | - | - | - | - | out-of-sample | claude-opus-5-5 | - | harness |",
}


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


class _Fixture(unittest.TestCase):
    """Two Done stories, a retro over them, the earlier VELOCITY rows, and an open build run
    whose meter reads a transcript directory with a subagent beside the main thread."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.rs = meter._live("lib.run_state")
        self.retro, self.sprint = meter._live("retro"), meter._live("sprint")
        self.root = Path(tmp.name) / "repo"
        self.tx = meter._Transcripts(Path(tmp.name) / "transcripts")
        env = unittest.mock.patch.dict(os.environ, {self.rs.TRANSCRIPTS_ENV: str(self.tx.dir)})
        env.start()
        self.addCleanup(env.stop)
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in UNITS:
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Done\n> **Points:** 2\n", encoding="utf-8")
        retros = self.root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        self.page = retros / f"{RETRO}-priced.md"
        self.page.write_text(f"# RETRO-0003: priced\n\n> **Batch:** {', '.join(UNITS)}\n",
                             encoding="utf-8")
        (retros / "VELOCITY.md").write_text(
            "# Velocity history\n\n" + OLD_HEADER + "\n" + "| --- " * 20 + "|\n"
            + "\n".join(EARLIER.values()) + "\n", encoding="utf-8")

    def run_meter(self, agents: bool = True, goal: str = "done") -> dict:
        """The meter before the open, the open, the work, and the report stamp. Returns the
        components the run spent."""
        self.tx.main_says("msg_main_1", meter.MAIN_1)
        if agents:      # without, the session has no subagents directory at all
            self.tx.agent_says("a1", "msg_agent_a", meter.AGENT_A)
        self.rs.open_run(self.root, batch=list(UNITS), goal=goal)
        self.tx.main_says("msg_main_2", meter.MAIN_2)
        if agents:
            self.tx.agent_says("b2", "msg_agent_b", meter.AGENT_B, depth=2)
        self.rs.stamp_tokens(self.root, "report")
        return meter._sum(meter.MAIN_2, meter.AGENT_B) if agents else meter._parts(meter.MAIN_2)

    def accuracy(self, *extra: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = self.retro.main(["--root", str(self.root), "accuracy", "--id", RETRO,
                                  "--write", *extra])
        self.assertEqual(0, rc, out.getvalue())
        return out.getvalue()

    def block(self) -> list[str]:
        """The accuracy block's lines, and only its lines."""
        text = self.page.read_text(encoding="utf-8")
        inner = text.split(self.retro.ACCURACY_BEGIN, 1)[1].split(self.retro.ACCURACY_END, 1)[0]
        return inner.splitlines()

    def rows(self) -> dict[str, dict[str, str]]:
        """VELOCITY.md's rows by retro id, each cell under its header's name."""
        lines = (self.root / "sdlc-studio" / "retros" / "VELOCITY.md").read_text(
            encoding="utf-8").splitlines()
        header = next(_cells(line) for line in lines if line.startswith("| Retro |"))
        return {c[0]: dict(zip(header, c)) for line in lines
                if line.startswith("| RETRO") and (c := _cells(line))}


class VelocityPricedBasisTests(_Fixture):
    def test_accuracy_writes_components_priced_per_point_and_the_basis(self) -> None:
        """AC1. MUTANTS: the row's Source left as `harness` (`harness_source` returning its
        kind), so two bases pool into one rate unnamed; an earlier row rewritten under the new
        definition (its Source relabelled, or a Priced/pt computed for it); the components
        emitted only in JSON and never on the page (`_priced_lines` dropped from
        `_points_lines`); the per-point figure taken from the input + output + cache-write sum
        rather than the priced total; the rate's basis not naming the Sources it pooled."""
        comps = self.run_meter()
        spent, priced = meter._tokens(comps), meter._priced(comps)
        per_point = round(priced / 4)
        self.assertNotEqual(round(spent / 4), per_point, "the fixture tells the two apart")
        self.accuracy("--tokens-from-harness")

        block = self.block()
        head = (f"**Priced cost: {priced:,} priced input-equivalent tokens**, {per_point:,} per "
                f"point over 4 delivered points. Read once per message from the main thread and "
                f"every subagent transcript.")
        self.assertTrue(any(line.startswith(head) for line in block), block)
        for c in meter.COMPONENTS:
            self.assertIn(f"- {NAMES[c]}: {comps[c]:,} x{meter.WEIGHTS[c]:g}", block)

        rows = self.rows()
        new = rows[RETRO]
        self.assertEqual(f"{per_point:,}", new["Priced/pt"])
        self.assertEqual(NEW_BASIS, new["Source"])
        self.assertEqual(f"{spent:,}", new["Actual (tokens)"])
        read = next(r for r in self.retro.velocity_history(self.root) if r["id"] == RETRO)
        self.assertEqual(per_point, read["priced_per_point"])
        self.assertIs(int, type(read["priced_per_point"]))

        for rid, line in EARLIER.items():
            with self.subTest(earlier=rid):
                self.assertEqual(dict(zip(_cells(OLD_HEADER), _cells(line))),
                                 {k: v for k, v in rows[rid].items() if k != "Priced/pt"})
                self.assertEqual("-", rows[rid]["Priced/pt"])

        rate = self.sprint.tokens_per_point(self.root)
        self.assertEqual(["RETRO0001", "RETRO0002", RETRO], rate["ids"])
        self.assertEqual(["harness", NEW_BASIS], rate["sources"])
        self.assertIn(f"It pooled rows under 2 Sources (`harness`; `{NEW_BASIS}`), so it is a "
                      f"rate across them, not one figure", rate["basis"])

    def test_one_source_is_named_as_the_only_one(self) -> None:
        """The positive control. MUTANT: every rate called pooled across Sources."""
        rate = self.sprint.tokens_per_point(self.root)
        self.assertEqual(["RETRO0001", "RETRO0002"], rate["ids"])
        self.assertIn("Every row it pooled has the Source `harness`.", rate["basis"])
        self.assertNotIn("not one figure", rate["basis"])


class PricedCellLifecycleTests(_Fixture):
    def test_a_reused_capture_keeps_its_priced_cell_and_the_block_says_why(self) -> None:
        """MUTANTS: the reused row's Priced/pt dropped; its Source relabelled; the block
        silent about why it states no priced figure."""
        self.run_meter()
        self.accuracy("--tokens-from-harness")
        first = self.rows()[RETRO]
        self.accuracy("--tokens-from-harness")
        again = self.rows()[RETRO]
        self.assertEqual(first, again)
        self.assertTrue(any(line.startswith("**Priced cost: not stated.** the token actual "
                                            "already recorded was reused")
                            for line in self.block()))

    def test_a_typed_total_drops_the_priced_cell(self) -> None:
        """MUTANT: a priced figure kept beside a figure it was not formed from."""
        self.run_meter()
        self.accuracy("--tokens-from-harness")
        self.accuracy("--tokens", "900000")
        row = self.rows()[RETRO]
        self.assertEqual(("900,000", "supplied", "-"),
                         (row["Actual (tokens)"], row["Source"], row["Priced/pt"]))

    def test_a_main_thread_reading_names_its_own_basis(self) -> None:
        """MUTANTS: every once-per-message capture labelled as holding the subagents; the
        harness+supplied kind left unqualified; a supplied delegated total priced into the
        figure, or not said to be outside it."""
        comps = self.run_meter(agents=False)
        self.accuracy("--delegated-tokens", "250000", "--delegated-agent", "builder",
                      "--tokens-from-harness")
        row = self.rows()[RETRO]
        self.assertEqual("harness+supplied (main thread, once per message)", row["Source"])
        self.assertEqual(f"{meter._tokens(comps) + 250_000:,}", row["Actual (tokens)"])
        self.assertEqual(f"{round(meter._priced(comps) / 4):,}", row["Priced/pt"])
        head = next(line for line in self.block() if line.startswith("**Priced cost:"))
        self.assertIn("Read once per message from the main thread only, a lower bound", head)
        self.assertTrue(head.endswith(
            "The 250,000 tokens supplied by delegated agents are outside it."), head)

    def test_a_run_short_of_the_build_rung_earns_no_priced_cell(self) -> None:
        """MUTANT: a priced figure per point written for a design run, whose few terminal units
        are not the work it paid for."""
        comps = self.run_meter(goal="design")
        self.accuracy("--tokens-from-harness")
        self.assertEqual("-", self.rows()[RETRO]["Priced/pt"])
        head = next(line for line in self.block() if line.startswith("**Priced cost:"))
        self.assertTrue(head.startswith(
            f"**Priced cost: {meter._priced(comps):,} priced input-equivalent tokens**. No "
            f"per-point figure: the run was driven to the `design` rung, and only a build run "
            f"earns one. Read once per message"), head)

    def test_readings_without_components_state_no_priced_figure(self) -> None:
        """MUTANT: a priced figure of 0, or one formed from `tokens`, for a reading taken before
        the meter priced its components."""
        self.run_meter()
        state = self.rs.read(self.root)
        base = {k: v for k, v in state[self.rs.TOKEN_BASELINE].items() if k != "components"}
        self.rs.update(self.root, **{self.rs.TOKEN_BASELINE: base})
        self.accuracy("--tokens-from-harness")
        row = self.rows()[RETRO]
        self.assertEqual((NEW_BASIS, "-"), (row["Source"], row["Priced/pt"]))
        self.assertTrue(any(line.startswith("**Priced cost: not stated.** 1 meter reading(s) "
                                            "were written before the meter priced")
                            for line in self.block()))


if __name__ == "__main__":
    unittest.main()
