"""US1091: the token meter reads the main thread and every subagent transcript once per message,
prices each component from one weight table, and the close and the report state that priced cost
as their headline (CR0651, D0390).

The harness writes a session's subagent transcripts beside the session's own file, under
`<session-id>/subagents/agent-*.jsonl`, a depth-2 agent in the same flat directory, and each
file repeats a message's usage on every record of it as the main thread's does. The meter read
the main thread alone, so a run that delegated its work published a fraction of its cost, and it
left the cache reads out, which are most of what a run is billed.

Pinned here, one class per criterion's Verify line:

* the reading carries input, output, cache write at 5 minutes and at 1 hour, and cache read,
  once per `message.id`, split into main thread and subagents (AC1);
* `priced` weighs each component from `run_state.TOKEN_WEIGHTS`, read when it is formed, and
  the report's Estimates and the close report state it first, labelled, with the
  input + output + cache-write sum beside it (AC2);
* the run total carries the priced delta and each component's delta, and a run whose stamps
  carry no priced figure reports `priced` None with a reason (AC3);
* a supplied builder total is not added over a reading that holds the subagents, and is still
  added over one that does not (AC4);
* a reading taken on an earlier counting basis is re-derived from the transcript up to its own
  time, never subtracted from, or summed with, one on the current basis (US1097 AC1).

Every fixture is a throwaway transcript directory in the harness's layout. Run from the repo
root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

SESSION = "5e5510n-0000-4000-8000-000000000001"
RETRO = "RETRO0001"
UNITS = ("US0101", "US0102")
MODEL = "claude-opus-5-5"
T0 = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)

#: D0390's table, typed here and nowhere in the code under test: the test checks the shipped
#: table against it, then prices the fixture with these numbers.
WEIGHTS = {"input": 1, "cache_write_5m": 1.25, "cache_write_1h": 2.0, "cache_read": 0.1,
           "output": 5}
COMPONENTS = ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read")


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _iso(at: datetime) -> str:
    return at.isoformat().replace("+00:00", "Z")


def _usage(inp: int, out: int, five: int, hour: int, read: int) -> dict:
    """One message's usage in the harness's shape: the cache write is stated in total and split
    by duration under `cache_creation`."""
    return {"input_tokens": inp, "output_tokens": out,
            "cache_creation_input_tokens": five + hour,
            "cache_creation": {"ephemeral_5m_input_tokens": five,
                               "ephemeral_1h_input_tokens": hour},
            "cache_read_input_tokens": read}


def _parts(usage: dict) -> dict:
    split = usage["cache_creation"]
    return {"input": usage["input_tokens"], "output": usage["output_tokens"],
            "cache_write_5m": split["ephemeral_5m_input_tokens"],
            "cache_write_1h": split["ephemeral_1h_input_tokens"],
            "cache_read": usage["cache_read_input_tokens"]}


def _sum(*usages: dict) -> dict:
    return {c: sum(_parts(u)[c] for u in usages) for c in COMPONENTS}


def _tokens(parts: dict) -> int:
    return parts["input"] + parts["output"] + parts["cache_write_5m"] + parts["cache_write_1h"]


def _priced(parts: dict) -> int:
    return round(sum(parts[c] * WEIGHTS[c] for c in COMPONENTS))


#: The main thread writes the one-hour cache and the subagents the five-minute one, as this
#: project's transcripts do, so a reader folding one duration into the other moves the price.
MAIN_1 = _usage(10, 100, 0, 1_000, 50_000)
MAIN_2 = _usage(30, 300, 0, 2_000, 80_000)
AGENT_A = _usage(20, 200, 3_000, 0, 70_000)
AGENT_B = _usage(5, 40, 600, 0, 9_000)       # the depth-2 agent, run in a worktree


class _Transcripts:
    """A harness transcript directory: the session's own file and its subagents beside it."""

    def __init__(self, d: Path) -> None:
        self.dir = d
        d.mkdir(parents=True, exist_ok=True)
        self.main = d / f"{SESSION}.jsonl"
        self.subagents = d / SESSION / "subagents"

    @staticmethod
    def _records(msg_id: str, usage: dict, at: datetime | None, cwd: str) -> list[str]:
        """One assistant message as the harness writes it: one record per content block, each
        repeating the message's full usage under the same id."""
        out = []
        for n, block in enumerate(("thinking", "text", "tool_use")):
            rec = {"type": "assistant", "cwd": cwd,
                   "message": {"id": msg_id, "model": MODEL, "role": "assistant",
                               "content": [{"type": block}], "usage": dict(usage)}}
            if at is not None:
                rec["timestamp"] = (at + timedelta(milliseconds=n)).isoformat(
                    timespec="milliseconds").replace("+00:00", "Z")
            out.append(json.dumps(rec))
        return out

    @staticmethod
    def _append(path: Path, lines: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    def main_says(self, msg_id: str, usage: dict, at: datetime | None = None) -> None:
        self._append(self.main, self._records(msg_id, usage, at, "/work/repo"))

    def agent_says(self, agent: str, msg_id: str, usage: dict, at: datetime | None = None,
                   depth: int = 1) -> None:
        cwd = "/work/repo" if depth == 1 else f"/work/repo/.claude/worktrees/agent-{agent}"
        self._append(self.subagents / f"agent-{agent}.jsonl",
                     self._records(msg_id, usage, at, cwd))
        (self.subagents / f"agent-{agent}.meta.json").write_text(
            json.dumps({"agentType": "general-purpose", "spawnDepth": depth}), encoding="utf-8")


class _Workspace:
    """Two Ready stories whose one criterion passes, a retro over them, and an open run whose
    meter reads the fixture transcripts (the env var points every stamp at them)."""

    def __init__(self, d: Path, agents: bool = True) -> None:
        self.root = d / "repo"
        self.tx = _Transcripts(d / "transcripts")
        (self.root / "src").mkdir(parents=True)
        (self.root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in UNITS:
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Points:** 2\n\n## Acceptance Criteria"
                "\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n", encoding="utf-8")
        retros = self.root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-meter.md").write_text(
            f"# RETRO-0001: meter\n\n> **Batch:** {', '.join(UNITS)}\n", encoding="utf-8")
        self.tx.main_says("msg_main_1", MAIN_1)
        if agents:
            self.tx.agent_says("a1", "msg_agent_a", AGENT_A)
        self.rs = _live("lib.run_state")

    def open(self) -> None:
        self.rs.open_run(self.root, batch=list(UNITS), goal="g")
        self.rs.update(self.root, sprint_goal="the run states what it cost",
                       plan_snapshot={"units": {uid: {
                           "planned_points": 2, "forecast_minutes": 20.0,
                           "forecast_tokens": 2_000, "added": False} for uid in UNITS}})

    def state(self) -> dict:
        return self.rs.read(self.root)

    def lane(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("sprint").main(["lane", *argv, "--root", str(self.root)])
        return rc, out.getvalue()

    def page(self) -> dict:
        return _live("sprint_report").build_report(self.root, RETRO)

    def checklist_cost(self) -> dict:
        """The close checklist's cost row as `sprint_report.py checklist` prints it."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            _live("sprint_report").main(["--root", str(self.root), "checklist", "--id", RETRO,
                                         "--format", "json"])
        return next(r for r in json.loads(out.getvalue())["items"] if r["id"] == "cost")

    @staticmethod
    def estimates(page: dict) -> list[dict]:
        return next(s for s in page["sections"] if s["key"] == "estimates")["rows"]

    def row(self, page: dict, measure: str) -> dict:
        return next(r for r in self.estimates(page) if r["est_measure"]["value"] == measure)


class _Case(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.rs = _live("lib.run_state")

    def workspace(self, agents: bool = True) -> _Workspace:
        ws = _Workspace(self.tmp / ("with" if agents else "without"), agents=agents)
        env = unittest.mock.patch.dict(os.environ, {self.rs.TRANSCRIPTS_ENV: str(ws.tx.dir)})
        env.start()
        self.addCleanup(env.stop)
        return ws


class MeterComponentsTests(_Case):
    def test_main_and_subagent_components_are_counted_once_per_message(self) -> None:
        """AC1. MUTANTS: the subagents directory not read (`subagents` reads None and every
        total drops to the main thread's); the 1h writes folded into 5m (the main thread's
        3,000 read as cache_write_5m); a subagent's repeated records counted per record (each
        agent's figures tripled, BG1111's defect on the new path); the subagent files filtered
        by `_records_cwd` against the repo (the depth-2 worktree agent's 645 dropped)."""
        tx = _Transcripts(self.tmp / "tx")
        tx.main_says("msg_main_1", MAIN_1)
        tx.main_says("msg_main_2", MAIN_2)
        tx.agent_says("a1", "msg_agent_a", AGENT_A)
        tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)
        self.assertEqual(2, len(list(tx.subagents.glob("agent-*.jsonl"))),
                         "premise: both agents, depths 1 and 2, sit in one flat directory")
        reading = self.rs.session_tokens(self.tmp / "repo", tx.dir)

        main, agents = _sum(MAIN_1, MAIN_2), _sum(AGENT_A, AGENT_B)
        both = {c: main[c] + agents[c] for c in COMPONENTS}
        self.assertEqual(main, reading["main"], "the main thread, once per message")
        self.assertEqual(agents, reading["subagents"], "both subagents, once per message")
        self.assertEqual(both, reading["components"])
        self.assertEqual((0, 3_000, 3_600, 0),
                         (reading["main"]["cache_write_5m"], reading["main"]["cache_write_1h"],
                          reading["subagents"]["cache_write_5m"],
                          reading["subagents"]["cache_write_1h"]),
                         "each write is booked to the duration the transcript names")
        self.assertEqual(_tokens(both), reading["tokens"],
                         "tokens is input + output + cache write over both")
        self.assertEqual(7_305, reading["tokens"])
        self.assertTrue(reading["includes_subagents"])
        self.assertIn("2 subagent transcript", reading["basis"])
        self.assertNotIn("LOWER BOUND", reading["basis"])

    def test_a_session_with_no_subagents_directory_reads_the_main_thread_and_says_so(
            self) -> None:
        """MUTANT: an absent or reshaped subagents directory read as zero subagent spend - the
        reading then claims subagents it never read (`includes_subagents` True or a 0 split)."""
        tx = _Transcripts(self.tmp / "tx")
        tx.main_says("msg_main_1", MAIN_1)
        for shape in ("absent", "reshaped"):
            with self.subTest(shape=shape):
                if shape == "reshaped":       # the directory is there, in a layout not known
                    (tx.subagents / "nested").mkdir(parents=True)
                    (tx.subagents / "nested" / "agent-x.jsonl").write_text(
                        "\n".join(_Transcripts._records("m", AGENT_A, None, "/w")) + "\n",
                        encoding="utf-8")
                reading = self.rs.session_tokens(self.tmp / "repo", tx.dir)
                self.assertEqual(_tokens(_parts(MAIN_1)), reading["tokens"])
                self.assertIsNone(reading["subagents"], "no subagent figure, not a zero one")
                self.assertFalse(reading["includes_subagents"])
                self.assertIn("MAIN THREAD only", reading["basis"])
                self.assertIn(str(tx.subagents), reading["basis"])
                self.assertIn("LOWER BOUND", reading["basis"])

    def test_a_message_is_counted_at_its_largest_reading_when_a_later_repeat_is_smaller(
            self) -> None:
        """BG1111's rule, pinned on the component reduction. MUTANT: keep-last
        (`per_message[msg_id] = (side, parts)` in `_aggregate`), which books each message at
        its final record's 12 output tokens instead of the 300 an earlier repeat carried, on the
        main thread and in a subagent alike. The control: the same fixture with the repeats in
        growing order reads the same 300, so the pin is the largest reading, not the order."""
        for order in ("shrinking", "growing"):
            with self.subTest(order=order):
                tx = _Transcripts(self.tmp / order)
                outputs = (300, 12) if order == "shrinking" else (12, 300)
                for out in outputs:
                    tx.main_says("msg_main_1", dict(MAIN_1, output_tokens=out))
                    tx.agent_says("a1", "msg_agent_a", dict(AGENT_A, output_tokens=out))
                reading = self.rs.session_tokens(self.tmp / "repo", tx.dir)
                self.assertEqual((300, 300), (reading["main"]["output"],
                                              reading["subagents"]["output"]))
                self.assertEqual(_tokens(_sum(dict(MAIN_1, output_tokens=300),
                                              dict(AGENT_A, output_tokens=300))),
                                 reading["tokens"])

    def test_a_malformed_subagent_record_refuses_the_whole_read(self) -> None:
        """MUTANT: a subagent file that cannot be read skipped, so the reading is quietly short
        of that agent's spend."""
        tx = _Transcripts(self.tmp / "tx")
        tx.main_says("msg_main_1", MAIN_1)
        tx.agent_says("a1", "msg_agent_a", dict(AGENT_A, output_tokens="lots"))
        reading = self.rs.session_tokens(self.tmp / "repo", tx.dir)
        self.assertIsNone(reading["tokens"])
        self.assertIn("agent-a1.jsonl carries a malformed usage record", reading["reason"])


