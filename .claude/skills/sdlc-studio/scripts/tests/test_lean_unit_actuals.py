"""US0871: each batch unit's elapsed time and tokens are measured as it is delivered.

BG0797: or as its delegated agents report them, tagged to the unit. The lean loop runs several
agents at once and moves a unit from Draft to Done at landing, so an In Progress span on the
shared main-thread meter is either absent or counts the other units' traffic. Each agent's own
reported total, recorded with `retro.py accuracy --delegated-unit`, is the unit's spend.

Every test drives `transition.py set` through `transition.main`, in a temporary workspace with
its own transcript directory, so the token meter read is one the test wrote and the clock is
one the test set. Nothing reads the operator's real transcripts or this repository's state.
"""
from __future__ import annotations

import contextlib
import importlib
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
RETRO = "RETRO0001"


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

    def _tagged_run(self) -> None:
        """An open run over US0001 and US0002, a plan snapshot forecasting both, and a retro,
        so `retro.py accuracy` can record against it and the report can derive."""
        retros = self.ws.root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-a-sprint.md").write_text(
            f"# {RETRO}: a sprint\n\n> **Batch:** US0001, US0002\n", encoding="utf-8")
        self.ws.spend(1000)
        run_state.open_run(self.ws.root, batch=["US0001", "US0002"], goal="g")
        run_state.update(self.ws.root, plan_snapshot={"units": {
            uid: {"planned_points": 2, "forecast_minutes": 20.0, "forecast_tokens": 200_000,
                  "added": False} for uid in ("US0001", "US0002")}})

    def _record(self, *argv: str) -> None:
        retro = importlib.import_module("retro")
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = retro.main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                             "--delegated-agent", "a story agent", *argv])
        self.assertEqual(0, rc, out.getvalue())

    def _report(self) -> tuple[dict, str]:
        sr = importlib.import_module("sprint_report")
        rep = sr.build_report(self.ws.root, RETRO)
        return rep, sr.render_markdown(rep)

    @staticmethod
    def _section(rep: dict, key: str) -> dict:
        return next(s for s in rep["sections"] if s["key"] == key)

    def _unit_rows(self, rep: dict) -> dict:
        return {r["unit_id"]["value"]: r for r in self._section(rep, "estimates")["unit_rows"]}

    def test_a_unit_s_tagged_delegated_totals_are_its_actuals(self) -> None:
        """AC1. MUTANTS: HEAD's ledger, which reads only the In Progress span (5.0 minutes and
        300 tokens of main-thread traffic here); summing the tokens but not the minutes; no
        label, so an agent's figure reads as a span."""
        self._tagged_run()
        ws = self.ws
        ws.move("US0001", "In Progress", T0)
        ws.spend(300)                                  # main-thread traffic, not US0001's own
        ws.move("US0001", "Done", T0 + timedelta(minutes=5))
        self._record("--delegated-tokens", "40000", "--delegated-unit", "us0001",
                     "--delegated-minutes", "12")
        self._record("--delegated-tokens", "2500", "--delegated-unit", "US0001",
                     "--delegated-minutes", "3.5")
        rep, md = self._report()
        row = self._unit_rows(rep)["US0001"]
        self.assertEqual((42_500, "agent tokens"),
                         (row["eu_tokens"]["value"], row["eu_tokens"].get("label")))
        self.assertEqual((15.5, "agent minutes"),
                         (row["eu_minutes"]["value"], row["eu_minutes"].get("label")))
        self.assertIn("| 15.5 agent minutes |", md)
        self.assertIn("| 42,500 agent tokens |", md)
        # The headers name no single source: each cell's label does, in both renders.
        self.assertIn("| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |", md)
        html = importlib.import_module("sprint_report").render_html(rep)
        for label, page in (("markdown", md), ("html", html)):
            text = " ".join(page.split())
            self.assertIn("Each cell names its source.", text, label)
            self.assertNotIn("measured over its own open span", text, label)
            self.assertNotIn("(open span)", text, label)
        self.assertIn('<th scope="col" class="num">Minutes</th>', html)
        self.assertIn('<th scope="col" class="num">Tokens</th>', html)
        self.assertIn("15.5 agent minutes", html)

    def test_tagged_totals_count_once_in_the_run_total(self) -> None:
        """AC2. MUTANT: add the per-unit sums to the run's total beside the records they came
        from, so the tagged 42,500 counts twice."""
        self._tagged_run()
        ws = self.ws
        ws.spend(500)
        ws.move("US0001", "In Progress", T0)           # a second reading: the meter moved 500
        self._record("--delegated-tokens", "40000", "--delegated-unit", "US0001")
        self._record("--delegated-tokens", "2500", "--delegated-unit", "US0001")
        self._record("--delegated-tokens", "7000")      # untagged: the reviewer's own total
        state = run_state.read(ws.root)
        self.assertEqual(49_500, run_state.delegated_total(state))
        rep, _md = self._report()
        tokens = next(r for r in self._section(rep, "estimates")["rows"]
                      if r["est_measure"]["value"] == "Tokens")
        self.assertEqual(500 + 49_500, tokens["est_actual"]["value"])
        delegated = self._section(rep, "cost")["figures"]["tokens_delegated"]
        self.assertEqual(49_500, delegated["value"])
        self.assertEqual(42_500, self._unit_rows(rep)["US0001"]["eu_tokens"]["value"])

    def test_an_unmeasured_unit_names_why(self) -> None:
        """AC3. MUTANT: the bare `not recorded` RPT0010 printed, which names no source and no
        remedy."""
        self._tagged_run()
        self._record("--delegated-tokens", "40000", "--delegated-unit", "US0001")
        rep, md = self._report()
        row = self._unit_rows(rep)["US0002"]
        for key in ("eu_minutes", "eu_tokens"):
            cell = row[key]
            self.assertEqual("NOT MEASURED", cell["value"], key)
            self.assertIn("In Progress span", cell["reason"], key)
            self.assertIn("tagged", cell["reason"], key)
            self.assertIn("--delegated-unit US0002", cell["reason"], key)
        self.assertIn("--delegated-unit US0002", md)
        # US0001's agent recorded tokens and no minutes: the minutes cell says that instead,
        # and names a remedy that can be followed - not a flag that adds a second record.
        minutes = self._unit_rows(rep)["US0001"]["eu_minutes"]
        self.assertEqual("NOT MEASURED", minutes["value"])
        self.assertIn("0 of its 1 tagged agent(s) reported minutes", minutes["reason"])
        self.assertIn("cannot be added afterwards", minutes["reason"])

    def test_minutes_from_some_of_a_unit_s_agents_are_not_its_minutes(self) -> None:
        """MUTANT: sum minutes over the records that carry them while tokens sum every record,
        so 12 minutes from one agent of two reads as the unit's time beside both agents'
        tokens."""
        self._tagged_run()
        self._record("--delegated-tokens", "40000", "--delegated-unit", "US0001",
                     "--delegated-minutes", "12")
        self._record("--delegated-tokens", "2500", "--delegated-unit", "US0001")
        row = self._unit_rows(self._report()[0])["US0001"]
        self.assertEqual(42_500, row["eu_tokens"]["value"])
        self.assertEqual("NOT MEASURED", row["eu_minutes"]["value"])
        self.assertIn("1 of its 2 tagged agent(s) reported minutes (12.0 between them)",
                      row["eu_minutes"]["reason"])

    def test_minutes_must_be_finite(self) -> None:
        """MUTANT: a positive-number check alone, which passes `inf` and `nan` into the run
        record as `Infinity` and `NaN` and onto the page as `inf agent minutes`."""
        self._tagged_run()
        retro = importlib.import_module("retro")
        for bad in ("inf", "nan", "0", "-3"):
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = retro.main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                                 "--delegated-tokens", "5", "--delegated-unit", "US0001",
                                 "--delegated-minutes", bad])
            self.assertEqual(1, rc, bad)
            self.assertIn("positive finite number", err.getvalue(), bad)
        self.assertEqual([], run_state.read(self.ws.root).get(run_state.DELEGATED) or [])
        self._record("--delegated-tokens", "5", "--delegated-unit", "US0001",
                     "--delegated-minutes", "2")                      # the control lands

    def test_a_unit_outside_the_batch_is_warned_and_recorded(self) -> None:
        """A tag naming a unit the run does not hold would show on no per-unit row: said on
        stderr, never refused. MUTANT: no warning."""
        self._tagged_run()
        retro = importlib.import_module("retro")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = retro.main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                             "--delegated-tokens", "5", "--delegated-unit", "US0099"])
        self.assertEqual(0, rc, err.getvalue())
        self.assertIn("US0099 is not in the open run's batch", err.getvalue())
        self.assertEqual("US0099", run_state.read(self.ws.root)[run_state.DELEGATED][-1]["unit"])
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            retro.main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                        "--delegated-tokens", "5", "--delegated-unit", "US0001"])
        self.assertNotIn("warning", err.getvalue(), "the control: a batch unit is not warned")

    def test_a_tag_without_a_total_is_refused(self) -> None:
        """A unit or minutes with no `--delegated-tokens` would record nothing, silently."""
        self._tagged_run()
        retro = importlib.import_module("retro")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = retro.main(["--root", str(self.ws.root), "accuracy", "--id", RETRO,
                             "--delegated-unit", "US0001"])
        self.assertEqual(2, rc)
        self.assertIn("--delegated-tokens", err.getvalue())
        self.assertEqual([], run_state.read(self.ws.root).get(run_state.DELEGATED) or [])


if __name__ == "__main__":
    unittest.main()
