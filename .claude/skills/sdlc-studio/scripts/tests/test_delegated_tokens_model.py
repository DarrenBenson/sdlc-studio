"""US0999: a delegated agent's token total records the model that spent it (CR0610).

A builder's total supplied with `sprint lane return --tokens` and one supplied with `retro.py
accuracy --delegated-tokens` landed on the run record with no model, so the spend most of a
fan-out sprint costs could not be said to have run on anything. Each recorder now takes the model
the agent reported (`lane return --model`, `lane accept --model`, `accuracy --delegated-model`),
stores it on the delegated entry and prints it. A total given with no model carries none: the
main thread's model is never filled in for it, since that would price a smaller model's subagent
at the session's larger model's rate.

Every test drives the shipped entry points in-process against a throwaway workspace with its own
transcript directory, reusing the lane workspace of `test_lean_lane_delegated_tokens`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from datetime import timedelta
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_lean_lane_delegated_tokens import RETRO, T0, _live, _Workspace  # noqa: E402

#: the main thread's own model, written into the session transcript, so a recorder that filled a
#: missing model in from the session would be seen doing it
SESSION_MODEL = "claude-opus-5-5"
#: the keys a supplied, unit-tagged total carried before a model could be given
BEFORE = {"tokens", "agent", "note", "provenance", "recorded_at", "unit"}


class DelegatedModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = _Workspace(self._tmp.name)
        with (self.ws.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": SESSION_MODEL, "usage": {
                "input_tokens": 4000, "output_tokens": 0}}}) + "\n")
        env = unittest.mock.patch.dict(
            os.environ, {_live("lib.run_state").TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def records(self) -> dict:
        rs = _live("lib.run_state")
        return {r.get("unit"): r for r in rs.delegated_records(rs.read(self.ws.root))}

    def accuracy(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("retro").main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                                      *argv])
        return rc, out.getvalue()

    def accept_passthrough(self, *argv: str) -> list[str]:
        """The argv `lane accept` hands the `lane return` an APPROVE ends with."""
        got: dict = {}

        def recorder(*a, **k):
            got.update(k)
            return 0
        with unittest.mock.patch.object(_live("lib.lanes"), "accept", recorder):
            rc, out = self.ws.lane("accept", "--unit", "US0101", "--verdict", "v.txt",
                                   "--reviewer", "qa-seat", *argv, at=T0)
        self.assertEqual(0, rc, out)
        return list(got["passthrough"])

    def test_both_recorders_store_the_model(self) -> None:
        """AC1. MUTANTS: `--model` parsed but never passed to `record_delegated_tokens`, so the
        lane entry carries no model; `--delegated-model` parsed and dropped the same way; the
        model stored but not printed by either command; `lane accept` not handing `--model` to
        the return it ends with; a split total recording the model on none of its shares."""
        ws = self.ws
        out = ws.deliver("US0101", "--tokens", "120000", "--model", "claude-sonnet-4-6")
        self.assertIn("120,000 tokens, model claude-sonnet-4-6", out)
        rc, said = self.accuracy("--delegated-tokens", "80000", "--delegated-agent", "reviewer",
                                 "--delegated-unit", "US0102",
                                 "--delegated-model", "claude-opus-5-5")
        self.assertEqual(0, rc, said)
        self.assertIn("80,000 for reviewer against US0102, model claude-opus-5-5", said)
        recs = self.records()
        self.assertEqual("claude-sonnet-4-6", recs["US0101"]["model"])
        self.assertEqual(120_000, recs["US0101"]["tokens"])
        self.assertEqual("claude-opus-5-5", recs["US0102"]["model"])
        self.assertEqual(80_000, recs["US0102"]["tokens"])
        # lane accept hands the model on, beside the total it describes
        back = self.accept_passthrough("--tokens", "1200", "--model", "claude-sonnet-4-6")
        self.assertIn(("--model", "claude-sonnet-4-6"), list(zip(back, back[1:])))
        self.assertIn(("--tokens", "1200"), list(zip(back, back[1:])))
        self.assertNotIn("--model", self.accept_passthrough("--tokens", "1200"))
        # one total split between two units by points: each share names the model
        rc, out = ws.lane("return", "--units", "US0101", "US0102", "--tokens", "90000",
                          "--model", "claude-haiku-4-5", at=T0 + timedelta(minutes=9))
        self.assertEqual(0, rc, out)
        recs = self.records()
        rs = _live("lib.run_state")
        for uid in ("US0101", "US0102"):
            self.assertEqual("claude-haiku-4-5", recs[uid]["model"], uid)
            self.assertIsInstance(recs[uid].get(rs.APPORTIONED), dict, uid)
        self.assertEqual(2, out.count("model claude-haiku-4-5"), out)

    def test_a_missing_model_is_never_guessed(self) -> None:
        """AC2. MUTANTS: a missing model defaulted to the main thread's model (the session
        transcript names one); an empty model recorded as an empty `model` key; a blank
        `--model` recorded as given; the print naming a model for a total that has none; the
        page reading differently for a run whose totals carry no model."""
        ws = self.ws
        out = ws.deliver("US0101", "--tokens", "120000")
        line = next(ln for ln in out.splitlines() if "agent total recorded" in ln)
        self.assertNotIn("model", line)
        self.assertNotIn(SESSION_MODEL, out)
        rc, said = self.accuracy("--delegated-tokens", "80000", "--delegated-unit", "US0102")
        self.assertEqual(0, rc, said)
        recorded = next(ln for ln in said.splitlines() if "delegated total recorded" in ln)
        self.assertEqual("delegated total recorded (supplied, not measured): 80,000 against "
                         "US0102", recorded)
        recs = self.records()
        for uid in ("US0101", "US0102"):
            self.assertEqual(BEFORE, set(recs[uid]), uid)
        # a blank model is no model
        rs = _live("lib.run_state")
        got = rs.record_delegated_tokens(ws.root, 5000, unit="US0101", model="  ")
        self.assertNotIn("model", got)
        # a model with no total to describe records nothing
        rc, said = self.accuracy("--delegated-model", "claude-opus-5-5")
        self.assertEqual(2, rc, said)
        self.assertIn("nothing was recorded", said)
        self.assertEqual(3, len(rs.delegated_records(rs.read(ws.root))))
        # every record holds only the keys it held before a model could be given, so the page,
        # which derives from the record, reads as it did; its delegated figure names no model
        page = ws.page()
        self.assertEqual(205_000, ws.delegated(page)["value"])
        self.assertNotIn(SESSION_MODEL, json.dumps(ws.delegated(page), default=str))
        self.assertNotIn("claude-", json.dumps(
            next(s for s in page["sections"] if s["key"] == "estimates"), default=str))


if __name__ == "__main__":
    unittest.main()
