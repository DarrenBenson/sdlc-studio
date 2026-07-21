"""BG0236: the run's session-token baseline - the reading `open_run` stamps so a close can
report what THIS run spent rather than what the session has spent.

The harness transcript is one cumulative meter per session. Without a baseline the second
sprint closed in a session books the first sprint's tokens as its own, and the third books
both; that shipped 341,450 and then 472,691 tokens per point against a measured ~25,000/pt
rate, twice corrected by hand afterwards.

The properties pinned here are the writer's half:

* a FRESH run is stamped with the meter reading and the session it was read from;
* a RE-PLAN of the open run leaves that reading alone (moving it forward mid-run would
  discount everything spent before the re-cut);
* every later write PRESERVES it - `update`, a review round, `close_run`, the archive
  (L-0156: an upsert that rewrites a whole record erases the field it was told to keep);
* an unreadable session leaves it ABSENT rather than zero, and never fails the plan.

The reading half - what a close does with a missing baseline - is pinned in `test_retro.py`
(`TokenCaptureIsAttributedToTheRun`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k run_state
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import run_state  # noqa: E402


class TokenBaselineTests(unittest.TestCase):
    """The baseline `open_run` stamps, and everything that must not lose it."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.transcripts = self.root / "transcripts"
        self.transcripts.mkdir()
        env = mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self.tmp.cleanup)

    def _meter(self, tokens: int, name: str = "s1.jsonl") -> Path:
        """Append `tokens` to a session transcript - the harness meter running on."""
        p = self.transcripts / name
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"usage": {"input_tokens": tokens}}}) + "\n")
        return p

    def _baseline(self) -> dict | None:
        return run_state.read(str(self.root)).get(run_state.TOKEN_BASELINE)

    def test_run_state_open_run_stamps_the_session_meter_and_its_source(self) -> None:
        src = self._meter(120_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        base = self._baseline()
        self.assertEqual(base["tokens"], 120_000)
        self.assertEqual(base["source"], str(src))
        self.assertTrue(base["at"], "the reading is timestamped")

    def test_run_state_replanning_an_open_run_leaves_its_baseline_alone(self) -> None:
        self._meter(100_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self._meter(400_000)                       # the run spends while it is open
        run_state.open_run(str(self.root), batch=["BG0002"])   # a mid-run re-cut
        self.assertEqual(self._baseline()["tokens"], 100_000,
                         "a re-plan must not discount what the run has already spent")
        self.assertEqual(run_state.read(str(self.root))["batch"], ["BG0001", "BG0002"])

    def test_run_state_the_next_run_takes_a_fresh_baseline(self) -> None:
        self._meter(100_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self._meter(900_000)                       # the first run's spend
        run_state.close_run(str(self.root), run_state.GOAL_REACHED)
        run_state.open_run(str(self.root), batch=["BG0002"], goal="g2")
        self.assertEqual(self._baseline()["tokens"], 1_000_000,
                         "the second run starts from where the first one left the meter")

    def test_run_state_the_baseline_survives_every_later_write(self) -> None:
        # L-0156: `update` and `close_run` rewrite the whole record. Each is a chance to drop
        # the field, and a dropped baseline reads exactly like a run opened before it existed.
        self._meter(250_000)
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        run_state.update(str(self.root), appetite={"minutes": 90, "units": 6})
        self.assertEqual(self._baseline()["tokens"], 250_000, "update dropped it")
        run_state.record_review_round(str(self.root), "APPROVE", units=["BG0001"])
        self.assertEqual(self._baseline()["tokens"], 250_000, "a review round dropped it")
        run_state.record_ceiling_override(str(self.root), at_round=2, ceiling=1)
        self.assertEqual(self._baseline()["tokens"], 250_000, "a ceiling override dropped it")
        closed = run_state.close_run(str(self.root), run_state.GOAL_REACHED, handoff="HO0001")
        self.assertEqual(self._baseline()["tokens"], 250_000, "the close dropped it")
        self.assertEqual(closed[run_state.TOKEN_BASELINE]["tokens"], 250_000)
        archived = run_state.read_archived(str(self.root), closed["run_id"])
        self.assertEqual(archived[run_state.TOKEN_BASELINE]["tokens"], 250_000,
                         "the archived record carries the baseline too")

    def test_run_state_an_unreadable_session_leaves_the_baseline_absent(self) -> None:
        # No transcript at all: the plan must still open its run, and the baseline must be
        # None rather than 0 - a zero baseline would make the close publish the whole
        # session total as the sprint's own cost, which is the defect.
        with mock.patch.dict(os.environ, {"SDLC_STUDIO_TRANSCRIPTS": str(self.root / "nope")}):
            state = run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self.assertTrue(state["run_id"], "the run still opens")
        self.assertIsNone(state[run_state.TOKEN_BASELINE])

    def test_run_state_a_session_with_no_usage_yet_leaves_the_baseline_absent(self) -> None:
        # A deliberate false negative, stated where it is made: a transcript that exists but
        # carries no usage has a true baseline of zero, and this refuses to assume it. The
        # sprint then reports NOT ATTRIBUTABLE - a lost measurement, never a wrong one.
        (self.transcripts / "s1.jsonl").write_text('{"type": "meta"}\n', encoding="utf-8")
        run_state.open_run(str(self.root), batch=["BG0001"], goal="g")
        self.assertIsNone(self._baseline())

    def test_run_state_a_run_nobody_opened_has_no_baseline(self) -> None:
        self._meter(700_000)
        run_state.update(str(self.root), goal="g")
        self.assertIsNone(self._baseline(), "no fabricated baseline on a blank record")

    def test_run_state_the_baseline_field_is_declared_in_fields(self) -> None:
        # FIELDS documents the record; a field the module writes but does not list there is
        # a field the next reader of this module does not know exists.
        self.assertIn(run_state.TOKEN_BASELINE, run_state.FIELDS)


class SessionTokenReaderTests(unittest.TestCase):
    """`session_tokens` is the ONE meter reader, shared by the baseline stamp and the close.
    Its own contract - cache reads excluded, a stated reason when it cannot read - is pinned
    through `retro.harness_tokens` in `test_retro.py`; what matters here is that the two are
    literally the same function, so they cannot drift apart."""

    def test_run_state_reader_is_the_same_object_retro_exposes(self) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import retro
        self.assertIs(retro.harness_tokens, run_state.session_tokens)
        self.assertEqual(retro.TRANSCRIPTS_ENV, run_state.TRANSCRIPTS_ENV)


if __name__ == "__main__":
    unittest.main()