class MeterPricedTests(_Case):
    def test_priced_reads_the_weight_table_and_is_the_headline(self) -> None:
        """AC2. MUTANTS: weights typed beside the sum (the patched table leaves `priced`
        where it was); one weight for both cache-write durations (the 1h writes priced at
        1.25, or the 5m at 2.0); the headline left as the unpriced sum (the Estimates' first
        cost row and the close report's COST line read 7,305, not 34,665, unlabelled)."""
        self.assertEqual(WEIGHTS, self.rs.TOKEN_WEIGHTS, "D0390's table")
        tx = _Transcripts(self.tmp / "tx")
        tx.main_says("msg_main_1", MAIN_1)
        tx.main_says("msg_main_2", MAIN_2)
        tx.agent_says("a1", "msg_agent_a", AGENT_A)
        tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)
        reading = self.rs.session_tokens(self.tmp / "repo", tx.dir)
        both = _sum(MAIN_1, MAIN_2, AGENT_A, AGENT_B)
        self.assertEqual(_priced(both), reading["priced"])
        self.assertEqual(34_665, reading["priced"])
        with unittest.mock.patch.dict(self.rs.TOKEN_WEIGHTS, {"output": 7}):
            moved = self.rs.session_tokens(self.tmp / "repo", tx.dir)
        self.assertEqual(34_665 + 2 * both["output"], moved["priced"],
                         "a weight changed in-process moves the priced figure")
        with unittest.mock.patch.dict(self.rs.TOKEN_WEIGHTS, {"cache_write_1h": 3}):
            hour = self.rs.session_tokens(self.tmp / "repo", tx.dir)
        self.assertEqual(34_665 + both["cache_write_1h"], hour["priced"],
                         "the 1h weight prices the 1h writes and nothing else")

        # The headline: the report and the close state `priced` first, labelled.
        ws = self.workspace()
        ws.open()
        ws.tx.main_says("msg_main_2", MAIN_2)
        ws.tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)
        self.rs.stamp_tokens(ws.root, "report")
        spent = _sum(MAIN_2, AGENT_B)
        page = ws.page()
        measures = [r["est_measure"]["value"] for r in ws.estimates(page)]
        self.assertEqual(measures.index("Tokens") - 1, measures.index("Priced cost"),
                         f"the priced cost leads the token rows: {measures}")
        head = ws.row(page, "Priced cost")
        self.assertEqual(_priced(spent), head["est_actual"]["value"])
        self.assertIn("priced input-equivalent tokens", head["est_basis"]["value"])
        self.assertIn(f"input + output + cache write {_tokens(spent):,}",
                      head["est_basis"]["value"], "the sum is listed beside it")
        self.assertEqual(_tokens(spent), ws.row(page, "Tokens")["est_actual"]["value"],
                         "the sum stays a component, on its own row")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            _live("sprint")._tell_the_operator(ws.root)
        cost = out.getvalue().split("  COST\n", 1)[1].split("\n\n", 1)[0]
        self.assertTrue(cost.strip().startswith(
            f"{_priced(spent):,} priced input-equivalent tokens"), cost)
        self.assertIn(f"input + output + cache write {_tokens(spent):,}", cost)
        self.assertIn(f"{_priced(spent):,} priced input-equivalent tokens",
                      ws.checklist_cost()["detail"], "the close checklist names it too")


