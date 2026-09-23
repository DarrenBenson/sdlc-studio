"""US0871: each batch unit's elapsed time and tokens are measured as it is delivered.

Every test drives `transition.py set` through `transition.main`, in a temporary workspace with
its own transcript directory, so the token meter read is one the test wrote and the clock is
one the test set. Nothing reads the operator's real transcripts or this repository's state.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import transition  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

T0 = datetime(2026, 9, 23, 9, 0, tzinfo=timezone.utc)


class _Workspace:
    def __init__(self, d: str, units=("US0001", "US0002")) -> None:
        self.root = Path(d) / "repo"
        self.transcripts = Path(d) / "transcripts"
        self.transcripts.mkdir()
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid in units:
            (stories / f"{uid}-u.md").write_text(
                f"# {uid}: u\n\n> **Status:** Ready\n> **Points:** 2\n\n"
                "## Acceptance Criteria\n\n- **AC1:** works\n", encoding="utf-8")

    def spend(self, tokens: int) -> None:
        """Append one usage record to the session transcript - the meter moves by `tokens`."""
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def move(self, uid: str, status: str, at: datetime) -> str:
        buf = io.StringIO()
        stamp = at.isoformat().replace("+00:00", "Z")
        with mock.patch.object(run_state, "_unit_clock", lambda: stamp), \
                contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = transition.main(["set", "--id", uid, "--status", status, "--force",
                                  "--root", str(self.root)])
        assert rc == 0, buf.getvalue()
        text = (self.root / "sdlc-studio" / "stories" / f"{uid}-u.md").read_text(
            encoding="utf-8")
        return sdlc_md.extract_field(text, "Status") or ""

    def actuals(self) -> dict:
        return run_state.read(self.root).get(run_state.UNIT_ACTUALS) or {}


class UnitActualsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.ws = _Workspace(self._tmp.name)
        env = mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(self.ws.transcripts)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(self._tmp.cleanup)

    def test_starting_a_unit_stamps_its_time_and_tokens(self) -> None:
        """AC1. MUTANTS: stamp the session meter's raw reading instead of the run's total; skip
        the stamp; stamp at any status rather than In Progress. Each misstates `start_tokens`,
        leaves no entry, or records the Ready move."""
        ws = self.ws
        ws.spend(1000)
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        ws.spend(200)
        self.assertEqual(ws.move("US0001", "In Progress", T0), "In Progress")
        entry = ws.actuals()["US0001"]
        self.assertEqual(entry["started_at"], "2026-09-23T09:00:00Z")
        self.assertEqual(entry["start_tokens"], 200, "the run's total, not the meter's 1200")
        self.assertIs(entry["open"], True)

    def test_finishing_a_unit_records_minutes_and_tokens(self) -> None:
        """AC2. MUTANTS: restart rather than accumulate on re-entry; restart the clock when an
        open unit re-enters In Progress; never close the entry. Each misstates the totals."""
        ws = self.ws
        ws.spend(1000)
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        ws.move("US0001", "In Progress", T0)
        ws.spend(300)
        ws.move("US0001", "Review", T0 + timedelta(minutes=5))
        ws.move("US0001", "In Progress", T0 + timedelta(minutes=8))    # still open: no restart
        self.assertEqual(ws.move("US0001", "Done", T0 + timedelta(minutes=12)), "Done")
        entry = ws.actuals()["US0001"]
        self.assertEqual((entry["minutes"], entry["tokens"], entry["open"]), (12.0, 300, False))
        # reopened and delivered again: the second span adds to the first
        ws.move("US0001", "In Progress", T0 + timedelta(minutes=30))
        ws.spend(50)
        ws.move("US0001", "Done", T0 + timedelta(minutes=33))
        entry = ws.actuals()["US0001"]
        self.assertEqual((entry["minutes"], entry["tokens"], entry["open"]), (15.0, 350, False))

    def test_a_unit_outside_a_run_records_nothing(self) -> None:
        """AC3. MUTANTS: record for any unit an open run's state names, or with no open run.
        Each writes an entry; the transitions themselves must still land."""
        ws = self.ws
        ws.spend(1000)
        self.assertEqual(ws.move("US0001", "In Progress", T0), "In Progress")
        self.assertEqual(ws.move("US0001", "Done", T0 + timedelta(minutes=5)), "Done")
        self.assertFalse(run_state.path(ws.root).exists(), "a run state was written")
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        self.assertEqual(ws.move("US0002", "In Progress", T0), "In Progress")
        self.assertEqual(ws.move("US0002", "Done", T0 + timedelta(minutes=5)), "Done")
        self.assertEqual(ws.actuals(), {})

    def test_an_unreadable_meter_is_not_measured(self) -> None:
        """AC4. MUTANT: default an unmeasured token total to 0, so the unit reads 0 tokens."""
        ws = self.ws                     # the transcript directory holds no transcript at all
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        ws.move("US0001", "In Progress", T0)
        ws.move("US0001", "Done", T0 + timedelta(minutes=7))
        entry = ws.actuals()["US0001"]
        self.assertIsNone(entry["start_tokens"])
        self.assertIsNone(entry["tokens"], "an unread meter was recorded as a number")
        self.assertEqual(entry["minutes"], 7.0, "the clock is measured even when tokens are not")

    def test_an_end_the_meter_cannot_read_is_not_measured(self) -> None:
        """AC4, the closing end. MUTANTS: take the delta from the run's total when no closing
        reading was taken, so the unit reads 0; accept a closing reading from another session,
        whose meter is not the one the span opened on, so the unit reads 0 again. The control:
        the same span with a closing reading of the opening session is measured."""
        ws = self.ws
        ws.spend(1000)
        run_state.open_run(ws.root, batch=["US0001", "US0002"], goal="g")
        ws.move("US0001", "In Progress", T0)
        ws.move("US0002", "In Progress", T0)
        ws.spend(300)
        self.assertEqual(ws.move("US0002", "Done", T0 + timedelta(minutes=4)), "Done")
        self.assertEqual(ws.actuals()["US0002"]["tokens"], 300, "the control was not measured")
        ws.spend(500)
        with mock.patch.object(run_state, "_stamp", lambda *a, **k: None):   # meter unreadable
            self.assertEqual(ws.move("US0001", "Done", T0 + timedelta(minutes=5)), "Done")
        entry = ws.actuals()["US0001"]
        self.assertIsNone(entry["tokens"], "a span with no closing reading read as a number")
        self.assertEqual(entry["minutes"], 5.0)

        ws.move("US0002", "In Progress", T0 + timedelta(minutes=10))
        later = Path(self._tmp.name) / "later-session"      # the unit finishes in a new session
        later.mkdir()
        (later / "other.jsonl").write_text(json.dumps({"message": {"model": "m", "usage": {
            "input_tokens": 9000, "output_tokens": 0}}}) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(later)}):
            ws.move("US0002", "Done", T0 + timedelta(minutes=12))
        self.assertIsNone(ws.actuals()["US0002"]["tokens"],
                          "a span closed on another session's meter read as a number")

    def test_a_closed_run_records_nothing(self) -> None:
        """AC3, a run that has closed. MUTANT: drop the outcome check, so a closed run whose
        batch still names the unit keeps recording."""
        ws = self.ws
        ws.spend(1000)
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        run_state.update(ws.root, outcome="goal-reached")
        self.assertEqual(run_state.read(ws.root)["batch"], ["US0001"], "premise: batch named")
        self.assertEqual(ws.move("US0001", "In Progress", T0), "In Progress")
        self.assertEqual(ws.move("US0001", "Done", T0 + timedelta(minutes=5)), "Done")
        self.assertEqual(ws.actuals(), {})

    def test_a_failed_recording_never_fails_the_transition(self) -> None:
        """The transition has landed before anything is recorded. MUTANT: narrow the catch
        round the recording, so a TypeError from a corrupt entry escapes after the write."""
        ws = self.ws
        run_state.open_run(ws.root, batch=["US0001"], goal="g")
        with mock.patch.object(run_state, "record_unit_actual",
                               side_effect=TypeError("corrupt unit_actuals")):
            self.assertEqual(ws.move("US0001", "In Progress", T0), "In Progress")


if __name__ == "__main__":
    unittest.main()
