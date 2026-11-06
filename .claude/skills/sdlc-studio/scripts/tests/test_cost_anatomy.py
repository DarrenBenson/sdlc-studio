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
import sys
import unittest
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

#: q0's prompt reads as a reviewer's, and no record names q0.
REVIEWER_WORDED_PROMPT = ("You are the independent reviewer of US0101. Review the builder's "
                          "diff as the QA seat reviewer and return a verdict.")


def _ctx(usage: dict) -> int:
    p = meter._parts(usage)
    return p["input"] + p["cache_write_5m"] + p["cache_write_1h"] + p["cache_read"]


def _assistant(msg_id: str | None, usage: dict, blocks: list[dict]) -> str:
    msg = {"model": meter.MODEL, "role": "assistant", "content": blocks, "usage": dict(usage)}
    if msg_id is not None:
        msg["id"] = msg_id
    return json.dumps({"type": "assistant", "cwd": "/work/repo", "message": msg})


def _tool_use(tid: str, name: str, **inp) -> dict:
    return {"type": "tool_use", "id": tid, "name": name, "input": inp}


def _result(tid: str, size: int, as_list: bool = False) -> str:
    content = [{"type": "text", "text": "x" * size}] if as_list else "y" * size
    return json.dumps({"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tid, "content": content}]}})


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


if __name__ == "__main__":
    unittest.main()
