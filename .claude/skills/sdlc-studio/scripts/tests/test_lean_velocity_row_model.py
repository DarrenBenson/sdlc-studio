"""BG0892: the velocity row records the model the run's meter names.

VELOCITY.md rows RETRO0121-RETRO0129 carry `-` in the model column, so the plan's calibration
found no row for claude-opus-5-5 and fell back to a July row of another model. The close records
the row with `retro.py accuracy --write --tokens-from-harness`, and a close run again (a second
attempt, a re-close) reuses the token actual already on the row - and rewrote the row with no
model, because only a fresh capture carried one. The row's model is now the one the run's meter
names whenever no fresh capture supplies it.

Every test drives `retro.main` against a throwaway workspace with its own transcript directory.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

MODEL = "claude-opus-5-5"
OTHER = "claude-opus-4-8"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


class VelocityRowModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.transcripts = Path(self._tmp.name) / "transcripts"
        self.transcripts.mkdir()
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        env = unittest.mock.patch.dict(
            os.environ, {_live("lib.run_state").TRANSCRIPTS_ENV: str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def _transcript(self, tokens: int) -> Path:
        path = self.transcripts / "session.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": MODEL, "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")
        return path

    def _run(self, n: int) -> str:
        """Retro RETRO000n over one Done 3-point story, and an open run over it whose meter
        - its baseline and its stamps - names MODEL. Returns the retro id."""
        uid, rid = f"US010{n}", f"RETRO000{n}"
        (self.root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Done\n> **Points:** 3\n", encoding="utf-8")
        (self.root / "sdlc-studio" / "retros" / f"{rid}-x.md").write_text(
            f"# {rid}: x\n\n> **Date:** 2026-10-0{n}\n> **Batch:** {uid}\n", encoding="utf-8")
        src = str(self._transcript(1000))
        stamp = {"tokens": 1000 * n, "source": src, "at": f"2026-10-0{n}T09:00:00Z",
                 "kind": "open", "model": MODEL}
        state = {"schema": 1, "run_id": f"RUN-{n}", "started_at": f"2026-10-0{n}T09:00:00Z",
                 "ended_at": None, "outcome": "running", "goal": "done", "batch": [uid],
                 "session_token_baseline": {"tokens": 1000 * n, "source": src},
                 "session_token_stamps": [stamp]}
        p = self.root / "sdlc-studio" / ".local" / "run-state.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state), encoding="utf-8")
        self._transcript(60_000)                          # the run's spend
        return rid

    def _close(self, rid: str) -> None:
        """What the close's tail runs to record the row."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("retro").main(["--root", str(self.root), "accuracy", "--id", rid,
                                      "--write", "--tokens-from-harness"])
        self.assertEqual(0, rc, out.getvalue())

    def _row(self, rid: str) -> dict:
        return next(r for r in _live("retro").velocity_history(self.root) if r["id"] == rid)

    def test_the_velocity_row_names_the_run_model(self) -> None:
        """AC1. MUTANT: HEAD, where a close run again reuses the row's token actual and
        rewrites the row with `-`, because only a fresh capture carried a model."""
        rid = self._run(1)
        self._close(rid)
        self.assertEqual(MODEL, self._row(rid)["model"], "premise: a fresh capture names it")
        self._close(rid)                                  # the close run again
        row = self._row(rid)
        self.assertEqual(MODEL, row["model"])
        self.assertEqual(60_000, row["actual_tokens"], "the actual is reused, not re-captured")
        rate = _live("retro").measured_rate(self.root, model=MODEL)
        self.assertEqual([rid], rate["by_model"][MODEL]["sprints"], "counted for its model")

    def test_a_re_close_keeps_the_row_s_model_else_reads_the_meter_s(self) -> None:
        """The two sources, in order. MUTANTS: read only the row's own model, so a row an
        earlier close already wrote with `-` (RETRO0121-RETRO0129) stays model-less on a
        re-close; read only the run's meter, so a run whose stamps name no model erases the
        model the row's fresh capture recorded."""
        retro = _live("retro")
        rid = self._run(1)
        self._close(rid)
        rs = _live("lib.run_state")
        state = rs.read(self.root)
        state["session_token_stamps"] = [{k: v for k, v in s.items() if k != "model"}
                                         for s in state["session_token_stamps"]]
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        self._close(rid)                                  # the meter names no model now
        self.assertEqual(MODEL, self._row(rid)["model"], "the row's own model was erased")
        rid = self._run(2)
        self._close(rid)
        path = retro.velocity_path(self.root)              # as a pre-fix close left it
        text = path.read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if ln.startswith(f"| {rid} |"))
        path.write_text(text.replace(line, line.replace(f"| {MODEL} |", "| - |")),
                        encoding="utf-8")
        self.assertIsNone(self._row(rid)["model"], "premise: the row names no model")
        self._close(rid)
        self.assertEqual(MODEL, self._row(rid)["model"], "the run's meter was not read")

    def test_a_meter_naming_several_models_books_the_row_mixed(self) -> None:
        """BG0892 round 1. MUTANT N4: read the meter's model only when its stamps name one, so
        a run whose stamps name two models fills a model-less row with nothing (or with one of
        them) instead of `mixed`, which calibration must keep out of either model's rate."""
        retro = _live("retro")
        rid = self._run(1)
        self._close(rid)
        rs = _live("lib.run_state")
        state = rs.read(self.root)
        state["session_token_stamps"].append({**state["session_token_stamps"][0],
                                              "model": OTHER, "kind": "unit-start"})
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        path = retro.velocity_path(self.root)              # as a pre-fix close left it
        text = path.read_text(encoding="utf-8")
        line = next(ln for ln in text.splitlines() if ln.startswith(f"| {rid} |"))
        path.write_text(text.replace(line, line.replace(f"| {MODEL} |", "| - |")),
                        encoding="utf-8")
        self._close(rid)
        self.assertEqual(retro.MODEL_MIXED, self._row(rid)["model"])

    def test_three_named_rows_end_the_calibration_fallback(self) -> None:
        """AC2, the tokens-per-point rate (the minutes rate is BG0907). MUTANT: HEAD's rows,
        which name no model after a second close, so the plan's tokens rate falls back to the
        latest row of another model (the July row)."""
        retro = _live("retro")
        retro.record_velocity(self.root, {     # the July row of another model
            "id": "RETRO0009", "date": "2026-07-15", "n_units": 1, "n_measured": 0,
            "n_forecast": 0, "models": [OTHER], "constants": None, "sample": "-",
            "batch": {"delivered_points": 3, "actual_tokens": 9_000, "ratio": None,
                      "wall_time_s": None}})
        for n in (1, 2, 3):
            rid = self._run(n)
            self._close(rid)
            self._close(rid)
        rate = retro.measured_rate(self.root)
        self.assertEqual(MODEL, rate["model"], "premise: the plan prices for the run's model")
        self.assertTrue(rate["source"].startswith(f"measured on {MODEL}"), rate["source"])
        self.assertEqual(["RETRO0001", "RETRO0002", "RETRO0003"], rate["sprints"])


if __name__ == "__main__":
    unittest.main()
