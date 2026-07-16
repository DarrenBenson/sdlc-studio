"""The sprint report (US0174) + its config gate (US0176).

The load-bearing properties are the honesty ones: cost sums over ATTEMPTS (rework counted), an
unpriced model is named not guessed, an interactive batch says so rather than reporting $0, and the
config switch gates RENDERING only - never recording.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sprint_report as sr  # noqa: E402
import telemetry as tel  # noqa: E402

BATCH = "US0001, US0002"
RETRO = f"""# RETRO-9100: a sprint

> **Batch:** {BATCH}

## Delivered
- shipped

## What went well
- good

## What was hard / what stalled
- hard

## Lessons
- a real lesson worth keeping for next time

## Actions raised
| Finding | Disposition |
| --- | --- |
| something | BG0500 |
| another | declined: not ours |
"""


def _story(root: Path, sid: str, pts: int) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}-s.md").write_text(f"# {sid}: s\n\n> **Status:** Done\n> **Points:** {pts}\n",
                                   encoding="utf-8")


class ReportBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO9100-t.md").write_text(RETRO, encoding="utf-8")
        _story(self.root, "US0001", 3)
        _story(self.root, "US0002", 5)
        self.addCleanup(self.tmp.cleanup)


class CompositionTests(ReportBase):
    def test_delivered_points_and_tickets_and_lessons(self) -> None:
        rep = sr.report(self.root, "RETRO9100")
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["delivered_points"], 8)
        self.assertIn("BG0500", rep["tickets"])       # the filed finding
        self.assertEqual(len(rep["lessons"]), 1)

    def test_cost_sums_over_attempts_with_rework(self) -> None:
        tel.record(str(self.root), {"id": "US0001", "type": "story",
                                    "attempts": [{"model": "claude-haiku-4-5", "tokens": 50000},
                                                 {"model": "claude-opus-4-8", "tokens": 200000}]})
        sp = sr.report(self.root, "RETRO9100")["spend"]
        self.assertEqual(sp["tokens"], 250000)
        self.assertAlmostEqual(sp["cost"], 6.05, places=2)   # 0.05 haiku + 6.0 opus
        self.assertEqual(sp["measured_units"], 1)

    def test_unpriced_model_named_not_guessed(self) -> None:
        tel.record(str(self.root), {"id": "US0001", "type": "story",
                                    "attempts": [{"model": "mystery-model", "tokens": 100000}]})
        sp = sr.report(self.root, "RETRO9100")["spend"]
        self.assertEqual(sp["cost"], 0.0)
        self.assertEqual(sp["tokens"], 100000)               # tokens still counted
        self.assertIn("mystery-model", sp["unpriced"])

    def test_interactive_batch_says_so_not_zero_dollars(self) -> None:
        # no telemetry at all -> the cost line must not read as a real $0 measurement
        line = sr._spend_line(sr.report(self.root, "RETRO9100")["spend"], None)
        self.assertIn("no per-unit token telemetry", line)

    def test_velocity_unmeasured_without_elapsed(self) -> None:
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep["velocity"]["points_per_elapsed_hour"])

    def test_velocity_from_supplied_elapsed(self) -> None:
        rep = sr.report(self.root, "RETRO9100", elapsed_hours=2.0)
        self.assertEqual(rep["velocity"]["points_per_elapsed_hour"], 4.0)  # 8 / 2h

    def test_render_is_deterministic_text(self) -> None:
        text = sr.render(sr.report(self.root, "RETRO9100", sprint_tokens=200000))
        self.assertIn("Sprint report - RETRO9100", text)
        self.assertIn("8 points", text)
        self.assertNotIn("saved", text.lower())    # never an avoided-cost headline


    def test_model_less_attempt_renders_without_crashing(self) -> None:
        # MAJOR-1 at report level: a tokens-only attempt must not crash render's join over unpriced.
        tel.record(str(self.root), {"id": "US0001", "type": "story",
                                    "attempts": [{"tokens": 50000}]})
        text = sr.render(sr.report(self.root, "RETRO9100"))
        self.assertIn("unrecorded", text)


class ConfigGateTests(ReportBase):
    def test_rendering_disabled_by_config_but_measurement_untouched(self) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text("report:\n  enabled: false\n")
        self.assertFalse(sr.rendering_enabled(self.root))
        import argparse
        args = argparse.Namespace(root=str(self.root), id="RETRO9100", tokens=None,
                                  elapsed_hours=None, format="text")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = sr.cmd_show(args)
        self.assertEqual(rc, 0)
        self.assertIn("rendering disabled", buf.getvalue())
        self.assertIn("Telemetry is unaffected", buf.getvalue())

    def test_rendering_enabled_by_default(self) -> None:
        self.assertTrue(sr.rendering_enabled(self.root))


class GoalTests(ReportBase):
    """US0183: the report shows the Sprint Goal and the review's goal verdict when the
    open/last run's batch names this sprint's units - a stale foreign run is ignored."""

    def _run_state(self, batch, goal="make it honest", verdict=None):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        run_state.open_run(self.root, batch=batch, goal="done")
        extra = {"sprint_goal": goal}
        if verdict:
            extra["sprint_goal_verdict"] = verdict
        run_state.update(self.root, **extra)

    def test_goal_and_verdict_displayed_when_batch_matches(self) -> None:
        self._run_state(["US0001", "US0002"],
                        verdict={"verdict": "achieved", "note": "shipped"})
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["sprint_goal"], "make it honest")
        text = sr.render(rep)
        self.assertIn("Sprint Goal: make it honest", text)
        self.assertIn("achieved", text)
        self.assertIn("shipped", text)

    def test_goal_without_verdict_reads_not_judged(self) -> None:
        self._run_state(["US0001", "US0002"])
        text = sr.render(sr.report(self.root, "RETRO9100"))
        self.assertIn("Sprint Goal: make it honest", text)
        self.assertIn("not judged", text)

    def test_foreign_run_state_goal_is_ignored(self) -> None:
        # the elapsed-confounder lesson: a run-state naming OTHER units says nothing here
        self._run_state(["US0900"], verdict={"verdict": "achieved", "note": "x"})
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep.get("sprint_goal"))
        self.assertNotIn("Sprint Goal", sr.render(rep))


if __name__ == "__main__":
    unittest.main()