class MeterStampsTests(_Case):
    def test_the_run_total_carries_priced_deltas_and_names_legacy_stamps(self) -> None:
        """AC3. MUTANTS: `priced` defaulting to 0 for a legacy stamp (it reads 0, not None);
        `priced` derived from `tokens` times a constant rather than from the stamped
        components (no constant turns this delta's 2,975 tokens into its 15,385 priced)."""
        ws = self.workspace()
        ws.open()
        ws.tx.main_says("msg_main_2", MAIN_2)
        ws.tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)   # a subagent completes
        self.rs.stamp_tokens(ws.root, "unit-end")
        total = self.rs.run_token_total(ws.state())
        spent = _sum(MAIN_2, AGENT_B)
        self.assertEqual(_tokens(spent), total["tokens"])
        self.assertEqual(spent, total["components"], "each component's delta beside tokens")
        self.assertEqual(_priced(spent), total["priced"])
        self.assertEqual((2_975, 15_385), (total["tokens"], total["priced"]))
        self.assertTrue(total["includes_subagents"])
        with unittest.mock.patch.dict(self.rs.TOKEN_WEIGHTS, {"cache_read": 0.2}):
            self.assertEqual(_priced(spent) + round(spent["cache_read"] * 0.1),
                             self.rs.run_token_total(ws.state())["priced"],
                             "the run total prices the stamped components from the table")

        src = str(ws.tx.main)
        legacy = {self.rs.TOKEN_STAMPS: [
            {"tokens": 1_000, "source": src, "at": _iso(T0), "kind": "open", "model": MODEL},
            {"tokens": 4_000, "source": src, "at": _iso(T0 + timedelta(hours=1)),
             "kind": "report", "model": MODEL}]}
        old = self.rs.run_token_total(legacy)
        self.assertEqual(3_000, old["tokens"], "a legacy run's tokens are unchanged")
        self.assertIsNone(old["priced"], "no priced figure, never 0")
        self.assertIsNone(old["components"])
        self.assertIn("written before", old["priced_reason"])
        self.assertFalse(old["includes_subagents"])


