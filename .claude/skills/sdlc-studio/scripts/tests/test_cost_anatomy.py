"""US1124: `sprint.py cost --anatomy` breaks a session's spend down by role and names the tool
outputs that drove it (CR0666).

Every case runs over US1091's fixture harness store (`test_meter_reads_true`): the session's own
transcript and its subagents' `agent-<id>.jsonl` files beside it. Roles come from the run's own
records, written by the shipped writers: `sprint lane return --agent` for a builder and its
repair, and `critic.record_verdict` (the writer `sprint lane accept` drives through `critic.py
record`) for each reviewer. The expected figures are formed here from the fixture's usages and
the fixture's own weight table, never read back from the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace

_usage = meter._usage

MAIN_2 = _usage(30, 300, 0, 2_000, 80_000)
MAIN_2_EARLY_OUTPUT = 120
MAIN_3 = _usage(12, 120, 0, 3_000, 90_000)
MAIN_4 = _usage(8, 80, 0, 500, 95_000)
BUILD_X = _usage(40, 400, 5_000, 0, 120_000)
BUILD_X_EARLY_OUTPUT = 90
BUILD_Y = _usage(15, 150, 800, 0, 30_000)
REVIEW_Q3 = _usage(6, 60, 4_000, 0, 40_000)
REVIEW_Q4 = _usage(7, 70, 4_100, 0, 41_000)
REPAIR_Z = _usage(25, 250, 2_500, 0, 60_000)
STRAY_Q0 = _usage(3, 30, 900, 0, 9_000)
#: messages read on two transcripts: msg_shared partial on the main thread and whole on agent-x1,
#: msg_shared_2 whole on the main thread and partial on agent-x1
SHARED = _usage(9, 900, 0, 1_500, 20_000)
SHARED_PARTIAL_OUTPUT = 10
OWN_X1 = _usage(4, 40, 700, 0, 8_000)
#: an agent whose first call is small and whose later call is its largest (US1132 AC4)
H5_START = _usage(5, 50, 20_000, 0, 0)
H5_LATER = _usage(5, 50, 1_000, 0, 140_000)
#: a start of 10,005 and one of 125,005, either side of a 100,000 budget (US1132 round 1)
LEAN_START = _usage(5, 50, 0, 0, 10_000)
HEAVY_START = _usage(5, 50, 0, 0, 125_000)

#: q0's prompt reads as a reviewer's, and no record names q0.
REVIEWER_WORDED_PROMPT = ("You are the independent reviewer of US0101. Review the builder's "
                          "diff as the QA seat reviewer and return a verdict.")


def _ctx(usage: dict) -> int:
    p = meter._parts(usage)
    return p["input"] + p["cache_write_5m"] + p["cache_write_1h"] + p["cache_read"]


def _stamp(at: datetime | None) -> dict:
    """A record's `timestamp`, as the harness writes it, or none."""
    return {} if at is None else {"timestamp": at.isoformat(timespec="milliseconds").replace(
        "+00:00", "Z")}


def _assistant(msg_id: str | None, usage: dict, blocks: list[dict],
               at: datetime | None = None) -> str:
    msg = {"model": meter.MODEL, "role": "assistant", "content": blocks, "usage": dict(usage)}
    if msg_id is not None:
        msg["id"] = msg_id
    return json.dumps({"type": "assistant", "cwd": "/work/repo", "message": msg} | _stamp(at))


def _tool_use(tid: str, name: str, **inp) -> dict:
    return {"type": "tool_use", "id": tid, "name": name, "input": inp}


