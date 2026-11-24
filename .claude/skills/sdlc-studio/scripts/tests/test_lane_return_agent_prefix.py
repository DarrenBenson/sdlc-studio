"""BG1454: `sprint lane return --agent agent-<id>` prices the unit, as the bare id does.

`lane land` prints the builder as `agent-<id>`, so that is the form an operator copies; the
return looked for `agent-agent-<id>.jsonl` and recorded nothing. The id is now taken with or
without its `agent-` prefix.

Every case drives the command (`sprint.main(["lane", "return", ...])`) over US1091's fixture
harness store (`test_meter_reads_true`) and reads the record the command wrote.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_meter_reads_true as meter  # noqa: E402 - US1091's harness store and workspace

BUILD = meter._usage(40, 400, 5_000, 0, 120_000)


def _says(tx, agent: str, msg_id: str, usage: dict) -> None:
    """`agent` logs one message to its own transcript, `agent-<agent>.jsonl`."""
    tx._append(tx.subagents / f"agent-{agent}.jsonl", [json.dumps(
        {"type": "assistant", "cwd": "/work/repo",
         "message": {"id": msg_id, "model": meter.MODEL, "role": "assistant",
                     "content": [{"type": "text"}], "usage": usage}})])


class LaneReturnAgentPrefixTests(meter._Case):
    def _returned(self, transcript: str, given: str) -> tuple[list[dict], str]:
        """A builder whose transcript is `agent-<transcript>.jsonl`, returned with
        `--agent <given>`: the unit's delegated records and the command's output."""
        ws = self.workspace()
        ws.open()
        _says(ws.tx, transcript, "msg_build", BUILD)
        rc, out = ws.lane("return", "--units", "US0101", "--agent", given)
        self.assertEqual(0, rc, out)
        recs = [r for r in ws.state().get(self.rs.DELEGATED) or [] if r.get("unit") == "US0101"]
        return recs, out

    def _assert_priced(self, recs: list[dict], out: str, transcript: str) -> None:
        self.assertEqual(1, len(recs), out)
        [rec] = recs
        self.assertEqual(f"agent-{transcript}.jsonl", Path(rec["transcript"]).name)
        self.assertEqual(meter._priced(meter._parts(BUILD)), rec["priced"])
        self.assertEqual(self.rs.READ_FROM_TRANSCRIPT, rec["provenance"])
        self.assertEqual(f"agent-{transcript}", rec["agent"])
        self.assertNotIn("was not priced", out)

    def test_the_printed_agent_prefixed_id_prices_the_unit(self) -> None:
        """AC1. MUTANT: the id used as given, so the return reads `agent-agent-<id>.jsonl`,
        finds none and records no priced cost."""
        recs, out = self._returned("a19d0c", "agent-a19d0c")
        self._assert_priced(recs, out, "a19d0c")

    def test_the_bare_id_still_prices_the_unit(self) -> None:
        """The control: the bare id, which worked before, prices the same transcript."""
        recs, out = self._returned("a19d0c", "a19d0c")
        self._assert_priced(recs, out, "a19d0c")

    def test_a_bare_id_holding_agent_but_not_as_its_prefix_is_kept(self) -> None:
        """The control on the prefix test: `xagent-7` does not start with `agent-`, so it is
        read as given, from `agent-xagent-7.jsonl`."""
        recs, out = self._returned("xagent-7", "xagent-7")
        self._assert_priced(recs, out, "xagent-7")

    def test_a_missing_transcript_is_still_named_unpriced(self) -> None:
        """The control on the refusal: a prefixed id with no transcript records no priced
        cost and says so, naming the bare id's transcript it looked for."""
        ws = self.workspace()
        ws.open()
        rc, out = ws.lane("return", "--units", "US0101", "--agent", "agent-nobody1")
        self.assertEqual(0, rc, out)
        self.assertIn("WARNING --agent nobody1 was not priced", out)
        self.assertIn("agent-nobody1.jsonl", out)
        self.assertNotIn("agent-agent-", out)


if __name__ == "__main__":
    unittest.main()