class MeterDelegatedTests(_Case):
    def test_a_supplied_total_is_not_added_over_a_reading_that_holds_subagents(self) -> None:
        """AC4. MUTANTS: delegated totals added unconditionally (the builder's 250,000 counted
        on top of the subagent transcript that already holds its spend); delegated totals
        suppressed for every run (the run with no subagent reading, and a legacy run, lose the
        250,000 and an earlier signed page moves)."""
        sr, retro = _live("sprint_report"), _live("retro")
        for agents in (True, False):
            with self.subTest(subagents=agents):
                ws = self.workspace(agents=agents)
                ws.open()
                rc, out = ws.lane("brief", "--units", "US0101")
                self.assertEqual(0, rc, out)
                ws.tx.main_says("msg_main_2", MAIN_2)
                if agents:
                    ws.tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)   # the builder
                rc, out = ws.lane("return", "--units", "US0101", "--tokens", "250000")
                self.assertEqual(0, rc, out)
                self.rs.stamp_tokens(ws.root, "report")
                state = ws.state()
                spent = _tokens(_sum(MAIN_2, AGENT_B) if agents else _parts(MAIN_2))
                added = 0 if agents else 250_000
                total = self.rs.run_token_total(state)
                self.assertEqual(agents, total["includes_subagents"])
                self.assertEqual((spent + added, 0 if agents else 1),
                                 sr._run_tokens_actual(state, total))
                page = ws.page()
                basis = ws.row(page, "Tokens")["est_basis"]["value"]
                cost = next(s for s in page["sections"] if s["key"] == "cost")["figures"]
                self.assertEqual(spent + added, cost["tokens_total"]["value"],
                                 "the appendix total agrees with the Estimates actual")
                self.assertEqual(f"{spent + added:,} tokens, measured", ws.checklist_cost()["value"],
                                 "the close checklist's cost row agrees too")
                cap = retro.run_attributed_tokens(ws.root, RETRO)
                self.assertEqual(spent + added, cap["tokens"], cap)
                printed = io.StringIO()
                with contextlib.redirect_stdout(printed), \
                        contextlib.redirect_stderr(io.StringIO()):
                    retro.main(["--root", str(ws.root), "accuracy", "--id", RETRO,
                                "--tokens-from-harness"])
                if agents:
                    self.assertIn("already in", basis)
                    self.assertIn("already in", cap["basis"])
                    self.assertEqual(0, cap["delegated_tokens"])
                    self.assertIn(f"harness transcript: {spent:,} (", printed.getvalue(),
                                  "the close's line states the figure, not a floor")
                else:
                    self.assertIn("delegated agent(s)' reported totals", basis)
                    self.assertEqual(250_000, cap["delegated_tokens"])
                    self.assertIn(f"harness transcript: AT LEAST {spent + added:,} (",
                                  printed.getvalue())

        # A run whose stamps carry no flag, as every run before this change: still added.
        self._legacy_run_still_adds(sr)

    def test_a_reading_that_holds_the_subagents_states_the_tokens_ratio(self) -> None:
        """MUTANT: the ratio withheld for want of supplied totals over a meter that already read
        the subagents - the Estimates Tokens ratio reads NOT MEASURED, "no delegated spend was
        supplied", though the actual is whole. The control: the same run without a subagent
        reading still withholds it."""
        for agents in (True, False):
            with self.subTest(subagents=agents):
                ws = self.workspace(agents=agents)
                ws.open()
                ws.tx.main_says("msg_main_2", MAIN_2)
                if agents:
                    ws.tx.agent_says("b2", "msg_agent_b", AGENT_B, depth=2)
                self.rs.stamp_tokens(ws.root, "report")
                ratio = ws.row(ws.page(), "Tokens")["est_ratio"]
                if agents:
                    self.assertEqual(f"{round(_tokens(_sum(MAIN_2, AGENT_B)) / 4_000, 2)}x",
                                     ratio["value"])
                else:
                    self.assertEqual("NOT MEASURED", ratio["value"])
                    self.assertIn("no delegated spend was supplied", ratio["reason"])

    def _legacy_run_still_adds(self, sr) -> None:
        legacy = {self.rs.TOKEN_STAMPS: [
            {"tokens": 1_000, "source": "s", "at": _iso(T0), "kind": "open"},
            {"tokens": 4_000, "source": "s", "at": _iso(T0 + timedelta(hours=1)),
             "kind": "report"}],
            self.rs.DELEGATED: [{"tokens": 250_000, "agent": "build lane",
                                 "provenance": self.rs.SUPPLIED}]}
        self.assertEqual((253_000, 1),
                         sr._run_tokens_actual(legacy, self.rs.run_token_total(legacy)))


