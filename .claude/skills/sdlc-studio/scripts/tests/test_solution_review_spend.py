"""`critic.py approach spend` adds a seat agent's priced spend on a unit's solution review to the
unit's delegated spend in the open run, read from that agent's own transcript, and `approach
panel` names it on each seat's line.

Every case builds the meter's workspace (`test_meter_reads_true`): its harness store and open
run, with US0101 at 3 points under a Persona and US0102 under none, the repository's seat cards,
a persona registry, a panel of three seats and a complete approach note. The builder is priced
through `sprint.py lane return`, and the verbs run through the shipped CLI, `python3 critic.py`,
with the store's env.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace

SKILL = meter.SCRIPTS.parent
REPO = SKILL.parents[2]
CRITIC = meter.SCRIPTS / "critic.py"
CATALOGUE = SKILL / "reference-scripts-review.md"
UNIT, OTHER = meter.UNITS
QA, PRODUCT, PERSONA = "Sam Eriksson (qa)", "Lena Marsh (product)", "Abena Osei (persona)"
AUTHOR = "Dani Okafor (engineering)"
PANEL = "review:\n  solution_review:\n    min_points: 3\n    panel: [qa, product, persona]\n"
STORY = ("# {uid}: x\n\n> **Status:** Ready\n> **Points:** 3\n{persona}\n## Acceptance Criteria"
         "\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n")
NOTE = ("# approach\n\n## Reading\n\nAs written.\n\n## Design\n\nOne function.\n\n"
        "## May break\n\nNothing reads it.\n\n## Tests\n\nAC1 gets a test.\n\n"
        "## Sentences\n\nThe fragment.\n")
CARD = ("# Abena Osei\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
        "| **Cast role** | Primary |\n\n## Who They Are\n\nSomebody who upgrades the tool.\n")

BUILD = meter._usage(40, 400, 5_000, 0, 120_000)
QA_1 = meter._usage(10, 100, 1_000, 0, 20_000)
QA_2 = meter._usage(7, 70, 700, 0, 9_000)        # the qa agent's transcript, grown
PRODUCT_1 = meter._usage(12, 120, 1_200, 0, 30_000)
PERSONA_1 = meter._usage(3, 30, 300, 0, 5_000)
SEAT_NOTE = "solution review ({})"


def _priced(*usages: dict) -> int:
    return meter._priced(meter._sum(*usages))


class SolutionReviewSpendTests(meter._Case):
    def panel_ws(self, verdicts: bool = False) -> meter._Workspace:
        """The meter's workspace under the panel, its run open, the builder priced through
        `lane return`, and, with `verdicts`, each seat's GO recorded on the note."""
        ws = self.workspace()
        root = ws.root
        stories = root / "sdlc-studio" / "stories"
        (stories / f"{UNIT}-x.md").write_text(
            STORY.format(uid=UNIT, persona="> **Persona:** Abena Osei\n"), encoding="utf-8")
        (stories / f"{OTHER}-x.md").write_text(STORY.format(uid=OTHER, persona=""),
                                               encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        for card in sorted((REPO / "sdlc-studio" / "personas" / "seats").glob("*.md")):
            shutil.copy(card, seats / card.name)
        pdir = root / "sdlc-studio" / "personas"
        (pdir / "abena-osei.md").write_text(CARD, encoding="utf-8")
        (pdir / "index.md").write_text("# Personas\n\n## Primary\n\n- [Abena Osei](abena-osei.md)"
                                       " - the lead\n", encoding="utf-8")
        (root / "sdlc-studio" / ".config.yaml").write_text(PANEL, encoding="utf-8")
        (root / "note.md").write_text(NOTE, encoding="utf-8")
        ws.open()
        self.assertIsNotNone(self.rs.record_unit_actual(root, UNIT, self.rs.UNIT_START_STATUS,
                                                        False))
        if verdicts:
            for reviewer in (QA, PRODUCT, PERSONA):
                rc, out, err = self.cli(ws, "approach", "record", "--unit", UNIT, "--verdict",
                                        "go", "--note", str(root / "note.md"), "--reviewer",
                                        reviewer, "--author", AUTHOR)
                self.assertEqual(0, rc, out + err)
        ws.tx.agent_says("builder1", "msg_build", BUILD)
        rc, out = ws.lane("return", "--units", UNIT, "--agent", "builder1")
        self.assertEqual(0, rc, out)
        self.assertNotIn("was not priced", out)
        return ws

    @staticmethod
    def cli(ws: meter._Workspace, *argv: str) -> tuple[int, str, str]:
        """The shipped CLI, in its own interpreter, with the store's env."""
        p = subprocess.run([sys.executable, str(CRITIC), *argv, "--root", str(ws.root)],
                           capture_output=True, text=True, env=dict(os.environ), timeout=120)
        return p.returncode, p.stdout, p.stderr

    def spend(self, ws: meter._Workspace, seat: str, agent: str,
              unit: str = UNIT) -> tuple[int, str, str]:
        return self.cli(ws, "approach", "spend", "--unit", unit, "--seat", seat, "--agent", agent)

    def panel(self, ws: meter._Workspace, unit: str = UNIT) -> tuple[int, str, str]:
        return self.cli(ws, "approach", "panel", "--unit", unit, "--note",
                        str(ws.root / "note.md"))

    def records(self, ws: meter._Workspace) -> list[dict]:
        return list(ws.state().get(self.rs.DELEGATED) or [])

    def seat_records(self, ws: meter._Workspace) -> list[dict]:
        return [r for r in self.records(ws)
                if r.get("unit") == UNIT and r["note"].startswith("solution review (")]

    def write_state(self, ws: meter._Workspace, **fields) -> None:
        state = ws.state()
        state.update(fields)
        self.rs.path(ws.root).write_text(json.dumps(state), encoding="utf-8")

    def assert_nothing(self, run: tuple[int, str, str], rc: int, *words: str) -> None:
        got, out, err = run
        self.assertEqual((rc, ""), (got, out), err)
        self.assertNotIn("Traceback", err)
        for word in words:
            self.assertIn(word, err)

    def test_each_seat_agent_s_spend_is_added_to_the_unit_once(self) -> None:
        """AC1. MUTANTS: `reading=` dropped (no priced figure, and the grown qa reading is
        added beside the first); provenance SUPPLIED; the `agent-` strip removed (`agent-s1`
        reads `agent-agent-s1.jsonl`); the note's seat dropped; `unit=` dropped; `harness=` set."""
        ws = self.panel_ws(verdicts=True)
        ledger = ws.root / "sdlc-studio" / "reviews" / "solution-reviews.md"
        before = ledger.read_bytes()
        actuals = ws.state()[self.rs.UNIT_ACTUALS][UNIT]
        self.assertFalse(actuals.get("open"), actuals)
        for agent, usage in (("q1", QA_1), ("p1", PRODUCT_1), ("s1", PERSONA_1)):
            ws.tx.agent_says(agent, f"msg_{agent}_1", usage)
        outs = {}
        for seat, agent in (("qa", "q1"), ("product", "p1"), ("persona", "agent-s1")):
            rc, outs[seat], err = self.spend(ws, seat, agent)
            self.assertEqual(0, rc, err)
        ws.tx.agent_says("q1", "msg_q1_2", QA_2)
        rc, outs["qa again"], err = self.spend(ws, "qa", "q1")
        self.assertEqual(0, rc, err)
        priced = {"agent-builder1": _priced(BUILD), "agent-q1": _priced(QA_1, QA_2),
                  "agent-p1": _priced(PRODUCT_1), "agent-s1": _priced(PERSONA_1)}
        state = ws.state()
        totals = self.rs.unit_agent_totals(state)[UNIT]
        self.assertEqual(sum(priced.values()), totals["priced"])
        self.assertEqual(4, totals["priced_agents"])
        recs = self.seat_records(ws)
        self.assertEqual(["agent-p1", "agent-s1", "agent-q1"],
                         [r["agent"] for r in recs], "the second qa reading replaced the first")
        for rec, seat in zip(recs, ("product", "persona", "qa")):
            self.assertEqual(self.rs.READ_FROM_TRANSCRIPT, rec["provenance"])
            self.assertEqual(SEAT_NOTE.format(seat), rec["note"])
            self.assertEqual(priced[rec["agent"]], rec["priced"])
            self.assertEqual(f"{rec['agent']}.jsonl", Path(rec["transcript"]).name)
            self.assertNotIn(self.rs.HARNESS, rec)
            self.assertNotIn("minutes", rec)
        self.assertEqual(meter._tokens(meter._sum(QA_1, QA_2)), recs[-1]["tokens"])
        self.assertEqual(4, len(state[self.rs.DELEGATED]))
        self.assertEqual(sum(r["tokens"] for r in state[self.rs.DELEGATED]),
                         self.rs.delegated_total(state))
        self.assertEqual(before, ledger.read_bytes())
        self.assertEqual(actuals, state[self.rs.UNIT_ACTUALS][UNIT])
        for key, seat, agent in (("qa", "qa", "agent-q1"), ("product", "product", "agent-p1"),
                                 ("persona", "persona", "agent-s1"),
                                 ("qa again", "qa", "agent-q1")):
            figure = _priced(QA_1) if key == "qa" else priced[agent]
            self.assertIn(f"recorded {UNIT}'s {seat} seat agent {agent} ", outs[key])
            self.assertIn(f": {figure:,} priced tokens", outs[key])

    def test_an_agent_with_no_readable_transcript_records_nothing(self) -> None:
        """AC2. MUTANTS: the priced-None guard removed; the no-run check removed; the
        transcript read before the no-run check; exit 1 read as 0."""
        ws = self.panel_ws()
        ws.tx.agent_says("p1", "msg_p1_1", PRODUCT_1)
        ws.tx.agent_says("s1", "msg_s1_1", PERSONA_1)
        before = self.records(ws)
        reading = self.rs.agent_transcript_tokens(ws.root, "nobody1")
        self.assertIsNone(reading["priced"])
        self.assert_nothing(self.spend(ws, "product", "nobody1"), 1, "nobody1",
                            reading["searched"])
        self.assertEqual(before, self.records(ws))
        rc, out, err = self.spend(ws, "product", "p1")
        self.assertEqual(0, rc, err)
        self.assertEqual(["agent-p1"], [r["agent"] for r in self.seat_records(ws)])
        self.rs.path(ws.root).unlink()
        run = self.spend(ws, "persona", "nobody1")
        self.assert_nothing(run, 1, "no run is open")
        self.assertNotIn(reading["reason"], run[2])
        self.assert_nothing(self.spend(ws, "persona", "s1"), 1, "no run is open")
        self.assertEqual({}, ws.state())

    def test_the_panel_and_the_catalogue_name_the_spend_command(self) -> None:
        """AC3. MUTANTS: the clause dropped; its seat fixed to `qa`; the clause on the skipped
        lines; a catalogue phrase cut."""
        ws = self.panel_ws()
        rc, out, err = self.panel(ws)
        self.assertEqual(0, rc, err)
        seated = [ln for ln in out.splitlines() if ln.startswith("- ")]
        self.assertEqual(3, len(seated), out)
        for line, seat in zip(seated, ("qa", "product", "persona")):
            self.assertTrue(line.endswith(
                f"; when its agent returns: critic.py approach spend --unit {UNIT} --seat {seat} "
                f"--agent <agent id>"), line)
        rc, out, err = self.panel(ws, OTHER)
        self.assertEqual(0, rc, err)
        lines = [ln for ln in out.splitlines() if ln.startswith("- ")]
        [skipped] = [ln for ln in lines if ln.startswith("- persona is skipped: ")]
        self.assertNotIn("approach spend", skipped)
        self.assertEqual([f"critic.py approach spend --unit {OTHER} --seat {s} --agent <agent id>"
                          for s in ("qa", "product")],
                         [ln.split("; when its agent returns: ")[1] for ln in lines
                          if ln is not skipped])
        (ws.root / "sdlc-studio" / ".config.yaml").write_text(
            PANEL.replace("[qa, product, persona]", "[]"), encoding="utf-8")
        rc, out, err = self.panel(ws)
        self.assertEqual(0, rc, err)
        self.assertIn("is unset, so one seat's GO", out)
        self.assertNotIn("approach spend", out)
        [para] = [p for p in CATALOGUE.read_text(encoding="utf-8").split("\n\n")
                  if p.startswith("`approach spend --unit <id> --seat <role> --agent <id>`")]
        for phrase in ("reads that seat agent's own transcript", "no verdict row", "not checked against the panel",
                       "refuses the builder's own transcript", "no run is open"):
            self.assertIn(phrase, para)
        p = subprocess.run([sys.executable, str(meter.SCRIPTS / "docgen.py"), "surface",
                            "--check", "--root", str(REPO)], capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)

    def test_a_sealed_run_records_nothing(self) -> None:
        """A run sealed, then one whose page is filed: the record's WARNING, exit 1, nothing on
        stdout. MUTANTS: the None return dropped (the recorded line printed); exit 1 read as 0."""
        ws = self.panel_ws()
        ws.tx.agent_says("q1", "msg_q1_1", QA_1)
        state = ws.state()
        said = f"{UNIT}'s qa seat agent's spend was not recorded"
        for outcome, report, why in (("achieved", None, "is sealed"),
                                     (self.rs.RUNNING, "RPT0001", "is filed")):
            self.write_state(ws, outcome=outcome, report=report)
            run = self.spend(ws, "qa", "q1")
            self.assert_nothing(run, 1, "WARNING", why, said)
            self.assertNotIn(f"recorded {UNIT}'s", run[2])
        after = ws.state()
        for key in (self.rs.DELEGATED, self.rs.UNIT_ACTUALS):
            self.assertEqual(json.dumps(state[key]), json.dumps(after[key]))

    def test_an_off_panel_seat_is_recorded_as_given(self) -> None:
        """A seat the panel does not name is recorded as typed, stripped; the same agent run
        again under the right seat replaces it. MUTANT: the seat lower-cased or checked."""
        ws = self.panel_ws()
        ws.tx.agent_says("q1", "msg_q1_1", QA_1)
        for seat, noted in (("qq", "qq"), (" Lead QA ", "Lead QA"), ("qa", "qa")):
            rc, out, err = self.spend(ws, seat, "q1")
            self.assertEqual(0, rc, err)
            self.assertEqual([SEAT_NOTE.format(noted)], [r["note"] for r in self.seat_records(ws)])

    def test_the_builder_s_own_agent_is_refused(self) -> None:
        """The builder's transcript, already the unit's, is refused and its record kept; a seat
        record of the same transcript is still replaced. MUTANTS: the guard removed; its note
        test inverted."""
        ws = self.panel_ws()
        [builder] = self.records(ws)
        self.assertTrue(builder["note"].startswith("sprint lane return ("), builder)
        for agent in ("builder1", "agent-builder1"):
            self.assert_nothing(self.spend(ws, "qa", agent), 2, "approach spend refused",
                                "agent-builder1", UNIT, builder["note"])
        self.assertEqual([builder], self.records(ws))
        ws.tx.agent_says("q1", "msg_q1_1", QA_1)
        for _ in range(2):
            rc, out, err = self.spend(ws, "qa", "q1")
            self.assertEqual(0, rc, err)
        self.assertEqual([builder["agent"], "agent-q1"], [r["agent"] for r in self.records(ws)])
        rc, out, err = self.spend(ws, "qa", "builder1", unit=OTHER)
        self.assertEqual(0, rc, err)
        self.assertEqual([(UNIT, builder["note"]), (UNIT, SEAT_NOTE.format("qa")),
                          (OTHER, SEAT_NOTE.format("qa"))],
                         [(r["unit"], r["note"]) for r in self.records(ws)],
                         "only a record against the unit itself is kept from replacement")

    def test_refused_and_unreadable_inputs_record_nothing(self) -> None:
        """A blank seat and an unknown unit exit 2; a reading the record refuses and an
        unreadable run state exit 1; an id holding `agent` but not as its prefix is read as
        given. Nothing is recorded by any refusal."""
        ws = self.panel_ws()
        ws.tx.agent_says("q1", "msg_q1_1", QA_1)
        before = self.records(ws)
        self.assert_nothing(self.spend(ws, "  ", "q1"), 2, "approach spend refused", "seat")
        self.assert_nothing(self.spend(ws, "qa", "q1", unit="US0999"), 2,
                            "approach spend refused", "US0999")
        self.assertEqual(before, self.records(ws))
        self.write_state(ws, **{self.rs.DELEGATED: [*before, "junk"]})
        for agent in ("xagent-7", "agentx9"):
            ws.tx.agent_says(agent, f"msg_{agent}", QA_1)
            rc, out, err = self.spend(ws, "qa", agent)
            self.assertEqual(0, rc, err)
            [rec] = [r for r in self.records(ws) if r["agent"] == f"agent-{agent}"]
            self.assertEqual(f"agent-{agent}.jsonl", Path(rec["transcript"]).name)
        self.rs.path(ws.root).write_text("{not json", encoding="utf-8")
        self.assert_nothing(self.spend(ws, "qa", "q1"), 1, "not valid JSON")
        self.assertEqual("{not json", self.rs.path(ws.root).read_text(encoding="utf-8"))

    def test_a_reading_the_record_refuses_records_nothing(self) -> None:
        """A reading of no positive total, which the record refuses, exits 1 naming why, and is
        never read as a refused input. The fixture's reader gives no such reading (a transcript
        of cache reads alone carries no usage records), so the reading is stood in, in-process.
        MUTANT: the record's refusal let through to the verb's exit 2."""
        import critic  # noqa: PLC0415 - in-process, so the reader can be stood in
        ws = self.panel_ws()
        before = self.records(ws)
        source = str(ws.tx.subagents / "agent-c1.jsonl")
        reading = {"tokens": 0, "priced": 5_000, "source": source,
                   "components": {c: 0 for c in meter.COMPONENTS}}
        err = io.StringIO()
        with unittest.mock.patch.object(critic.run_state, "agent_transcript_tokens",
                                        return_value=reading), \
                contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(err):
            rc = critic.main(["approach", "spend", "--unit", UNIT, "--seat", "qa", "--agent",
                              "c1", "--root", str(ws.root)])
        self.assertEqual((1, ""), (rc, out.getvalue()), err.getvalue())
        self.assertIn("positive integer", err.getvalue())
        self.assertEqual(before, self.records(ws))


if __name__ == "__main__":
    unittest.main()