def _result(tid: str, size: int, as_list: bool = False, at: datetime | None = None) -> str:
    content = [{"type": "text", "text": "x" * size}] if as_list else "y" * size
    return json.dumps({"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tid, "content": content}]}} | _stamp(at))


def _prompt(text: str) -> str:
    return json.dumps({"type": "user", "message": {"role": "user", "content": text}})


def _cli(ws, *argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = meter._live("sprint").main(["cost", "--anatomy", *argv, "--root", str(ws.root)])
    return rc, out.getvalue() + err.getvalue()


class CostAnatomyTests(meter._Case):
    def _session(self):
        """An open run over the fixture session. Main thread: four calls, the second logged on
        two lines (the first with a smaller output count), and two tool outputs. US0101 built by
        b7 (eleven small Grep outputs between its two calls, its first call logged partial then
        whole), REJECTed by agent-q3, repaired by r9 (whose 200,000-character output no later
        call re-reads), then APPROVEd by agent-q3; q4, recorded bare, APPROVEs US0102. a1 and
        q0 are named by no record."""
        ws = self.workspace()
        ws.open()
        tx = ws.tx
        tx._append(tx.main, [
            _assistant("msg_main_2", dict(MAIN_2, output_tokens=MAIN_2_EARLY_OUTPUT),
                       [{"type": "thinking"}]),
            _assistant("msg_main_2", MAIN_2, [_tool_use("t_log", "Bash", command="git log -p")]),
            _result("t_log", 40_000),
            _assistant("msg_main_3", MAIN_3, [_tool_use("t_big", "Read",
                                                        file_path="src/huge.py")]),
            _result("t_big", 70_000, as_list=True),
            _assistant("msg_main_4", MAIN_4, [{"type": "text"}])])
        b7 = tx.subagents / "agent-b7.jsonl"
        grep = [line for n in range(1, 12) for line in (
            _assistant("msg_b7_x", BUILD_X, [_tool_use(f"g{n}", "Grep", pattern=f"p{n}")]),
            _result(f"g{n}", 100 * n))]
        tx._append(b7, [_prompt("Build US0101."),
                        _assistant("msg_b7_x", dict(BUILD_X, output_tokens=BUILD_X_EARLY_OUTPUT),
                                   [{"type": "thinking"}]),
                        *grep, _assistant("msg_b7_y", BUILD_Y, [{"type": "text"}])])
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        critic = meter._live("critic")
        tx._append(tx.subagents / "agent-q3.jsonl",
                   [_assistant("msg_q3", REVIEW_Q3, [{"type": "text"}])])
        critic.record_verdict(ws.root, "US0101", "REJECT", reviewer="agent-q3",
                              author="agent-b7", issues="BLOCKING: [new] the criterion is red")
        tx._append(tx.subagents / "agent-r9.jsonl", [
            _assistant("msg_r9", REPAIR_Z, [_tool_use("t_dump", "Bash", command="cat dump")]),
            _result("t_dump", 200_000)])
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "r9")
        self.assertEqual(0, rc, out)
        tx._append(tx.subagents / "agent-q4.jsonl",
                   [_assistant("msg_q4", REVIEW_Q4, [{"type": "text"}])])
        # round 2 is re-checked by the round-1 reviewer (critic's round rule); q4, recorded by its
        # bare id, reviews US0102
        critic.record_verdict(ws.root, "US0101", "APPROVE", reviewer="agent-q3", author="agent-r9")
        critic.record_verdict(ws.root, "US0102", "APPROVE", reviewer="q4", author="agent-zz")
        tx._append(tx.subagents / "agent-q0.jsonl",
                   [_prompt(REVIEWER_WORDED_PROMPT),
                    _assistant("msg_q0", STRAY_Q0, [{"type": "text"}])])
        return ws

    def _json(self, ws) -> dict:
        rc, out = _cli(ws, "--format", "json")
        self.assertEqual(0, rc, out)
        return json.loads(out)

    def test_per_role_rows_from_lane_records(self) -> None:
        """AC1. MUTANTS: a message counted at its first, partial usage record (main's msg_main_2
        at output 120, b7's msg_b7_x at 90); a message counted once per record (msg_b7_x has
        twelve); the repair booked as a builder (agents of a unit not split by its first
        verdict's author); a role's first context taken from its last call, or from its first
        agent alone rather than each agent's first call (reviewer, other); the average taken over
        the role's agents rather than its calls; a share formed over one role alone; a message
        read on two transcripts counted at its first transcript's partial usage (msg_shared at
        output 10 on the main thread, 900 on agent-x1), or at its later copy rather than its
        largest (msg_shared_2, whole first), or counted on both, or booked to the last
        transcript reading it rather than the side the meter books it to. Each moves a
        figure asserted."""
        ws = self._session()
        by_agent = {  # each role's agents, each agent's calls in order
            "orchestrator": ((meter.MAIN_1, MAIN_2, MAIN_3, MAIN_4),),
            "builder": ((BUILD_X, BUILD_Y),),
            "reviewer": ((REVIEW_Q3,), (REVIEW_Q4,)),
            "repair": ((REPAIR_Z,),),
            "other": ((meter.AGENT_A,), (STRAY_Q0,)),
        }
        roles = {r: tuple(u for calls in a for u in calls) for r, a in by_agent.items()}
        agents = {r: len(a) for r, a in by_agent.items()}
        firsts = {r: sum(_ctx(calls[0]) for calls in a) / len(a) for r, a in by_agent.items()}
        priced = {r: meter._priced(meter._sum(*us)) for r, us in roles.items()}
        total = meter._priced(meter._sum(*(u for us in roles.values() for u in us)))
        got = self._json(ws)
        self.assertEqual(list(roles), [row["role"] for row in got["roles"]])
        for row in got["roles"]:
            us, role = roles[row["role"]], row["role"]
            parts = meter._sum(*us)
            self.assertEqual(agents[role], row["agents"], role)
            self.assertEqual(len(us), row["calls"], role)
            self.assertEqual(priced[role], row["priced"], role)
            self.assertAlmostEqual(priced[role] / sum(priced.values()), row["share"], 9, role)
            self.assertEqual(parts, row["components"], role)
            weighed = {c: parts[c] * meter.WEIGHTS[c] for c in meter.COMPONENTS}
            whole = sum(weighed.values())
            self.assertAlmostEqual(weighed["cache_read"] / whole, row["split"]["cache_read"], 9)
            self.assertAlmostEqual((weighed["cache_write_5m"] + weighed["cache_write_1h"]) / whole,
                                   row["split"]["cache_write"], 9)
            self.assertAlmostEqual(weighed["output"] / whole, row["split"]["output"], 9)
            self.assertAlmostEqual(firsts[role], row["first_context"], 6, role)
            self.assertAlmostEqual(sum(_ctx(u) for u in us) / len(us), row["avg_context"], 6)
        self.assertEqual(total, got["total"]["priced"])
        # the anatomy's whole is the meter's own reading of the same session
        self.assertEqual(meter._live("lib.run_state").claude_tokens(ws.root)["priced"], total)
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)
        builder = next(line for line in text.splitlines() if line.startswith("builder "))
        self.assertIn(f"{priced['builder']:,}", builder)
        self.assertIn(f"{100 * priced['builder'] / sum(priced.values()):.1f}%", builder)
        self.assertIn(f"{_ctx(BUILD_X):,}", builder)
        # a message read on two transcripts counts once at its largest usage across both, booked
        # to the side that read it first, as the meter reads it
        ws = self.workspace(agents=False)
        partial = dict(SHARED, output_tokens=SHARED_PARTIAL_OUTPUT)
        ws.tx._append(ws.tx.main, [_assistant("msg_shared", partial, [{"type": "text"}]),
                                   _assistant("msg_shared_2", SHARED, [{"type": "text"}])])
        ws.tx._append(ws.tx.subagents / "agent-x1.jsonl", [
            _assistant("msg_shared", SHARED, [{"type": "text"}]),
            _assistant("msg_shared_2", partial, [{"type": "text"}]),
            _assistant("msg_x1", OWN_X1, [{"type": "text"}])])
        doc = self._json(ws)
        got = {row["role"]: row for row in doc["roles"]}
        run_state = meter._live("lib.run_state")
        reading = run_state.claude_tokens(ws.root)
        self.assertEqual(meter._priced(meter._sum(meter.MAIN_1, SHARED, SHARED, OWN_X1)),
                         doc["total"]["priced"])
        self.assertEqual(reading["priced"], doc["total"]["priced"])
        self.assertEqual(meter._priced(meter._sum(meter.MAIN_1, SHARED, SHARED)),
                         got["orchestrator"]["priced"])
        self.assertEqual(run_state.price(reading["main"]), got["orchestrator"]["priced"])
        self.assertEqual(meter._priced(meter._sum(OWN_X1)), got["other"]["priced"])
        self.assertEqual((3, 1), (got["orchestrator"]["calls"], got["other"]["calls"]))

    def test_the_heaviest_tool_outputs_are_named(self) -> None:
        """AC2. MUTANTS: outputs ranked by size alone (r9's 200,000-character dump, which no later
        call re-reads, and t_big ahead of t_log); the later calls counted over the whole session
        rather than the output's own transcript; a call counted once per record (msg_b7_x's
        twelve records); a list-shaped result sized as zero; more or fewer than ten named; the
        producer not named. Each moves the list asserted."""
        ws = self._session()
        got = self._json(ws)["outputs"]
        expected = [("Bash: git log -p", 40_000, 2), ("Read: src/huge.py", 70_000, 1)] + [
            (f"Grep: p{n}", 100 * n, 1) for n in range(11, 3, -1)]
        self.assertEqual(expected, [(o["producer"], o["size"], o["later_calls"]) for o in got])
        self.assertEqual([s * k for _p, s, k in expected], [o["cost"] for o in got])
        self.assertEqual(["orchestrator", "orchestrator"] + ["builder"] * 8,
                         [o["role"] for o in got])
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)
        tail = text.split("Heaviest tool outputs", 1)[1]
        self.assertIn("80,000", tail.splitlines()[1])
        self.assertIn("Bash: git log -p", tail.splitlines()[1])
        self.assertNotIn("cat dump", tail)

    def test_an_unrecorded_agent_is_other(self) -> None:
        """AC3. MUTANTS: a role guessed from prompt wording (q0's prompt names it the reviewer);
        an agent the records do not name dropped from the reading rather than counted under
        other; a reviewer matched only with its `agent-` prefix (q4 is recorded bare). Each moves
        the roles or the agents asserted."""
        ws = self._session()
        anatomy = meter._live("lib.cost_anatomy")
        roles = anatomy.agent_roles(ws.state(), meter._live("critic").read_verdicts(ws.root))
        self.assertEqual({"b7": "builder", "r9": "repair", "q3": "reviewer", "q4": "reviewer"},
                         roles)
        got = {row["role"]: row for row in self._json(ws)["roles"]}
        self.assertEqual(2, got["other"]["agents"])
        self.assertEqual(["agent-a1", "agent-q0"], got["other"]["agent_ids"])
        self.assertEqual(["agent-q3", "agent-q4"], got["reviewer"]["agent_ids"])
        self.assertEqual(meter._priced(meter._sum(meter.AGENT_A, STRAY_Q0)),
                         got["other"]["priced"])

    def test_no_per_call_context_is_not_available(self) -> None:
        """AC4. MUTANTS: a missing context printed as 0, in the text or the JSON; a reading with
        no per-call records given a call count; a role with no calls given a context of 0. Each
        prints a 0 or a figure where `not available` is asserted."""
        anatomy = meter._live("lib.cost_anatomy")
        parts = meter._sum(meter.MAIN_1, meter.AGENT_A)
        reading = {"harness": "cursor", "tokens": meter._tokens(parts),
                   "priced": meter._priced(parts), "components": parts}
        got = anatomy.from_reading(reading)
        text = anatomy.render(got)
        for row in got["roles"]:
            self.assertIsNone(row["first_context"], row["role"])
            self.assertIsNone(row["avg_context"], row["role"])
        other = next(r for r in got["roles"] if r["role"] == "other")
        self.assertIsNone(other["calls"])
        self.assertEqual(meter._priced(parts), other["priced"])
        for line in text.splitlines():
            role = line.split(" ", 1)[0]
            if role in ("orchestrator", "builder", "reviewer", "repair", "other"):
                self.assertTrue(line.rstrip().endswith("not available  not available"), line)
        # a transcript whose usage records carry no message id gives no per-call context either
        ws = self.workspace(agents=False)
        ws.tx.main.write_text(_assistant(None, meter.MAIN_1, [{"type": "text"}]) + "\n"
                              + _assistant(None, MAIN_2, [{"type": "text"}]) + "\n",
                              encoding="utf-8")
        rc, out = _cli(ws, "--format", "json")
        self.assertEqual(0, rc, out)
        orch = json.loads(out)["roles"][0]
        self.assertEqual(("orchestrator", None, None, None),
                         (orch["role"], orch["calls"], orch["first_context"], orch["avg_context"]))
        self.assertEqual(meter._priced(meter._sum(meter.MAIN_1, MAIN_2)), orch["priced"])
        rc, text = _cli(ws)
        orch_line = next(line for line in text.splitlines() if line.startswith("orchestrator"))
        self.assertTrue(orch_line.rstrip().endswith("not available  not available"), orch_line)

    def test_the_main_thread_start_context_is_named(self) -> None:
        """US1130 AC4. MUTANTS: the header line dropped; the start context read from the main
        thread's largest call, its last, its average, or the role table's first context averaged
        over every role's agents; the line printed below the table rather than in the header; a
        main thread with no per-call record given 0 rather than `not available`. The fixture's
        first main-thread call (MAIN_1) is neither its largest nor its last, so each moves it."""
        ws = self._session()
        main = (meter.MAIN_1, MAIN_2, MAIN_3, MAIN_4)
        first = _ctx(meter.MAIN_1)
        self.assertNotIn(first, (max(map(_ctx, main)), _ctx(main[-1]),
                                 sum(map(_ctx, main)) / len(main)))
        self.assertEqual(first, self._json(ws)["start_context"])
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)
        header = text.split("\n\n", 1)[0]
        line = next((ln for ln in header.splitlines() if "main thread start context" in ln), None)
        self.assertIsNotNone(line, header)
        self.assertIn(f"{first:,} tokens", line)
        self.assertIn("input + cache", line)
        got = meter._live("lib.cost_anatomy").from_reading(
            {"harness": "cursor", "components": meter._sum(meter.MAIN_1)})
        self.assertIsNone(got["start_context"])
        self.assertIn("main thread start context: not available",
                      meter._live("lib.cost_anatomy").render(got))

    def test_a_subagent_over_its_start_budget_is_flagged(self) -> None:
        """US1132 AC4. MUTANTS: the flag comparing an agent's largest call (h5's), its last or its
        average (b7's) rather than its first; the budget a constant rather than
        `cost.agent_start_budget` read from the config (the override and the shipped default
        differ); the main thread flagged as a subagent; the flag line dropped from the text, or
        its start or budget left out; the key missing from config-defaults.yaml or undocumented."""
        ws = self._session()
        # h5 starts lean and grows past the budget; b7 starts over it and then shrinks
        ws.tx._append(ws.tx.subagents / "agent-h5.jsonl", [
            _assistant("msg_h5_1", H5_START, [_tool_use("t_h5", "Read", file_path="a.py")]),
            _result("t_h5", 10),
            _assistant("msg_h5_2", H5_LATER, [{"type": "text"}])])
        budget = 100_000
        self.assertGreater(_ctx(BUILD_X), budget)
        self.assertLess(max(_ctx(BUILD_Y), (_ctx(BUILD_X) + _ctx(BUILD_Y)) / 2), budget)
        self.assertLess(_ctx(H5_START), budget)
        self.assertGreater(_ctx(H5_LATER), budget)
        defaults = (meter.SCRIPTS.parent / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        m = re.search(r"^cost:\n(?:  .*\n)*?  agent_start_budget: (\d+)", defaults, re.M)
        self.assertIsNotNone(m, "config-defaults.yaml ships no cost.agent_start_budget")
        shipped = int(m.group(1))
        self.assertNotEqual(budget, shipped)
        self.assertGreater(_ctx(meter.MAIN_1), shipped)  # the main thread starts over it
        got = self._json(ws)
        self.assertEqual(shipped, got["start_budget"])
        over = [o["agent"] for o in got["over_start_budget"]]
        self.assertIn("agent-b7", over)
        self.assertEqual([], [a for a in over if a in ("session", "agent-h5")], over)
        doc = (meter.SCRIPTS.parent / "reference-config.md").read_text(encoding="utf-8")
        self.assertIn("| `cost.agent_start_budget` |", doc)
        (ws.root / "sdlc-studio" / ".config.yaml").write_text(
            f"cost:\n  agent_start_budget: {budget}\n", encoding="utf-8")
        got = self._json(ws)
        self.assertEqual(budget, got["start_budget"])
        self.assertEqual([{"agent": "agent-b7", "role": "builder", "start": _ctx(BUILD_X)}],
                         got["over_start_budget"])
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)
        flagged = [ln for ln in text.splitlines() if "over the start budget" in ln]
        self.assertEqual(1, len(flagged), text)
        self.assertIn("agent-b7", flagged[0])
        self.assertIn(f"{_ctx(BUILD_X):,} tokens", flagged[0])
        self.assertIn(f"{budget:,}", flagged[0])

    def test_a_subagent_start_is_its_first_call_whatever_the_window(self) -> None:
        """US1132 AC4 under BG1254's window (round-1 REJECT). MUTANTS: a subagent's start read
        from its first call inside the open run's window rather than its transcript's first call
        (agent-lean, which started at 10,005 before the run and grew past the budget inside it,
        flagged; agent-heavy, which started at 125,005 before the run, missed); the window no
        longer deciding which subagents count (agent-gone, wholly before the run, flagged)."""
        ws = self._two_runs()
        start = meter._live("lib.sdlc_md").parse_iso8601(ws.state()["started_at"])
        before, inside = start - timedelta(minutes=10), start + timedelta(seconds=30)
        for name, calls in (("lean", ((LEAN_START, before), (HEAVY_START, inside))),
                            ("heavy", ((HEAVY_START, before), (LEAN_START, inside))),
                            ("gone", ((HEAVY_START, before),))):
            ws.tx._append(ws.tx.subagents / f"agent-{name}.jsonl", [
                _assistant(f"msg_{name}_{n}", usage, [{"type": "text"}], at=at)
                for n, (usage, at) in enumerate(calls)])
        budget = 100_000
        self.assertEqual((10_005, 125_005), (_ctx(LEAN_START), _ctx(HEAVY_START)))
        (ws.root / "sdlc-studio" / ".config.yaml").write_text(
            f"cost:\n  agent_start_budget: {budget}\n", encoding="utf-8")
        doc = self._json(ws)
        self.assertFalse(doc["window"]["whole_session"], doc["window"])
        self.assertEqual([("agent-b7", _ctx(BUILD_X)), ("agent-heavy", 125_005)],
                         sorted((o["agent"], o["start"]) for o in doc["over_start_budget"]))
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)
        flagged = [ln for ln in text.splitlines() if "over the start budget" in ln]
        self.assertEqual(2, len(flagged), text)
        self.assertTrue(any("agent-heavy" in ln and "125,005 tokens" in ln for ln in flagged))
        # the path beside: the whole session judges agent-gone too, at the same first calls
        rc, out = _cli(ws, "--session", "--format", "json")
        self.assertEqual(0, rc, out)
        self.assertEqual([("agent-b7", _ctx(BUILD_X)), ("agent-gone", 125_005),
                          ("agent-heavy", 125_005)],
                         sorted((o["agent"], o["start"])
                                for o in json.loads(out)["over_start_budget"]))

    def test_a_subagent_with_no_per_call_record_reads_not_available(self) -> None:
        """US1132 AC4 (round-1 REJECT). MUTANTS: a subagent whose records carry no message id
        skipped silently, with no not-available line for it; the whole check reading "none
        started over the start budget" when no subagent can be judged; an id-less subagent
        counted as cleared or flagged."""
        ws = self._session()
        noid = ws.tx.subagents / "agent-n1.jsonl"
        ws.tx._append(noid, [_assistant(None, HEAVY_START, [{"type": "text"}])])
        (ws.root / "sdlc-studio" / ".config.yaml").write_text(
            "cost:\n  agent_start_budget: 100000\n", encoding="utf-8")
        doc = self._json(ws)
        self.assertEqual(["agent-b7"], [o["agent"] for o in doc["over_start_budget"]])
        self.assertEqual(["agent-n1"], [o["agent"] for o in doc["start_not_available"]])
        rc, text = _cli(ws)
        self.assertEqual(0, rc, text)

        def section(rendered: str) -> str:
            return rendered.split("Subagent starts", 1)[1].split("\n\n", 1)[0]
        named = [ln for ln in section(text).splitlines() if "agent-n1" in ln]
        self.assertEqual(1, len(named), text)
        self.assertIn("not available", named[0])
        self.assertNotIn("over the start budget", named[0])
        # no subagent can be judged: the whole check is not available, not "none started over"
        lib = meter._live("lib.cost_anatomy")
        got = lib.build(ws.tx.main, [noid], {}, budget=100_000)
        self.assertIsNone(got["over_start_budget"])
        self.assertEqual(["agent-n1"], [o["agent"] for o in got["start_not_available"]])
        whole = section(lib.render(got))
        self.assertIn("not available", whole)
        self.assertNotIn("none started", whole)
        self.assertNotIn("no budget is configured", whole)
        # the path beside: a harness total has no per-call record, whatever the budget
        total = section(lib.render(lib.from_reading(
            {"harness": "cursor", "components": meter._sum(meter.MAIN_1)})))
        self.assertIn("not available: no per-call record exists", total)
        self.assertNotIn("no budget is configured", total)


    def _two_runs(self):
        """BG1254. A session that worked before the open run, every record timestamped as the
        harness writes them. Before the run: the main thread's msg_pre_1 (MAIN_1, whose Bash
        output of 500,000 characters three later calls re-read) and msg_pre_2 (MAIN_4), stamped
        at the very second the run starts; agent-old (AGENT_A), wholly before; agent-x2's first
        call (STRAY_Q0). Inside it: the main thread's msg_in_1 (MAIN_2, with a 3,000-character
        Read output) and msg_in_2 (MAIN_3); b7, the run's builder (BUILD_X, BUILD_Y); agent-x2's
        second call (OWN_X1). The run opens between the two, its start fixed so msg_pre_2 sits on
        it, and its opening reading holds exactly the first part."""
        ws = self._timed("two-runs")
        sdlc_md = meter._live("lib.sdlc_md")
        start = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=30)
        tx, before = ws.tx, start - timedelta(minutes=30)
        tx._append(tx.main, [
            _assistant("msg_pre_1", meter.MAIN_1,
                       [_tool_use("t_pre", "Bash", command="cat old.log")], at=before),
            _result("t_pre", 500_000, at=before + timedelta(seconds=1)),
            _assistant("msg_pre_2", MAIN_4, [{"type": "text"}], at=start)])
        tx._append(tx.subagents / "agent-old.jsonl",
                   [_assistant("msg_old", meter.AGENT_A, [{"type": "text"}], at=before)])
        tx._append(tx.subagents / "agent-x2.jsonl",
                   [_assistant("msg_x2_pre", STRAY_Q0, [{"type": "text"}], at=before)])
        with unittest.mock.patch.object(sdlc_md, "now_iso8601",
                                        return_value=start.strftime("%Y-%m-%dT%H:%M:%SZ")):
            ws.open()
        self.assertEqual(start, sdlc_md.parse_iso8601(ws.state()["started_at"]))

        def inside(n: int) -> datetime:
            return start + timedelta(seconds=5 + n)
        tx._append(tx.main, [
            _assistant("msg_in_1", MAIN_2, [_tool_use("t_in", "Read", file_path="src/a.py")],
                       at=inside(0)),
            _result("t_in", 3_000, at=inside(1)),
            _assistant("msg_in_2", MAIN_3, [{"type": "text"}], at=inside(2))])
        tx._append(tx.subagents / "agent-b7.jsonl", [
            _assistant("msg_b7_x", BUILD_X, [{"type": "text"}], at=inside(3)),
            _assistant("msg_b7_y", BUILD_Y, [{"type": "text"}], at=inside(4))])
        tx._append(tx.subagents / "agent-x2.jsonl",
                   [_assistant("msg_x2_in", OWN_X1, [{"type": "text"}], at=inside(5))])
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "b7")
        self.assertEqual(0, rc, out)
        return ws

    def _figures(self, doc: dict, expected: dict[str, tuple[int, tuple]]) -> None:
        """Each role's agents, calls and priced, and the total, against `expected`: role ->
        (agents, the usages of its calls)."""
        got = {row["role"]: row for row in doc["roles"]}
        for role, (agents, usages) in expected.items():
            self.assertEqual((agents, len(usages)), (got[role]["agents"], got[role]["calls"]), role)
            self.assertEqual(meter._priced(meter._sum(*usages)) if usages else 0,
                             got[role]["priced"], role)
        every = [u for _a, us in expected.values() for u in us]
        self.assertEqual(meter._priced(meter._sum(*every)), doc["total"]["priced"])
        self.assertEqual(sum(a for a, _us in expected.values()), doc["total"]["agents"])

    def _header(self, ws, *argv: str) -> str:
        rc, text = _cli(ws, *argv)
        self.assertEqual(0, rc, text)
        return text.split("\n\n", 1)[0]

    def test_the_anatomy_is_windowed_to_the_open_run(self) -> None:
        """BG1254 AC1. MUTANTS: `build` counting every record regardless of its timestamp; the
        window applied to the main thread alone, not the subagents (agent-old, agent-x2's first
        call); a subagent wholly before the run still counted as one of its agents; a tool output
        from before the run still named (t_pre's 1,500,000 would head the list); the window
        bounded at or before the start rather than after it; the header line dropped. The control:
        the meter's own delta over the run, its closing reading less its opening one."""
        ws = self._two_runs()
        state = ws.state()
        doc = self._json(ws)
        self._figures(doc, {"orchestrator": (1, (MAIN_2, MAIN_3)),
                            "builder": (1, (BUILD_X, BUILD_Y)), "reviewer": (0, ()),
                            "repair": (0, ()), "other": (1, (OWN_X1,))})
        other = next(row for row in doc["roles"] if row["role"] == "other")
        self.assertEqual(["agent-x2"], other["agent_ids"])
        self.assertEqual([("Read: src/a.py", 3_000, 1)],
                         [(o["producer"], o["size"], o["later_calls"]) for o in doc["outputs"]])
        self.assertEqual({"run_id": state["run_id"], "since": state["started_at"],
                          "whole_session": False, "reason": None}, doc["window"])
        # the start context stays the session's first call, which the window does not move
        self.assertEqual(_ctx(meter.MAIN_1), doc["start_context"])
        rs = meter._live("lib.run_state")
        self.assertIsNotNone(rs.stamp_tokens(ws.root, "close"))
        stamps = ws.state()[rs.TOKEN_STAMPS]
        self.assertEqual(stamps[-1]["priced"] - stamps[0]["priced"], doc["total"]["priced"])
        line = next((ln for ln in self._header(ws).splitlines() if "window:" in ln), "")
        self.assertIn(f"the open run {state['run_id']}", line)
        self.assertIn(f"after its start {state['started_at']}", line)

    def test_the_session_flag_reads_the_whole_session(self) -> None:
        """BG1254 AC2. MUTANTS: `--session` ignored, so the window still applies; `--session`
        reading the run's window for the subagents; the header still naming the run. The control:
        the meter's own reading of the whole session."""
        ws = self._two_runs()
        rc, out = _cli(ws, "--session", "--format", "json")
        self.assertEqual(0, rc, out)
        doc = json.loads(out)
        self._figures(doc, {"orchestrator": (1, (meter.MAIN_1, MAIN_4, MAIN_2, MAIN_3)),
                            "builder": (1, (BUILD_X, BUILD_Y)), "reviewer": (0, ()),
                            "repair": (0, ()),
                            "other": (2, (meter.AGENT_A, STRAY_Q0, OWN_X1))})
        self.assertEqual(meter._live("lib.run_state").claude_tokens(ws.root)["priced"],
                         doc["total"]["priced"])
        self.assertEqual(("Bash: cat old.log", 500_000, 3),
                         tuple(doc["outputs"][0][k] for k in ("producer", "size", "later_calls")))
        self.assertEqual({"run_id": None, "since": None, "whole_session": True,
                          "reason": "--session names the whole session"}, doc["window"])
        line = next((ln for ln in self._header(ws, "--session").splitlines() if "window:" in ln),
                    "")
        self.assertIn("the whole session", line)
        self.assertIn("--session", line)
        self.assertNotIn(ws.state()["run_id"], line)

    def test_with_no_open_run_the_session_is_named_not_zeroed(self) -> None:
        """BG1254 AC3. MUTANTS: a window with no start defaulting to nothing, which prints a zero
        anatomy; a closed run's start still taken as the window; a header that does not say no
        run is open; a usage record with no timestamp dropped from a windowed read rather than
        the whole session read and named; a harness reading given no window. The control: the
        meter's own reading of the whole session, which is not zero."""
        rs = meter._live("lib.run_state")

        def closed():
            ws = self._two_runs()
            rs.close_run(ws.root, rs.GOAL_REACHED)
            self.assertFalse(rs.is_open(ws.root), "premise: the run is closed")
            return ws, {"orchestrator": (1, (meter.MAIN_1, MAIN_4, MAIN_2, MAIN_3)),
                        "builder": (1, (BUILD_X, BUILD_Y)),
                        "other": (2, (meter.AGENT_A, STRAY_Q0, OWN_X1))}

        def never():
            ws = self._timed("never-opened")   # points the meter at its own transcripts
            ws.tx._append(ws.tx.main, [
                _assistant("msg_n1", meter.MAIN_1, [{"type": "text"}],
                           at=datetime.now(timezone.utc) - timedelta(hours=2))])
            self.assertEqual({}, ws.state(), "premise: no run was ever opened")
            return ws, {"orchestrator": (1, (meter.MAIN_1,))}

        for make in (closed, never):
            case, expected = make()
            doc = self._json(case)
            self.assertNotEqual(0, doc["total"]["priced"])
            self.assertEqual(rs.claude_tokens(case.root)["priced"], doc["total"]["priced"])
            self._figures(doc, {r: expected.get(r, (0, ())) for r in
                                ("orchestrator", "builder", "reviewer", "repair", "other")})
            self.assertEqual({"run_id": None, "since": None, "whole_session": True,
                              "reason": "no run is open"}, doc["window"])
            line = next((ln for ln in self._header(case).splitlines() if "window:" in ln), "")
            self.assertIn("the whole session", line)
            self.assertIn("no run is open", line)
        # an open run over usage records that carry no timestamp reads the whole session, and
        # says why, rather than dropping the records it cannot place
        doc = self._json(self._session())
        self.assertTrue(doc["window"]["whole_session"])
        self.assertIn("no timestamp", doc["window"]["reason"])
        self.assertNotEqual(0, doc["total"]["priced"])
        anatomy = meter._live("lib.cost_anatomy")
        got = anatomy.from_reading({"harness": "cursor", "components": meter._sum(meter.MAIN_1)})
        self.assertTrue(got["window"]["whole_session"])
        self.assertIn("window: the whole session", anatomy.render(got))

if __name__ == "__main__":
    unittest.main()