class OpenStampBasisTests(_Case):
    """US1097 AC1: a reading taken on an earlier counting basis is re-derived from the
    transcript up to its own time, never subtracted from, or summed with, one on the current
    basis."""

    def _timed(self, name: str) -> _Workspace:
        """A workspace whose transcript records carry their times, as the harness writes them."""
        ws = _Workspace(self.tmp / name, agents=False)
        shutil.rmtree(ws.tx.dir)
        ws.tx = _Transcripts(ws.tx.dir)
        env = unittest.mock.patch.dict(os.environ, {self.rs.TRANSCRIPTS_ENV: str(ws.tx.dir)})
        env.start()
        self.addCleanup(env.stop)
        return ws

    def _legacy(self, ws: _Workspace, *readings: tuple) -> None:
        """The run's readings as an earlier meter wrote them: counted per record (three records
        a message), main thread only, naming no basis. The first is the opening one and the
        baseline."""
        stamps = [{"tokens": 3 * _tokens(_sum(*usages)), "source": str(ws.tx.main),
                   "at": _iso(at), "kind": kind, "model": MODEL} for kind, at, usages in readings]
        base = {k: stamps[0][k] for k in ("tokens", "source", "at")}
        self.rs.update(ws.root, **{self.rs.TOKEN_BASELINE: base, self.rs.TOKEN_STAMPS: stamps})

    def _opened_before_the_change(self, name: str) -> _Workspace:
        ws = self._timed(name)
        ws.tx.main_says("msg_main_1", MAIN_1, at=T0)
        ws.tx.agent_says("a1", "msg_agent_a", AGENT_A, at=T0 + timedelta(minutes=1))
        ws.open()
        self._legacy(ws, ("open", T0 + timedelta(minutes=5), (MAIN_1,)))
        ws.tx.main_says("msg_main_2", MAIN_2, at=T0 + timedelta(minutes=10))
        ws.tx.agent_says("b2", "msg_agent_b", AGENT_B, at=T0 + timedelta(minutes=12), depth=2)
        return ws

    def test_an_open_stamp_on_an_earlier_basis_is_re_derived_not_subtracted(self) -> None:
        """MUTANTS: the earlier-basis open stamp subtracted from a current-basis reading (3,975,
        where the run spent 2,975: RUN-01M5EM9N's open stamp is 48,420,326 per record and
        19,227,104 once per message on the main thread); the re-derivation reading past the
        stamp's time (the open moment re-derived as the whole transcript, 7,305, not 4,330); a
        re-derivation that cannot be had read as none owed (the gone records' run then reads one
        uncovered reading, and its reason names no basis change)."""
        ws = self._opened_before_the_change("held")
        report = self.rs.stamp_tokens(ws.root, "report")          # the close's reading
        spent = _sum(MAIN_2, AGENT_B)
        redone = [s for s in ws.state()[self.rs.TOKEN_STAMPS] if s["kind"] == self.rs.REDERIVED]
        self.assertEqual(
            [(_iso(T0 + timedelta(minutes=5)), report["at"], _tokens(_sum(MAIN_1, AGENT_A)))],
            [(s[self.rs.REDERIVES], s["at"], s["tokens"]) for s in redone],
            "the open moment re-derived once, main thread and subagents, by the reading that "
            "took it")

        total = self.rs.run_token_total(ws.state())
        self.assertEqual(2_975, total["tokens"])
        self.assertEqual(_tokens(spent), total["tokens"])
        self.assertEqual(_priced(spent), total["priced"])
        self.assertIn("1 reading(s) taken on an earlier counting basis were re-derived",
                      total["basis"])
        self.assertEqual(_tokens(spent), ws.row(ws.page(), "Tokens")["est_actual"]["value"],
                         "the report forms the same total")
        cap = _live("retro").run_attributed_tokens(ws.root, RETRO)
        self.assertEqual(_tokens(spent), cap["tokens"], cap)
        self.assertIn(f"re-derived from the transcript up to {_iso(T0 + timedelta(minutes=5))} "
                      f"as {_tokens(_sum(MAIN_1, AGENT_A)):,}", cap["basis"])

        # The transcript no longer holds the records up to the open stamp when the first
        # current-basis reading lands: not attributable, naming the basis change.
        gone = self._opened_before_the_change("gone")
        lines = gone.tx.main.read_text(encoding="utf-8").splitlines()
        gone.tx.main.write_text("\n".join(lines[3:]) + "\n", encoding="utf-8")
        (gone.tx.subagents / "agent-a1.jsonl").unlink()
        self.rs.stamp_tokens(gone.root, "report")
        total = self.rs.run_token_total(gone.state())
        self.assertIsNone(total["tokens"], total)
        self.assertIn("taken on an earlier counting basis and cannot be re-derived",
                      total["reason"])
        self.assertIn("no longer holds a usage record up to the stamp's time", total["reason"])
        self.assertEqual("NOT MEASURED", gone.row(gone.page(), "Tokens")["est_actual"]["value"])
        cap = _live("retro").run_attributed_tokens(gone.root, RETRO)
        self.assertIsNone(cap["tokens"], cap)
        self.assertIn("was taken on an earlier counting basis and cannot be re-derived",
                      cap["reason"])

    def test_a_session_wholly_on_an_earlier_basis_is_re_derived_with_the_run(self) -> None:
        """MUTANT: the rule applied per session, not per run - the session whose readings were
        all taken on the earlier basis keeps its per-record delta (6,990, where it spent 2,330)
        and is summed with the other session's current-basis one."""
        ws = self._timed("sessions")
        ws.tx.main_says("msg_main_1", MAIN_1, at=T0)
        ws.open()
        ws.tx.main_says("msg_main_2", MAIN_2, at=T0 + timedelta(minutes=10))
        self._legacy(ws, ("open", T0 + timedelta(minutes=5), (MAIN_1,)),
                     ("handoff", T0 + timedelta(minutes=15), (MAIN_1, MAIN_2)))
        # The run resumes in a second session, whose transcript is now the newest.
        later = ws.tx.dir / "5e5510n-0000-4000-8000-000000000002.jsonl"
        _Transcripts._append(later, _Transcripts._records(
            "msg_later_1", MAIN_1, T0 + timedelta(minutes=30), "/work/repo"))
        self.rs.stamp_tokens(ws.root, "resume")
        _Transcripts._append(later, _Transcripts._records(
            "msg_later_2", AGENT_B, T0 + timedelta(minutes=40), "/work/repo"))
        self.rs.stamp_tokens(ws.root, "report")

        total = self.rs.run_token_total(ws.state())
        self.assertEqual(_tokens(_sum(MAIN_2)) + _tokens(_sum(AGENT_B)), total["tokens"], total)
        self.assertEqual(2, total["session_count"])
        self.assertIn("2 reading(s) taken on an earlier counting basis were re-derived",
                      total["basis"])

    def test_a_run_holding_only_its_legacy_baseline_is_re_derived(self) -> None:
        """MUTANTS: the re-derivation owed only by the sessions the earlier stamps name (a run
        whose one earlier-basis reading is its legacy baseline reads not attributable at its
        first current-basis stamp, where it spent 2,975); the baseline subtracted from a
        current-basis closing reading (3,975)."""
        ws = self._opened_before_the_change("baseline")
        self.rs.update(ws.root, **{self.rs.TOKEN_STAMPS: []})
        spent = _tokens(_sum(MAIN_2, AGENT_B))
        closing = self.rs.run_token_total(ws.state(), self.rs.session_tokens(ws.root))
        self.assertEqual(spent, closing["tokens"], closing)
        self.assertIn("1 reading(s) taken on an earlier counting basis were re-derived",
                      closing["basis"])
        self.rs.stamp_tokens(ws.root, "report")
        total = self.rs.run_token_total(ws.state())
        self.assertEqual(spent, total["tokens"], total)
        self.assertIn(f"the legacy {self.rs.TOKEN_BASELINE}", total["shape"])
        self.assertEqual(spent, _live("retro").run_attributed_tokens(ws.root, RETRO)["tokens"])

    def test_a_span_or_a_window_ending_before_the_change_is_never_measured_across_it(
            self) -> None:
        """MUTANTS: a unit span opened on the earlier basis measured to a current-basis end
        (its tokens read 0, a difference across two bases, where they are not measured); the
        re-derivations stamped with the earlier reading's own time, so a page measured to a
        moment before the first current-basis reading is rebased (2,330, where it was filed at
        the per-record 6,990)."""
        ws = self._timed("span")
        ws.tx.main_says("msg_main_1", MAIN_1, at=T0)
        ws.open()
        ws.tx.main_says("msg_main_2", MAIN_2, at=T0 + timedelta(minutes=10))
        started = T0 + timedelta(minutes=11)
        self._legacy(ws, ("open", T0 + timedelta(minutes=5), (MAIN_1,)),
                     ("unit-start", started, (MAIN_1, MAIN_2)))
        self.rs.update(ws.root, **{self.rs.UNIT_ACTUALS: {UNITS[0]: {
            "minutes": 0.0, "tokens": 0, "started_at": _iso(started), "start_tokens": 6_990,
            "open": True, "start_source": str(ws.tx.main)}}})
        sr = _live("sprint_report")
        end = T0 + timedelta(minutes=20)
        filed = self.rs.run_token_total(sr._metered(ws.state(), end))
        self.assertEqual(6_990, filed["tokens"], "premise: the page as it was filed")

        ws.tx.main_says("msg_main_3", AGENT_B, at=T0 + timedelta(minutes=12))
        entry = self.rs.record_unit_actual(ws.root, UNITS[0], "Done", terminal=True)
        self.assertIsNone(entry["tokens"], entry)
        self.assertEqual(filed, self.rs.run_token_total(sr._metered(ws.state(), end)),
                         "the page measured to before the change re-derives unchanged")
        self.assertEqual(_tokens(_sum(MAIN_2, AGENT_B)),
                         self.rs.run_token_total(ws.state())["tokens"])


if __name__ == "__main__":
    unittest.main()
