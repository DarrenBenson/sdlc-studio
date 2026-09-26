"""The sprint report (US0174) + its config gate (US0176).

The load-bearing properties are the honesty ones: cost sums over ATTEMPTS (rework counted), an
unpriced model is named not guessed, an interactive batch says so rather than reporting $0, and the
config switch gates RENDERING only - never recording.
"""
import contextlib
import io
import json
import re
import subprocess
import shutil
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - the confined git helper, resolved by module name like its siblings
import sprint_report as sr  # noqa: E402
from lib import run_state  # noqa: E402
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


class ConfigGateJsonTests(ReportBase):
    """The page-versus-data gate: `report.enabled: false` withholds the text PAGE, and
    `--format json` still returns the whole composed report. Intended behaviour, so it is
    asserted here rather than left for a reader to discover in the source."""

    def _disabled(self) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text("report:\n  enabled: false\n")

    def _show(self, fmt: str) -> tuple[int, str]:
        import argparse
        args = argparse.Namespace(root=str(self.root), id="RETRO9100", tokens=None,
                                  elapsed_hours=None, format=fmt)
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = sr.cmd_show(args)
        return rc, buf.getvalue()

    def test_json_returns_the_composed_report_under_a_disabled_config(self) -> None:
        self._disabled()
        rc, out = self._show("json")
        self.assertEqual(rc, 0)
        self.assertNotIn("rendering disabled", out)      # no page notice on the data path
        rep = json.loads(out)                            # it really is the composed report
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["id"], "RETRO9100")
        self.assertEqual(rep["delivered_points"], 8)     # the whole payload, not a stub

    def test_text_page_is_withheld_under_the_same_config(self) -> None:
        # The other half of the same gate: same config, same retro, no page.
        self._disabled()
        rc, out = self._show("text")
        self.assertEqual(rc, 0)
        self.assertIn("rendering disabled", out)
        self.assertNotIn("Delivered:", out)

    def test_notice_states_json_data_remains_available(self) -> None:
        # The notice must not claim rendering is disabled outright when data is still reachable.
        self._disabled()
        _rc, out = self._show("text")
        self.assertIn("json data remains available", out)


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
        # The GOAL LINE, not the string: the checklist's goal-review row names the Sprint Goal
        # in order to report that there was none, which is the opposite of claiming one.
        self.assertNotIn("Sprint Goal: ", sr.render(rep))


def _mutation():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mutation", Path(__file__).resolve().parents[1] / "mutation.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mutation"] = mod
    spec.loader.exec_module(mod)
    return mod


class MutationCostTests(ReportBase):
    """US0309 (CR0379 AC4): the close is where the keep-or-cut decision is actually taken, so
    the trade belongs there. Asked directly at the RUN-01KY03GS close, the best available
    answer had to be reconstructed by hand from timeouts and timestamps."""

    #: The sprint being reported ran 08:00-10:00, so a row stamped 09:00 is ITS row. The window
    #: is what joins the project-wide series to this report; without one nothing can be
    #: attributed, which is a fact and not a licence to publish the newest row going.
    WINDOW = ("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z")

    def setUp(self) -> None:
        super().setUp()
        self._window(*self.WINDOW, batch=["US0001", "US0002"])

    def _window(self, started: str, ended: str | None, batch: list[str]) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        run_state.open_run(self.root, batch=batch, goal="done")
        run_state.update(self.root, started_at=started, ended_at=ended)

    def _run(self, *, survived: int, elapsed: float, refused: bool = False,
             applied: int = 10, at: str = "2026-07-22T09:00:00Z") -> str:
        mut = _mutation()
        rid = mut._new_run_id()
        mut.append_series(self.root, {
            "run_id": rid, "generated_at": at, "git_rev": "abc1234",
            "test_cmd": "python3 -m unittest discover", "targets": ["src/thing.py"],
            "refused": refused, "unchecked": [],
            "summary": {"applied": 0 if refused else applied,
                        "killed": 0 if refused else applied - survived,
                        "survived": 0 if refused else survived,
                        "errors": 0, "unviable": 0, "truncated": 0}}, elapsed)
        return rid

    def _bug(self, name: str, run_id: str) -> None:
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}-a-survivor.md").write_text(
            f"# {name}: a survivor\n\n> **Status:** Open\n> **Severity:** High\n"
            f"> **Mutation-run:** {run_id}\n\n## Summary\n\ns\n", encoding="utf-8")

    def test_the_report_renders_mutation_cost_beside_yield(self) -> None:
        rid = self._run(survived=3, elapsed=612.5)
        self._bug("BG0232", rid)
        rep = sr.report(self.root, "RETRO9100")
        text = sr.render(rep)
        self.assertIn("612.5s", text)          # what it cost
        self.assertIn("BG0232", text)          # what it produced
        self.assertIn("3 survived", text)      # and the raw survivors beside the yield
        # one place, not three sections
        line = next(ln for ln in text.splitlines() if ln.startswith("Mutation gate"))
        self.assertIn("612.5s", line)
        self.assertIn("BG0232", line)

    def test_the_report_shows_the_trailing_mutation_history(self) -> None:
        old = self._run(survived=1, elapsed=100.0)
        self._bug("BG0100", old)
        self._run(survived=2, elapsed=200.0)
        current = self._run(survived=3, elapsed=300.0)
        text = sr.render(sr.report(self.root, "RETRO9100"))
        self.assertIn("300.0s", text)          # the current run
        self.assertIn("200.0s", text)          # ...and the ones before it
        self.assertIn("100.0s", text)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], current)
        self.assertEqual(len(rep["mutation"]["trailing"]), 2)

    def test_a_run_without_mutation_evidence_is_named_not_zeroed(self) -> None:
        # no series at all: the step was skipped, so there is nothing to count
        rep = sr.report(self.root, "RETRO9100")
        text = sr.render(rep)
        self.assertIn("no mutation evidence", text)
        self.assertNotIn("0 survived", text)   # a zero would read as a run that found nothing
        self.assertIsNone(rep["mutation"]["current"])
        # ...and a run that WAS attempted and refused says so, rather than reading as a
        # clean sweep of zero survivors
        self._run(survived=0, elapsed=44.0, refused=True)
        text = sr.render(sr.report(self.root, "RETRO9100"))
        self.assertIn("no mutation evidence", text)
        self.assertIn("refused", text)
        self.assertNotIn("0 survived", text)

    def test_cost_per_finding_is_derived_only_where_both_halves_exist(self) -> None:
        barren = self._run(survived=3, elapsed=400.0)         # cost, no filed artefact
        fruitful = self._run(survived=2, elapsed=600.0)       # both halves
        self._bug("BG0233", fruitful)
        rep = sr.report(self.root, "RETRO9100")
        cur = rep["mutation"]["current"]
        self.assertEqual(cur["run_id"], fruitful)
        self.assertEqual(cur["cost_per_finding_s"], 600.0)    # 600s / 1 filed
        prev = rep["mutation"]["trailing"][0]
        self.assertEqual(prev["run_id"], barren)
        self.assertIsNone(prev["cost_per_finding_s"])         # never a divide by zero
        self.assertTrue(prev["cost_per_finding_note"])        # and never a blank that reads free
        text = sr.render(rep)
        self.assertIn("600.0s per finding", text)
        self.assertIn(prev["cost_per_finding_note"], text)

    def test_an_unreadable_series_does_not_break_the_report(self) -> None:
        p = self.root / "sdlc-studio" / ".local" / "mutation-series.jsonl"
        p.write_text("{not json\n", encoding="utf-8")
        rep = sr.report(self.root, "RETRO9100")
        self.assertTrue(rep["ok"])
        self.assertIn("no mutation evidence", sr.render(rep))


class MutationBelongsToThisRunTests(ReportBase):
    """MAJOR, RUN-01KY3MFX review: `current` was the newest row of the PROJECT-WIDE series,
    whichever run wrote it. A sprint that ran no mutation therefore republished the PREVIOUS
    sprint's cost and yield as its own and UNLABELLED, while the trailing rows beneath it were
    correctly prefixed `previous run`. US0309 AC1 says "the run's wall-clock cost" and AC3 says
    a run with no evidence is named as such; both were false on that path.

    The precedent is `_sprint_goal` in the same file, which refuses a run state whose batch
    does not name this sprint's units."""

    def _run(self, at: str, elapsed: float, survived: int = 3) -> str:
        mut = _mutation()
        rid = mut._new_run_id()
        mut.append_series(self.root, {
            "run_id": rid, "generated_at": at, "git_rev": "abc1234",
            "test_cmd": "t", "targets": ["src/thing.py"], "refused": False, "unchecked": [],
            "summary": {"applied": 10, "killed": 10 - survived, "survived": survived,
                        "errors": 0, "unviable": 0, "truncated": 0}}, elapsed)
        return rid

    def _window(self, started: str, ended: str | None, batch: list[str]) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        run_state.open_run(self.root, batch=batch, goal="done")
        run_state.update(self.root, started_at=started, ended_at=ended)

    def test_a_previous_runs_row_is_not_republished_as_this_sprints(self) -> None:
        self._run("2026-07-21T12:00:00Z", 987.0)          # yesterday's sprint proved something
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep["mutation"]["current"],
                          "this sprint ran no mutation, so it HAS no mutation row")
        text = sr.render(rep)
        self.assertIn("no mutation evidence", text)
        self.assertNotIn("987.0s, 10 applied", text)      # never as this run's own figure
        # ...and the older row is still shown, labelled as what it is
        self.assertIn("previous run", text)
        self.assertIn("987.0s", text)

    def test_a_row_inside_the_runs_window_is_this_sprints(self) -> None:
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        rid = self._run("2026-07-22T09:00:00Z", 612.5)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], rid)
        self.assertIn("612.5s", sr.render(rep))

    def test_a_row_after_the_run_closed_is_not_this_sprints(self) -> None:
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        self._run("2026-07-22T11:30:00Z", 55.0)           # the NEXT sprint's proving run
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep["mutation"]["current"])
        self.assertIn("no mutation evidence", sr.render(rep))

    def test_a_foreign_run_state_cannot_attribute_a_row_to_this_sprint(self) -> None:
        self._run("2026-07-22T09:00:00Z", 400.0)
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0900"])
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep["mutation"]["current"])
        text = sr.render(rep)
        self.assertIn("no mutation evidence", text)
        self.assertIn("no run state names this sprint", text)

    def test_an_exact_batch_beats_an_open_SUPERSET_run(self) -> None:
        """Round 3 MAJOR 3. `cover` is bounded above by len(want), so ANY run whose batch is a
        SUPERSET of this sprint's units TIES the run that delivered them - and with live tried
        first, the open superset took the window. Closeness breaks the tie: fewest units that
        are not this sprint's."""
        self._window("2026-07-01T08:00:00Z", "2026-07-01T10:00:00Z", ["US0001", "US0002"])
        true_rid = self._run("2026-07-01T09:00:00Z", 300.0)
        # a later, still-open run that touches BOTH units plus a great deal else
        self._window("2026-07-20T08:00:00Z", None,
                     ["US0001", "US0002"] + [f"US{n:04d}" for n in range(500, 540)])
        self._run("2026-07-20T09:00:00Z", 55.0, survived=1)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], true_rid,
                         "a superset must not outrank the batch that IS this sprint")
        self.assertIn("300.0s", sr.render(rep))

    def test_the_run_covering_this_sprint_beats_an_open_run_touching_one_unit(self) -> None:
        """MAJOR, round 2: the LIVE record was tried first unconditionally, so a partial
        one-unit intersection with whatever run happens to be open beat a full match in the
        archive. An open run has no `ended_at`, so every later project-wide row then read as
        this sprint's - the republishing defect the window was added to stop, returning
        through its own fix."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        self._window("2026-07-01T08:00:00Z", "2026-07-01T10:00:00Z", ["US0001", "US0002"])
        mine = self._run("2026-07-01T09:00:00Z", 300.0)
        run_state.archive(self.root)
        self._window("2026-07-20T08:00:00Z", None, ["US0001", "US0900"])   # re-touches ONE unit
        self._run("2026-07-20T09:00:00Z", 55.0)                            # the LATER run's row
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], mine)
        text = sr.render(rep)
        self.assertIn("300.0s", text)
        self.assertNotIn("55.0s, 10 applied", text)

    def test_a_tie_on_coverage_keeps_the_live_record(self) -> None:
        """Both records name every unit. The live one is the run being closed, and the report
        is normally rendered from it before the close archives it."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        self._window("2026-07-01T08:00:00Z", "2026-07-01T10:00:00Z", ["US0001", "US0002"])
        self._run("2026-07-01T09:00:00Z", 300.0)
        run_state.archive(self.root)
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        rid = self._run("2026-07-22T09:00:00Z", 55.0)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], rid)
        self.assertIn("55.0s", sr.render(rep))

    def test_an_unstamped_row_is_named_rather_than_reported_as_a_skipped_step(self) -> None:
        """MINOR, round 2: a row with no `at` is dropped from both buckets, and the renderer
        then said the step was skipped or killed before it could record anything. Neither is
        true of a row that exists and carries counts."""
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        self._run(None, 71.0)
        rep = sr.report(self.root, "RETRO9100")
        self.assertIsNone(rep["mutation"]["current"])
        self.assertEqual(1, rep["mutation"]["unstamped"])
        text = sr.render(rep)
        self.assertIn("no timestamp", text)
        self.assertEqual(1, text.count("no timestamp"))   # said once, not once per writer
        self.assertNotIn("killed before it could record anything", text)

    def test_an_unstamped_row_is_named_even_when_this_run_has_a_row_of_its_own(self) -> None:
        """It is dropped from the trailing history too, so the drop is said out loud rather
        than leaving the reader to count the rows they cannot see."""
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        self._run(None, 71.0)
        self._run("2026-07-22T09:00:00Z", 612.5)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(1, rep["mutation"]["unstamped"])
        # ...and `attribution` stays None: this run HAS a row, so nothing went unattributed
        self.assertIsNone(rep["mutation"]["attribution"])
        text = sr.render(rep)
        self.assertIn("612.5s", text)
        self.assertIn("no timestamp", text)

    def test_an_unreadable_archive_record_does_not_break_the_window(self) -> None:
        """MINOR, round 2: `_run_window` wrapped `run_state.archived` in `except OSError`,
        which is dead - `archived` documents and implements never-raising, skipping the record
        it cannot read. The guard is gone; this pins the contract it was standing in for."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        d = run_state.archive_dir(self.root)
        d.mkdir(parents=True, exist_ok=True)
        (d / "RUN-BROKEN.json").write_text("{not json", encoding="utf-8")
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        rid = self._run("2026-07-22T09:00:00Z", 88.0)
        rep = sr.report(self.root, "RETRO9100")
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["mutation"]["current"]["run_id"], rid)

    def test_a_closed_run_is_found_in_the_archive(self) -> None:
        """The report is normally read AFTER the close, and the close archives the run. A
        window that only exists in the archive is still this sprint's window."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib import run_state
        self._window("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z", ["US0001", "US0002"])
        rid = self._run("2026-07-22T09:00:00Z", 300.0)
        run_state.archive(self.root)
        run_state.open_run(self.root, batch=["US0900"], goal="done")   # the NEXT run is live
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["run_id"], rid)


class ExecutionActualsTests(ReportBase):
    """US0499: the close reports what test execution actually cost, against the policy the
    plan declared. Measured on one run: the suite executed about 52 times for about 218
    minutes against 35 minutes of delivery, and the retro said only what was delivered."""

    WINDOW = ("2026-07-28T09:00:00Z", "2026-07-28T18:00:00Z")

    def _run(self) -> None:
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-EXEC", "batch": ["US0001", "US0002"], "outcome": "running",
            "started_at": self.WINDOW[0], "ended_at": self.WINDOW[1]}), encoding="utf-8")

    def _ledger(self, runs: list[dict]) -> None:
        (self.root / "sdlc-studio" / ".local" / "test-execution.json").write_text(
            json.dumps({"runs": runs}), encoding="utf-8")

    def _plan(self, declared: dict) -> None:
        (self.root / "sdlc-studio" / ".local" / "sprint-plan.json").write_text(json.dumps({
            "test_strategy": {"execution": {"declared": declared}}}), encoding="utf-8")

    def test_the_close_reports_runs_against_the_policy(self) -> None:
        """AC1: how many full-suite runs happened, how many were selected, what they cost -
        set against what the policy declared."""
        self._run()
        self._plan({"per_commit": "selected", "at_close": "full", "at_release": "full"})
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 300,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T11:00:00Z", "mode": "full", "seconds": 310,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T12:00:00Z", "mode": "selected", "seconds": 40,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T13:00:00Z", "mode": "reuse", "seconds": 0,
             "verdict": "pass", "moment": "close"},
            {"at": "2026-07-27T10:00:00Z", "mode": "full", "seconds": 9999,
             "verdict": "pass", "moment": "commit"},   # BEFORE the window: another sprint's
        ])
        act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        self.assertTrue(act["measured"])
        self.assertEqual(act["full_runs"], 2, "the row outside this run's window is not ours")
        self.assertEqual(act["selected_runs"], 1)
        self.assertEqual(act["reused_runs"], 1)
        self.assertEqual(act["seconds"], 650)
        self.assertEqual(act["declared"]["per_commit"], "selected")
        text = "\n".join(sr._execution_lines({"execution": act}))
        self.assertIn("2 full", text)
        self.assertIn("650", text)
        self.assertIn("selected", text, "the declared policy is stated beside the actuals")

    def test_an_unmeasured_cost_is_not_reported_as_zero(self) -> None:
        """AC2: a run with no recorded execution data says the cost was not captured and why.
        A total of 0 reads as a sprint that tested for free."""
        self._run()                      # a window exists, but nothing was ever recorded
        act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        text = "\n".join(sr._execution_lines({"execution": act}))
        self.assertFalse(act["measured"])
        self.assertIsNone(act["seconds"], "unknown is not zero")
        self.assertIn("NOT CAPTURED", text)
        self.assertNotIn("0s", text)
        self.assertIn("not zero", text)

    def test_an_unattributable_run_says_so_rather_than_claiming_the_series(self) -> None:
        """Without a run window, every row belongs to SOME run and none provably to this one -
        the same confounder the mutation summary had to learn."""
        self._ledger([{"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 300,
                       "verdict": "pass", "moment": "commit"}])
        act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        self.assertFalse(act["measured"])
        self.assertEqual(act["full_runs"], 0)
        self.assertIn("no run state", act["why"])

    def test_the_report_carries_the_execution_block(self) -> None:
        """LANE test, not a library test (LL0040): the three above call the helpers directly,
        so deleting the call from `report`/`render` would leave them all green."""
        self._run()
        self._plan({"per_commit": "selected", "at_close": "full", "at_release": "full"})
        self._ledger([{"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 300,
                       "verdict": "pass", "moment": "commit"}])
        with contextlib.redirect_stderr(io.StringIO()):
            rep = sr.report(self.root, "RETRO9100")
            text = sr.render(rep)
        self.assertIn("execution", rep)
        self.assertIn("Test execution:", text)
        self.assertIn("1 full", text)


class OverheadRatioTests(ReportBase):
    """US0523 + US0524 (CR0462): the close reports delivery time against overhead time.

    On RUN-01KYHVWK that ratio was about 9:1 and surfaced only because the operator said it
    felt slow and it was then computed by hand. Every component here comes from a record the
    run wrote - the test-execution ledger, the mutation series, the review-round stamps - and a
    component nothing recorded reads UNMEASURED, never as a cheap zero.
    """

    #: A ten-hour run. 08:00-18:00 = 36,000s of measured wall-clock.
    WINDOW = ("2026-07-28T08:00:00Z", "2026-07-28T18:00:00Z")

    def _run(self, rounds: list[dict] | None = None, ended: str | None = "") -> None:
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-OVERHEAD", "batch": ["US0001", "US0002"], "outcome": "running",
            "started_at": self.WINDOW[0],
            "ended_at": self.WINDOW[1] if ended == "" else ended,
            "review_rounds": rounds if rounds is not None else [
                {"round": 1, "verdict": "REJECT", "recorded_at": "2026-07-28T12:00:00Z"},
                {"round": 2, "verdict": "APPROVE", "recorded_at": "2026-07-28T13:00:00Z"},
            ]}), encoding="utf-8")

    def _ledger(self, runs: list[dict]) -> None:
        (self.root / "sdlc-studio" / ".local" / "test-execution.json").write_text(
            json.dumps({"runs": runs}), encoding="utf-8")

    def _mutation_run(self, elapsed: float, at: str = "2026-07-28T09:00:00Z") -> str:
        mut = _mutation()
        rid = mut._new_run_id()
        mut.append_series(self.root, {
            "run_id": rid, "generated_at": at, "git_rev": "abc1234",
            "test_cmd": "t", "targets": ["src/thing.py"], "refused": False, "unchecked": [],
            "summary": {"applied": 10, "killed": 7, "survived": 3,
                        "errors": 0, "unviable": 0, "truncated": 0}}, elapsed)
        return rid

    def _measured_sprint(self) -> None:
        """21,600s of test execution + 1,800s of mutation + a 3,600s review-and-repair span =
        27,000s of overhead inside a 36,000s run, leaving 9,000s of delivery: 3.0:1."""
        self._run()
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 18000,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T14:00:00Z", "mode": "full", "seconds": 3600,
             "verdict": "pass", "moment": "close"},
            {"at": "2026-07-27T10:00:00Z", "mode": "full", "seconds": 9999,
             "verdict": "pass", "moment": "commit"},   # BEFORE the window: another sprint's
        ])
        self._mutation_run(1800.0)

    def _report(self) -> dict:
        with contextlib.redirect_stderr(io.StringIO()):
            return sr.report(self.root, "RETRO9100")

    def test_the_close_reports_the_ratio(self) -> None:
        """US0523 AC1: delivery time, overhead time and the ratio between them, on the page the
        close draws - a LANE test, so deleting the call from `report`/`render` fails here."""
        self._measured_sprint()
        rep = self._report()
        ov = rep["overhead"]
        self.assertTrue(ov["measured"])
        self.assertEqual(ov["overhead_s"], 27000.0)
        self.assertEqual(ov["delivery_s"], 9000.0)
        self.assertEqual(ov["ratio"], 3.0)
        text = sr.render(rep)
        line = next(ln for ln in text.splitlines() if ln.startswith("Overhead vs delivery"))
        self.assertIn("3.0:1", line)
        self.assertIn("delivery", line)
        # ...beside the figures the report already carries
        self.assertIn("8 points", text)

    def test_an_unmeasured_component_is_not_credited_to_delivery(self) -> None:
        """BG0495. Delivery is TOTAL MINUS OVERHEAD, so every minute the instruments failed to
        attribute lands in the delivery figure - it is an upper bound by exactly the amount the
        ratio is a lower one. The ratio already said "at least"; the delivery figure beside it
        said a bare number, so one sentence carried a qualified claim and an unqualified one
        about the same arithmetic.

        Mutant: print the delivery figure unqualified while the ratio stays qualified - the
        reader is told the ratio is a floor and left to assume the delivery minutes are exact,
        which is the direction that flatters the loop.
        """
        self._run()
        self._ledger([{"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 3600,
                       "verdict": "pass", "moment": "commit"}])
        # no mutation series recorded, so one component is UNMEASURED
        rep = self._report()
        ov = rep["overhead"]
        self.assertIn("mutation", ov["unmeasured"])
        self.assertEqual(ov["bound"], "lower")
        line = next(ln for ln in sr.render(rep).splitlines()
                    if ln.startswith("Overhead vs delivery"))
        self.assertIn("at least", line, "the ratio is a floor and must say so")
        self.assertIn("at most", line,
                      "the delivery figure is a CEILING for the same reason, and said so with "
                      "no qualifier at all")

    def test_the_two_qualifiers_come_from_one_decision(self) -> None:
        """The negative control, and the reason it is shaped this way: `bound == "exact"` is not
        reachable through a real run here - the review-and-repair component is a floor by
        construction, so every measured sprint is already a lower bound. What CAN be pinned is
        that the ratio's qualifier and the delivery figure's are derived from the same `bound`
        rather than written beside each other.

        Mutant: hard-code either qualifier - one fires without the other and this reddens. The
        exact case is exercised on the renderer directly, because no fixture reaches it.
        """
        exact = {"measured": True, "ratio": 3.0, "overhead_s": 27000.0, "delivery_s": 9000.0,
                 "total_s": 36000.0, "components": [], "unmeasured": [], "bound": "exact"}
        line = sr._overhead_lines({"overhead": exact})[0]
        self.assertNotIn("at least", line)
        self.assertNotIn("at most", line)
        lower = sr._overhead_lines({"overhead": {**exact, "bound": "lower"}})[0]
        self.assertIn("at least", lower)
        self.assertIn("at most", lower)

    def test_the_components_are_derived_not_estimated(self) -> None:
        """US0523 AC2: every component traces to a record the run wrote. Proved by MOVING the
        record - a figure invented at close would not follow it."""
        self._measured_sprint()
        by_name = {c["name"]: c for c in self._report()["overhead"]["components"]}
        self.assertEqual(by_name["test execution"]["seconds"], 21600.0)
        self.assertEqual(by_name["mutation"]["seconds"], 1800.0)
        self.assertEqual(by_name["review and repair"]["seconds"], 3600.0)
        for comp in by_name.values():
            self.assertTrue(comp["source"], "a component names the record it came from")
        # the ledger gains another 1,800s: overhead follows the record, delivery falls by it
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 18000,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T14:00:00Z", "mode": "full", "seconds": 3600,
             "verdict": "pass", "moment": "close"},
            {"at": "2026-07-28T15:00:00Z", "mode": "full", "seconds": 1800,
             "verdict": "pass", "moment": "close"},
        ])
        ov = self._report()["overhead"]
        self.assertEqual(ov["overhead_s"], 28800.0)
        self.assertEqual(ov["delivery_s"], 7200.0)
        self.assertEqual(ov["ratio"], 4.0)
        self.assertEqual(round(ov["overhead_s"] + ov["delivery_s"], 1), ov["total_s"],
                         "the parts sum to the measured run, so nothing was invented")

    def test_an_unmeasured_component_is_not_zero(self) -> None:
        """US0524 AC1: a run with no recorded review round has UNMEASURED review time, and the
        ratio says which part it excludes. A zero there would read as a review that was free."""
        self._run(rounds=[])
        self._ledger([{"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 21600,
                       "verdict": "pass", "moment": "commit"}])
        self._mutation_run(1800.0)
        rep = self._report()
        ov = rep["overhead"]
        review = next(c for c in ov["components"] if c["name"] == "review and repair")
        self.assertFalse(review["measured"])
        self.assertIsNone(review["seconds"], "unknown is not zero")
        self.assertTrue(review["why"])
        self.assertEqual(ov["unmeasured"], ["review and repair"])
        self.assertEqual(ov["overhead_s"], 23400.0, "only the measured parts are summed")
        self.assertEqual(ov["bound"], "lower", "an excluded component makes the ratio a floor")
        text = sr.render(rep)
        self.assertIn("UNMEASURED", text)
        self.assertIn("EXCLUDES", text)
        self.assertIn("review and repair", text)
        self.assertNotIn("review and repair 0", text)
        # and with NOTHING recorded, the whole ratio is unmeasured rather than a tidy 0:1
        self._ledger([])
        (self.root / "sdlc-studio" / ".local" / "mutation-series.jsonl").write_text(
            "", encoding="utf-8")
        ov = self._report()["overhead"]
        self.assertFalse(ov["measured"])
        self.assertIsNone(ov["ratio"])
        self.assertIsNone(ov["delivery_s"])
        self.assertIn("not zero", ov["why"])
        self.assertIn("UNMEASURED", sr.render(self._report()))

    def test_the_ratio_reaches_the_velocity_record(self) -> None:
        """US0524 AC2: the ratio joins the velocity figures rather than sitting in a block of
        its own, so a reader of the velocity record meets it without knowing to look."""
        self._measured_sprint()
        rep = self._report()
        vel = rep["velocity"]
        self.assertEqual(vel["overhead_ratio"], 3.0)
        self.assertEqual(vel["overhead_ratio"], rep["overhead"]["ratio"],
                         "ONE computation, so the two readings cannot drift")
        self.assertEqual(vel["overhead_excludes"], [])
        text = sr.render(rep)
        idx = [i for i, ln in enumerate(text.splitlines())]
        lines = text.splitlines()
        vpos = next(i for i in idx if lines[i].startswith("Velocity"))
        opos = next(i for i in idx if lines[i].startswith("Overhead vs delivery"))
        self.assertLess(vpos, opos, "the ratio sits with the velocity figures")
        self.assertLess(opos - vpos, 4, "...not paragraphs away from them")


class OverheadReviewTermTests(unittest.TestCase):
    """US0535 / BG0366. `_component_review` could only measure the span BETWEEN round stamps -
    nothing before the first round, and zero when rounds were stamped together at close. So the
    largest overhead component of the last two sprints was reported UNMEASURED, and the ratio,
    which computes delivery by subtraction, credited that time to delivery."""

    def _rounds(self, *seconds):
        return [{"round": i, "verdict": "REJECT", "recorded_at": "2026-07-28T10:00:00Z",
                 "seconds": s} for i, s in enumerate(seconds, 1)]

    def _ctx(self, rounds):
        return {"state": {sr.run_state.REVIEW_ROUNDS: rounds}}

    def test_recorded_round_durations_feed_the_overhead_term(self) -> None:
        c = sr._component_review(self._ctx(self._rounds(600, 900)))
        self.assertTrue(c["measured"])
        self.assertEqual(c["seconds"], 1500.0)

    def test_every_round_timed_is_exact_and_a_mix_is_a_lower_bound(self) -> None:
        """A sum of durations counts the review itself rather than the gaps between stamps, so
        it is exact when every round carries one. A mix stays a floor: the untimed rounds
        contribute nothing, and counting them as zero is the error being removed."""
        exact = sr._component_review(self._ctx(self._rounds(600, 900)))
        self.assertEqual(exact["bound"], "exact")
        UN = sr.run_state.UNMEASURED
        mixed = sr._component_review(self._ctx(self._rounds(600, UN)))
        self.assertTrue(mixed["measured"])
        self.assertEqual(mixed["seconds"], 600.0)
        self.assertEqual(mixed["bound"], "lower")

    def test_the_floor_caveat_tracks_actual_unmeasured_components(self) -> None:
        """The caveat qualifies a number. It must be stated while a component is genuinely
        unmeasured and dropped when none is - a permanent 'at least' is noise a reader learns
        to skip, and an absent one on an incomplete measurement is a false precision."""
        UN = sr.run_state.UNMEASURED
        none_timed = sr._component_review(self._ctx(self._rounds(UN, UN)))
        self.assertFalse(none_timed["measured"])
        # It falls through to the stamp-span reading, which correctly refuses too - and says
        # so in its own words. The assertion is that it is NOT reported as free, however it
        # reaches that answer.
        self.assertIn("not a review that was free", none_timed["why"])
        self.assertIsNone(none_timed["seconds"])

    def test_no_rounds_at_all_is_still_unmeasured_not_zero(self) -> None:
        c = sr._component_review(self._ctx([]))
        self.assertFalse(c["measured"])
        self.assertIsNone(c["seconds"])


class GoalVersusCountTests(unittest.TestCase):
    """US0544. A close whose units all reached terminal while the goal was NOT achieved is the
    most misreadable state a report can be in: every number looks like success. The verdict
    was printed above the count and left to be inferred."""

    def _rep(self, verdict: str, clauses=None) -> dict:
        gv = {"verdict": verdict, "note": "", "rounds": 1}
        if clauses:
            gv["clauses"] = clauses
        return {"ok": True, "id": "RETRO0001", "date": "2026-07-28",
                "sprint_goal": "ship the widget", "sprint_goal_verdict": gv,
                "units": ["US0001", "US0002"], "delivered_points": 8,
                "velocity": {"points_per_elapsed_hour": None, "elapsed_hours": None,
                             "elapsed_source": None, "points_per_worker_hour": None,
                             "tokens_per_point": None, "sprint_tokens_per_point": None,
                             "overhead_ratio": None, "overhead_bound": None,
                             "overhead_excludes": []},
                "accuracy": {"ratio": None, "refused": None, "n_measured": 0, "models": []},
                "spend": {"measured_units": 0, "cost": 0, "unpriced": []},
                "lessons": [], "tickets": [], "declined": [], "delegated_signoffs": [],
                "mutation": {}, "execution": {}, "overhead": {}, "flow": {}}

    def test_all_units_terminal_with_an_unachieved_goal_says_so(self) -> None:
        out = sr.render(self._rep("partial"))
        self.assertIn("the goal was partial", out)
        self.assertIn("not the same as", out)

    def test_an_achieved_goal_adds_no_such_line(self) -> None:
        """The line must not become constant furniture - one that always appears is one a
        reader stops seeing, and the state it warns about would then be invisible again."""
        out = sr.render(self._rep("achieved"))
        self.assertNotIn("not the same as", out)

    def test_each_clause_verdict_is_printed_under_the_goal(self) -> None:
        out = sr.render(self._rep("partial", [{"clause": "seams have owners",
                                               "verdict": "achieved"},
                                              {"clause": "the goal is judged",
                                               "verdict": "missed"}]))
        self.assertIn("clause: seams have owners -> achieved", out)
        self.assertIn("clause: the goal is judged -> missed", out)


class SeamCoverageTests(unittest.TestCase):
    """US0540. A run that shipped with unowned seams is not the same as one whose pairs were
    all accounted for, and a close report that omits the difference lets the second read like
    the first."""

    def _cov(self, total, unowned):
        return {"available": True, "total": total, "unowned": unowned}

    def test_unowned_seams_are_named_at_close(self) -> None:
        """NAMED, not counted: a number tells a reader how many pairs went unaccounted for and
        not which ones, and the value of the report is that somebody can go and look."""
        lines = sr._seam_lines({"seams": self._cov(
            3, [{"units": ["US0529", "US0530"], "shared": ["src/init.py"]}])})
        joined = " ".join(lines)
        self.assertIn("US0529 + US0530", joined)
        self.assertIn("src/init.py", joined)

    def test_a_fully_owned_batch_says_so_rather_than_going_quiet(self) -> None:
        self.assertIn("all owned", " ".join(sr._seam_lines({"seams": self._cov(4, [])})))

    def test_a_batch_with_no_seams_is_distinguishable_from_one_nobody_mapped(self) -> None:
        self.assertIn("no pair", " ".join(sr._seam_lines({"seams": self._cov(0, [])})))
        self.assertEqual(sr._seam_lines({"seams": {"available": False}}), [])


class UnreadableBatchTests(unittest.TestCase):
    """BG0362. A Batch line written as prose yields no unit ids, and the report then stated the
    sprint delivered nothing. Zero units is an empty MEASUREMENT presented as a finding - and
    the two readings call for opposite responses (fix the retro, versus explain a sprint that
    shipped nothing), so the report must not pick the alarming one by default."""

    def _rep(self, units):
        return {"ok": True, "id": "RETRO0001", "date": "2026-07-28", "units": units,
                "delivered_points": 0 if not units else 8,
                "velocity": {"points_per_elapsed_hour": None, "elapsed_hours": None,
                             "elapsed_source": None, "points_per_worker_hour": None,
                             "tokens_per_point": None, "sprint_tokens_per_point": None,
                             "overhead_ratio": None, "overhead_bound": None,
                             "overhead_excludes": []},
                "accuracy": {"ratio": None, "refused": None, "n_measured": 0, "models": []},
                "spend": {"measured_units": 0, "cost": 0, "unpriced": []},
                "lessons": [], "tickets": [], "declined": [], "delegated_signoffs": [],
                "mutation": {}, "execution": {}, "overhead": {}, "flow": {}, "seams": {}}

    def test_no_units_reads_as_unreadable_not_as_nothing_delivered(self) -> None:
        out = sr.render(self._rep([]))
        self.assertIn("UNREADABLE, not zero", out)
        self.assertIn("Batch", out)

    def test_a_readable_batch_still_reports_its_count(self) -> None:
        out = sr.render(self._rep(["US0001", "US0002"]))
        self.assertIn("Delivered: 2 unit(s), 8 points.", out)
        self.assertNotIn("UNREADABLE", out)


class ProofObligationCoverageTests(unittest.TestCase):
    """BG0358. RUN-01KYJZGZ named six units owing mutation-plus-unit proof; zero mutation runs
    were recorded, all six reached terminal, both suites were green, the gate passed and the
    close ran. No lane, gate or close ever compared what the strategy DEMANDED against what the
    delivery PRODUCED - so an obligation voided for a good reason removed the strategy's central
    proof with nothing anywhere to notice the trade."""

    def _rep(self, unmet):
        return {"proof": {"available": True, "units": 6, "unmet": unmet}}

    def test_an_undischarged_declared_obligation_is_named_with_its_unit(self) -> None:
        lines = " ".join(sr._proof_lines(self._rep([{"unit": "US0493",
                                                    "unmet": ["mutation", "unit"]}])))
        self.assertIn("US0493", lines)
        self.assertIn("mutation", lines)
        self.assertIn("nothing else compares the two sides", lines)

    def test_a_fully_discharged_batch_says_so(self) -> None:
        self.assertIn("was discharged", " ".join(sr._proof_lines(self._rep([]))))

    def test_an_underivable_strategy_reports_nothing_rather_than_all_clear(self) -> None:
        """A missing TSD tells you nothing about the risk of the change, so silence here must
        not read as every obligation met."""
        self.assertEqual(sr._proof_lines({"proof": {"available": False}}), [])


# --- The compulsory sprint checklist (EP0192 / CR0505) ----------------------------------

def _unit(root: Path, uid: str, status: str, pts: int = 3, type_dir: str = "stories") -> None:
    """Write (or REWRITE) a unit at a status. Same filename as `_story`, deliberately: a second
    file for the same id leaves two artefacts with one id, and the resolver then answers with
    whichever it sorts first - which made a fixture that thought it had set Blocked silently
    keep Done."""
    d = root / "sdlc-studio" / type_dir
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-s.md").write_text(f"# {uid}: x\n\n> **Status:** {status}\n> **Points:** {pts}\n",
                                   encoding="utf-8")


class ChecklistBase(unittest.TestCase):
    """A tree with a retro, a run record and whatever each test needs on top."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        (self.root / "sdlc-studio" / "retros" / "RETRO9100-t.md").write_text(RETRO,
                                                                             encoding="utf-8")
        _story(self.root, "US0001", 3)
        _story(self.root, "US0002", 5)
        self.addCleanup(self.tmp.cleanup)

    def _run(self, **fields) -> dict:
        """Write a run record directly. The checklist reads run state, not the CLI that wrote
        it, so a fixture that goes through `open_run` would be testing the writer twice."""
        state = {"schema": 1, "run_id": "RUN-TEST01", "started_at": "2026-01-01T00:00:00Z",
                 "outcome": "running", "batch": ["US0001", "US0002"], "batch_changes": []}
        state.update(fields)
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        return state

    def _ck(self, **run_fields) -> dict:
        self._run(**run_fields)
        return sr.checklist(self.root, "RETRO9100")

    def _row(self, ck: dict, item_id: str) -> dict:
        return next(r for r in ck["items"] if r["id"] == item_id)


class CoverageConsistencyTests(ChecklistBase):
    """US0596. One question - is this unit covered? - was answered by three computations that
    could disagree, and did: one close reported `9/9 covered`, `0 covered, 37 uncovered` and
    `71 recorded passes` about the same batch.

    The fixture makes the readings DIVERGE. On two units with one clean APPROVE each every
    recompute agrees, "recompute its own figure" changes no output, and the test measures
    nothing - so the batch here is a strict subset of the report's units, which is one of the
    three lane differences that produced the original contradiction.
    """

    def _reviews(self, rows: list[tuple]) -> None:
        path = self.root / "sdlc-studio" / "reviews"
        path.mkdir(parents=True, exist_ok=True)
        body = ["| Base | Reviewer | Author | Verdict | Date | Units | Findings |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for verdict, units, date in rows:
            body.append(f"| abc123 | qa; seat; r | agent | {verdict} | {date} | {units} | none |")
        (path / "sprint-review-record.md").write_text(
            "# Sprint reviews\n\n" + "\n".join(body) + "\n", encoding="utf-8")

    def test_coverage_has_one_source(self) -> None:
        """Mutant: revert `_ck_closing_review` to counting `ctx['sprint_reviews']` itself.

        The number is asserted, not merely the equality of two calls - two calls agreeing is
        satisfied by both being wrong in the same way.
        """
        self._reviews([("APPROVE", "US0001", "2026-01-02")])
        ck = self._ck()
        row = self._row(ck, "closing-review")
        self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
        self.assertIn("US0002", row["detail"], "the uncovered unit was not named")
        self.assertIn("1", self._row(ck, "coverage-consistency")["value"])
        # STRUCTURAL, not behavioural. `open_units = list(units)` - the closing review deciding
        # coverage for itself, which is exactly what this criterion forbids - survived the whole
        # suite, because every assertion above is satisfied by a second computation that happens
        # to agree. So `_coverage` is patched and the row is required to move with it: a unit the
        # shared reading calls covered must stop holding the row, whatever any other lane thinks.
        with mock.patch.object(sr, "_coverage",
                               return_value={"US0001": {"covered": True, "by": "x"},
                                             "US0002": {"covered": True, "by": "x"}}):
            self._run()
            moved = self._row(sr.checklist(self.root, "RETRO9100"), "closing-review")
        self.assertEqual(sr.RAN, moved["state"],
                         "the closing review did not read the shared coverage value - it is "
                         "computing coverage for itself, so the readings can diverge again")

    def test_a_disagreement_is_outstanding(self) -> None:
        """Mutant: drop one of the two readings from the row's value.

        Both figures must appear: a row saying the readings disagree without saying WHAT they
        each said leaves the reader unable to decide which lane is wrong. And `_resolve_item`
        turns any resolver exception into the same UNANSWERED, so a state-only assertion is
        satisfied by a resolver that crashes.
        """
        with mock.patch.object(sr, "_coverage", return_value={"US0001": {"covered": True},
                                                              "US0002": {"covered": True}}):
            self._run()
            ck = sr.checklist(self.root, "RETRO9100")
        row = self._row(ck, "coverage-consistency")
        self.assertEqual(sr.UNANSWERED, row["state"])
        self.assertIn("2", row["value"])
        self.assertIn("0", row["value"])
        self.assertIn("coverage-consistency", ck["outstanding"])

    def test_the_shipped_checklist_command_carries_the_coverage_row(self) -> None:
        """The SHIPPED entry point. `checklist()` could compute the row perfectly while the
        command never printed it, and the command is what the close and a reader both act on."""
        self._reviews([("APPROVE", "US0001", "2026-01-02")])
        self._run()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = sr.main(["--root", str(self.root), "checklist", "--id", "RETRO9100"])
        out = buf.getvalue()
        self.assertIn("Coverage computed once", out)
        # The DISCRIMINATING fact, not merely that the row printed. Only US0001 is approved, so
        # the shared reading must leave US0002 uncovered and the command must say so - an
        # implementation that clears the row whenever any review row exists prints the heading
        # just as happily.
        # Assert what ONLY the closing-review row says. `US0002` alone does not discriminate:
        # the attribution row names it too, so an implementation that clears the closing review
        # whenever any review row exists still prints the id and still prints the heading.
        line = next(ln for ln in out.splitlines() if "Closing full-diff review" in ln)
        self.assertTrue(line.startswith("[NOT RUN]"),
                        f"the closing review cleared on a batch one unit of which was "
                        f"reviewed: {line}")
        self.assertIn("unreviewed", line)
        self.assertEqual(1, rc, "the uncovered unit did not hold the close")

    def test_the_attribution_row_reads_the_shared_value_too(self) -> None:
        """AC1 names THREE readers. Mutant: `shared = {}` in `_ck_review_attribution`.

        It survived the whole suite before this test existed, which meant the row computed the
        shared reading and decided nothing with it - AC1 false in the one row the story's own
        notes single out. A unit covered by a lane that carries no per-unit verdict must be
        reported as covered BY THAT LANE, and must not also appear as unreviewed: printing
        `UNREVIEWED US0001` beside `US0001 by adversarial evidence` is the self-contradiction
        this unit exists to remove.
        """
        with mock.patch.object(sr, "_coverage",
                               return_value={"US0001": {"covered": True,
                                                        "by": "adversarial evidence"},
                                             "US0002": {"covered": False, "by": None}}):
            self._run()
            row = self._row(sr.checklist(self.root, "RETRO9100"), "review-attribution")
        self.assertIn("by a non-verdict lane", row["value"], row["value"])
        self.assertIn("US0001 by adversarial evidence", row["detail"])
        self.assertNotIn("UNREVIEWED US0001", row["detail"],
                         "a unit the shared reading covered was also printed as unreviewed")

    def test_two_agreeing_readings_are_answered(self) -> None:
        """The positive control. Without it a resolver hard-coded to the disagreement state
        kills neither mutant - the always-refuses guard."""
        ck = self._ck()
        row = self._row(ck, "coverage-consistency")
        self.assertEqual(sr.ANSWERED, row["state"], row["detail"])
        self.assertIn("agree", row["value"])
        self.assertNotIn("coverage-consistency", ck["outstanding"])


class ChecklistWindowTests(ChecklistBase):
    """US0591. An item whose window shut before the close was being raised where a waiver was
    its only exit, and a gate whose only exit at firing time is a waiver is a receipt."""

    def test_every_item_declares_its_enforcer(self) -> None:
        """Mutant: stamp every row's window with the close, so none can expire.

        A PRESENCE assertion is killed by deleting a key and passes on that mutant while
        delivering nothing - so this asserts the VALUE: the rows the plan enforces must carry a
        window that is not the close, and every window must name a verb the tooling exposes.
        """
        pre_close = {"reconciled-before-plan", "goal-seat-reviewed", "batch-groomed",
                     "run-opened"}
        rows = {i["id"]: i for i in sr.CHECKLIST}
        self.assertTrue(pre_close <= set(rows), "a pre-close row was renamed or removed")
        for rid in pre_close:
            self.assertNotEqual(sr.CLOSE_WINDOW, sr._window(rows[rid]),
                                f"{rid} is enforced before the close, but declares the close as "
                                f"the last command that could satisfy it")
        for item in sr.CHECKLIST:
            self.assertTrue(sr._window(item), f"{item['id']} declares no window")
        # Resolvability, asserted through `cycle_drift` itself rather than against a set built
        # here. The first version of this guarded the check behind `if known:` and `known` was
        # PERMANENTLY EMPTY - `cycle_drift` returns {unresolved, uncovered, unverifiable} and
        # never `covered`/`verbs` - so a window naming a verb nothing exposes passed the whole
        # file. `cycle_drift` now walks windows on the same terms as commands.
        self.assertEqual([], sr.cycle_drift()["unresolved"],
                         "a checklist row names a command or window nothing exposes")

    def test_an_expired_item_reports_rather_than_gates(self) -> None:
        """Mutant: delete the expired bucket's line from `render_checklist`.

        Dropping the state out of `_OUTSTANDING` alone leaves both buckets empty and the close
        printing `none outstanding` - the row VANISHES instead of being reported. So this
        asserts it appears in the render, carrying the command that should have enforced it.
        """
        ck = self._ck()
        row = self._row(ck, "goal-seat-reviewed")
        self.assertEqual(sr.EXPIRED, row["state"], row["detail"])
        self.assertNotIn("goal-seat-reviewed", ck["outstanding"],
                         "an item past its window is holding the close")
        self.assertIn("goal-seat-reviewed", ck["expired"])
        self.assertIn("sprint plan", row["detail"])
        rendered = sr.render_checklist(ck)
        self.assertIn("PAST THEIR WINDOW", rendered)
        self.assertIn("enforce at `sprint plan`", rendered)

    def test_the_shipped_checklist_command_reports_the_expired_item_and_does_not_refuse_on_it(
            self) -> None:
        """The SHIPPED entry point, not the library behind it.

        `cmd_checklist` exits non-zero while any compulsory item is outstanding, and that exit
        code is what the close chain and a reader both act on. A library test cannot see the
        wiring: `checklist()` could return the expired row correctly while the command still
        counted it as outstanding and refused. Both halves are asserted here - the row is
        printed with its enforcing command, and the exit code does not hold on it.
        """
        self._run()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = sr.main(["--root", str(self.root), "checklist", "--id", "RETRO9100"])
        out = buf.getvalue()
        self.assertIn("PAST THEIR WINDOW", out)
        self.assertIn("enforce at `sprint plan`", out)
        # Non-zero here, but for the CLOSING REVIEW - a close-window item - never for the
        # expired ones. A command that refused on an expired row would be the receipt again.
        self.assertEqual(1, rc)
        self.assertIn("closing-review", out)

    def test_a_close_window_item_still_gates(self) -> None:
        """Mutant: `_expired` returns True unconditionally.

        The control against moving windows disarming the items the close genuinely owns. The
        criterion first named an unwritten retro; that row reports `ran` for a missing file
        (BG0540), so the example is the closing review, which gates as the table intends.
        """
        ck = self._ck()
        row = self._row(ck, "closing-review")
        self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
        self.assertIn("closing-review", ck["outstanding"])
        self.assertNotIn("closing-review", ck["expired"])

    def test_a_satisfied_close_item_is_in_no_bucket(self) -> None:
        """The positive control beside AC3: without it, an implementation reporting everything
        outstanding passes the test above."""
        ck = self._ck()
        row = self._row(ck, "retro")
        self.assertEqual(sr.RAN, row["state"], row["detail"])
        self.assertNotIn("retro", ck["outstanding"])
        self.assertNotIn("retro", ck["expired"])


class TickVerificationTests(ChecklistBase):
    """US0594. Two units of one run were closed on ticks the diff contradicted, and the
    checklist passed them.

    The seam is the changed-paths SOURCE (`_changed_paths`), never the comparison the row makes
    with it - a fixture patching the comparison patches away the thing under test and both
    mutants with it. Every test asserts the row's DETAIL as well as its state: `_resolve_item`
    turns any resolver exception into NOT_RUN with the message in `detail`, so a state-only
    assertion is satisfied by a resolver that raises on every input.
    """

    def _unit(self, uid: str, affects: str, ticked: bool) -> None:
        mark = "x" if ticked else " "
        # Overwrite the base fixture's own file rather than adding a second one: two files
        # carrying one id is a duplicate-id tree, and `find_by_id` would answer with whichever
        # it reached first - which is how this test first passed while measuring nothing.
        (self.root / "sdlc-studio" / "stories" / f"{uid}-s.md").write_text(
            f"# {uid}: s\n\n> **Status:** Done\n> **Affects:** {affects}\n> **Points:** 2\n\n"
            f"## Acceptance Criteria\n\n- [{mark}] **AC1** the thing\n", encoding="utf-8")

    def _resolve(self, changed, base="abc123") -> dict:
        self._run(base_ref=base)
        with mock.patch.object(sr, "_changed_paths", return_value=changed):
            ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
        return self._row(ck, "tick-verification")

    def test_a_tick_the_tree_contradicts_is_outstanding(self) -> None:
        """Mutant: emit a detail naming neither the unit nor the criterion.

        A row that says something is wrong without saying WHAT cannot be acted on, and the
        criterion makes naming both law.
        """
        self._unit("US0001", "src/touched.py", ticked=True)
        self._unit("US0002", "src/never_touched.py", ticked=True)
        row = self._resolve({"src/touched.py"})
        self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
        self.assertIn("US0002", row["detail"])
        self.assertIn("AC1", row["detail"])
        self.assertNotIn("US0001", row["detail"], "a supported tick was reported as contradicted")

    def test_a_supported_tick_passes(self) -> None:
        """The control. Mutant: delete the changed-surface consultation, flagging every tick."""
        self._unit("US0001", "src/touched.py", ticked=True)
        self._unit("US0002", "src/also.py", ticked=True)
        row = self._resolve({"src/touched.py", "src/also.py"})
        self.assertEqual(sr.RAN, row["state"], row["detail"])

    def test_an_unrecorded_base_ref_refuses(self) -> None:
        """Mutant: fall back to HEAD when the recorded base ref is empty.

        A fallback treats everything as changed, passes every tick, and reproduces the defect
        this row exists to catch while reporting itself green.
        """
        self._unit("US0001", "src/never.py", ticked=True)
        self._unit("US0002", "src/never2.py", ticked=True)
        self._run(base_ref="")
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
        row = self._row(ck, "tick-verification")
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("base ref", row["detail"])

    def test_a_story_criterion_is_read_in_its_own_convention(self) -> None:
        """A story's claim is a `- **Verified:** yes` stamp under `### ACn`, not a checkbox.

        Reading only the box made this row inert for every story in the corpus - 0 of 651 - so
        it reported `ticks supported` across a whole batch having examined nothing, including
        the very unit whose two false ticks are the rationale this row cites.
        """
        (self.root / "sdlc-studio" / "stories" / "US0001-s.md").write_text(
            "# US0001: s\n\n> **Status:** Done\n> **Affects:** src/never.py\n"
            "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
            "- **Given** x\n- **Verified:** yes (2026-08-07)\n", encoding="utf-8")
        self.assertEqual(["AC1"], sr._ticked_criteria(
            (self.root / "sdlc-studio" / "stories" / "US0001-s.md").read_text(encoding="utf-8")))
        self._unit("US0002", "src/touched.py", ticked=True)
        row = self._resolve({"src/touched.py"})
        self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
        self.assertIn("US0001", row["detail"])
        self.assertIn("AC1", row["detail"])

    def test_a_criterion_stamped_NO_is_not_a_tick(self) -> None:
        """Mutant: widen `_VERIFIED_RE` to accept `no`.

        Eight artefacts in the corpus carry `- **Verified:** no`. Counting an explicitly
        UNVERIFIED criterion as a claim of doneness would make the row report contradictions
        for work nobody claimed - the opposite error, and just as wrong.
        """
        body = ("# US0009: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: a\n\n- **Verified:** no\n\n### AC2: b\n\n"
                "- **Verified:** yes (2026-08-07)\n")
        self.assertEqual(["AC2"], sr._ticked_criteria(body),
                         "a criterion stamped `no` was counted as a tick")

    def test_the_number_it_reports_is_the_number_it_examined(self) -> None:
        """Mutant: `examined += len(ticked)` -> `examined += 1`.

        The row prints the count, and a printed figure nothing pins is a figure that drifts.
        """
        (self.root / "sdlc-studio" / "stories" / "US0001-s.md").write_text(
            "# US0001: s\n\n> **Status:** Done\n> **Affects:** src/touched.py\n"
            "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
            "- **Verified:** yes (2026-08-07)\n\n### AC2: b\n\n"
            "- **Verified:** yes (2026-08-07)\n\n### AC3: c\n\n"
            "- **Verified:** yes (2026-08-07)\n", encoding="utf-8")
        self._unit("US0002", "src/touched.py", ticked=True)
        row = self._resolve({"src/touched.py"})
        self.assertEqual(sr.RAN, row["state"], row["detail"])
        self.assertIn("4 ticked", row["value"], f"the count is wrong: {row['value']}")

    def test_a_diff_that_changed_NOTHING_is_not_an_unreadable_diff(self) -> None:
        """Mutant: `if changed is None:` -> `if not changed:`.

        An empty set is an ANSWER - the run changed nothing - and it must contradict every tick.
        Treating it as unreadable reports the row unjudged, which is the failing-open direction.
        """
        self._unit("US0001", "src/never.py", ticked=True)
        self._unit("US0002", "src/never2.py", ticked=True)
        row = self._resolve(set())
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("unchanged since", row["detail"],
                      f"an empty diff was reported as unreadable rather than as a "
                      f"contradiction: {row['detail']}")

    def test_a_pass_over_no_ticks_at_all_is_refused(self) -> None:
        """A pass over an empty set is not a pass - the affirmative-over-nothing shape the
        sibling rows refuse by design. Mutant: return RAN when nothing was examined."""
        for uid in ("US0001", "US0002"):
            self._unit(uid, "src/touched.py", ticked=False)
        row = self._resolve({"src/touched.py"})
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("nothing was checked", row["detail"])

    def test_the_diff_source_is_exercised_against_real_git(self) -> None:
        """`_changed_paths` is MOCKED in every other test here, so nothing pinned it at all -
        four mutants survived the whole suite, each turning "cannot judge" into "nothing
        changed", which the row reads as every tick contradicted.

        Mutants this kills: a non-zero return, an unverifiable ref, and the exception path all
        answering `set()` instead of None; and `...` narrowed to `..`.
        """
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@x", "PATH": os.environ.get("PATH", ""),
               "HOME": str(d), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
        run = lambda *a: subprocess.run(["git", *a], cwd=str(d), env=env,
                                        capture_output=True, text=True, check=True)
        run("init", "-q", "-b", "main")
        (d / "first.txt").write_text("1\n", encoding="utf-8")
        run("add", "-A"); run("commit", "-qm", "one")
        base = run("rev-parse", "HEAD").stdout.strip()
        (d / "second.txt").write_text("2\n", encoding="utf-8")
        run("add", "-A"); run("commit", "-qm", "two")

        changed = sr._changed_paths(d, base)
        self.assertEqual({"second.txt"}, changed,
                         "the real diff was not read - this is the seam every other test mocks")
        # None, never an empty set: "could not look" and "nothing changed" lead to OPPOSITE
        # verdicts in the row above, and collapsing them certifies what it could not check.
        self.assertIsNone(sr._changed_paths(d, ""), "an empty base ref answered a set")
        self.assertIsNone(sr._changed_paths(d, "no-such-ref-at-all"),
                          "an unresolvable ref answered a set")
        self.assertIsNone(sr._changed_paths(d / "nowhere", base),
                          "an unusable repo answered a set")

    def test_a_ref_shaped_like_an_option_cannot_make_git_write_a_file(self) -> None:
        """The ref is interpolated into one argv token. Unverified, `--output=<path>` is read by
        git as an OPTION: it writes the file, exits 0, and returns an empty diff, which the row
        reads as every tick contradicted. Verified first, it is refused."""
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@x", "PATH": os.environ.get("PATH", ""),
               "HOME": str(d), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
        run = lambda *a: subprocess.run(["git", *a], cwd=str(d), env=env,
                                        capture_output=True, text=True, check=True)
        run("init", "-q", "-b", "main")
        (d / "f.txt").write_text("1\n", encoding="utf-8")
        run("add", "-A"); run("commit", "-qm", "one")
        victim = d / "written-by-git.txt"
        self.assertIsNone(sr._changed_paths(d, f"--output={victim}"))
        self.assertFalse(victim.exists(), "the ref was parsed as an option and git wrote a file")

    def test_an_unreadable_diff_is_unjudged_not_supported(self) -> None:
        """None is not an empty set. `could not be taken` and `nothing changed` lead to opposite
        verdicts, and collapsing them certifies what the row could not check."""
        self._unit("US0001", "src/a.py", ticked=True)
        self._unit("US0002", "src/b.py", ticked=True)
        row = self._resolve(None)
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("unjudged", row["detail"])


def _lean_unit(uid: str, affects: str, verdicts: list[str]) -> str:
    """A unit in the lean criterion shape every Sprint 4 unit uses: a bold `ACn:` bullet with a
    `Verify:` and a `Verified:` sub-bullet. An empty verdict leaves the stamp off entirely."""
    lines = [f"# {uid}: s", "", "> **Status:** Done", f"> **Affects:** {affects}",
             "> **Points:** 2", "", "## Acceptance Criteria", ""]
    for n, verdict in enumerate(verdicts, 1):
        lines += [f"- **AC{n}:** Given a thing, then it happens. Fails on: HEAD",
                  f"  - **Verify:** pytest tests/test_x.py::T::test_{n}"]
        if verdict:
            lines.append(f"  - **Verified:** {verdict}")
    return "\n".join(lines) + "\n"


class TickVerificationReadsTheLeanShapeTests(ChecklistBase):
    """BG0771: the row read a criterion as done only under a `### ACn` heading or a `- [x]` box.

    The lean shape - a `- **ACn:**` bullet with `Verify:` and `Verified: yes` sub-bullets - is
    what every Sprint 4 unit is written in, so RUN-01M3BK9Y's close examined none of its 35 units
    and refused `no ticked criteria found`. The bullet is read through the shared
    `sdlc_md.AC_BULLET_RE` and stands where the heading stood: the `Verified: yes` that follows
    it is the tick, and the bullet alone is not.
    """

    def test_a_lean_bullet_criterion_is_read(self) -> None:
        """AC1. MUTANTS: HEAD (reads none); ticking every `**ACn**` bullet without its Verified
        line; a private copy of the bullet pattern instead of the shared one."""
        lean = _lean_unit("US0001", "src/a.py",
                          ["yes (2026-09-25)", "no", "manual (2026-09-25) - retired, superseded "
                           "by US0915", "", "yes (2026-09-25)"])
        lean = lean.replace("**AC5:**", "**AC5a:**")
        self.assertEqual(["AC1", "AC5a"], sr._ticked_criteria(lean),
                         "a lean criterion was misread: `yes` is a tick, and `no`, a retired "
                         "`manual` stamp and a missing stamp are not")

        bug = ("# BG0001: b\n\n## Acceptance Criteria\n\n"
               "- [ ] **AC1** a thing\n  - **Verify:** pytest t.py::T::a\n"
               "  - **Verified:** yes (2026-09-25)\n"
               "- [ ] **AC2** never stamped\n  - **Verify:** pytest t.py::T::b\n"
               "- [x] **AC3** ticked by hand\n  - **Verified:** yes (2026-09-25)\n"
               "- [ ] **AC4** stamped no\n  - **Verified:** no\n")
        # AC3's stamp must not be credited to AC2, the unstamped bullet before it: a bullet
        # read as the heading is closed by the next bullet, ticked or not.
        self.assertEqual(["AC1", "AC3"], sr._ticked_criteria(bug))

        # The two readings that existed before are unchanged.
        heading = ("## Acceptance Criteria\n\n### AC1: a\n\n- **Verified:** yes (2026-08-07)\n\n"
                   "### AC2: b\n\n- **Verified:** no\n")
        self.assertEqual(["AC1"], sr._ticked_criteria(heading))
        boxes = "## Acceptance Criteria\n\n- [x] **AC1** the thing\n- [x] an unnamed one\n"
        self.assertEqual(["AC1", "an unnamed criterion"], sr._ticked_criteria(boxes))

        # The bullet is read through the SHARED pattern, not a copy: with it matching nothing,
        # the lean reading goes with it.
        with mock.patch.object(sr.sdlc_md, "AC_BULLET_RE", re.compile(r"(?!)")):
            self.assertEqual([], sr._ticked_criteria(lean),
                             "the bullet was read by a pattern other than sdlc_md.AC_BULLET_RE")

    def _git(self, *args: str) -> str:
        return gitutil.git(list(args), self.root, text=True).stdout.strip()

    def _commit(self, message: str) -> None:
        self._git("add", "-A")
        self._git("-c", "commit.gpgsign=false", "commit", "-qm", message)

    def _checklist_row(self) -> dict:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sr.main(["--root", str(self.root), "checklist", "--id", "RETRO9100",
                     "--format", "json"])
        return self._row(json.loads(buf.getvalue()), "tick-verification")

    def test_the_close_row_judges_lean_units(self) -> None:
        """AC2. Through the shipped `checklist` command over a real git diff, on a CLOSED run at
        the build rung. MUTANTS: HEAD (`no ticked criteria found`); fixing a copy of the reader
        the row does not call."""
        stories = self.root / "sdlc-studio" / "stories"
        (stories / "US0001-s.md").write_text(
            _lean_unit("US0001", "src/one.py", ["yes (2026-09-25)", "yes (2026-09-25)", "no"]),
            encoding="utf-8")
        (stories / "US0002-s.md").write_text(
            _lean_unit("US0002", "src/two.py", ["yes (2026-09-25)", "yes (2026-09-25)"]),
            encoding="utf-8")
        src = self.root / "src"
        src.mkdir()
        (src / "one.py").write_text("one = 1\n", encoding="utf-8")
        (src / "two.py").write_text("two = 2\n", encoding="utf-8")
        self._git("init", "-q", "-b", "main")
        self._commit("the base")
        base = self._git("rev-parse", "HEAD")
        self._run(base_ref=base, outcome=run_state.PARTIAL, ended_at="2026-09-25T12:00:00Z")
        import sprint  # noqa: PLC0415 - the rung's one reader, as the row calls it
        self.assertEqual("done", sprint.run_rung(run_state.read(self.root)),
                         "the fixture must sit on the build rung")

        # Only US0001's declared surface changed: US0002's two ticks are unsupported, by name.
        (src / "one.py").write_text("one = 11\n", encoding="utf-8")
        self._commit("US0001's work")
        row = self._checklist_row()
        self.assertEqual(sr.NOT_RUN, row["state"], row)
        self.assertIn("2 ticked criterion/criteria unsupported", row["value"])
        self.assertIn("US0002 AC1", row["detail"])
        self.assertIn("US0002 AC2", row["detail"])
        self.assertNotIn("US0001", row["detail"], "a supported tick was reported unsupported")

        # Both surfaces changed: every tick is supported and counted - 2 on US0001 (its AC3 is
        # stamped `no`) and 2 on US0002.
        (src / "two.py").write_text("two = 22\n", encoding="utf-8")
        self._commit("US0002's work")
        row = self._checklist_row()
        self.assertEqual(sr.RAN, row["state"], row)
        self.assertIn(f"4 ticked criterion/criteria supported by the diff since {base}",
                      row["value"])


class TickVerificationReadsTheRungTests(ChecklistBase):
    """BG0584: the row asked the BUILD rung's question of every run.

    `_ck_tick_verification` asks whether the tree supports what the units TICKED. On a `design`
    rung nothing is ticked and nothing should be - that rung's PRODUCT is authored criteria that
    are deliberately RED - so the row reported `no ticked criteria found` and held the close as a
    compulsory unanswered item. That reasoning is exactly right for a build rung and structurally
    unanswerable for a grooming one: it could not be ANSWERED, only waived, and D0144 waived it.
    A row whose only exit is a waiver trains the operator to waive.

    Same family as BG0582 - a lane that reads no rung and applies the build rung's question to a
    run that never targeted it.
    """

    def _unit(self, uid: str, affects: str, ticked: bool) -> None:
        mark = "x" if ticked else " "
        (self.root / "sdlc-studio" / "stories" / f"{uid}-s.md").write_text(
            f"# {uid}: s\n\n> **Status:** Done\n> **Affects:** {affects}\n> **Points:** 2\n\n"
            f"## Acceptance Criteria\n\n- [{mark}] **AC1** the thing\n", encoding="utf-8")

    def _row_for(self, goal: str, *, base: str = "abc123", changed=frozenset()) -> tuple:
        self._run(base_ref=base, goal=goal)
        with mock.patch.object(sr, "_changed_paths", return_value=changed):
            ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
        return self._row(ck, "tick-verification"), ck

    def test_the_rung_is_read_before_the_diff_branches(self) -> None:
        """AC1. MUTANT: move the rung check below the base-ref and diff-unreadable branches.

        Both of those return NOT_RUN, and the REAL close resolved this row as `diff unreadable` -
        so a rung check placed at `not examined` satisfies a fixture and leaves the observed wall
        standing. The fixture therefore breaks BOTH: no recorded base ref, and a diff that cannot
        be read. A correct implementation never reaches either.
        """
        self._unit("US0001", "src/a.py", ticked=False)
        self._unit("US0002", "src/b.py", ticked=False)
        self._run(base_ref="", goal="design")
        with mock.patch.object(sr, "_changed_paths", return_value=None):
            ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
        row = self._row(ck, "tick-verification")
        self.assertEqual(sr.RAN, row["state"], row["detail"])
        self.assertIn("design", row["value"])
        self.assertNotIn("base ref", row["detail"])
        self.assertNotIn("diff unreadable", row["value"])
        self.assertNotIn("tick-verification", ck["outstanding"])

    def test_a_ticked_criterion_on_a_design_rung_is_reported_not_blocking(self) -> None:
        """AC2. MUTANT: return NOT_RUN for a tick found on a design rung.

        `checklist` is not in `_DEFERRABLE_CLOSE_STAGES`, so a blocking row here is a hard
        refusal with no bounded exit - which is the shape this unit exists to REMOVE, not to
        relocate from the empty case to the ticked one. The tick is still worth saying, and the
        detail must name the unit or the report is a number nobody can act on.
        """
        self._unit("US0001", "src/a.py", ticked=True)
        self._unit("US0002", "src/b.py", ticked=False)
        row, ck = self._row_for("design")
        self.assertEqual(sr.RAN, row["state"], row["detail"])
        self.assertNotIn("tick-verification", ck["outstanding"])
        self.assertIn("US0001", row["detail"])
        self.assertIn("AC1", row["detail"])

    def test_the_build_rung_is_unchanged(self) -> None:
        """AC3. MUTANT: short-circuit on EVERY rung rather than only a non-`done` one.

        The regression this row exists to catch must survive the fix. BG0582 was rejected at
        round two for scoping its sibling on `!= done`, which moved the defect onto plan and
        triage instead of removing it - and the FIRST cut of this unit made the same mistake
        again, caught by its own review. So `plan` and `triage` are asserted here beside an
        explicit `done` and an ABSENT goal: their product is not grooming (`--goal plan`
        selects, sequences and estimates already-groomed units), so they keep exactly the
        behaviour they had. The earlier version of this test asserted only `done` and `None`,
        and the mutant `!= "done"` -> `== "design"` survived all 177 tests in this file.
        """
        for goal in ("done", None, "plan", "triage"):
            with self.subTest(goal=goal):
                self._unit("US0001", "src/touched.py", ticked=True)
                self._unit("US0002", "src/never_touched.py", ticked=True)
                fields = {"goal": goal} if goal else {}
                self._run(base_ref="abc123", **fields)
                with mock.patch.object(sr, "_changed_paths",
                                       return_value={"src/touched.py"}):
                    ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
                row = self._row(ck, "tick-verification")
                self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
                self.assertIn("US0002", row["detail"])
                self.assertIn("tick-verification", ck["outstanding"])

    def test_a_design_rung_over_unreadable_units_is_not_a_pass(self) -> None:
        """AC5. MUTANT: report `RAN` when no unit artefact resolved.

        The first cut returned `all 1 unit(s) carry criteria that are unticked` having opened
        ZERO files - the affirmative-over-an-empty-set shape the build-rung branch twenty lines
        below refuses in terms, with the honest rule written beside the branch that broke it.
        """
        # The batch must NAME the unit, or `_run_record` resolves no run, the rung defaults to
        # `done`, and this test would exercise the build branch while appearing to pass.
        self._run(base_ref="abc123", goal="design", batch=["US9999"])
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US9999"])
        row = self._row(ck, "tick-verification")
        self.assertEqual(sr.NOT_RUN, row["state"], row["detail"])
        self.assertIn("tick-verification", ck["outstanding"])
        self.assertIn("resolves to a file", row["detail"])

    def test_the_shipped_cli_resolves_the_row_on_a_design_rung(self) -> None:
        """AC6. MUTANT: delete the rung short-circuit from `_ck_tick_verification`.

        THE WIRING TEST. `verify_ac lane-check` reported this unit as changing a command while
        none of its verifiers entered the shipped entry point. `sprint_report.py checklist` is
        the command that renders this row to an operator, and a library test cannot see whether
        the resolver is reached by it.
        """
        import subprocess  # noqa: PLC0415 - the point is to leave this process
        script = Path(__file__).resolve().parents[1] / "sprint_report.py"
        self._unit("US0001", "src/a.py", ticked=False)
        self._unit("US0002", "src/b.py", ticked=False)
        self._run(base_ref="abc123", goal="design")
        r = subprocess.run([sys.executable, "-B", str(script), "--root", str(self.root),
                            "checklist", "--id", "RETRO9100"], capture_output=True, text=True)
        page = r.stdout + r.stderr
        self.assertIn("design rung's exit", page, page)
        self.assertNotIn("no ticked criteria found", page, page)

    def test_the_row_resolves_without_the_waiver(self) -> None:
        """AC4. MUTANT: leave D0144 accepted.

        A fix landing under a live waiver is a fix nobody can observe: `_resolve_item` lets a
        waiver override whatever the resolver found, so the row reads WAIVED whether it is
        repaired or not - and would conceal a regression in the repair just as effectively.
        Asserted against THIS repository's own decisions log, not a fixture, because the waiver
        being retracted is a fact about this repo.
        """
        import decisions  # noqa: PLC0415
        repo = Path(__file__).resolve().parents[5]
        # WITHOUT THIS the test is vacuous: `waiver_for` answers None for any tree with no
        # decisions log, so a wrong `parents[]` index passes it while measuring nothing. The
        # first cut of this test pointed at `.claude/` and passed for exactly that reason.
        self.assertTrue((repo / "sdlc-studio" / "decisions.md").is_file(),
                        f"decisions log not found under {repo} - this test is measuring nothing")
        # `assertIsNotNone(... or list_decisions(repo))` CANNOT FAIL - `list_decisions`
        # returns [] for a missing log and `[] is not None`. A review found it; it is the
        # same vacuity that made this test's first cut pass against `.claude/`. Assert the
        # log parsed to actual ROWS, which is what distinguishes "no such waiver" from
        # "nothing was read".
        self.assertTrue(decisions.list_decisions(repo),
                        "the decisions log parsed to zero rows, so an absent waiver is "
                        "indistinguishable from an unreadable log")
        self.assertIsNone(
            decisions.waiver_for(repo, "rule:sprint-checklist:tick-verification"),
            "D0144 is still live, so the tick-verification row reads WAIVED and this "
            "unit's repair cannot be observed at the close it was filed from")


class WaiverKindTests(ChecklistBase):
    """US0595 AC2. The retro counts the two kinds apart.

    The fixture is ASYMMETRIC on purpose - two expired against one deliberate. With one of each
    both figures are 1, and an implementation reporting the expired count under the deliberate
    label is byte-identical to a correct one.
    """

    def _waive(self, subject: str, kind: str) -> None:
        import decisions
        decisions.ensure_log(self.root)
        decisions.record_waiver(self.root, subject, "because", authorised_by="op", kind=kind)

    def test_expired_and_deliberate_are_counted_apart(self) -> None:
        """Mutant: collapse `expired` and `deliberate` into one figure in `rep["waivers"]`."""
        self._waive("rule:sprint-checklist:goal-seat-reviewed", "expired")
        self._waive("rule:sprint-checklist:batch-groomed", "expired")
        self._waive("rule:sprint-checklist:retro", "deliberate")
        self._run()
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(2, rep["waivers"]["expired"])
        self.assertEqual(1, rep["waivers"]["deliberate"])
        rendered = sr.render(rep)
        self.assertIn("2 expired before anyone was asked", rendered)
        self.assertIn("1 deliberate", rendered)

    def test_a_log_with_no_waivers_prints_no_waiver_line(self) -> None:
        """The control. A line printed unconditionally is a line nobody reads."""
        self._run()
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual({"deliberate": 0, "expired": 0, "unkinded": 0}, rep["waivers"])
        self.assertNotIn("WAIVERS:", sr.render(rep))

    def test_an_unreadable_log_says_so_rather_than_reporting_zero(self) -> None:
        """Unreadable is not empty. Zeroes read as nothing to report; only one of the two means
        somebody should go and look."""
        rep = {"waivers": None}
        self.assertIn("not zero, unread", "\n".join(sr._waiver_lines(rep)))


class ClosingReviewVerdictTests(ChecklistBase):
    """US0593. The row counted recorded passes and reported `ran` over four rounds of which
    three rejected. A count cannot see a verdict.

    Every fixture writes into BOTH ledgers the resolver reads - the sprint-review rows and the
    run-state rounds - because against a fixture that populates only one, the old counting
    implementation returns `none recorded`, which is the same OUTSTANDING state a correct
    resolver returns, and the mutant survives its own test.
    """

    def _ledgers(self, rows: list[tuple], rounds: list[tuple]) -> None:
        """`rows` as (verdict, units, date); `rounds` as (verdict, units, recorded_at)."""
        path = self.root / "sdlc-studio" / "reviews"
        path.mkdir(parents=True, exist_ok=True)
        body = ["| Base | Reviewer | Author | Verdict | Date | Units | Findings |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for verdict, units, date in rows:
            body.append(f"| abc123 | qa; seat; r | agent | {verdict} | {date} | {units} | none |")
        (path / "sprint-review-record.md").write_text(
            "# Sprint reviews\n\n" + "\n".join(body) + "\n", encoding="utf-8")
        self._extra_rounds = [
            {"round": i + 1, "verdict": v, "reviewer": "qa; seat", "units": u.split(","),
             "recorded_at": at}
            for i, (v, u, at) in enumerate(rounds)]

    def _resolve(self) -> dict:
        ck = self._ck(review_rounds=getattr(self, "_extra_rounds", []))
        return self._row(ck, "closing-review")

    def test_reject_only_rounds_are_outstanding(self) -> None:
        """Mutant: revert the resolver to `len(ctx['sprint_reviews'])`, reading no verdict."""
        self._ledgers([("REJECT", "US0001,US0002", "2026-01-02")],
                      [("REJECT", "US0001,US0002", "2026-01-02T10:00:00Z")])
        row = self._resolve()
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertNotIn("none recorded", row["value"],
                         "outstanding because the verdicts were read must be distinguishable "
                         "from outstanding because nothing was found")
        self.assertIn("unresolved", row["value"])
        self.assertIn("US0001", row["detail"])

    def test_a_rejection_stays_terminal_even_when_a_lane_says_covered(self) -> None:
        """Mutant: delete the terminal-verdict clause from `open_units`.

        This is the regression US0596 introduced and the repair removed, and it had NO test:
        deleting the clause left the whole suite green while a run whose verdicts were all
        REJECT reported `N unit(s) approved`. The other fixtures cannot catch it, because
        `review_coverage` already calls a rejected unit uncovered - so the clause only bites
        where a NON-VERDICT lane says covered and a verdict says otherwise, which is exactly the
        shape that produced the false green.
        """
        self._ledgers([("REJECT", "US0001,US0002", "2026-01-02")],
                      [("REJECT", "US0001,US0002", "2026-01-02T10:00:00Z")])
        self._run(review_rounds=getattr(self, "_extra_rounds", []))
        with mock.patch.object(sr, "_coverage",
                               return_value={"US0001": {"covered": True, "by": "evidence"},
                                             "US0002": {"covered": True, "by": "evidence"}}):
            row = self._row(sr.checklist(self.root, "RETRO9100"), "closing-review")
        self.assertEqual(sr.NOT_RUN, row["state"],
                         f"a recorded rejection stopped being terminal: {row['value']}")
        self.assertIn("unresolved", row["value"])

    def test_an_approve_covering_every_unit_passes(self) -> None:
        """The control. A row that never clears satisfies the test above for free."""
        self._ledgers([("APPROVE", "US0001,US0002", "2026-01-02")],
                      [("APPROVE", "US0001,US0002", "2026-01-02T10:00:00Z")])
        row = self._resolve()
        self.assertEqual(sr.RAN, row["state"], row["detail"])

    def test_a_later_approve_clears_an_earlier_reject(self) -> None:
        """Mutant: take `rows[0]` rather than `rows[-1]` per unit.

        The two rounds carry distinct ordered stamps on purpose: `record_verdict` writes a date
        with no time, so two verdicts in one sitting tie and a date-keyed max picks either.
        """
        self._ledgers([("REJECT", "US0001,US0002", "2026-01-02"),
                       ("APPROVE", "US0001,US0002", "2026-01-03")],
                      [("REJECT", "US0001,US0002", "2026-01-02T10:00:00Z"),
                       ("APPROVE", "US0001,US0002", "2026-01-03T10:00:00Z")])
        row = self._resolve()
        self.assertEqual(sr.RAN, row["state"], row["detail"])

    def test_a_partially_covered_run_names_the_uncovered_unit(self) -> None:
        """Mutant: clear the row when ANY unit carries an approval.

        That implementation kills all three mutants above and still reports `ran` on a batch of
        twelve where one was reviewed, which is the counted-passes defect one level down.
        """
        self._ledgers([("APPROVE", "US0001", "2026-01-02")],
                      [("APPROVE", "US0001", "2026-01-02T10:00:00Z")])
        row = self._resolve()
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("unreviewed", row["value"])
        self.assertIn("US0002", row["detail"])
        self.assertNotIn("US0001", row["detail"].replace("US0002", ""))


class SprintChecklistStageTests(ChecklistBase):
    """US0574. The compulsory set is the cycle's own stages, so a stage nobody held is visible
    on the page rather than inferred from its absence."""

    def test_every_stage_carries_a_state_and_none_is_blank(self) -> None:
        ck = self._ck()
        stages = [r for r in ck["items"] if r["kind"] == sr.STAGE]
        self.assertTrue(stages, "the checklist carries no stage rows at all")
        for row in stages:
            self.assertIn(row["state"], (sr.RAN, sr.NOT_RUN, sr.WAIVED, sr.EXPIRED),
                          f"{row['id']} has state {row['state']!r}, which is not one of the "
                          f"four a stage may hold")
            self.assertTrue(str(row["value"]).strip(),
                            f"{row['id']} reports an empty value, which reads as 'nothing to "
                            f"say' - the one thing a stage that never ran must not read as")

    def test_a_stage_that_did_not_run_is_named_not_omitted(self) -> None:
        # No goal-review record and a run that stopped short with no handoff.
        ck = self._ck(outcome="blocked", handoff=None)
        text = sr.render_checklist(ck)
        # `goal-seat-reviewed` is enforced at `sprint plan`, so at a close it is EXPIRED
        # rather than NOT RUN (US0591) - still NAMED, which is what this test is about, and
        # still carrying the command that should have enforced it.
        self.assertEqual(self._row(ck, "goal-seat-reviewed")["state"], sr.EXPIRED)
        self.assertEqual(self._row(ck, "handoff")["state"], sr.NOT_RUN)
        self.assertIn("goal-seat-reviewed",
                      " ".join(ck["outstanding"] + ck["expired"]) + " " + text)
        self.assertIn("Handoff", text)
        self.assertIn("NOT RUN", text)

    def test_the_stage_set_and_the_cycle_cannot_drift_apart(self) -> None:
        drift = sr.cycle_drift()
        self.assertEqual(drift["unresolved"], [],
                         "a checklist row names a command that no longer ships")
        self.assertEqual(drift["uncovered"], [],
                         "a ceremony verb has no checklist row and is not declared "
                         "mechanics in NON_CEREMONY_VERBS")
        # The THIRD bucket, which this assertion did not make. It was non-empty on the shipped
        # tree - `retro.py` built its subparsers inside `main()`, so two of the eighteen rows
        # were certified unchecked - while a caller asserting only the first two read green.
        # A guard reporting its own blindness into a bucket nobody asserts is not a guard.
        self.assertEqual(drift["unverifiable"], [],
                         "a checklist row's script publishes no build_parser(), so the row "
                         "cannot be checked and the guard is reporting its own blindness")

    def test_a_new_ceremony_verb_with_no_row_is_CAUGHT(self) -> None:
        """The guard's own falsifiability: it must fail when the cycle really does gain a
        stage. Without this the green result above proves only that the guard is quiet."""
        import sprint as sprint_mod
        real = sprint_mod.build_parser

        def with_extra_verb():
            p = real()
            for action in p._actions:
                if isinstance(action.choices, dict):
                    action.choices["retrospective"] = None
                    break
            return p

        sprint_mod.build_parser = with_extra_verb
        try:
            # Script-qualified now, because the guard walks every ceremony script and a bare
            # verb name would not say which one gained a stage.
            self.assertIn("sprint retrospective", sr.cycle_drift()["uncovered"])
        finally:
            sprint_mod.build_parser = real

    def test_every_row_s_script_publishes_a_parser_so_none_is_UNVERIFIABLE(self) -> None:
        """The third bucket on its own. It was non-empty on the shipped tree and asserted
        nowhere: `retro.py` built its subparsers inside `main()`, so two of the eighteen rows
        were certified unchecked while a caller reading the other two buckets saw green."""
        self.assertEqual([], sr.cycle_drift()["unverifiable"])
        # ...and the bucket still WORKS: a row whose script publishes no parser lands in it.
        import retro as retro_mod
        real = retro_mod.build_parser
        del retro_mod.build_parser
        try:
            drift = sr.cycle_drift()["unverifiable"]
            self.assertTrue(any("retro" in d for d in drift),
                            "a script with no build_parser() is not reported unverifiable, so "
                            "the empty bucket above proves only that the guard is quiet")
        finally:
            retro_mod.build_parser = real

    def test_a_ceremony_verb_added_to_a_NON_sprint_script_is_caught(self) -> None:
        """The half the guard did not have. Six of the eighteen rows hold a stage in `critic`,
        `retro`, `lessons` or `handoff`, and `uncovered` walked `sprint` alone - so a ceremony
        added to any of those grew no row and nothing said so, while the shipped doctrine told
        a consuming project the two could not part."""
        import critic as critic_mod
        real = critic_mod.build_parser

        def with_extra_verb():
            p = real()
            for action in p._actions:
                if isinstance(action.choices, dict):
                    action.choices["absolution"] = None
                    break
            return p

        critic_mod.build_parser = with_extra_verb
        try:
            self.assertIn("critic absolution", sr.cycle_drift()["uncovered"])
        finally:
            critic_mod.build_parser = real

    def test_an_unresolvable_command_is_not_reported_as_unverifiable(self) -> None:
        """A row naming a script that does not exist is BROKEN; a row whose script ships but
        publishes no parser is UNJUDGED. Reporting the first as the second fails open."""
        broken = ({"id": "x", "kind": sr.STAGE, "authority": sr.DERIVED, "title": "t",
                   "command": "no_such_script verb", "resolver": "_ck_retro"},)
        real = sr.CHECKLIST
        sr.CHECKLIST = broken
        try:
            drift = sr.cycle_drift()
        finally:
            sr.CHECKLIST = real
        self.assertEqual(len(drift["unresolved"]), 1)
        self.assertEqual(drift["unverifiable"], [])


class SprintChecklistReviewRowTests(ChecklistBase):
    """US0575. An under-covered round must not read like a full one on the page the reviewer of
    record signs off from."""

    def _verdict(self, unit: str, verdict: str, reviewer: str) -> None:
        import critic
        critic.record_verdict(self.root, unit, verdict, reviewer=reviewer, author="builder",
                              issues="probed")

    def test_the_review_row_names_the_units_the_reviewer_and_the_seat(self) -> None:
        seats = self.root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "qa.md").write_text("# Priya Raman\n\n<!-- role: qa -->\n", encoding="utf-8")
        self._verdict("US0001", "APPROVE", "Priya Raman")
        self._verdict("US0002", "APPROVE", "some contractor")
        row = self._row(self._ck(), "review-attribution")
        self.assertIn("US0001", row["detail"])
        self.assertIn("Priya Raman", row["detail"])
        self.assertIn("qa", row["detail"])
        self.assertIn("NO DECLARED SEAT", row["detail"],
                      "a verdict recorded under no declared seat must be reported as "
                      "seat-less, never rendered as if it were a seat review")

    def test_a_single_lens_round_is_reported_as_under_covered(self) -> None:
        """One reviewer, one lens, and the under-covered marker follows from the count."""
        self._verdict("US0001", "APPROVE", "lonely reviewer")
        self._verdict("US0002", "APPROVE", "lonely reviewer")
        row = self._row(self._ck(), "review-attribution")
        self.assertIn("1 lens", row["value"])
        self.assertIn("UNDER-COVERED", row["value"])

    def test_two_distinct_reviewers_are_not_reported_as_under_covered(self) -> None:
        """The control for the test above: the marker must depend on the count, not be
        constant. A warning that is always printed is a warning nobody reads."""
        self._verdict("US0001", "APPROVE", "reviewer one")
        self._verdict("US0002", "APPROVE", "reviewer two")
        self.assertNotIn("UNDER-COVERED", self._row(self._ck(), "review-attribution")["value"])

    def test_two_reviewers_sharing_ONE_SEAT_are_one_lens(self) -> None:
        """The discriminator the row was named for and did not make. It counted distinct
        reviewer NAMES, so two people in seat `qa` reported "2 lens(es)" and escaped the
        under-covered mark - contradicting the row's own title, the constant `MIN_LENSES` and
        the shipped doctrine. A lens is a point of view, not a person."""
        seats = self.root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "qa.md").write_text("# Priya Raman\n\n<!-- role: qa -->\n", encoding="utf-8")
        # Two DIFFERENT reviewers, both standing in the qa seat - the shape this repo's own
        # delegated reviews take ("qa seat (independent, isolated worktree)").
        self._verdict("US0001", "APPROVE", "qa seat alpha")
        self._verdict("US0002", "APPROVE", "qa seat beta")
        row = self._row(self._ck(), "review-attribution")
        self.assertIn("1 lens", row["value"],
                      "two reviewers in one seat were counted as two lenses")
        self.assertIn("UNDER-COVERED", row["value"])

    def test_two_reviewers_with_NO_seat_are_not_collapsed_into_one(self) -> None:
        """The other side of it. A reviewer with no declared seat is not interchangeable with
        another seat-less reviewer, so they must not fold into a single anonymous lens - that
        would under-report coverage instead of over-reporting it, which is no better."""
        self._verdict("US0001", "APPROVE", "contractor one")
        self._verdict("US0002", "APPROVE", "contractor two")
        row = self._row(self._ck(), "review-attribution")
        self.assertIn("2 lens", row["value"])
        self.assertNotIn("UNDER-COVERED", row["value"])

    def test_a_rejected_unit_is_not_counted_as_covered(self) -> None:
        self._verdict("US0001", "APPROVE", "reviewer one")
        self._verdict("US0001", "REJECT", "reviewer two")     # the LATEST verdict rejects
        row = self._row(self._ck(), "review-attribution")
        self.assertIn("1 rejected", row["value"])
        self.assertIn("REJECTED US0001", row["detail"])
        self.assertNotIn("1 covered", row["value"].split(",")[0] + ",")


class SprintChecklistKnownIssuesBlindnessTests(ChecklistBase):
    """US0571. The row is the one RECORDED-authority item on the page, and it failed OPEN: an
    empty scan and a scan that could not run rendered identically as ANSWERED "none carried",
    over a workspace with open findings on disk. The impediments row draws exactly that
    distinction beside it, so the honest treatment already existed and this one contradicted
    it."""

    def _bug(self, uid: str, stamp: str) -> None:
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Open\n> **Raised-in-batch:** {stamp}\n",
            encoding="utf-8")

    def test_a_run_record_with_no_start_time_reports_UNREADABLE_not_none(self) -> None:
        self._bug("BG0500", "none open 2026-06-01T00:00:00Z")
        ck = self._ck(started_at=None)
        row = self._row(ck, "known-issues")
        self.assertEqual("unreadable", row["value"],
                         "a scan that could not date any finding reported 'none carried'")
        self.assertIn(row["state"], ("UNANSWERED", "unanswered"))
        self.assertIn("UNKNOWN", row["detail"].upper())

    def test_a_missing_retro_makes_the_whole_row_unreadable(self) -> None:
        """Deleting the retro takes out the run-record join as well as the carried table, so
        this exercises the row end to end and NOT the carried-table branch alone - which is why
        it is named for what it does. The branch itself is pinned below."""
        (self.root / "sdlc-studio" / "retros" / "RETRO9100-t.md").unlink()
        row = self._row(self._ck(), "known-issues")
        self.assertEqual("unreadable", row["value"])

    def test_the_carried_table_reports_BLINDNESS_rather_than_an_empty_table(self) -> None:
        """The branch on its own. `retro.find_retro` answers None rather than raising, so the
        reader returned [] for a retro it could not locate - dressing "we could not look" as
        "there was nothing to see" one layer above the exception handler, where the end-to-end
        test above cannot see it."""
        self.assertIsNone(sr._carried_issues(self.root, "RETRO-NOSUCH"),
                          "a retro that cannot be located read as an empty carried table")
        self.assertEqual([], sr._carried_issues(self.root, "RETRO9100"),
                         "the control: a retro that IS found with no rows is empty, not blind")

    def test_a_carried_table_that_RAISES_is_blindness_too(self) -> None:
        """The exception limb, which the missing-retro test does not reach: `find_retro` answers
        None there rather than raising. Both limbs must report blindness or the row can still be
        made to say "none carried" while it saw nothing."""
        # The module sprint_report CALLS, not a fresh `import retro`: in a full pytest run another
        # module can leave a second `retro` in sys.modules, and patching that one reached nothing.
        retro_mod = sr.retro
        real = retro_mod.carried_issues

        def boom(_text):
            raise ValueError("the table is malformed")

        retro_mod.carried_issues = boom
        try:
            self.assertIsNone(sr._carried_issues(self.root, "RETRO9100"),
                              "an unreadable carried table read as an empty one")
        finally:
            retro_mod.carried_issues = real

    def test_a_scan_that_RAN_and_found_nothing_still_says_so(self) -> None:
        """The control: the repair must not turn every clean sprint into 'unreadable'."""
        row = self._row(self._ck(), "known-issues")
        self.assertEqual("none carried", row["value"])
        self.assertIn("the scan ran", row["detail"])


class SprintChecklistImpedimentTests(ChecklistBase):
    """US0576. A blocker recorded mid-run is lost at the close, so the next run rediscovers
    it."""

    def test_a_blocked_unit_is_reported_with_its_blocker(self) -> None:
        """Named for the blocker and asserting only the unit id, which is how the row shipped
        naming who was blocked and never by what. `Blocked By` / `Depends on` is a shipped read
        convention; an operator told a unit is blocked and not what to unstick has been told
        half of it."""
        _unit(self.root, "US0001", "Blocked")
        path = self.root / "sdlc-studio" / "stories" / "US0001-s.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "> **Status:** Blocked", "> **Status:** Blocked\n> **Blocked By:** US0002"),
            encoding="utf-8")
        ck = self._ck(pending_decisions=[{"unit": "US0001", "question": "ship it or hold?",
                                          "resolution": None}])
        row = self._row(ck, "impediments")
        self.assertIn("blocked US0001", row["detail"])
        self.assertIn("US0002", row["detail"], "the recorded blocker is not named")
        self.assertIn("1 blocked", row["value"])

    def test_a_blocked_unit_with_NO_recorded_blocker_is_named_as_such(self) -> None:
        """The absent case, which is the worse one: an impediment nobody can act on must not
        render identically to one with a known cause."""
        _unit(self.root, "US0001", "Blocked")
        row = self._row(self._ck(), "impediments")
        self.assertIn("NO RECORDED BLOCKER", row["detail"])

    def test_an_unresolved_decision_is_reported_with_its_question(self) -> None:
        ck = self._ck(pending_decisions=[
            {"unit": "US0001", "question": "answered already", "resolution": {"choice": "a"}},
            {"unit": "US0002", "question": "which schema wins?", "resolution": None}])
        row = self._row(ck, "impediments")
        self.assertIn("which schema wins?", row["detail"])
        self.assertNotIn("answered already", row["detail"],
                         "a resolved decision is not an impediment")
        self.assertIn("1 open question", row["value"])

    def test_none_and_unreadable_do_not_render_the_same(self) -> None:
        clean = self._row(self._ck(), "impediments")
        self.assertEqual(clean["state"], sr.ANSWERED)
        self.assertEqual(clean["value"], "none")
        # No run record at all: whether anything was blocked is UNKNOWN, not "nothing was".
        (self.root / "sdlc-studio" / ".local" / "run-state.json").unlink()
        blind = self._row(sr.checklist(self.root, "RETRO9100"), "impediments")
        # US0951: a row with nothing to measure reads `not measured`, never `none`.
        self.assertEqual(blind["state"], sr.UNMEASURABLE)
        self.assertNotEqual(blind["value"], clean["value"])


class SprintChecklistDerivedFiguresTests(ChecklistBase):
    """US0569. A report nobody could have filled in from memory."""

    def test_planned_and_delivered_are_both_derived_and_reported(self) -> None:
        """ONE drop and NO adds, deliberately. The original fixture dropped one unit and added
        another, so the batch as it stands (3) and the batch as approved (3) were the same
        number - and the assertion could not tell the reconstruction from the raw list.
        Deleting `_planned_ids`' reconstruction entirely survived it. With 1 drop and 0 adds
        the two readings are 2 and 3, so only the right one passes."""
        _unit(self.root, "US0003", "Ready")
        ck = self._ck(batch=["US0001", "US0002"],
                      batch_changes=[{"action": "drop", "id": "US0003", "reason": "descoped"}])
        row = self._row(ck, "planned-vs-delivered")
        self.assertEqual(row["state"], sr.ANSWERED)
        self.assertIn("/3 unit(s)", row["value"],
                      "planned must be the batch as APPROVED (US0001-US0003), reconstructed "
                      "from the change ledger - not the batch as it stands now (2)")
        # Points on BOTH sides: US0569 AC1 asks for commitment beside actual, and a row that
        # states one in units and the other in points leaves the operator doing the arithmetic.
        self.assertRegex(row["value"], r"\d+/\d+ point\(s\)",
                         "planned points are not reported beside delivered points")

    def test_planned_POINTS_are_reported_beside_delivered(self) -> None:
        """US0569 AC1 asks for planned units AND POINTS beside the delivered figures, so an
        operator can read commitment against actual without arithmetic. Planned points were
        computed nowhere and appeared nowhere; the row stated one side in units and the other
        in points."""
        _unit(self.root, "US0003", "Ready", pts=5)
        ck = self._ck(batch=["US0001", "US0002"],
                      batch_changes=[{"action": "drop", "id": "US0003", "reason": "descoped"}])
        row = self._row(ck, "planned-vs-delivered")
        # US0001=3 + US0002=5 + US0003=5 planned; only the terminal ones delivered.
        self.assertIn("/13 point(s)", row["value"],
                      "the planned points total is absent or is not summed from the planned "
                      "units' own artefacts")

    def test_planned_points_tells_an_ABSENT_total_from_a_real_zero(self) -> None:
        """None and 0 are different facts. A sprint whose planned units cannot be resolved has
        no points total to report; one whose units genuinely carry no points has a total of
        zero. Collapsing them would let the first read as a sprint that committed to nothing."""
        self.assertIsNone(sr._planned_points(self.root, ["US9999"]),
                          "an unresolvable planned set reported a total anyway")
        _unit(self.root, "US0007", "Ready", pts=0)
        self.assertEqual(0, sr._planned_points(self.root, ["US0007"]),
                         "a genuine zero was reported as absent")

    def test_scope_creep_is_reported_as_a_count_and_a_ratio(self) -> None:
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        for n in (1, 2, 3, 4):
            (bugs / f"BG000{n}-x.md").write_text(
                f"# BG000{n}: x\n\n> **Status:** Open\n"
                f"> **Raised-in-batch:** none open 2026-01-02T00:00:00Z\n", encoding="utf-8")
        row = self._row(self._ck(), "scope-creep")
        self.assertIn("4 filed against 2 planned", row["value"])
        self.assertIn("ratio 2.0", row["value"],
                      "the RATIO is the signal - a list of titles is not")

    def test_an_unanswerable_figure_is_unknown_not_zero(self) -> None:
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text("{}",
                                                                            encoding="utf-8")
        ck = sr.checklist(self.root, "RETRO9100")
        for item_id in ("planned-vs-delivered", "scope-creep"):
            row = self._row(ck, item_id)
            # US0951: not measured, which is neither a known issue nor an answer.
            self.assertEqual(row["state"], sr.UNMEASURABLE)
            self.assertIn("unknown", row["value"])
            self.assertNotIn("0 filed against 0", row["value"])

    def test_every_compulsory_item_is_a_row_of_the_report(self) -> None:
        """One artefact, not two. Two close-time documents that both claim to record the run
        is the drift this repo keeps filing bugs about."""
        self._run()
        rep = sr.report(self.root, "RETRO9100")
        self.assertIn("checklist", rep)
        ids = {r["id"] for r in rep["checklist"]["items"]}
        # US0951 AC2: a row that does not apply here is omitted - this fixture is not the
        # skill's own repository, so the verb-surface row has no question to answer.
        applicable = [i for i in sr.CHECKLIST if i["id"] != "doc-surface"]
        self.assertEqual(ids, {i["id"] for i in applicable})
        text = sr.render(rep)
        self.assertIn("## Sprint checklist", text)
        for item in applicable:
            self.assertIn(item["title"], text, f"{item['id']} is not on the rendered page")


class SprintChecklistNotDeliveredTests(ChecklistBase):
    """US0570. Delivered plus dropped plus held plus carried over, with no unit unaccounted
    for."""

    def test_the_report_names_each_dropped_unit_with_its_reason(self) -> None:
        row = self._row(self._ck(batch=["US0001"], batch_changes=[
            {"action": "drop", "id": "US0002", "reason": "the API it needs is not built"}]),
            "not-delivered")
        self.assertIn("dropped US0002", row["detail"])
        self.assertIn("the API it needs is not built", row["detail"])

    def test_held_is_distinguishable_from_dropped_and_delivered(self) -> None:
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "In Progress")
        _unit(self.root, "US0003", "Ready")
        # BOTH lists, because `decision defer` writes both. A fixture carrying only
        # `deferred_units` models a state the writer cannot produce.
        row = self._row(self._ck(batch=["US0001", "US0002"], deferred_units=["US0002"],
                                 pending_decisions=[{"unit": "US0002", "question": "which?",
                                                     "resolution": None}],
                                 batch_changes=[{"action": "drop", "id": "US0003",
                                                 "reason": "descoped"}]), "not-delivered")
        self.assertIn("1 dropped, 1 held", row["value"])
        self.assertIn("held US0002", row["detail"])
        self.assertNotIn("carry-over US0002", row["detail"],
                         "a unit held on an operator decision is not a unit that just did not "
                         "finish - collapsing the two misreports the run")

    def test_a_unit_whose_decision_was_ANSWERED_and_which_shipped_is_not_held(self) -> None:
        """`deferred_units` is append-only and `decision resolve` had no remover, so a unit
        whose question was answered and which then shipped rendered "held (operator decision
        pending)" AND was counted delivered on the same page. Held is a live state: the
        decision must still be outstanding and the unit must still be unfinished."""
        _unit(self.root, "US0001", "Done")
        row = self._row(self._ck(batch=["US0001"], deferred_units=["US0001"],
                                 pending_decisions=[]), "not-delivered")
        self.assertNotIn("held US0001", row["detail"],
                         "a resolved-and-shipped unit is still being reported as held")
        self.assertEqual("none", row["value"],
                         "the unit shipped and its question was answered, so there is nothing "
                         "outstanding to report")

    def test_a_PLANNED_unit_the_retro_never_lists_is_named_not_absorbed(self) -> None:
        """The row read the retro's Batch, so a planned unit that never reached the retro was
        invisible to it and the page asserted "every planned unit was delivered" while
        planned-vs-delivered beside it read 1/2. A unit nobody can account for is the one thing
        this row exists to surface."""
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "Ready")
        self._run(batch=["US0001", "US0002"])
        # The retro lists ONLY US0001; the run planned both.
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001"])
        row = self._row(ck, "not-delivered")
        self.assertIn("US0002", row["detail"])
        self.assertNotEqual("none", row["value"],
                            "a planned unit missing from the retro was absorbed into "
                            "'every planned unit was delivered'")

    def test_carry_over_is_measured_against_the_PLAN_not_the_retro(self) -> None:
        """A unit the retro lists but the run never planned is scope creep, and it has its own
        row. Reading the retro's Batch for this one folded it into commitment-versus-actual,
        so an unplanned unit that did not finish read as a broken promise."""
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "In Progress")     # in the retro, never planned
        self._run(batch=["US0001"])
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001", "US0002"])
        row = self._row(ck, "not-delivered")
        self.assertNotIn("carry-over US0002", row["detail"],
                         "an unplanned unit is being reported against the plan")

    def test_ONE_unit_appears_under_exactly_ONE_heading(self) -> None:
        """Dropped, held, unaccounted and carried must partition the planned set. A planned,
        deferred, non-terminal unit the retro does not list was emitted under BOTH held and
        UNACCOUNTED, so one undelivered unit read "1 held, 1 UNACCOUNTED" beside "1/2 unit(s)"
        - the arithmetic this row exists to make readable, stating two problems where there was
        one. The unpinned UNACCOUNTED bucket is what let it through: deleting the bucket
        entirely survived the whole suite, because the only assertion on it was satisfied by
        the carry-over bucket already naming the same id."""
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "In Progress")
        # PLANNED, DEFERRED on an open question, non-terminal, and absent from the retro.
        self._run(batch=["US0001", "US0002"], deferred_units=["US0002"],
                  pending_decisions=[{"unit": "US0002", "question": "which?",
                                      "resolution": None}])
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001"])   # retro omits US0002
        row = self._row(ck, "not-delivered")
        self.assertEqual(1, row["detail"].count("US0002"),
                         f"US0002 is reported more than once: {row['detail']}")
        self.assertIn("1 held", row["value"])
        self.assertNotIn("UNACCOUNTED", row["value"],
                         "a held unit is also being counted as unaccounted")

    def test_a_unit_both_DROPPED_and_deferred_is_reported_once(self) -> None:
        """The same partition rule at the other boundary. A unit deferred on a question and then
        dropped from the batch is one departure, not two: rendering "1 dropped, 1 held" for it
        states two problems where there is one, and dropped is the later and truer fact."""
        _unit(self.root, "US0002", "In Progress")
        self._run(batch=["US0001"], deferred_units=["US0002"],
                  pending_decisions=[{"unit": "US0002", "question": "which?",
                                      "resolution": None}],
                  batch_changes=[{"action": "drop", "id": "US0002", "reason": "descoped"}])
        row = self._row(sr.checklist(self.root, "RETRO9100"), "not-delivered")
        self.assertIn("1 dropped", row["value"])
        self.assertIn("0 held", row["value"],
                      "a dropped unit is also being counted as held")
        self.assertEqual(1, row["detail"].count("US0002"),
                         f"US0002 is reported more than once: {row['detail']}")

    def test_the_UNACCOUNTED_bucket_is_what_names_a_unit_the_retro_omits(self) -> None:
        """The bucket on its own. Its own heading must carry the unit, not merely some heading:
        deleting it left carry-over naming the same id and every assertion still passed."""
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "Done")            # TERMINAL, so carry-over cannot claim it
        self._run(batch=["US0001", "US0002"])
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=["US0001"])
        row = self._row(ck, "not-delivered")
        self.assertIn("UNACCOUNTED US0002", row["detail"],
                      "a delivered-but-unlisted planned unit is named by no bucket at all")
        self.assertIn("1 UNACCOUNTED", row["value"])

    def test_the_planned_set_reconciles_with_no_unit_unaccounted_for(self) -> None:
        _unit(self.root, "US0001", "Done")
        _unit(self.root, "US0002", "Review")            # neither delivered nor dropped
        row = self._row(self._ck(), "not-delivered")
        self.assertIn("1 carried over", row["value"])
        self.assertIn("carry-over US0002", row["detail"])
        self.assertIn("Review", row["detail"])


class SprintChecklistKnownIssueTests(ChecklistBase):
    """US0571. 'Carried' and 'nobody looked' must never read the same."""

    def _open_bug(self, uid: str, status: str = "Open") -> None:
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** {status}\n"
            f"> **Raised-in-batch:** none open 2026-01-02T00:00:00Z\n", encoding="utf-8")

    def _rulings(self, *rows: str) -> None:
        path = self.root / "sdlc-studio" / "retros" / "RETRO9100-t.md"
        path.write_text(path.read_text(encoding="utf-8")
                        + "\n## Known issues carried\n\n| Issue | Ruling | Ruled by | Date |\n"
                        + "| --- | --- | --- | --- |\n" + "".join(f"{r}\n" for r in rows),
                        encoding="utf-8")

    def test_a_carried_issue_records_its_ruling_and_who_made_it(self) -> None:
        self._open_bug("BG0001")
        self._rulings("| BG0001 | not-stop-ship | Darren Benson | 2026-01-03 |")
        row = self._row(self._ck(), "known-issues")
        self.assertEqual(row["state"], sr.ANSWERED)
        self.assertIn("BG0001 not-stop-ship by Darren Benson", row["detail"])

    def test_an_unruled_carried_issue_is_reported_as_unruled(self) -> None:
        self._open_bug("BG0001")
        self._open_bug("BG0002")
        self._rulings("| BG0001 | not-stop-ship | Darren Benson | 2026-01-03 |")
        row = self._row(self._ck(), "known-issues")
        self.assertEqual(row["state"], sr.UNANSWERED)
        self.assertIn("UNRULED BG0002", row["detail"])
        self.assertNotIn("UNRULED BG0001", row["detail"])

    def test_an_anonymous_ruling_does_not_pass_as_a_judgement(self) -> None:
        """Who ruled is not decoration: an unattributed ruling cannot be questioned, which is
        exactly what separates a judgement somebody made from one nobody did."""
        self._open_bug("BG0001")
        self._rulings("| BG0001 | not-stop-ship |  | 2026-01-03 |")
        row = self._row(self._ck(), "known-issues")
        self.assertEqual(row["state"], sr.UNANSWERED)
        self.assertIn("records no ruler", row["detail"])

    def test_a_ruling_outside_the_vocabulary_is_not_a_ruling(self) -> None:
        """`| BG0001 | probably fine | ... |` is prose in a ruling column. Accepting it would
        let any word at all discharge the one item the tree cannot derive."""
        self._open_bug("BG0001")
        self._rulings("| BG0001 | probably fine | Darren Benson | 2026-01-03 |")
        row = self._row(self._ck(), "known-issues")
        self.assertEqual(row["state"], sr.UNANSWERED)
        self.assertIn("not one of", row["detail"])
        self.assertIn("1 malformed", row["value"])

    def test_a_stop_ship_ruling_holds_the_close(self) -> None:
        import sprint
        self._open_bug("BG0001")
        self._rulings("| BG0001 | stop-ship | Darren Benson | 2026-01-03 |")
        self._run()
        ck = sr.checklist(self.root, "RETRO9100")
        self.assertIn("STOP-SHIP", self._row(ck, "known-issues")["value"])
        ok, detail, _ = sprint._close_checklist(self.root, "RETRO9100", self._run())
        self.assertFalse(ok, "a stop-ship ruling that stops nothing is a note, not a ruling")
        self.assertIn("known-issues", detail)

    def test_a_closed_finding_is_not_carried_and_needs_no_ruling(self) -> None:
        self._open_bug("BG0001", status="Fixed")
        row = self._row(self._ck(), "known-issues")
        self.assertEqual(row["state"], sr.ANSWERED)
        self.assertIn("none carried", row["value"])


class SprintChecklistAuthorityTests(ChecklistBase):
    """US0572. A practice that is compulsory in prose is compulsory in fact."""

    def test_the_close_refuses_on_an_unanswered_item_and_names_it(self) -> None:
        import sprint
        state = self._run()
        ok, detail, remedy = sprint._close_checklist(self.root, "RETRO9100", state)
        self.assertFalse(ok)
        outstanding = sr.checklist(self.root, "RETRO9100")["outstanding"]
        self.assertTrue(outstanding)
        for item_id in outstanding:
            self.assertIn(item_id, detail, "the refusal must NAME the item, not count them")
        self.assertIn("waive", remedy)

    def test_every_compulsory_item_has_exactly_one_authority(self) -> None:
        ids = [i["id"] for i in sr.CHECKLIST]
        self.assertEqual(len(ids), len(set(ids)), "a duplicated item id")
        for item in sr.CHECKLIST:
            self.assertIn(item["authority"], (sr.DERIVED, sr.RECORDED),
                          f"{item['id']} has no authority, so it silently passes")
            self.assertIn(item["kind"], (sr.STAGE, sr.FIGURE))
            resolver = sr.__dict__.get(item["resolver"])
            self.assertTrue(callable(resolver),
                            f"{item['id']} names resolver {item['resolver']!r}, which does not "
                            f"resolve - an item with no reader is one that always passes")

    def test_waiving_a_compulsory_item_is_recorded_with_a_reason(self) -> None:
        import decisions
        state = self._run()
        # An OUTSTANDING item: since US0951 an unmetered cost is not measured, not owed.
        before = sr.checklist(self.root, "RETRO9100")["outstanding"]
        self.assertIn("tick-verification", before)
        decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:tick-verification",
                                "no criterion in this batch was ticked by hand",
                                authorised_by="the operator")
        row = self._row(sr.checklist(self.root, "RETRO9100"), "tick-verification")
        self.assertEqual(row["state"], sr.WAIVED)
        self.assertTrue(row["waiver"], "the waiver's decision id is not recorded on the row")
        self.assertNotIn("tick-verification",
                         sr.checklist(self.root, "RETRO9100")["outstanding"])
        self.assertIsNone(decisions.waiver_for(self.root, f"{sr.WAIVER_SUBJECT}:known-issues"),
                          "a waiver of one item must not cover its neighbours")

    def test_an_unexplained_waiver_is_REFUSED_at_record_time(self) -> None:
        import decisions
        with self.assertRaises(ValueError):
            decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:cost", "")

    def test_a_resolver_that_raises_is_OUTSTANDING_never_silently_benign(self) -> None:
        """A checklist row that fails open certifies the thing it could not check."""
        real = sr._ck_cost

        def boom(_ctx):
            raise RuntimeError("the ledger is on fire")

        sr._ck_cost = boom
        try:
            self._run()
            ck = sr.checklist(self.root, "RETRO9100")
        finally:
            sr._ck_cost = real
        row = self._row(ck, "cost")
        self.assertEqual(row["state"], sr.UNANSWERED)
        self.assertIn("the ledger is on fire", row["detail"])
        self.assertIn("cost", ck["outstanding"])

    def test_the_close_does_not_deadlock_on_what_it_is_about_to_do(self) -> None:
        """The handoff is produced BY the close. Holding the chain on it makes the only exit the
        step it blocks, which is a deadlock, not a gate."""
        ck = self._ck(outcome="blocked", handoff=None)
        self.assertNotIn("handoff", ck["outstanding"])
        self.assertIn("handoff", ck["pending_in_close"])
        self.assertIn("discharge", sr.render_checklist(ck))

    def test_a_waiver_naming_NO_REAL_ITEM_is_refused(self) -> None:
        """The scope tail was never validated, so a waiver of an item that does not exist
        recorded cleanly and was read by nothing - the close stayed blocked by an item the log
        said had been waived. Verbatim the defect the conformance scope check already existed
        to prevent, in the next rule along."""
        import decisions
        self._run()
        with self.assertRaises(ValueError) as ctx:
            decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:not-a-real-item",
                                    "because I say so", authorised_by="someone")
        self.assertIn("not a checklist item", str(ctx.exception))

    def test_a_PADDED_scope_tail_cannot_record_a_waiver_that_covers_nothing(self) -> None:
        """The validator stripped the scope tail before checking while the store kept it, so
        the validator was MORE PERMISSIVE than the store: `rule:sprint-checklist: cost` passed,
        was written with the space intact, and the lookup - reading the unpadded key - never
        found it. The waiver recorded cleanly, read as accepted, and covered nothing, which is
        the exact defect the scope check was added to end."""
        import decisions
        self._run()
        subject = f"{sr.WAIVER_SUBJECT}: cost"
        decisions.record_waiver(self.root, subject, "no telemetry",
                                authorised_by="the operator")
        self.assertIsNotNone(decisions.waiver_for(self.root, f"{sr.WAIVER_SUBJECT}:cost"),
                             "the padded subject was stored under a key nothing looks up")
        self.assertNotIn("cost", sr.checklist(self.root, "RETRO9100")["outstanding"],
                         "the item is still outstanding, so the waiver covered nothing")

    def test_a_BARE_rule_waiver_covers_nothing_and_is_refused(self) -> None:
        """The close reads a waiver per ITEM, so a row naming the family alone recorded clean
        while every item stayed outstanding."""
        import decisions
        self._run()
        with self.assertRaises(ValueError):
            decisions.record_waiver(self.root, sr.WAIVER_SUBJECT, "blanket",
                                    authorised_by="someone")

    def test_a_waiver_records_WHO_authorised_it_and_it_reads_back(self) -> None:
        """A waiver is somebody deciding a rule does not apply here. Recorded without a name it
        is a decision with no decider, and the one question a later reader asks has no answer."""
        import decisions
        self._run()
        with self.assertRaises(ValueError) as ctx:
            decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:cost", "no telemetry")
        self.assertIn("WHO authorised", str(ctx.exception))
        decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:cost", "no telemetry",
                                authorised_by="Darren Benson (operator)")
        self.assertEqual("Darren Benson (operator)",
                         decisions.waiver_authoriser(self.root, f"{sr.WAIVER_SUBJECT}:cost"))

    def test_the_close_step_PASSES_once_every_item_is_answered_or_waived(self) -> None:
        """The control for the refusal test: a gate that never passes is not a gate. Waive
        each outstanding item and the same step must go green."""
        import decisions
        import sprint
        state = self._run()
        for item_id in sr.checklist(self.root, "RETRO9100")["outstanding"]:
            decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:{item_id}",
                                    "waived for this test's control",
                                    authorised_by="the operator")
        ok, detail, _ = sprint._close_checklist(self.root, "RETRO9100", state)
        self.assertTrue(ok, f"the step still refuses with everything waived: {detail}")
        self.assertIn("none outstanding", detail)


class CloseReportTests(unittest.TestCase):
    """Being informed is the operator's half of the contract.

    A report nobody is told about is the same as no report. If the operator is not a step in
    the machine, the machine has to reach them - which means the close SAYS what happened
    rather than leaving a file to be discovered.
    """

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sprint_report", Path(__file__).resolve().parent.parent / "sprint_report.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["sprint_report"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_the_close_reports_all_four(self) -> None:
        """MUTANT: drop any one of shipped / carried / cost / findings.

        Each is asserted separately. A report missing the cost is not 75% of a report - it is
        one the operator has to go and look something up for, which is the behaviour being
        removed.
        """
        mod = self._mod()
        out = mod.close_report({
            "run_id": "RUN-X", "shipped": ["US0001", "US0002"], "carried": ["BG0009"],
            "cost": {"tokens": 1234, "points": 8},
            "findings": ["BG0010 filed from the boundary review"],
        })
        for want in ("US0001", "BG0009", "1,234", "BG0010"):
            self.assertIn(want, out, f"the close report never mentions {want}")
        for heading in ("SHIPPED", "CARRIED", "COST", "FINDINGS"):
            self.assertIn(heading, out.upper(), f"the report has no {heading} section")

    def test_an_absent_figure_is_named_absent(self) -> None:
        """MUTANT: omit the line when the value is missing.

        A dropped line reads as nothing to report. 'Not attributable' and 'nothing happened'
        are different facts, and only one of them means somebody should look.
        """
        mod = self._mod()
        out = mod.close_report({"run_id": "RUN-X", "shipped": [], "carried": [],
                                "cost": {}, "findings": []})
        self.assertIn("COST", out.upper(),
                      "the cost section vanished entirely when the figure was missing")
        # Anchored to the COST SECTION, not to the whole report. Scanning the document for
        # "none" was satisfied by the SHIPPED, CARRIED and FINDINGS empty-listings, so blanking
        # the cost line left this green while the section rendered empty - which is exactly the
        # omission this criterion forbids. A verifier a neighbouring section can satisfy is not
        # checking its own subject.
        section = out.split("  COST", 1)[1].split("  FINDINGS", 1)[0].strip().lower()
        self.assertTrue(section, "the COST section is empty - the absent figure was dropped")
        self.assertTrue("not attributable" in section or "not captured" in section
                        or "none" in section,
                        f"an absent cost was silently dropped:\n{out}")


class TruncationIsMarkedTests(unittest.TestCase):
    """BG0463: a silent cap reads as "that is all there was".

    Two rows render a slice and only one said so. The impediments row dropped everything past
    twelve with no marker, so an operator could not tell a batch with twelve blockers from one
    with forty. Its sibling - the review-coverage row - already appends the marker; this is the
    same fact rendered two ways in one report.
    """

    def test_the_impediments_row_marks_what_it_dropped(self) -> None:
        """MUTANT: drop the `(+N more)` suffix, restoring the bare slice.

        Twenty blocked units on disk, because the row derives them by reading each unit's
        status rather than taking a list - a dict fixture skipped silently and asserted nothing.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            ids = [f"BG{i:04d}" for i in range(1, 21)]
            for uid in ids:
                (bugs / f"{uid}-x.md").write_text(
                    f"# {uid}: b\n\n> **Status:** Blocked\n> **Points:** 2\n", encoding="utf-8")
            ctx = {"root": root, "units": ids, "run": {"pending_decisions": []}}
            state, value, detail = sr._ck_impediments(ctx)
        self.assertIn("(+8 more)", detail,
                      f"20 blocked units rendered 12 with no marker: {detail}")

class ExecutionModeAgreementTests(ReportBase):
    """The regression an independent seat found: US0639 added a fifth ledger mode and only ONE
    of the two readers learned about it.

    `_RAN_MODES` was an allow-list of ("full", "selected", "none"). Six `preflight` rows carrying
    623.2 measured seconds were reported by `sprint_report` as "none carries a duration", while
    `sprint.close_cost` read the same six rows and reported 623.2s. The report's sentence was
    false about the bytes on disk - and because `_overhead_ratio` derives delivery by
    SUBTRACTION, 600 seconds of measured, attributed gate time was credited to delivery.

    These pin the PROPERTY (the two readers agree) rather than the enumeration, because pinning
    the list is what failed: a test asserting the tuple's contents would have passed unchanged
    while the ledger grew a mode underneath it.
    """

    def _ledger(self, rows):
        (self.root / "sdlc-studio" / ".local" / "test-execution.json").write_text(
            json.dumps({"runs": rows}), encoding="utf-8")

    def _run(self):
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-MODES", "batch": ["US0001", "US0002"], "outcome": "running",
            "started_at": "2026-07-28T08:00:00Z", "ended_at": "2026-07-28T18:00:00Z"}),
            encoding="utf-8")

    def test_a_mode_this_reader_has_never_heard_of_still_counts_its_seconds(self) -> None:
        """THE property, and the reason it is written this way: the mode below is invented here
        and appears nowhere in the source. Mutant: restore an allow-list - an unknown mode's real
        seconds are discarded and reported as NOT CAPTURED."""
        self._run()
        self._ledger([{"at": "2026-07-28T10:00:00Z", "mode": "a-mode-invented-in-this-test",
                       "seconds": 300.0, "verdict": "pass", "moment": "commit"}])
        with contextlib.redirect_stderr(io.StringIO()):
            act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        self.assertTrue(act["measured"], act)
        self.assertEqual(act["seconds"], 300.0)
        self.assertNotIn("a-mode-invented-in-this-test",
                         pathlib.Path(sr.__file__).read_text(encoding="utf-8"),
                         "the reader names this mode, so it is enumerating what counts rather "
                         "than excluding what does not")

    def test_the_report_and_close_cost_agree_on_one_ledger(self) -> None:
        """Two readers of one ledger must not disagree (LL0016). Mutant: exclude any mode from
        one reader and not the other - the two figures diverge and this reddens.

        `preflight` is named explicitly here because it is the mode that actually broke this,
        but the assertion is an EQUALITY between the readers, not a check that the list contains
        the right strings."""
        self._run()
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "preflight", "seconds": 300.0,
             "verdict": "fail", "moment": "close", "run_id": "RUN-MODES"},
            {"at": "2026-07-28T11:00:00Z", "mode": "preflight", "seconds": 300.0,
             "verdict": "fail", "moment": "close", "run_id": "RUN-MODES"},
            {"at": "2026-07-28T12:00:00Z", "mode": "full", "seconds": 77.6,
             "verdict": "pass", "moment": "close", "run_id": "RUN-MODES"},
        ])
        import sprint as sprint_mod
        with contextlib.redirect_stderr(io.StringIO()):
            act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        cost = sprint_mod.close_cost(self.root, "RUN-MODES")
        self.assertEqual(act["seconds"], cost["gate_seconds"],
                         "the report and the close cost read the same ledger differently")
        self.assertEqual(act["seconds"], 677.6)

    def test_a_reuse_row_is_counted_apart_and_not_as_cost(self) -> None:
        """The negative control, and it is DEFENSIVE rather than live - said plainly because a
        test that hides which it is misleads the next reader.

        The shipped writer records `seconds: 0.0` on a reuse row, so counting one today adds
        nothing and the exclusion changes no number. The row below carries 999s deliberately, to
        pin the INTENT against a future writer that records the seconds a reuse SAVED: folding
        those in would publish a saving as a cost, which is the direction a cost report must
        never fail in. A fixture using the shipped 0.0 would let that mutant survive - it did,
        on the first attempt at this test.

        Mutant: count every mode without exception - 999 saved seconds are billed as spent."""
        self._run()
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "full", "seconds": 100.0,
             "verdict": "pass", "moment": "commit"},
            {"at": "2026-07-28T11:00:00Z", "mode": "reuse", "seconds": 999.0,
             "verdict": "pass", "moment": "close"},
        ])
        with contextlib.redirect_stderr(io.StringIO()):
            act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        self.assertEqual(act["seconds"], 100.0)
        self.assertEqual(act["reused_runs"], 1)

    def test_measured_gate_time_is_not_credited_to_delivery(self) -> None:
        """The consequence, pinned where it actually hurt. Delivery is total MINUS overhead, so
        a component the reader discards is silently added to delivery. Mutant: discard the
        preflight seconds - the overhead ratio collapses towards zero and the delivery figure
        absorbs ten minutes of measured gate time."""
        self._run()
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "preflight", "seconds": 300.0,
             "verdict": "fail", "moment": "close"},
            {"at": "2026-07-28T11:00:00Z", "mode": "preflight", "seconds": 300.0,
             "verdict": "fail", "moment": "close"},
        ])
        with contextlib.redirect_stderr(io.StringIO()):
            act = sr._execution_actuals(self.root, ["US0001", "US0002"])
            ov = sr._overhead_ratio(self.root, ["US0001", "US0002"], act, {"measured": False})
        self.assertEqual(act["seconds"], 600.0)
        self.assertGreaterEqual(ov["overhead_s"], 600.0,
                                "measured gate time went missing from overhead, which means it "
                                "was credited to delivery by subtraction")

    def test_the_rendered_sentence_accounts_for_every_row_on_the_ledger(self) -> None:
        """The half the first repair missed, and an independent seat found.

        Inverting the `seconds` rule to an exclusion left the three counts beside it as an
        allow-list, so a preflight-only ledger rendered `0 full run(s), 0 selected - 623s of
        test time` - a sentence contradicting itself, printed three lines below a comment
        citing LL0043 against exactly that shape. Every earlier test asserted `act["seconds"]`
        and none asserted the rendered sentence, so nothing could see it.

        The invariant is derivable rather than enumerable: the counts named in the sentence sum
        to the number of rows attributed to the run. Mutant: render from `full_runs` and
        `selected_runs` again - a ledger whose modes this file has not been taught reports zero
        runs beside a non-zero duration, and this reddens while `seconds` stays right.
        """
        self._run()
        self._ledger([
            {"at": "2026-07-28T10:00:00Z", "mode": "preflight", "seconds": 300.0,
             "verdict": "fail", "moment": "close"},
            {"at": "2026-07-28T10:30:00Z", "mode": "preflight", "seconds": 323.2,
             "verdict": "pass", "moment": "close"},
            {"at": "2026-07-28T11:00:00Z", "mode": "full", "seconds": 400.0,
             "verdict": "pass", "moment": "commit"},
            # A mode nobody has taught this file about. It must still be accounted for.
            {"at": "2026-07-28T12:00:00Z", "mode": "smoke", "seconds": 12.0,
             "verdict": "pass", "moment": "commit"},
        ])
        with contextlib.redirect_stderr(io.StringIO()):
            act = sr._execution_actuals(self.root, ["US0001", "US0002"])
        line = sr._execution_lines({"execution": act})[0]
        self.assertEqual(sum((act.get("by_mode") or {}).values()), act["runs"],
                         "the ledger's rows are not all accounted for by mode")
        for mode in ("preflight", "full", "smoke"):
            self.assertIn(mode, line, f"{mode} ran and the sentence does not say so")
        self.assertNotIn("0 full", line)


class OperatorSummaryTests(ReportBase):
    """US0645: human in the LEAD, not human in the loop.

    The seats judge at their speed; the operator reads what happened and reverses what they
    disagree with, at theirs. That only works if the summary is a READ of the ledgers rather
    than prose the signing party composes about its own decision - a seat writing its own
    summary is a seat marking its own homework, and the operator would then be leading from an
    account with a stake in the answer.
    """

    def _verdict(self, uid, verdict, **kw):
        import critic
        critic.record_verdict(self.root, uid, verdict, reviewer="qa", author="dev", **kw)

    def test_an_unrecorded_component_reads_unmeasured(self) -> None:
        """EVERY component, asserted over `.keys()` rather than over a list of field names.

        The earlier version named two of the four, and an independent seat killed it: mutating
        `tokens` to fall back on `0` survived all 131 tests in this module and all 8 in this
        class, because the negative test never looked at that field and the positive control
        only exercises values that are PRESENT. `delivered_points` had no absent branch at all
        and the shipped page rendered `over None points`. That is LL0013 - an assertion that
        enumerates its cases exempts the case it forgot - in a test written to catch exactly
        this class of defect one round earlier.

        Mutant: give any component a zero or a passthrough fallback - this reddens naming the
        field, and a component added later is covered without anyone remembering to add it.
        """
        # A report carrying NOTHING, so every component is genuinely absent and the assertion
        # can range over the keys rather than over a list somebody has to remember to extend.
        cost = sr._sprint_cost_line({"ok": True})
        self.assertTrue(cost, "the cost line is empty, so asserting over its keys proves nothing")
        for field, value in cost.items():
            self.assertEqual(value, sr.UNMEASURED,
                             f"{field} did not state its absence - a run that measured nothing "
                             f"must not read as a run that cost nothing")
        # ...and through the shipped derivation on a real run, for the components that fixture
        # genuinely lacks. A library assertion cannot see a component the summary drops.
        with contextlib.redirect_stderr(io.StringIO()):
            s = sr.operator_summary(self.root, "RETRO9100")
        self.assertTrue(s["ok"], s)
        for field in ("tokens", "elapsed_hours", "overhead_ratio"):
            self.assertEqual(s["cost"][field], sr.UNMEASURED, field)
        # ...and the WORD itself, as a literal, exactly once. Every assertion above compares
        # against `sr.UNMEASURED`, so mutating the constant moves both sides together and the
        # whole class passes while the shipped page prints `Cost: 0 tokens over 8 points` -
        # verbatim the mutant AC1 names. An independent seat found that, and it was introduced
        # BY the repair that replaced four open-coded literals with one constant: the literal
        # assertions it removed were the only thing pinning the word. A self-referential
        # assertion cannot fail, however many of them there are.
        self.assertEqual(sr.UNMEASURED, "UNMEASURED",
                         "the absent-word is only ever compared against itself - a constant "
                         "meaning zero would read as a sprint that cost nothing")

    def test_nought_delivered_points_is_an_answer_not_an_absence(self) -> None:
        """The distinction the blanket rule would destroy, and the reason `delivered_points`
        cannot simply be truth-tested like the rest. A run whose units all sat at Review
        accepted nothing: nought is a real and unwelcome measurement, and reporting UNMEASURED
        there hides it behind a word that means nobody looked.

        Mutant: fold `delivered_points` into the same `or UNMEASURED` test as tokens - a sprint
        that accepted nothing becomes indistinguishable from one that was never metered, which
        is the flattering direction.
        """
        cost = sr._sprint_cost_line({"ok": True, "delivered_points": 0,
                                     "velocity": {}, "overhead": {}})
        self.assertEqual(cost["delivered_points"], 0)
        absent = sr._sprint_cost_line({"ok": True, "velocity": {}, "overhead": {}})
        self.assertEqual(absent["delivered_points"], sr.UNMEASURED)

    def test_a_cost_component_the_renderer_has_never_heard_of_still_reaches_the_page(self) -> None:
        """The completeness claim was true of the dict and false of the PAGE.

        `_sprint_cost_line` asserts over its `.keys()`, so a component added later is pinned -
        but `render_operator_summary` hand-enumerated four field names, so a fifth would be
        derived correctly, returned correctly and silently never printed. An independent seat
        proved it: adding a key survived all 134 tests. A figure that is right and unseen is the
        state `critic brief --tier` was in for a whole sprint.

        Mutant: hand-enumerate the four names again, or drop keys with no phrase entry - the
        unknown component vanishes from the page and this reddens naming it.
        """
        page = sr.render_operator_summary({
            "ok": True, "id": "R", "run_id": "RUN-X", "sprint_goal": "g",
            "goal_verdict": "achieved", "shipped": [], "rejected": [], "carried": [],
            "filed": [], "reversal_candidates": [],
            "cost": {"tokens": 1, "delivered_points": 2, "elapsed_hours": 3.0,
                     "overhead_ratio": 4.0, "wall_clock_hours": 99.5}})
        self.assertIn("99.5", page,
                      "a cost component the renderer has no phrase for went missing from the "
                      "page - the derivation is complete and the reader is not")
        self.assertIn("wall_clock_hours", page)

    def test_a_filed_finding_reaches_the_page(self) -> None:
        """`filed` was computed, returned in the dict and never rendered, while the verb's own
        --help and the changelog fragment both promised "what is carried and where it is filed".
        A derivation that is right and never printed is the state `critic brief --tier` was in
        for a whole sprint.

        Mutant: drop the filed line from the renderer - the id is derived correctly and the
        operator never sees it.
        """
        page = sr.render_operator_summary({
            "ok": True, "id": "RETRO9100", "run_id": "RUN-X", "sprint_goal": "g",
            "goal_verdict": "achieved", "shipped": [], "rejected": [], "carried": [],
            "filed": ["BG0777"], "reversal_candidates": [],
            "cost": {"tokens": 1, "delivered_points": 1,
                     "elapsed_hours": 1.0, "overhead_ratio": 1.0}})
        self.assertIn("BG0777", page)

    def test_a_measured_component_reports_its_value_not_the_word(self) -> None:
        """THE POSITIVE CONTROL, and its absence was a blocking review finding: reducing the
        whole of `_sprint_cost_line` to four constants passed 124 tests, because every existing
        assertion only checked that something read UNMEASURED - which a constant makes trivially
        true. The incident is not hypothetical: a commit carrying exactly that mutant reached
        `main` and passed the pre-commit suites green.

        So this asserts the DERIVATION: every field tracks the report it is read from, and none
        of the four is a constant. Mutant: hard-code any one of them - that field stops tracking
        and this reddens on it by name.
        """
        rep = {"ok": True, "sprint_actual_tokens": 1_234_567, "delivered_points": 41,
               "velocity": {"elapsed_hours": 3.5}, "overhead": {"measured": True, "ratio": 2.5}}
        cost = sr._sprint_cost_line(rep)
        self.assertEqual(cost["tokens"], 1_234_567)
        self.assertEqual(cost["delivered_points"], 41)
        self.assertEqual(cost["elapsed_hours"], 3.5)
        self.assertEqual(cost["overhead_ratio"], 2.5)
        # ...and it TRACKS: move every input and every output must move with it
        moved = sr._sprint_cost_line({"ok": True, "sprint_actual_tokens": 999,
                                      "delivered_points": 7,
                                      "velocity": {"elapsed_hours": 1.0},
                                      "overhead": {"measured": True, "ratio": 9.9}})
        self.assertEqual([moved["tokens"], moved["delivered_points"],
                          moved["elapsed_hours"], moved["overhead_ratio"]], [999, 7, 1.0, 9.9])
        self.assertNotEqual(set(cost.values()) & set(moved.values()), set(cost.values()),
                            "a field did not move when its input did - it is a constant")

    def test_a_measured_run_reaches_the_rendered_page(self) -> None:
        """The lane half: a derivation that is correct and never printed is the state `critic
        brief --tier` was in for a whole sprint. Mutant: drop the cost line from the renderer -
        the figures are right and the operator never sees them."""
        rep = {"ok": True, "id": "RETRO9100", "run_id": "RUN-X", "sprint_goal": "g",
               "goal_verdict": "achieved", "shipped": [], "rejected": [], "carried": [],
               "filed": [], "reversal_candidates": [],
               "cost": {"tokens": 1_234_567, "delivered_points": 41,
                        "elapsed_hours": 3.5, "overhead_ratio": 2.5}}
        page = sr.render_operator_summary(rep)
        self.assertIn("1234567", page.replace(",", ""))
        self.assertIn("41 points", page)

    def test_the_signing_seat_contributes_no_prose(self) -> None:
        """THE property. Mutant: interpolate the verdict's note into the summary - a seat marks
        its own homework, and the two summaries differ."""
        self._verdict("US0001", "APPROVE", issues="I judged this excellent work of mine")
        with contextlib.redirect_stderr(io.StringIO()):
            first = sr.operator_summary(self.root, "RETRO9100")
        self._verdict("US0001", "APPROVE", issues="something entirely different, at length")
        with contextlib.redirect_stderr(io.StringIO()):
            second = sr.operator_summary(self.root, "RETRO9100")
        self.assertEqual(first, second,
                         "a party to the decision reached the operator's page")

    def test_the_reversal_candidates_are_named_with_their_ids(self) -> None:
        """Leading is a bounded act only if the summary says where to look. Mutant: list the
        delivered units alone - the summary is a manifest, and the operator must re-read the
        whole batch to lead it."""
        self._verdict("US0001", "REJECT", issues="the test could not fail")
        with contextlib.redirect_stderr(io.StringIO()):
            s = sr.operator_summary(self.root, "RETRO9100")
        why = {r["unit"]: r["why"] for r in s["reversal_candidates"]}
        self.assertIn("US0001", why)
        self.assertIn("rejected", why["US0001"])
        page = sr.render_operator_summary(s)
        self.assertIn("What to overturn", page)
        self.assertIn("US0001", page)

    def test_a_finding_carried_under_the_policy_is_named_with_its_id(self) -> None:
        """AC3's Given names "a finding filed under the carry-forward policy", and no test
        touched it - a review seat emptied both `carried` and `filed` and 124 tests passed.

        Under D0129 a REJECT files its findings and the run ships, so the carried list IS the
        operator's action list: "some findings were carried" is not something anybody can act
        on, and a list of ids is. Mutant: empty either list - this reddens on the id.
        """
        run_started = "2026-07-28T08:00:00Z"
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps({
            "run_id": "RUN-CARRY", "batch": ["US0001", "US0002"], "outcome": "running",
            "started_at": run_started, "ended_at": "2026-07-28T18:00:00Z"}), encoding="utf-8")
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0901-carried.md").write_text(
            "# BG0901: a finding this run filed and did not fix\n\n"
            "> **Status:** Open\n> **Severity:** Medium\n> **Points:** 2\n"
            "> **Raised-in-batch:** RUN-CARRY 2026-07-28T09:00:00Z\n\n"
            "## Summary\nA carried finding.\n", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            s = sr.operator_summary(self.root, "RETRO9100")
        self.assertIn("BG0901", s["filed"], s)
        self.assertIn("BG0901", s["carried"], s)
        self.assertIn("BG0901", sr.render_operator_summary(s))


    def test_the_shipped_verb_prints_it(self) -> None:
        """THE LANE TEST (LL0040). A summary reachable only from a library call is one no
        operator can read. Mutant: add the function and forget the subparser."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            # `--root` is a TOP-LEVEL argument on this parser, so it precedes the verb. A lane
            # test that guesses the argument order tests the guess, not the wiring.
            rc = sr.main(["--root", str(self.root), "operator-summary",
                          "--id", "RETRO9100"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertIn("Operator summary", out.getvalue())
        self.assertIn("What to overturn", out.getvalue())


class StaleMutantRowsAreNotEvidenceTests(unittest.TestCase):
    """US0835 AC5, SUPERSEDED by US0875: the one-page report states no mutation evidence, so a
    stale ledger row cannot be published as evidence the tests can fail. The node is kept
    because US0835's stamped Verify line names this class.

    MUTANT: put a per-unit mutant figure back on the page - a row applied to bytes the file no
    longer holds would then read as killed evidence again."""

    def test_the_report_publishes_no_mutation_evidence(self) -> None:
        d = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        fixture_run(d)                      # carries a mutation ledger for every unit
        ledger = d / "sdlc-studio" / ".local" / "mutation-runs.json"
        self.assertTrue(ledger.is_file(), "the fixture carries no mutation ledger to ignore")
        rep = sr.build_report(d, FIX_RETRO)
        self.assertFalse([f"{sec}.{k}" for sec, k, f in _leaf_figures(rep)
                          if "mutation" in str(f.get("source") or "") or "mutant" in k],
                         "a figure on the page is derived from the mutation ledger")


class ReportIndexTests(unittest.TestCase):
    """US0836 AC5: a filed report leaves its type's index present, like every other type.

    `report` is registered in `ARTIFACT_TYPES`, so `reconcile detect` requires
    `sdlc-studio/reports/_index.md` the moment the first RPT file exists - and no template
    shipped to create one from. Filing the very first report therefore put the tree into a
    state the repo's own pre-commit gate calls drift and `reconcile apply` cannot clear,
    which is a wall every consuming project hits on its first close and not just this one.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_filing_a_report_creates_its_index_and_leaves_no_drift(self) -> None:
        """MUTANT: write the JSON and the Markdown twin and stop, as the filer did - the
        first close of every project then ends with a gate that refuses the commit the close
        told it to make, and the remedy names a template that does not exist.
        """
        fixture_run(self.root)
        rep = sr.build_report(self.root, FIX_RETRO)
        rid = sr.file_report(self.root, rep)
        idx = self.root / "sdlc-studio" / "reports" / "_index.md"
        self.assertTrue(idx.is_file(), "the report was filed without its type's index")
        text = idx.read_text(encoding="utf-8")
        self.assertIn(rid, text, "the index carries no row for the report just filed")
        self.assertIn("| ID |", text, "the index carries no table a reconcile can sync")
        # ...and a SECOND report joins the same index rather than replacing it.
        second = sr.file_report(self.root, sr.build_report(self.root, FIX_RETRO))
        text = idx.read_text(encoding="utf-8")
        self.assertIn(rid, text, "filing a second report dropped the first one's row")
        self.assertIn(second, text)


class DocSurfaceRowTests(unittest.TestCase):
    """US0655 AC3: the close row is DERIVED, never a number somebody wrote down."""

    def test_the_close_row_is_derived_from_the_measurement(self) -> None:
        """Mutant: render the row from a constant rather than from the measurement."""
        import importlib.util as _iu, sys as _s, pathlib as _p
        d = _p.Path(__file__).resolve().parent.parent
        _s.path.insert(0, str(d)); _s.path.insert(0, str(d / "lib"))
        spec = _iu.spec_from_file_location("command_audit", d / "command_audit.py")
        ca = _iu.module_from_spec(spec); _s.modules["command_audit"] = ca
        spec.loader.exec_module(ca)
        # BG0559: was `parents[4]`, which is `.claude` rather than the repository. The
        # mocked measurement hid it - the row is now gated on the tree being a skill repo
        # BEFORE the measurement is called, so the wrong root reads as not applicable.
        root = str(_p.Path(__file__).resolve().parents[5])
        real = ca.verb_coverage
        try:
            ca.verb_coverage = lambda *a, **k: {  # noqa: ARG005
                "verbs": 7, "documented": 3, "undocumented": 4, "ratio": 42.9, "missing": []}
            state, value, detail = sr._ck_doc_surface({"root": root})
        finally:
            ca.verb_coverage = real
        self.assertEqual(sr.RAN, state)
        self.assertIn("3 of 7", value,
                      "the close row is not derived from the measurement - a figure typed into "
                      "a report is one that stops being true the day after")
        self.assertTrue(detail.strip(), "the row states no reason a reader can act on")


class DocSurfaceReportRowTests(unittest.TestCase):
    """BG0559 AC5: the second reader. The close report calls the identical measurement, so a
    repair that satisfied only the gate left the same permanent advisory in every consuming
    project's close report."""

    def test_doc_surface_row_is_not_applicable_outside_the_skill_repo(self) -> None:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
        import sprint_report as sr  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            state, value, _detail = sr._ck_doc_surface({"root": d})
            # US0951 AC2: not applicable, so the checklist omits the row.
            self.assertEqual(sr.NOT_APPLICABLE, state)
            self.assertIn("not applicable", value)
            self.assertNotIn("unreadable", value)


class ChecklistHonestyTests(unittest.TestCase):
    """BG0540/BG0544: two rows reported `ran` for a ceremony that had not happened."""

    def test_a_retro_that_was_never_written_reports_not_run(self) -> None:
        """MUTANT: drop the `val.get("path") is None` arm from `_ck_retro`.

        `retro.validate` reports a MISSING file as an error like any other, so the row read
        `ran` - the ceremony reporting itself performed on the strength of a file that does not
        exist. `path` is None only when nothing was found.
        """
        state, value, _d = sr._ck_retro({"retro_validate": {
            "ok": False, "path": None, "errors": ["no retro file for RETRO9999"]}})
        self.assertEqual("not-run", state)
        self.assertIn("no retro file", value)

    def test_a_malformed_retro_still_reports_ran(self) -> None:
        """The control - a retro that exists and is wrong DID run, badly."""
        state, _v, _d = sr._ck_retro({"retro_validate": {
            "ok": False, "path": "x.md", "errors": ["bad heading"]}})
        self.assertEqual("ran", state)

    def test_an_uncovered_unit_with_an_approve_is_not_reported_as_reviewed(self) -> None:
        """MUTANT: restore `unreviewed = [u for u in open_units if not latest.get(u)]`.

        The residue - uncovered, verdict present, verdict is an APPROVE - matched neither
        bucket, fell through both, and the row reported `ran` over a unit the shared coverage
        reading calls uncovered. An APPROVE against a unit no independent pass covers is a
        verdict with nothing behind it.
        """
        import unittest.mock as _m
        ctx = {"units": ["US0001"], "review_rounds": [{"r": 1}]}
        with _m.patch.object(sr, "_verdict_entries", lambda c: [("k", sr._APPROVE, ["US0001"])]), \
                _m.patch.object(sr, "_coverage", lambda c: {"US0001": {"covered": False}}):
            state, value, _d = sr._ck_closing_review(ctx)
        self.assertEqual("not-run", state)
        self.assertIn("unreviewed", value)

    def test_a_covered_unit_with_an_approve_still_reports_ran(self) -> None:
        """The control - the fold must not swallow a genuinely reviewed unit."""
        import unittest.mock as _m
        ctx = {"units": ["US0001"], "review_rounds": [{"r": 1}]}
        with _m.patch.object(sr, "_verdict_entries", lambda c: [("k", sr._APPROVE, ["US0001"])]), \
                _m.patch.object(sr, "_coverage", lambda c: {"US0001": {"covered": True}}):
            state, _v, _d = sr._ck_closing_review(ctx)
        self.assertEqual("ran", state)



class ChecklistRosterTests(unittest.TestCase):
    """BG0612: the close checklist roster was asserted by COUNT ALONE, so deleting an entry
    moved the number and the test simply reported a different one - a roster nobody could lose
    an item from without noticing was exactly what the test did not give. And an entry naming a
    resolver this module does not define failed only when the close REACHED that item, minutes
    into a close, on the one run that needed it."""

    #: The roster's exact membership, in order. Named rather than counted: a count answers "how
    #: many" and the question is "which", and the two differ precisely when one entry is dropped
    #: and another added in the same change.
    EXPECTED = (
        "reconciled-before-plan", "goal-seat-reviewed", "batch-groomed", "run-opened",
        "closing-review", "tick-verification", "goal-judged",
        "retro", "lessons", "handoff", "planned-vs-delivered", "not-delivered",
        "scope-creep", "coverage-consistency", "doc-surface",
        "review-attribution", "impediments", "known-issues", "cost",
    )

    def test_the_roster_asserts_its_exact_names_and_count(self) -> None:
        """AC2. MUTANT: drop the `known-issues` entry from the CHECKLIST literal.

        A count alone cannot see a swap, and it reports a dropped entry as a number rather than
        as the item that went missing. The names are the assertion; the count is stated beside
        them so a reader sees both move together."""
        got = tuple(item["id"] for item in sr.CHECKLIST)
        self.assertEqual(self.EXPECTED, got,
                         "the close checklist roster changed - add the new entry here "
                         "deliberately, or restore the one that went missing")
        self.assertEqual(len(self.EXPECTED), len(sr.CHECKLIST))

    def _import_with_resolver(self, replacement: str):
        """Import a COPY of the shipped module whose first roster entry names `replacement`.

        A real import, because the check under test is a module-level loop and nothing else can
        say whether it runs. Re-implementing the loop here would be a private copy of the thing
        under test - the defect this repository has now shipped twice - and it would pass with
        the loop deleted."""
        import importlib.util  # noqa: PLC0415
        script = Path(__file__).resolve().parents[1] / "sprint_report.py"
        text = script.read_text(encoding="utf-8")
        original = '"resolver": "_ck_reconciled"'
        assert text.count(original) == 1, "the roster's first resolver is no longer unique"
        copy_dir = Path(tempfile.mkdtemp(prefix="roster_"))
        self.addCleanup(shutil.rmtree, copy_dir, ignore_errors=True)
        copy = copy_dir / "sprint_report_probe.py"
        copy.write_text(text.replace(original, f'"resolver": "{replacement}"'), encoding="utf-8")
        sys.path.insert(0, str(script.parent))
        try:
            spec = importlib.util.spec_from_file_location("sr_probe", copy)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            sys.path.remove(str(script.parent))
            sys.modules.pop("sr_probe", None)
        return mod

    def test_an_undefined_or_uncallable_resolver_refuses_at_import(self) -> None:
        """AC3. MUTANTS: delete the module-level loop that walks CHECKLIST and resolves each
        name; narrow the import-time validation to a `hasattr` test, so an attribute that is
        not callable passes it.

        Two distinct typos one line apart, and a presence test catches only the first. An entry
        naming a resolver this module does not define fails only when the close REACHES that
        item - minutes into a close, on the one run that needed it."""
        for label, bad in (("undefined", "_ck_does_not_exist"), ("uncallable", "CHECKLIST")):
            with self.subTest(case=label), self.assertRaises(RuntimeError) as ctx:
                self._import_with_resolver(bad)
            self.assertIn(bad, str(ctx.exception),
                          f"the refusal does not name the resolver it could not use: "
                          f"{ctx.exception}")

    def test_a_fully_defined_roster_imports_normally(self) -> None:
        """AC4, the paired control. MUTANT: raise unconditionally from the import-time
        validation.

        A check that refused every roster would satisfy the row above perfectly and make the
        module unimportable - which is the shipped state, so this row is what says it is not."""
        import importlib.util  # noqa: PLC0415
        script = Path(__file__).resolve().parents[1] / "sprint_report.py"
        spec = importlib.util.spec_from_file_location("sr_probe_ok", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # the shipped roster, imported for real
        self.assertEqual(len(self.EXPECTED), len(mod.CHECKLIST))

# ---------------------------------------------------------------------------------------------
# THE REPORT OF RECORD - US0835, US0836, US0837, US0844, US0845, US0846.
#
# THE FIXTURE RUN is shaped on RUN-01M2JA6J and its artefacts DISAGREE on purpose: the retro's
# prose claims 25 units and 120 points while the run record's batch holds 23 and the unit files'
# `Points:` sum to 103. A deriver that read the wrong artefact is caught by its figure.
# ---------------------------------------------------------------------------------------------

FIX_RUN = "RUN-01TESTFIX"
FIX_RETRO = "RETRO9200"
#: 23 units, 103 points - the run record's batch and the unit files, which the retro contradicts.
FIX_POINTS = [5] * 19 + [3, 3, 1, 1]
FIX_UNITS = ([f"US{101 + i:04d}" for i in range(15)] + [f"BG{201 + i:04d}" for i in range(8)])
FIX_SHA = "ecff745d0ac1b2c3d4e5f60718293a4b5c6d7e8f"
FIX_GOAL = ("Nothing is left open silently: US0101, US0102 and BG0201 reach a terminal on their\n"
            "own verifiers; the lane passes against a baseline measured in CI; and a run can no\n"
            "longer end over an unanswered unit (D9001, D9002).")
FIX_MODEL = "test-model-9"
#: The two session readings: 4,271,975 stamped at open, 10,731,650 at report. Delta 6,459,675.
FIX_OPEN_READING = 4_271_975
FIX_REPORT_READING = 10_731_650
FIX_RUN_TOKENS = FIX_REPORT_READING - FIX_OPEN_READING


def _unit_file(root: Path, uid: str, points: int, *, status: str, acs: int = 3) -> Path:
    rel = "stories" if uid.startswith("US") else "bugs"
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    body = [f"# {uid}: a fixture unit", "",
            f"> **Status:** {status}", f"> **Points:** {points}",
            "> **Verification depth:** entry point 1 of 3", "",
            "## Acceptance Criteria", ""]
    for n in range(1, acs + 1):
        body += [f"### AC{n}: a criterion", "", "- **Given** a fixture", "- **When** it runs",
                 "- **Then** it holds", ""]
    p = d / f"{uid}-a-fixture-unit.md"
    p.write_text("\n".join(body), encoding="utf-8")
    return p


def _ci_runs_file(root: Path, rows: list[dict]) -> Path:
    d = root / "sdlc-studio" / ".local"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "ci-runs.json"
    p.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return p


FIX_CI_ROWS = [
    # THREE push-triggered runs, one of them red - 1 of 3 is 33%.
    {"databaseId": 900001, "event": "push", "conclusion": "success", "headBranch": "main",
     "headSha": "aaaa111", "workflowName": "Lint",
     "createdAt": "2026-09-15T06:00:00Z", "updatedAt": "2026-09-15T06:20:00Z"},
    {"databaseId": 900002, "event": "push", "conclusion": "failure", "headBranch": "main",
     "headSha": "bbbb222", "workflowName": "Lint",
     "createdAt": "2026-09-15T07:00:00Z", "updatedAt": "2026-09-15T07:29:00Z"},
    {"databaseId": 900003, "event": "push", "conclusion": "success", "headBranch": "main",
     "headSha": FIX_SHA, "workflowName": "Lint",
     "createdAt": "2026-09-15T08:00:00Z", "updatedAt": "2026-09-15T08:10:00Z"},
    # TWO runs that are not deployments. Counting these makes the rate read 20%.
    {"databaseId": 900004, "event": "workflow_dispatch", "conclusion": "success",
     "headBranch": "main", "headSha": FIX_SHA, "workflowName": "Lint",
     "createdAt": "2026-09-15T09:00:00Z", "updatedAt": "2026-09-15T09:05:00Z"},
    {"databaseId": 900005, "event": "schedule", "conclusion": "success", "headBranch": "main",
     "headSha": FIX_SHA, "workflowName": "Lint",
     "createdAt": "2026-09-15T10:00:00Z", "updatedAt": "2026-09-15T10:04:00Z"},
]

CONSULT = """# RV9001: stakeholder consult

> **Kind:** stakeholder-consult
> **Run:** {run}

| Persona | Perspective | Verdict | What it found |
| --- | --- | --- | --- |
| Rowan Vale | solo founder-engineer, primary | Concerns | the close moved rejected units on |
| Imre Kass | team lead, brownfield adoption, secondary | Concerns | no reader sees an abandoned unit |
| Petra Lund | enterprise delivery manager, negative | Reject | a hold can be released by its author |
"""

VERDICTS = """# Critic verdicts

| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""

PLAN_VERDICTS = """# Plan-review verdicts

| Unit | Verdict | Reviewer | Author | Date | Brief | Kind | Issues |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""


def _fixture_retro(root: Path, *, units: list[str]) -> Path:
    """The retro whose PROSE disagrees with the batch: 25 / 25 and 120 points."""
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    text = "\n".join([
        f"# RETRO-9200: {FIX_RUN}: a fixture sprint", "",
        "> **Date:** 2026-09-15",
        "> **Batch:** " + ", ".join(units),
        "> **Delivered:** 25 / 25   **Blocked:** 0",
        "",
        "The run delivered 120 points across 25 units, says this prose, and it is wrong.", "",
        "## Delivered", "", "- everything", "",
        "## What went well", "", "- the seats discriminated", "",
        "## What was hard / what stalled", "", "- the meter spanned two sessions", "",
        "## Lessons", "", "- a real lesson worth keeping for the next run", "",
        "## Known issues carried", "",
        # The doctrine's own shape, and its own ruling vocabulary: the ruling column reads one
        # of stop-ship / not-stop-ship / accepted-risk / deferred, never free prose.
        "| Issue | Ruling | Ruled by | Date |", "| --- | --- | --- | --- |",
        "| BG9001 | not-stop-ship | the operator | 2026-09-15 |",
        "| BG9002 | not-stop-ship | the operator | 2026-09-15 |", "",
        "## Actions raised", "",
        "| Finding | Disposition |", "| --- | --- |",
        "| a finding | BG9001 |", "| a second finding | BG9002 |", "",
    ])
    p = d / f"{FIX_RETRO}-a-fixture-sprint.md"
    p.write_text(text, encoding="utf-8")
    return p


def fixture_run(root: Path, *, consult: bool = True, ci: bool = True, goal: str | None = FIX_GOAL,
                verdict: str | None = "achieved", stamps: bool = True,
                legacy_baseline: bool = False) -> None:
    """THE FIXTURE RUN on `root`. Every option removes one artefact, which is how the criteria
    that assert an ABSENCE reads NOT MEASURED get a tree to assert it on."""
    (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / "reviews").mkdir(parents=True, exist_ok=True)
    for uid, pts in zip(FIX_UNITS, FIX_POINTS):
        _unit_file(root, uid, pts, status="Done" if uid.startswith("US") else "Fixed")
    _fixture_retro(root, units=FIX_UNITS)
    if consult:
        (root / "sdlc-studio" / "reviews" / "RV9001-stakeholder-consult.md").write_text(
            CONSULT.format(run=FIX_RUN), encoding="utf-8")
    if ci:
        _ci_runs_file(root, FIX_CI_ROWS)
    # The two review ledgers: three plan REJECTs and two delivery REJECTs (the rework signal).
    rows = []
    for i, uid in enumerate(FIX_UNITS):
        v = "REJECT" if i < 2 else "APPROVE"
        rows.append(f"| {uid} | {v} | Rowan Vale | author-session | 2026-09-15 | bf{i:04d} "
                    f"| full | {'one issue' if v == 'REJECT' else 'none'} |")
    (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").write_text(
        VERDICTS + "\n".join(rows) + "\n", encoding="utf-8")
    prows = []
    for i, uid in enumerate(FIX_UNITS):
        v = "REJECT" if i < 3 else "APPROVE"
        prows.append(f"| {uid} | {v} | Imre Kass | author-session | 2026-09-14 | pf{i:04d} "
                     f"| story | {'one issue' if v == 'REJECT' else 'none'} |")
    (root / "sdlc-studio" / "reviews" / "plan-review-verdicts.md").write_text(
        PLAN_VERDICTS + "\n".join(prows) + "\n", encoding="utf-8")
    # The mutation ledger: three killed rows per unit, none survived.
    entries = [{"target": f"scripts/{uid.lower()}.py", "run": "r1",
                "mutants": [{"unit": uid, "criterion": f"AC{n}", "row": n - 1,
                             "mutant": f"m{n}", "test": "t", "verdict": "killed"}
                            for n in (1, 2, 3)]}
               for uid in FIX_UNITS]
    (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(
        json.dumps({"version": 1, "dropped": 0, "entries": entries}), encoding="utf-8")
    state = {"schema": 1, "run_id": FIX_RUN, "started_at": "2026-09-15T05:00:00Z",
             "ended_at": "2026-09-15T13:00:00Z", "outcome": "goal-reached",
             "batch": list(FIX_UNITS), "goal": goal, "sprint_goal": goal,
             "sprint_goal_verdict": ({"verdict": verdict, "note": "all limbs met by execution"}
                                     if verdict else None),
             "base_ref": "0000000000000000000000000000000000000000",
             "verified_sha": FIX_SHA, "forecast_tokens": 2_575_000}
    if stamps:
        state["session_token_stamps"] = [
            {"tokens": FIX_OPEN_READING, "source": "/t/s1.jsonl", "at": "2026-09-15T05:00:00Z",
             "kind": "open", "model": FIX_MODEL},
            {"tokens": FIX_REPORT_READING, "source": "/t/s1.jsonl", "at": "2026-09-15T13:00:00Z",
             "kind": "report", "model": FIX_MODEL}]
    if legacy_baseline:
        state["session_token_baseline"] = {"tokens": FIX_OPEN_READING, "source": "/t/s1.jsonl",
                                           "at": "2026-09-15T05:00:00Z"}
    (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8")


def reopen_a_delivered_unit(root: Path) -> None:
    """Move a fact the run delivered: US0101, delivered at 5 points, is reopened, so
    `points_delivered` falls from 103 to 98. A re-sized Points line is not such a fact - the page
    replays its own reading of it (US0941) - so it cannot serve as the moved figure."""
    unit = root / "sdlc-studio" / "stories" / "US0101-a-fixture-unit.md"
    text = unit.read_text(encoding="utf-8")
    assert text.count("> **Status:** Done") == 1, "the reopen anchor is not unique"
    unit.write_text(text.replace("> **Status:** Done", "> **Status:** In Progress"),
                    encoding="utf-8")


def _leaf_figures(report: dict):
    """Every (section key, figure key, figure) triple in the report's figure set, in order.

    DELEGATES to production's own `leaf_figures`. This used to be a second, hand-kept copy, and
    it had already drifted: it did not yield a section's `not_measured` marker, which production
    yields and calls a figure. Every assertion over "every figure" was therefore made over a
    strictly smaller set than the report's, and a mutant defaulting a marker's source passed.
    A list of the thing under test, maintained beside the thing under test, goes stale silently.
    """
    return sr.leaf_figures(report)


class ReportOfRecordBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)


class ReportIsDerivedTests(ReportOfRecordBase):
    """US0835: the JSON of record, derived from the run's own artefacts."""

    def test_every_figure_carries_a_resolvable_source(self) -> None:
        """AC1. MUTANT: default a missing `source` to the string `derived`.

        Every figure then carries a source, none of them can be re-derived, and the Provenance
        section's whole claim is false while reading as satisfied."""
        # A fixture WITH unmeasured sections. `fixture_run(self.root)` supplies every artefact,
        # so it produces none at all, and the `not_measured` markers - which production counts
        # as figures - were never put in front of this assertion by anything. Each option below
        # removes one artefact, which is how a section that reads NOT MEASURED gets a tree to
        # read it on.
        fixture_run(self.root, consult=False, ci=False, stamps=False)
        rep = sr.build_report(self.root, FIX_RETRO)
        markers = [(sec, k) for sec, k, _f in _leaf_figures(rep) if k == "not_measured"]
        self.assertTrue(markers,
                        "the fixture produced no unmeasured section, so the marker half of the "
                        "figure set is asserted over nothing")
        seen = 0
        for section, key, fig in _leaf_figures(rep):
            self.assertIsInstance(fig, dict, f"{section}.{key} is not a figure object")
            self.assertIn("value", fig, f"{section}.{key} carries no value")
            self.assertIn("source", fig, f"{section}.{key} carries no source")
            src = fig["source"]
            self.assertTrue(isinstance(src, str) and src.strip(),
                            f"{section}.{key} carries an empty source")
            for part in [p.strip() for p in src.split(",") if p.strip()]:
                # PRODUCTION'S definition of "resolves", not a second one. A regex kept here
                # disagreed with the guard about `gh run list` and about the harness meter, so
                # the test and the thing it tests were answering different questions.
                resolvable = sr._source_resolves(self.root, part)
                self.assertTrue(resolvable,
                                f"{section}.{key} names {part!r}, which is neither a path under "
                                f"the root nor a forge run id")
            seen += 1
        self.assertGreater(seen, 40, "the figure set is too small to be the report")
        # ... and the refusal, with the positive control above it: a deriver that produced no
        # source exits 2 naming the figure's key and its section, and writes no JSON.
        out = io.StringIO()
        err = io.StringIO()
        real = sr.fig

        def sourceless(key, value, source, *a, **kw):
            made = real(key, value, source, *a, **kw)
            if key == "points_delivered":
                made.pop("source")          # a deriver that produced none
            return made

        with mock.patch.object(sr, "fig", sourceless), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "build", "--run", FIX_RUN,
                          "--format", "json"])
        self.assertEqual(rc, 2, "a sourceless figure did not refuse")
        msg = err.getvalue() + out.getvalue()
        self.assertIn("points_delivered", msg, "the refusal does not name the figure")
        self.assertIn("delivered", msg, "the refusal does not name the section")
        self.assertEqual(list((self.root / "sdlc-studio" / "reports").glob("*.json"))
                         if (self.root / "sdlc-studio" / "reports").exists() else [], [],
                         "the refused build wrote JSON anyway")

    def test_the_build_refuses_a_source_a_reader_cannot_go_to(self) -> None:
        """AC1's guard, asked directly. MUTANT: drop the resolution check from
        `_refuse_sourceless` and keep only "is it a non-empty string".

        Then a deriver may answer `derived`, or name a file that was deleted, for every figure
        it produces: each one carries a source, the Provenance section reads as satisfied, and
        not one of them can be re-derived by the reader it was written for. No fixture has a bad
        source at build time - that is the point of the guard - so the only way to put one in
        front of it is to make a deriver produce one.
        """
        fixture_run(self.root)
        self.assertTrue(sr.build_report(self.root, FIX_RETRO), "the control build refused")
        real = sr._signoff_section

        def bad(state_rel):                       # a source that resolves to nothing
            sec = real(state_rel)
            sec["figures"]["principal"]["source"] = "derived"
            return sec

        with unittest.mock.patch.object(sr, "_signoff_section", bad):
            with self.assertRaises(sr.ReportError) as caught:
                sr.build_report(self.root, FIX_RETRO)
        self.assertIn("resolves to nothing", str(caught.exception))
        self.assertIn("principal", str(caught.exception),
                      "the refusal does not name the figure whose source is unreachable")

    def test_figures_come_from_the_artefacts_not_the_retros_prose(self) -> None:
        """AC2. MUTANT: read the header counts from the retro's `Delivered: N / M` line.

        A hand-edited retro then rewrites the report's headline figures - and this repository
        has already shipped a retro header that contradicted its own batch."""
        fixture_run(self.root)
        rep = sr.build_report(self.root, FIX_RETRO)
        figs = {f"{s}.{k}": f for s, k, f in _leaf_figures(rep)}
        units = figs["delivered.planned_units"]
        points = figs["delivered.points_delivered"]
        self.assertEqual(units["value"], 23, "planned_units did not come from the run record")
        self.assertEqual(points["value"], 103, "points_delivered did not come from the unit files")
        self.assertIn("run-state.json", units["source"])
        self.assertIn("US0101-a-fixture-unit.md", points["source"],
                      "points_delivered is not sourced to the unit files")
        retro_rel = "sdlc-studio/retros/RETRO9200-a-fixture-sprint.md"
        sourced_to_retro = {name for name, f in figs.items() if retro_rel in (f["source"] or "")}
        self.assertEqual(set(), sourced_to_retro,
                         "a figure is sourced to the retro's prose, which a hand edit can rewrite")

    def test_the_stakeholder_section_names_its_absent_schema(self) -> None:
        """US0835 AC3, SUPERSEDED by US0875: the one-page report carries no stakeholder-consult
        section at all. The node is kept because US0835's stamped Verify line names it; what it
        pins now is that the report makes no consult claim either way - with a consult artefact
        on disk or without one - so a reader cannot take an absent consult for a clean one.

        MUTANT: put a consult section or figure back on the page."""
        fixture_run(self.root, consult=True)
        rep = sr.build_report(self.root, FIX_RETRO)
        self.assertNotIn("consult", [s["key"] for s in rep["sections"]])
        self.assertFalse([k for sec, k, f in _leaf_figures(rep)
                          if "stakeholder-consult" in str(f.get("source") or "")],
                         "a figure is sourced to the consult artefact")
        self.assertNotIn("Stakeholder consult", sr.render_markdown(rep))

    def test_the_fingerprint_covers_the_facts_and_not_the_signature(self) -> None:
        """AC4. MUTANT: fingerprint the whole JSON file.

        Signing the report then changes the fingerprint the signature just recorded, so every
        sealed run reads INVALIDATED under US0845 from the moment it is signed."""
        fixture_run(self.root)
        first = sr.build_report(self.root, FIX_RETRO)
        f = first["fingerprint"]
        later = dict(first)
        later["generated_at"] = "2099-01-01T00:00:00Z"
        self.assertEqual(sr.fingerprint(later), f, "the timestamp moved the fingerprint")
        signed = dict(first)
        signed["signature"] = {"principal": "the operator", "signed_at": "2026-09-16T09:00:00Z",
                               "fingerprint": f}
        self.assertEqual(sr.fingerprint(signed), f, "the signature moved the fingerprint")
        unit = self.root / "sdlc-studio" / "stories" / "US0101-a-fixture-unit.md"
        unit.write_text(unit.read_text(encoding="utf-8").replace("> **Points:** 5",
                                                                 "> **Points:** 8"),
                        encoding="utf-8")
        third = sr.build_report(self.root, FIX_RETRO)
        self.assertNotEqual(third["fingerprint"], f,
                            "a moved Points value left the fingerprint unchanged")


class RenderingTests(ReportOfRecordBase):
    """US0836 AC1: no fact of another run survives into a rendered page."""

    #: Numerals of two digits or more, and any percentage, in the templates' own STATIC text -
    #: derived from the templates rather than from a list, so a literal nobody listed is caught.
    _NUMERAL = re.compile(r"\d+(?:[.,]\d+)*\s*%|\b\d{2,}(?:[.,]\d{3})*\b")
    _NAME = re.compile(r"\b[A-Z][a-z]{2,} [A-Z][a-z]{2,}\b")

    @staticmethod
    def _static_text(template: str) -> str:
        """The template with every token, directive and stylesheet removed - what a render
        emits verbatim whatever the run."""
        text = re.sub(r"<style>.*?</style>", " ", template, flags=re.S)
        text = re.sub(r"<title>.*?</title>", " ", text, flags=re.S)
        text = re.sub(r"<link[^>]*>", " ", text)
        text = re.sub(r"\{\{[^}]*\}\}", " ", text)
        text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
        return text

    @staticmethod
    def _headings(template: str) -> str:
        return " ".join(re.findall(r"^#+ .*$", template, flags=re.M)
                        + re.findall(r"<h[123][^>]*>(.*?)</h[123]>", template, flags=re.S))

    def test_no_fact_of_another_run_survives_into_a_render(self) -> None:
        """AC1. MUTANT: check only the five ids and names first listed.

        The rendered page then ships another run's rework rate and change failure rate as
        prose, which is the defect in its most quotable form - so the forbidden set is DERIVED
        from the templates' own static text, and every numeral in the page is traced to the
        fixture's own data."""
        tpl_dir = Path(sr.__file__).resolve().parents[1] / "templates"
        md_tpl = (tpl_dir / "core" / "sprint-report.md").read_text(encoding="utf-8")
        html_tpl = (tpl_dir / "reports" / "sprint-report.html").read_text(encoding="utf-8")
        for name, tpl in (("sprint-report.md", md_tpl), ("sprint-report.html", html_tpl)):
            static = self._static_text(tpl)
            self.assertEqual(self._NUMERAL.findall(static), [],
                             f"{name} carries a numeral or percentage in prose no token covers - "
                             f"it is another run's fact on every page after the first")
            headings = self._headings(tpl)
            for hit in self._NAME.findall(static):
                self.assertIn(hit, headings,
                              f"{name} carries the proper name {hit!r} outside a heading")
        fixture_run(self.root)
        rep = sr.build_report(self.root, FIX_RETRO)
        allowed = set()
        for _s, _k, fig in _leaf_figures(rep):
            for form in (str(fig["value"]), f"{fig['value']:,}" if isinstance(fig["value"], int)
                         else str(fig["value"]), str(fig.get("source") or ""),
                         str(fig.get("reason") or ""), str(fig.get("mapping") or ""),
                         str(fig.get("band") or "")):
                allowed.update(self._NUMERAL.findall(form))
        allowed.update(self._NUMERAL.findall(rep["fingerprint"]))
        md = sr.render_markdown(rep)
        html = sr.render_html(rep)
        self.assertNotIn("{{", md)
        self.assertNotIn("{{", html)
        body = html.split("</style>", 1)[1]
        for name, text in (("the Markdown twin", md), ("the HTML rendering", body)):
            for hit in self._NUMERAL.findall(text):
                self.assertIn(hit, allowed,
                              f"{name} carries the numeral {hit!r}, which is no value of this "
                              f"run's own data")


class TemplateRenderingTests(ReportOfRecordBase):
    """US0836 AC2-AC4."""

    _HEADINGS_MD = re.compile(r"^#{2,3} (.+)$", re.M)
    _HEADINGS_HTML = re.compile(r"<h[23][^>]*>(.*?)</h[23]>", re.S)

    def test_an_empty_section_renders_not_measured_by_name_in_both(self) -> None:
        """AC2, over the one-page report. MUTANT: render an absent figure as an empty table
        cell - a reader then cannot separate a measured zero from a measurement nobody took.

        With no forge data, no meter stamps and no rulings, the DORA, Tokens by model and
        Rulings sections of the appendix have no data. (The stakeholder-consult section this
        criterion first named was removed from the report by US0875.)"""
        fixture_run(self.root, consult=False, ci=False, stamps=False)
        rep = sr.build_report(self.root, FIX_RETRO)
        md = sr.render_markdown(rep)
        html = sr.render_html(rep)
        self.assertEqual(self._HEADINGS_MD.findall(md),
                         [h.strip() for h in self._HEADINGS_HTML.findall(html)],
                         "the two renderings do not carry the same ordered section headings")
        for heading in ("DORA", "Tokens by model", "Rulings"):
            for label, text in (("Markdown", md), ("HTML", html)):
                body = self._section_body(text, heading)
                self.assertIn("NOT MEASURED", body,
                              f"the {heading} section of the {label} rendering does not read "
                              f"NOT MEASURED by name")
                after = body.split("NOT MEASURED", 1)[1]
                self.assertRegex(after, r"[A-Za-z]{3,}",
                                 f"{heading} gives no reason after NOT MEASURED in {label}")
                for placeholder in ("| 0 |", "| - |", "| None |", "| n/a |", "|  |",
                                    ">0<", ">-<", ">None<", ">n/a<"):
                    self.assertNotIn(placeholder, body,
                                     f"{heading} rendered an absent figure as {placeholder!r} "
                                     f"in the {label} rendering")
        for cell in re.findall(r"<td[^>]*>(.*?)</td>", html, flags=re.S):
            self.assertTrue(re.sub(r"<[^>]*>", "", cell).strip(),
                            "an absent figure rendered as an empty HTML cell")

    @staticmethod
    def _section_body(text: str, heading: str) -> str:
        """The body under a `##`/`###` heading (Markdown) or an h2/h3 (HTML), to the next."""
        if text.lstrip().startswith("#"):
            for part in re.split(r"^#{2,3} ", text, flags=re.M):
                if part.startswith(heading + "\n"):
                    return part
            raise AssertionError(f"no Markdown section {heading!r}")
        for chunk in re.split(r"<h[23][^>]*>", text):
            if chunk.startswith(heading):
                return chunk
        raise AssertionError(f"no HTML section {heading!r}")

    def test_the_twin_is_written_and_the_html_is_generated_on_demand(self) -> None:
        """AC3. MUTANT: write the HTML beside the twin at PREPARE time.

        A three-hundred-line generated page then churns in git on every re-prepare, which is
        the cost D2a's ruling was made to avoid."""
        fixture_run(self.root)
        rep = sr.build_report(self.root, FIX_RETRO)
        rid = sr.file_report(self.root, rep)
        reports = self.root / "sdlc-studio" / "reports"
        self.assertTrue((reports / f"{rid}.json").is_file(), "the JSON of record was not written")
        self.assertTrue(list(reports.glob(f"{rid}-*.md")), "the Markdown twin was not written")
        self.assertEqual(list((self.root / "sdlc-studio").rglob("*.html")), [],
                         "an HTML page was written into the tree at PREPARE time")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "render", "--report", rid,
                          "--to", "html"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertIn("<h2>Goal</h2>", out.getvalue())
        self.assertEqual(list((self.root / "sdlc-studio").rglob("*.html")), [],
                         "render with no --out created a file")
        target = self.root / "out" / "report.html"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = sr.main(["--root", str(self.root), "render", "--report", rid,
                          "--to", "html", "--out", str(target)])
        self.assertEqual(rc, 0)
        self.assertTrue(target.is_file())
        self.assertEqual(list((self.root / "sdlc-studio").rglob("*.html")), [])
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "render", "--report", rid, "--to", "html",
                          "--out", str(reports / "x.html")])
        self.assertEqual(rc, 2, "an --out inside sdlc-studio/reports/ was not refused")
        self.assertIn("D2a", err.getvalue(), "the refusal does not name D2a")

    def test_the_layout_comes_from_the_shipped_template(self) -> None:
        """AC4. MUTANT: build the Markdown from format strings in the renderer and keep the
        template as documentation.

        The two drift on the first change to either, and the "shipped templates" in this
        story's title then describe nothing that runs."""
        fixture_run(self.root)
        rep = sr.build_report(self.root, FIX_RETRO)
        tpl = (Path(sr.__file__).resolve().parents[1] / "templates" / "core"
               / "sprint-report.md").read_text(encoding="utf-8")
        altered = tpl.replace("## Known issues handed over", "## What this run is still carrying")
        self.assertNotEqual(altered, tpl)
        got = sr.render_markdown(rep, template=altered)
        self.assertIn("## What this run is still carrying", got,
                      "the altered heading did not reach the output, so the template is not the "
                      "source of the layout")
        self.assertNotIn("## Known issues handed over", got)
        unfillable = altered.replace("## Sign-off", "{{no_figure_answers_this}}\n\n## Sign-off")
        with self.assertRaises(sr.ReportError) as ctx:
            sr.render_markdown(rep, template=unfillable)
        self.assertIn("no_figure_answers_this", str(ctx.exception))


class TheGoalLeadsTests(ReportOfRecordBase):
    """US0837 AC1-AC2: the goal leads, verbatim."""

    def test_the_goal_is_first_and_verbatim_in_all_three_renderings(self) -> None:
        """AC1. MUTANT: render the goal through the first-sentence trim the status line uses.

        A goal that is a shopping list then reads as one tidy line, the defect a verbatim quote
        exposes is hidden again, and the section is still present and still labelled the
        sprint goal."""
        fixture_run(self.root)
        recorded = run_state.read(str(self.root))["sprint_goal"]
        self.assertIn("\n", recorded, "the fixture goal is not multi-line")
        rep = sr.build_report(self.root, FIX_RETRO)
        goal_fig = {s["key"]: s for s in rep["sections"]}["goal"]["figures"]["sprint_goal"]
        self.assertEqual(goal_fig["value"], recorded, "the JSON goal is not the recorded string")
        md = sr.render_markdown(rep)
        html = sr.render_html(rep)
        # A section HEADING is layout, not a reading, and the report's own section titles are
        # what the Provenance rows are named after - so a title cannot discriminate here.
        titles = {s["title"] for s in rep["sections"]}
        for label, text in (("the Markdown twin", md),
                            ("the HTML rendering", html.split("</style>", 1)[1])):
            self.assertIn(recorded, text, f"{label} does not carry the goal verbatim")
            at = text.index(recorded)
            for section, key, fig in _leaf_figures(rep):
                if section in ("goal", "identity", "invalidation"):
                    continue
                for form in {str(fig["value"]), f"{fig['value']:,}"
                             if isinstance(fig["value"], int) else str(fig["value"])}:
                    if (len(form) < 4 or form not in text or form in titles
                            or form == sr.NOT_MEASURED):
                        continue
                    self.assertGreater(text.index(form), at,
                                       f"{label}: the figure {section}.{key} ({form!r}) appears "
                                       f"before the sprint goal")
            verdict_at = text.index("all limbs met by execution")
            self.assertGreater(verdict_at, at, f"{label}: the verdict stands in for the goal")

    def test_an_unjudged_goal_reads_not_measured_and_a_goalless_run_refuses(self) -> None:
        """AC2. MUTANT: default the verdict to `achieved` when none is recorded.

        The run's own account then judges itself, and every reader of the report sees a verdict
        nobody gave."""
        fixture_run(self.root, verdict=None)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "build", "--run", FIX_RUN, "--format", "json"])
        self.assertEqual(rc, 0, err.getvalue())
        rep = json.loads(out.getvalue())
        goal = {s["key"]: s for s in rep["sections"]}["goal"]["figures"]
        self.assertEqual(goal["sprint_goal"]["value"], FIX_GOAL)
        self.assertEqual(goal["goal_verdict"]["value"], "NOT MEASURED")
        self.assertEqual(goal["goal_verdict"]["reason"],
                         "no goal verdict recorded on this run")
        self.assertNotIn("achieved", goal["goal_verdict"]["value"])
        second = Path(tempfile.mkdtemp(dir=self.tmp.name))
        fixture_run(second, goal=None, verdict=None)
        out2, err2 = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            rc = sr.main(["--root", str(second), "build", "--run", FIX_RUN,
                          "--format", "json"])
        self.assertEqual(rc, 2, "a run with no sprint goal did not refuse")
        self.assertIn("sprint goal", (err2.getvalue() + out2.getvalue()).lower())
        self.assertFalse((second / "sdlc-studio" / "reports").exists(),
                         "the refused build wrote a report anyway")


class TheDoraKeysTests(ReportOfRecordBase):
    """US0837 AC3: each key states this project's mapping."""

    def test_each_key_states_its_mapping_and_an_unsourced_key_reads_not_measured(self) -> None:
        """AC3. MUTANT: print the four keys and their elite bands with no mapping sentence.

        The report then asserts a comparison against an industry band on definitions nobody
        stated, and the two unmeasured keys read as elite performance."""
        fixture_run(self.root, ci=False)
        _git_window(self.root, commits=3)
        rep = sr.build_report(self.root, FIX_RETRO)
        dora = {s["key"]: s for s in rep["sections"]}["dora"]
        keys = {r["dora_key"]["value"]: r for r in dora["rows"]}
        self.assertEqual(list(keys), ["Deployment frequency", "Lead time for changes",
                                      "Change failure rate", "Time to restore"])
        for name, row in keys.items():
            for field in ("dora_value", "dora_mapping", "dora_source", "dora_band"):
                self.assertIn(field, row, f"{name} carries no {field}")
                self.assertTrue(str(row[field]["value"]).strip(), f"{name}'s {field} is empty")
            self.assertGreater(len(str(row["dora_mapping"]["value"]).split()), 4,
                               f"{name}'s mapping is not a sentence stating what is counted")
        freq = keys["Deployment frequency"]
        self.assertEqual(freq["dora_value"]["value"], 3)
        self.assertIn("git", freq["dora_source"]["value"],
                      "deployment frequency is not sourced to the git history")
        self.assertIn("push to main", freq["dora_mapping"]["value"])
        for name in ("Change failure rate", "Time to restore"):
            row = keys[name]
            self.assertEqual(row["dora_value"]["value"], "NOT MEASURED",
                             f"{name} printed a figure with no CI run data behind it")
            self.assertEqual(row["dora_value"]["reason"], "no forge run data")
            self.assertNotEqual(str(row["dora_value"]["value"]), "0%")


class DoraTests(ReportOfRecordBase):
    """US0846 AC1: the change failure rate, from this run's own push-triggered CI results."""

    def test_change_failure_rate_counts_push_triggered_runs_only(self) -> None:
        """AC1. MUTANT: count every CI run in the window rather than push-triggered ones alone.

        A dispatch or a schedule then counts as a deployment, and this run's rate reads 20%
        instead of 33%."""
        fixture_run(self.root)
        # Through the SHIPPED COMMAND, not `build_report` alone. `lane-check` is right that a
        # library call leaves the wiring unexercised, and this run's own headline defect was a
        # function that reached no caller - so the figure is read back out of the JSON the CLI
        # produced, which is the artefact an operator actually gets.
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "build", "--id", FIX_RETRO,
                          "--format", "json"])
        self.assertEqual(rc, 0, err.getvalue())
        rep = json.loads(out.getvalue())
        dora = {s["key"]: s for s in rep["sections"]}["dora"]
        keys = {r["dora_key"]["value"]: r for r in dora["rows"]}
        cfr = keys["Change failure rate"]
        self.assertEqual(cfr["dora_value"]["value"], "33%",
                         "the rate is not one failure in three push-triggered runs")
        self.assertEqual(keys["Deployment frequency"]["dora_value"]["value"], 3,
                         "a dispatch or a schedule was counted as a deployment")
        source = cfr["dora_source"]["value"]
        self.assertIn("bbbb222", source, "the failed sha is not named")
        self.assertIn("3", source, "the deploy count is not named")
        mapping = cfr["dora_mapping"]["value"]
        self.assertIn("push to main", mapping)
        self.assertIn("trunk", mapping.lower(),
                      "the mapping does not state that a push to main IS the deployment in a "
                      "trunk-based repository with no separate deploy step")


class CostRowTests(ReportOfRecordBase):
    """US0844 AC4: the legacy single baseline is still read, and named."""

    def test_a_legacy_single_baseline_is_read_and_named(self) -> None:
        """AC4. MUTANT: require the stamp list.

        Every run opened before this story lands then reports NOT MEASURED, including the run
        that delivers it, which is the fixture-green-is-not-target-green scar this project
        already carries."""
        fixture_run(self.root, stamps=False, legacy_baseline=True)
        transcripts = Path(tempfile.mkdtemp(dir=self.tmp.name))
        src = transcripts / "s1.jsonl"
        src.write_text(json.dumps({"message": {"model": FIX_MODEL, "usage": {
            "input_tokens": FIX_REPORT_READING, "output_tokens": 0,
            "cache_creation_input_tokens": 0}}}) + "\n", encoding="utf-8")
        state = json.loads((self.root / "sdlc-studio" / ".local"
                            / "run-state.json").read_text(encoding="utf-8"))
        state["session_token_baseline"]["source"] = str(src)
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        with mock.patch.dict(os.environ, {run_state.TRANSCRIPTS_ENV: str(transcripts)}):
            rep = sr.build_report(self.root, FIX_RETRO)
        cost = {s["key"]: s for s in rep["sections"]}["cost"]
        self.assertIsNone(cost.get("not_measured"),
                          "a run carrying only the legacy baseline was refused a cost row")
        self.assertEqual(cost["figures"]["tokens_total"]["value"], FIX_RUN_TOKENS)
        shape = cost["figures"]["token_shape"]["value"]
        self.assertIn("legacy", shape.lower(),
                      f"the cost row does not name the shape it read: {shape!r}")
        self.assertIn("session_token_baseline", shape)


class TheSealDoesNotMoveTheWindowTests(ReportOfRecordBase):
    """BG0718: the act of SEALING must not invalidate the page it seals.

    The window's end is carried on the page and replayed, rather than re-derived from a run
    record the seal has since written to. Re-deriving it is what made signing invalidate the
    page; bounding every re-derivation at the generation time instead only moved the failure
    onto pages built after a run ended, which an independent plan review demonstrated.
    """

    def _tree(self, *, open_run: bool, commit_at: str | None = None) -> pathlib.Path:
        """A REAL git repository: in a bare temp directory `_git_commits` returns nothing,
        every DORA figure falls back to the static CI fixture, and the window cannot be
        observed to move at all - which is how two of these mutants survived their first runs.

        `fixture_run` writes an `ended_at`, so an OPEN run has to be made one deliberately.
        Both criteria here claimed an open run in their Given while testing a closed one, so
        the fallback they were about never executed and deleting it was a no-op.
        """
        root = pathlib.Path(tempfile.mkdtemp(dir=self.tmp.name))
        fixture_run(root)
        st = root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        if open_run:
            state["ended_at"], state["outcome"] = None, "running"
            st.write_text(json.dumps(state), encoding="utf-8")
        for cmd in (["init", "-q", "."], ["config", "user.email", "t@example.com"],
                    ["config", "user.name", "t"], ["add", "-A"],
                    ["-c", "commit.gpgsign=false", "commit", "-qm", "the delivered batch"]):
            gitutil.git(cmd, root, check=False)
        if commit_at:
            (root / "README.md").write_text(f"work at {commit_at}\n", encoding="utf-8")
            gitutil.git(["add", "-A"], root, check=False)
            gitutil.git(["-c", "commit.gpgsign=false", "commit", "-qm", "later work",
                         "--date", commit_at], root, check=False,
                        env_extra={"GIT_COMMITTER_DATE": commit_at})
        return root

    def test_writing_ended_at_does_not_change_what_the_page_re_derives_to(self) -> None:
        """AC1. MUTANT: re-derive the window's end from the run record instead of replaying
        the one the page carries - the seal's `ended_at` then widens the window, and a run can
        never hold a valid signature over its own report.
        """
        root = self._tree(open_run=True, commit_at="2026-12-01T00:00:00+00:00")
        rep = sr.build_report(root, FIX_RETRO)
        rid = sr.file_report(root, rep)
        signed = json.loads(
            (root / "sdlc-studio" / "reports" / f"{rid}.json").read_text(encoding="utf-8")
        )["fingerprint"]

        st = root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        state["ended_at"] = "2027-01-01T00:00:00Z"        # the SEAL, in the respect that matters
        st.write_text(json.dumps(state), encoding="utf-8")

        v = sr.revalidate(root, rid)
        self.assertTrue(v["valid"],
                        f"sealing the run invalidated the page it sealed: {v['moved']}")
        self.assertEqual(signed, sr.fingerprint(
            sr.build_report(root, FIX_RETRO, as_of=rep["generated_at"],
                            window_end=rep.get("window_end"))))

    def test_an_open_run_is_still_bounded_at_its_generation_time(self) -> None:
        """AC2. MUTANT: leave an open run's window unbounded - every commit made after the page
        then enters its figures, and because this project ships the paperwork in the same commit
        as the code, committing the report invalidates the report.

        The run here is genuinely OPEN: `ended_at` is cleared, so the fallback this criterion is
        about actually executes. It did not before, and the mutant survived three times.
        """
        root = self._tree(open_run=True, commit_at="2026-12-01T00:00:00+00:00")
        state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                           .read_text(encoding="utf-8"))
        self.assertIsNone(state.get("ended_at"),
                          "the fixture's run is not open, so this criterion tests nothing")
        rep = sr.build_report(root, FIX_RETRO)
        self.assertEqual(rep["window_end"], rep["generated_at"],
                         "an open run's page did not record its generation time as the bound")
        again = sr.build_report(root, FIX_RETRO, as_of=rep["generated_at"],
                                window_end=rep["window_end"])
        self.assertEqual(sr.fingerprint(rep), sr.fingerprint(again),
                         "a commit made after the page entered its figures, so the window was "
                         "left open on the derivation that had no bound recorded")

    def test_a_page_built_after_the_run_ended_also_re_derives_valid(self) -> None:
        """AC3, which the plan review required: the repair must not move the defect onto the
        other case. A page derived AFTER a run ended bounds at `ended_at`, which is EARLIER
        than its own generation time, so a commit landing between the two belongs to neither
        the run nor the page.

        MUTANT: bound every re-derivation at the generation time - the first derivation then
        excludes that commit and the re-derivation includes it, and a page nobody has touched
        reads INVALID. That is the repair this criterion was added to refuse, and it is what
        the first fix for AC1 actually did.
        """
        root = self._tree(open_run=False, commit_at="2026-09-16T00:00:00+00:00")
        state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                           .read_text(encoding="utf-8"))
        self.assertTrue(state.get("ended_at"), "the fixture's run never ended")
        rep = sr.build_report(root, FIX_RETRO)
        rid = sr.file_report(root, rep)
        self.assertEqual(rep["window_end"], state["ended_at"],
                         "a page built after the run ended did not record the run's end as its "
                         "bound, so it cannot replay the window it was derived under")
        v = sr.revalidate(root, rid)
        self.assertTrue(v["valid"], "a page built on an ended run re-derives INVALID with "
                        f"nothing touched: {v['moved']}")

    def test_a_page_recording_no_bound_replays_the_one_it_was_derived_under(self) -> None:
        """AC4. A page filed before the bound was carried records none, and the two legacy
        cases need different bounds: derived while the run was OPEN, the bound is the page's
        own generation time; derived AFTER the run ended, it is `ended_at`, which is earlier.

        MUTANT: fall back to the generation time for both - the second case then re-derives
        over a wider window than it was written under, a commit landing between the run's end
        and the page enters only the re-derivation, and an untouched page reads INVALID. That
        is this bug's own defect surviving in exactly the pages the fallback exists to protect.

        The positive control is the other half and it is the one that guards a REAL signature:
        a legacy page derived while the run was open and sealed afterwards must keep re-deriving
        at its generation time, because the run now carries an `ended_at` LATER than the page.
        RPT0002 on this repository is that page.
        """
        # (i) derived AFTER the run ended, with a commit in between.
        root = self._tree(open_run=False, commit_at="2026-09-16T00:00:00+00:00")
        rep = sr.build_report(root, FIX_RETRO)
        rid = sr.file_report(root, rep)
        jp = root / "sdlc-studio" / "reports" / f"{rid}.json"
        data = json.loads(jp.read_text(encoding="utf-8"))
        data.pop("window_end")                       # as a page filed before this shipped
        jp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        v = sr.revalidate(root, rid)
        self.assertTrue(v["valid"], "a legacy page derived after its run ended re-derived over "
                                    f"a wider window than it was written under: {v['moved']}")

        # (ii) derived while OPEN, then sealed - the shape a signed page is actually in.
        root2 = self._tree(open_run=True, commit_at="2026-12-01T00:00:00+00:00")
        rep2 = sr.build_report(root2, FIX_RETRO)
        rid2 = sr.file_report(root2, rep2)
        jp2 = root2 / "sdlc-studio" / "reports" / f"{rid2}.json"
        d2 = json.loads(jp2.read_text(encoding="utf-8"))
        d2.pop("window_end")
        jp2.write_text(json.dumps(d2, indent=2), encoding="utf-8")
        st = root2 / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(st.read_text(encoding="utf-8"))
        state["ended_at"] = "2027-01-01T00:00:00Z"   # the seal, AFTER the page
        st.write_text(json.dumps(state), encoding="utf-8")
        v2 = sr.revalidate(root2, rid2)
        self.assertTrue(v2["valid"], "sealing a legacy page's run invalidated it - the bound "
                                     f"was taken from the seal rather than the page: {v2['moved']}")


    def test_the_bound_is_an_envelope_field_and_never_a_digest_figure(self) -> None:
        """AC5, required by the third plan review. The whole repair rests on one property that
        was stated only in a code comment: `window_end` must NOT enter the fingerprint.

        MUTANT: record it the way every other value on the page is recorded - as a header
        figure, `fig("window_end", ...)` beside `fig("ended_at", ...)`. That passes all four of
        this class's other selectors and all 208 tests in this module, and makes every page
        filed before the bound shipped read INVALIDATED with `moved=['window_end']`. It is this
        bug's own failure mode returning through its own repair, which is why it needs a row.
        """
        root = self._tree(open_run=True, commit_at="2026-12-01T00:00:00+00:00")
        rep = sr.build_report(root, FIX_RETRO)
        self.assertTrue(rep.get("window_end"), "the page records no bound at all")
        keys = [k for _sec, k, _f in _leaf_figures(rep)]
        self.assertNotIn("window_end", keys,
                         "the bound is a digest FIGURE, so recording it changes the very "
                         "fingerprint it exists to protect")
        # ...and directly: moving the bound must not move the fingerprint.
        before = sr.fingerprint(rep)
        moved = {**rep, "window_end": "1999-01-01T00:00:00Z"}
        self.assertEqual(before, sr.fingerprint(moved),
                         "changing the recorded bound changed the fingerprint")

    def test_the_bound_reaches_the_filed_page_not_only_the_derived_dict(self) -> None:
        """AC6, required by the third plan review. Every other criterion asserts `window_end`
        on the IN-MEMORY dict, so the design's central claim - the bound is recorded and
        replayed rather than inferred - was untested on the artefact that is actually read.

        MUTANT: strip `window_end` in `file_report` before writing. AC1, AC2 and AC3 all stay
        green, because `_legacy_window_end` happens to infer the same answer for their
        fixtures; across the whole module the only thing that notices is a `KeyError` in
        another test's FIXTURE SETUP, which a defensive `.pop(..., None)` would erase.
        """
        root = self._tree(open_run=True, commit_at="2026-12-01T00:00:00+00:00")
        rep = sr.build_report(root, FIX_RETRO)
        rid = sr.file_report(root, rep)
        stored = json.loads((root / "sdlc-studio" / "reports" / f"{rid}.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(rep["window_end"], stored.get("window_end"),
                         "the filed page does not carry the bound it was derived under, so a "
                         "reader re-deriving it must INFER the window rather than replay it")



class InvalidatedReportTests(ReportOfRecordBase):
    """US0845 AC1-AC2: invalidation is decided by re-derivation."""

    def _sealed(self) -> tuple[Path, str]:
        root = Path(tempfile.mkdtemp(dir=self.tmp.name))
        fixture_run(root)
        rep = sr.build_report(root, FIX_RETRO)
        rid = sr.file_report(root, rep)
        data = sr.read_report(root, rid)
        data["signature"] = {"principal": "the operator", "signed_at": "2026-09-16T09:00:00Z",
                             "fingerprint": data["fingerprint"]}
        # Through the seal's own writer, which re-renders the twin: a signature written into
        # the JSON alone leaves a twin that disagrees with it, and check reads that as an edit.
        sr.write_report(root, data)
        return root, rid

    @staticmethod
    def _snapshot(root: Path) -> dict:
        return {str(p.relative_to(root)): p.stat().st_mtime_ns
                for p in (root / "sdlc-studio").rglob("*") if p.is_file()}

    def three_trees(self) -> list[tuple[str, Path, str]]:
        """The three trees, in REAL git repositories.

        `mkdtemp` alone left `_git_commits` shelling out to git, getting a non-zero exit and
        returning `[]`, so every DORA figure came from the static `ci-runs.json` fixture and
        tree (ii)'s write was never committed. The one case AC1 calls discriminating was the
        one the fixture could not reach - and the defect it could not see was real: the DORA
        window is open-ended until SEAL, so on a git tree every later commit entered the
        figures and committing the report invalidated the report.
        """
        trees = []
        for name in ("untouched", "unrelated-write", "figure-moved"):
            root, rid = self._sealed()
            for cmd in (["init", "-q", "."], ["config", "user.email", "t@example.com"],
                        ["config", "user.name", "t"], ["add", "-A"],
                        ["-c", "commit.gpgsign=false", "commit", "-qm", "the delivered batch"]):
                gitutil.git(cmd, root, check=False)
            if name == "unrelated-write":
                # ...and COMMITTED, well after the report was generated. An uncommitted write
                # cannot exercise the window at all.
                (root / "README.md").write_text("a typo fixed\n", encoding="utf-8")
                gitutil.git(["add", "-A"], root, check=False)
                gitutil.git(["-c", "commit.gpgsign=false", "commit", "-qm", "fix a typo",
                             "--date", "2099-01-01T00:00:00+00:00"], root, check=False,
                            env_extra={"GIT_COMMITTER_DATE": "2099-01-01T00:00:00+00:00"})
            if name == "figure-moved":
                reopen_a_delivered_unit(root)
            trees.append((name, root, rid))
        return trees

    def test_an_open_runs_report_survives_the_commit_that_files_it(self) -> None:
        """AC1 on the shape a report is actually PRODUCED in: the run is still OPEN.

        MUTANT: leave the DORA window open-ended when `ended_at` is None - `end = _at(
        state.get("ended_at"))` with no fallback. Every commit made after the page then enters
        the run's figures, so an unrelated commit invalidates the report and, because this
        repository ships the paperwork in the same commit as the code, COMMITTING THE REPORT
        invalidates the report. No operator could obtain a page that stayed valid long enough
        to sign it.

        The sealed trees above cannot see this: `ended_at` is set there, so the window is
        already closed and the fallback never runs.
        """
        root = Path(tempfile.mkdtemp(dir=self.tmp.name))
        fixture_run(root)
        # THE PREPARE SHAPE: the run is open, so it carries no end time.
        sp = root / "sdlc-studio" / ".local" / "run-state.json"
        st = json.loads(sp.read_text(encoding="utf-8"))
        st["ended_at"], st["outcome"] = None, "running"
        sp.write_text(json.dumps(st), encoding="utf-8")
        for cmd in (["init", "-q", "."], ["config", "user.email", "t@example.com"],
                    ["config", "user.name", "t"], ["add", "-A"],
                    ["-c", "commit.gpgsign=false", "commit", "-qm", "the delivered batch"]):
            gitutil.git(cmd, root, check=False)
        rid = sr.file_report(root, sr.build_report(root, FIX_RETRO))
        self.assertTrue(sr.revalidate(root, rid)["valid"],
                        "the report did not re-derive even before anything moved")
        # ...and now the commit that files it, plus an unrelated one, both AFTER the page.
        (root / "README.md").write_text("a typo fixed\n", encoding="utf-8")
        gitutil.git(["add", "-A"], root, check=False)
        gitutil.git(["-c", "commit.gpgsign=false", "commit", "-qm",
                     "file the report of record and fix a typo",
                     "--date", "2099-01-01T00:00:00+00:00"], root, check=False,
                    env_extra={"GIT_COMMITTER_DATE": "2099-01-01T00:00:00+00:00"})
        after = sr.revalidate(root, rid)
        self.assertTrue(after["valid"],
                        f"a commit made after the page invalidated it: {after['moved']}")
        # The paired control, or this would pass on a digest covering nothing.
        reopen_a_delivered_unit(root)
        self.assertFalse(sr.revalidate(root, rid)["valid"],
                         "a moved figure still re-derives - the digest covers nothing")

    def test_invalidation_is_decided_by_re_deriving_the_facts(self) -> None:
        """AC1. MUTANT: invalidate whenever the tree has a tracked write newer than `signed_at`.

        Tree (ii) then reads INVALIDATED, every sealed report goes stale on the next unrelated
        commit, and the marker means only that time has passed."""
        for name, root, rid in self.three_trees():
            before = self._snapshot(root)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sr.main(["--root", str(root), "check", "--report", rid])
            printed = out.getvalue() + err.getvalue()
            if name == "figure-moved":
                self.assertNotEqual(rc, 0, f"{name}: a moved figure did not refuse")
                self.assertIn("INVALIDATED", printed)
                self.assertIn("points_delivered", printed,
                              f"{name}: the figure that moved is not named")
                self.assertIn("103", printed, f"{name}: the signed value is not named")
                self.assertIn("98", printed, f"{name}: the current value is not named")
            else:
                self.assertEqual(rc, 0, f"{name}: a valid report was refused - {printed}")
                self.assertIn("VALID", printed)
                self.assertNotIn("INVALIDATED", printed)
            self.assertEqual(self._snapshot(root), before, f"{name}: the check wrote to the tree")

    def test_both_renderings_lead_with_the_invalidation_banner(self) -> None:
        """AC2. MUTANT: render the banner at the foot, below Provenance.

        The reader takes the figures as signed and meets the warning after the decision, and
        every assertion that the banner exists still passes."""
        trees = {name: (root, rid) for name, root, rid in self.three_trees()}
        root, rid = trees["figure-moved"]
        rep = sr.read_report(root, rid)
        state = sr.revalidate(root, rid)
        self.assertFalse(state["valid"])
        self.assertIn("points_delivered", state["moved"])
        md = sr.render_markdown(rep, revalidation=state)
        html = sr.render_html(rep, revalidation=state)
        goal = rep["sections"][[s["key"] for s in rep["sections"]].index("goal")]
        goal_text = goal["figures"]["sprint_goal"]["value"]
        for label, text in (("the Markdown twin", md), ("the HTML rendering", html)):
            self.assertIn("INVALIDATED", text, f"{label} carries no banner")
            self.assertLess(text.index("INVALIDATED"), text.index(goal_text),
                            f"{label}: the banner does not lead the report")
            self.assertIn(rep["fingerprint"], text, f"{label}: the signed fingerprint is absent")
            self.assertIn(state["fingerprint"], text,
                          f"{label}: the current fingerprint is absent")
            self.assertIn("points_delivered", text, f"{label}: what moved is not named")
            self.assertIn("the operator", text,
                          f"{label}: the sign-off block was emptied rather than left standing")
            self.assertIn("2026-09-16", text, f"{label}: the signed date was emptied")
        root2, rid2 = trees["untouched"]
        rep2 = sr.read_report(root2, rid2)
        state2 = sr.revalidate(root2, rid2)
        self.assertTrue(state2["valid"])
        for text in (sr.render_markdown(rep2, revalidation=state2),
                     sr.render_html(rep2, revalidation=state2)):
            self.assertNotIn("INVALIDATED", text,
                             "a valid report carries the banner anyway")


def _git_window(root: Path, commits: int) -> None:
    """A git history holding `commits` commits inside the run's window, and no release tag."""
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e"}
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True, env=env)
    for n in range(commits):
        (root / f"f{n}.txt").write_text(f"{n}\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(root), check=True, env=env)
        subprocess.run(["git", "commit", "-q", "-m", f"c{n}",
                        "--date", f"2026-09-15T0{6 + n}:00:00Z"], cwd=str(root), check=True,
                       env={**env, "GIT_COMMITTER_DATE": f"2026-09-15T0{6 + n}:00:00Z"})


class FindingAttributionTests(ReportOfRecordBase):
    """BG0715. `_open_findings` dated a finding by the LAST WHITESPACE TOKEN of its
    `Raised-in-batch` stamp. The stamp written outside a batch is `none open - raised outside a
    delivery batch`, whose last token is `batch` - and a word sorts after every ISO timestamp, so
    with an OPEN run (`ended` None, the state a close runs in) it passed both comparisons and the
    finding was attributed to whichever run happened to be open. One run filed two findings and
    its close demanded stop-ship rulings for 81.

    The repair must not reverse the error's direction. Excluding prose-stamped findings outright
    made the close certify `none carried` over findings the run had itself raised - a silent
    under-count in place of a visible over-count, which `sprint.py`'s reader of the same field
    already names as the worse of the two. `Created` is the fallback, and a finding no source can
    date is COUNTED rather than dropped."""

    WINDOW = ("2026-07-22T08:00:00Z", "2026-07-22T10:00:00Z")
    PROSE = "none open - raised outside a delivery batch"

    def _bug(self, bid: str, stamp: str, created: str = "", status: str = "Open") -> None:
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        created_line = f"> **Created:** {created}\n" if created else ""
        (d / f"{bid}-x.md").write_text(
            f"# {bid}: x\n\n> **Status:** {status}\n> **Raised-in-batch:** {stamp}\n"
            f"{created_line}", encoding="utf-8")

    def _findings(self, ended=None):
        # `ended_at` None by default: that is the state a CLOSE runs in, and the only state in
        # which the original defect fires. A fixture carrying an end date is green against it,
        # because `batch` sorts after every timestamp and the upper bound excludes it.
        return sr._open_findings(self.root, {"started_at": self.WINDOW[0], "ended_at": ended})

    def test_a_prose_stamp_falls_back_to_created_and_is_attributed(self) -> None:
        """AC1. The word `batch` is never a date - but the finding still has one, in `Created`,
        and reading it is what keeps the finding attributable instead of invisible."""
        self._bug("BG9001", self.PROSE, created="2026-07-22")
        filed, still_open = self._findings()
        self.assertIn("BG9001", filed)
        self.assertIn("BG9001", still_open)

    def test_a_prose_stamp_created_before_the_run_is_not_this_run_s(self) -> None:
        """AC1b, and the half the shipped code got wrong: it attributed EVERY prose-stamped
        finding in the repository to whichever run was open, 307 of them here."""
        self._bug("BG9002", self.PROSE, created="2026-01-01")
        filed, _ = self._findings()
        self.assertNotIn("BG9002", filed,
                         "a finding created before the run opened is somebody else's backlog")

    def test_an_undatable_finding_is_not_attributed_but_the_row_cannot_say_none_carried(self) -> None:
        """AC2. Two ways to be wrong and both were taken in turn. Attributing these handed the
        close 47 findings to rule on that no run had touched; excluding them silently let the
        close certify `none carried` over findings it had raised. It is excluded from
        attribution AND visible to the row, so the row reports UNKNOWN rather than none."""
        self._bug("BG9003", self.PROSE)
        filed, _still_open = self._findings()
        self.assertNotIn("BG9003", filed, "an undatable finding is nobody's to rule on")
        undatable = sr._undatable_findings(self.root)
        self.assertIn("BG9003", undatable)
        state, summary, _detail = sr._ck_known_issues(
            {"carried_issues": [], "open_filed_in_run": [], "undatable_findings": undatable})
        self.assertEqual("unanswered", state,
                         "the row must not certify none carried over a set it could not judge")
        self.assertIn("undatable", summary)

    def test_the_row_still_says_none_carried_when_there_is_genuinely_nothing(self) -> None:
        """AC2b, the discriminating half - a row that never answers is not a check."""
        state, summary, _ = sr._ck_known_issues(
            {"carried_issues": [], "open_filed_in_run": [], "undatable_findings": []})
        self.assertEqual("answered", state)
        self.assertEqual("none carried", summary)

    def test_the_undatable_set_is_reported_and_reaches_the_checklist(self) -> None:
        """AC2b. A derivation nothing calls is a claim nobody can read - the first version of
        this shipped an uncalled function whose docstring said the close named these."""
        self._bug("BG9004", self.PROSE)
        self._bug("BG9005", self.PROSE, created="2026-07-22")
        undatable = sr._undatable_findings(self.root)
        self.assertIn("BG9004", undatable)
        self.assertNotIn("BG9005", undatable,
                         "a prose stamp is not undatable while `Created` still answers")
        # Scoped to what a close can ACT on. Round 2 deleted these two lines and the mutant that
        # drops `open_only` went from killed to surviving.
        self._bug("BG9020", self.PROSE, status="Fixed")
        self.assertNotIn("BG9020", sr._undatable_findings(self.root))
        self.assertIn("BG9020", sr._undatable_findings(self.root, open_only=False))

    def test_an_artefact_carrying_no_stamp_at_all_is_skipped(self) -> None:
        """AC2c. No stamp predates the mechanism that writes one, so nothing ever claimed the
        finding for a run. Counting these attributed the whole historical backlog to whichever
        run was open - 558 artefacts here against the 2 this run actually raised."""
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        # WITH a `Created` inside the window. Without it the guard is untestable: no stamp and
        # no Created already falls through the undatable branch, so the mutant that deletes this
        # skip survives. Of the 558 it excludes here, 402 carry no Created either.
        (d / "BG9009-x.md").write_text(
            "# BG9009: x\n\n> **Status:** Open\n> **Created:** 2026-07-22\n", encoding="utf-8")
        filed, _ = self._findings()
        self.assertNotIn("BG9009", filed)
        self.assertNotIn("BG9009", sr._undatable_findings(self.root),
                         "an artefact that never carried a stamp is not an undatable stamp")

    def test_created_is_a_FALLBACK_and_never_the_primary_source(self) -> None:
        """AC4b. Deleting the `Created` fallback must redden something, or the whole repair to
        the reviewer's blocking finding is unpinned - the mutant dropping it survived once."""
        self._bug("BG9010", self.PROSE, created="2026-07-22")
        filed, _ = self._findings()
        self.assertIn("BG9010", filed,
                      "without the Created fallback a prose-stamped finding is invisible again")

    def test_a_dated_stamp_inside_the_window_is_still_attributed(self) -> None:
        """AC3, the discriminating half - a parser attributing NOTHING would satisfy the rest."""
        self._bug("BG9006", "2026-07-22T09:00:00Z")
        filed, still_open = self._findings()
        self.assertIn("BG9006", filed)
        self.assertIn("BG9006", still_open)

    def test_a_dated_stamp_outside_the_window_is_not_attributed(self) -> None:
        """AC3b. The window must still bound: another run's finding is not this one's."""
        # SAME DAY as `ended_at`, one hour after it. The round-1 fixture was exactly this; I moved
        # it to the next day so it would stay green over a truncation regression, which is
        # weakening the test to fit the defect. A cross-day fixture cannot see a same-day bound.
        self._bug("BG9007", "2026-07-22T11:00:00Z")
        filed, _ = self._findings(ended=self.WINDOW[1])
        self.assertNotIn("BG9007", filed)

    def test_a_precise_timestamp_is_compared_precisely_not_to_the_day(self) -> None:
        """AC3c. Comparing both sides at day granularity let a 4h22m run claim 45 findings raised
        elsewhere that day, and made two different runs each claim the same eleven. A date-only
        `Created` can only be judged to the day; a stamp carrying a real moment must not be."""
        self._bug("BG9030", "2026-07-22T07:00:00Z")   # one hour BEFORE started_at, same day
        self._bug("BG9031", "2026-07-22T09:00:00Z")   # inside
        filed, _ = self._findings(ended=self.WINDOW[1])
        self.assertNotIn("BG9030", filed,
                         "a stamp an hour before the run opened is not this run's, same day or not")
        self.assertIn("BG9031", filed)

    def test_a_date_only_created_is_still_judged_to_the_day(self) -> None:
        """AC3d, the other half - the day-granularity path must survive, or a `Created` of
        2026-07-22 against a window opening at 08:00 that day would be excluded as 'before'."""
        self._bug("BG9032", self.PROSE, created="2026-07-22")
        filed, _ = self._findings(ended=self.WINDOW[1])
        self.assertIn("BG9032", filed)

    def test_an_unreadable_created_value_is_not_trusted_as_a_date(self) -> None:
        """AC4b. `Created: TBD` sorts after every ISO date, so an unguarded read attributed it to
        any open run AND left it out of the undatable set - this bug's own arithmetic one layer
        over. `_stamp_timestamp` already guards by shape; its sibling now does too."""
        self._bug("BG9033", self.PROSE, created="TBD")
        filed, _ = self._findings()
        self.assertNotIn("BG9033", filed)
        self.assertIn("BG9033", sr._undatable_findings(self.root),
                      "a value nothing can read is undatable, and must be disclosed as such")

    def test_an_artefact_with_neither_a_stamp_nor_a_created_is_not_undatable(self) -> None:
        """AC2d. The two readers must apply the SAME rule. An artefact that never carried a stamp
        is not an undatable stamp, whether or not it also lacks a `Created` - and 402 of this
        corpus's 558 unstamped artefacts carry neither."""
        d = self.root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG9034-x.md").write_text("# BG9034: x\n\n> **Status:** Open\n", encoding="utf-8")
        self.assertNotIn("BG9034", sr._undatable_findings(self.root))
        filed, _ = self._findings()
        self.assertNotIn("BG9034", filed)

    def test_the_stamp_timestamp_beats_a_contradicting_created(self) -> None:
        """AC4. The stamp is the precise record of when a batch claimed the finding; `Created`
        is only the fallback. A reader that preferred `Created` would mis-date every batch-stamped
        finding whose file was created on another day."""
        # The stamp carries text BEFORE the timestamp, so returning the whole stamp instead of
        # the parsed match is a different value. With a bare stamp the two are byte-identical and
        # the mutant survives - which it did, through two rounds.
        self._bug("BG9008", "batch RUN-TEST01 opened 2026-07-22T09:00:00Z", created="2026-01-01")
        filed, _ = self._findings()
        self.assertIn("BG9008", filed, "the stamp's own timestamp must win over `Created`")
        self._bug("BG9021", "batch RUN-TEST01 opened 2026-01-01T09:00:00Z", created="2026-07-22")
        filed2, _ = self._findings()
        self.assertNotIn("BG9021", filed2,
                         "a stamp dated outside the window must not be rescued by `Created`")

    def test_as_utc_marks_a_naive_stamp_as_utc(self) -> None:
        """`_as_utc`'s naive branch, direct: every fixture stamp elsewhere in this suite already
        carries `Z`, so a mutant returning the stamp unchanged had nothing here to fail it.

        MUTANT: `return stamp` unconditionally - a naive stamp comes back with no offset at all.
        """
        self.assertEqual("2026-07-22T09:00:00Z", sr._as_utc("2026-07-22T09:00:00"))
        # Already-offset stamps are untouched, the branch this one sits beside.
        self.assertEqual("2026-07-22T09:00:00Z", sr._as_utc("2026-07-22T09:00:00Z"))


class StopShipDischargeTests(ReportOfRecordBase):
    """BG0730. A carried stop-ship ruling was collected whatever its finding's status, so a
    ruling on a finding that had since been Fixed blocked every subsequent close, permanently,
    with editing a retro by hand the only way out."""

    def _ctx(self, rows):
        return {"carried_issues": rows}

    @staticmethod
    def _row(uid, *, terminal=False, unreadable=False, ruling="stop-ship"):
        return {"id": uid, "ruling": ruling, "by": "Someone", "date": "2026-09-01",
                "ok": True, "why": "", "status": None,
                "terminal": terminal, "unreadable": unreadable}

    def test_a_ruling_on_a_fixed_finding_is_discharged_and_an_open_one_still_blocks(self) -> None:
        """AC1, both directions in one fixture - the open row is the control that keeps the
        discharge from being a switch that lets everything through."""
        out = sr._known_issue_rulings(self._ctx([
            self._row("BG9201", terminal=True), self._row("BG9202")]))
        self.assertEqual(["BG9202"], out["stop_ship"])
        self.assertEqual(["BG9201"], out["stop_ship_discharged"])

    def test_an_unreadable_artefact_is_reported_and_still_blocks(self) -> None:
        """AC3. An id resolving to no file is a typo or a deletion; in neither case has anybody
        discharged the ruling, so silently releasing it would turn a typo into a released hold."""
        out = sr._known_issue_rulings(self._ctx([
            self._row("BG9203", unreadable=True)]))
        self.assertEqual(["BG9203"], out["stop_ship"])
        self.assertEqual(["BG9203"], out["stop_ship_unreadable"])
        self.assertEqual([], out["stop_ship_discharged"])

    def test_the_wiring_exists_end_to_end_on_a_real_workspace(self) -> None:
        """The join between the two halves, which nothing pinned. Both halves had their own test -
        `_known_issue_rulings` on hand-built rows, `carried_issues` on a real tree - and deleting
        the single `root=root` that connects them left every test green. That is this repo's own
        recorded scar: a correct library behind a dead entry point passed for a whole sprint."""
        retro_dir = self.root / "sdlc-studio" / "retros"
        retro_dir.mkdir(parents=True, exist_ok=True)
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / "BG9301-x.md").write_text("# BG9301: x\n\n> **Status:** Fixed\n", encoding="utf-8")
        (bugs / "BG9302-x.md").write_text("# BG9302: x\n\n> **Status:** Open\n", encoding="utf-8")
        (retro_dir / "RETRO9300-r.md").write_text(
            "# RETRO9300: a sprint\n\n## Known issues carried\n\n"
            "| Issue | Ruling | By | Date |\n| --- | --- | --- | --- |\n"
            "| BG9301 | stop-ship | Someone | 2026-09-01 |\n"
            "| BG9302 | stop-ship | Someone | 2026-09-01 |\n", encoding="utf-8")
        rows = sr._carried_issues(self.root, "RETRO9300")
        by_id = {r["id"]: r for r in rows}
        self.assertTrue(by_id["BG9301"]["terminal"],
                        "`_carried_issues` must pass its root through, or the join has nothing "
                        "to join on and the whole repair is inert")
        self.assertFalse(by_id["BG9302"]["terminal"])
        out = sr._known_issue_rulings({"carried_issues": rows})
        self.assertEqual(["BG9302"], out["stop_ship"])
        self.assertEqual(["BG9301"], out["stop_ship_discharged"])
        state, summary, detail = sr._ck_known_issues(
            {"carried_issues": rows, "open_filed_in_run": [], "undatable_findings": []})
        self.assertEqual("answered", state)
        self.assertIn("1 STOP-SHIP", summary)
        self.assertIn("1 discharged", summary,
                      "the row the operator reads must apply the same join as the gate")
        self.assertIn("BG9301", detail)

    def test_an_id_of_any_admitted_type_resolves(self) -> None:
        """The row grammar admits CR, BG, US, RFC, EP and LL. Guessing the type from the prefix
        marked four of the six UNREADABLE while their files sat there readable - asserting `no
        file resolves` about files that resolve, which is the opposite of what the flag means."""
        for uid, folder, status in (("US9401", "stories", "Done"),
                                    ("RFC9402", "rfcs", "Accepted"),
                                    ("EP9403", "epics", "Done")):
            d = self.root / "sdlc-studio" / folder
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{uid}-x.md").write_text(f"# {uid}: x\n\n> **Status:** {status}\n",
                                           encoding="utf-8")
        retro_dir = self.root / "sdlc-studio" / "retros"
        retro_dir.mkdir(parents=True, exist_ok=True)
        (retro_dir / "RETRO9400-r.md").write_text(
            "# RETRO9400: a sprint\n\n## Known issues carried\n\n"
            "| Issue | Ruling | By | Date |\n| --- | --- | --- | --- |\n"
            + "".join(f"| {u} | stop-ship | Someone | 2026-09-01 |\n"
                      for u in ("US9401", "RFC9402", "EP9403")), encoding="utf-8")
        rows = {r["id"]: r for r in sr._carried_issues(self.root, "RETRO9400")}
        for uid in ("US9401", "RFC9402", "EP9403"):
            with self.subTest(id=uid):
                self.assertFalse(rows[uid]["unreadable"],
                                 f"{uid} resolves to a readable file and must not be reported "
                                 f"as one that does not")
                self.assertTrue(rows[uid]["terminal"])

    def test_a_non_stop_ship_ruling_is_not_collected_either_way(self) -> None:
        """The discriminating half: the discharge must not become a general filter."""
        out = sr._known_issue_rulings(self._ctx([
            self._row("BG9204", ruling="accepted-risk"),
            self._row("BG9205", ruling="accepted-risk", terminal=True)]))
        self.assertEqual([], out["stop_ship"])
        self.assertEqual([], out["stop_ship_discharged"])


class WaiverDisclosureTests(ReportOfRecordBase):
    """BG0719. RPT0002 was SIGNED with D0214 (which stood `review.line_coverage` down from block
    to report for that seal) and D0215 (which waived a known-issues checklist row) in force, and
    the report named neither. The operator signed without being told which gate was not holding."""

    WINDOW_END = "2026-07-22T10:00:00Z"
    WINDOW_START = "2026-07-01T00:00:00Z"

    def _log(self, *rows: tuple[str, str, str, str, str]) -> None:
        d = self.root / "sdlc-studio"
        d.mkdir(parents=True, exist_ok=True)
        head = ("# Decisions\n\n| ID | Decision | Rationale | Status | Supersedes | Date |\n"
                "| --- | --- | --- | --- | --- | --- |\n")
        body = "".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |  | {r[4]} |\n" for r in rows)
        (d / "decisions.md").write_text(head + body, encoding="utf-8")

    def test_a_waiver_in_force_is_disclosed_with_its_subject_and_reason(self) -> None:
        """AC1. The signer is told which gate was not holding when they signed."""
        self._log(("D0214", "waiver: review.line_coverage",
                   "coverage cannot be measured on this interpreter", "accepted", "2026-07-22"))
        rows, _undated = sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)
        self.assertEqual(1, len(rows))
        self.assertEqual("D0214", rows[0]["waiver_id"]["value"])
        self.assertIn("review.line_coverage", rows[0]["waiver_subject"]["value"])
        self.assertIn("cannot be measured", rows[0]["waiver_reason"]["value"])
        self.assertTrue(all("source" in c for c in rows[0].values()),
                        "every cell must be a fig() dict - raw strings crash build")

    def test_an_ordinary_decision_is_not_a_waiver(self) -> None:
        """AC2, the discriminating half - listing every decision discloses nothing and buries
        what matters. The token `waiver:` is the marker, not a mention of one."""
        self._log(("D0216", "the batch is ordered by what compounds over the run",
                   "severity is not the ordering that matters", "accepted", "2026-07-22"),
                  ("D0217", "a decision mentioning a waiver of review.line_coverage in prose",
                   "not a waiver row", "accepted", "2026-07-22"))
        self.assertEqual([], sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)[0])

    def test_a_waiver_after_the_window_end_cannot_move_a_signed_page(self) -> None:
        """AC3. Bounded by the report's recorded `window_end`, the same bound the DORA figures
        use - BG0718 is the scar: a figure that moves after the signature invalidates the page."""
        self._log(("D0300", "waiver: something", "later", "accepted", "2026-09-01"))
        self.assertEqual([], sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)[0])
        self.assertEqual(1, len(sr._waivers_in_force(self.root, "2026-09-30T00:00:00Z",
                                                     self.WINDOW_START)[0]))

    def test_a_waiver_before_the_run_opened_is_not_in_force_for_it(self) -> None:
        """AC3b. Only the upper bound was applied at first, so this repository returned 67 rows -
        almost all one-shot per-story waivers discharged months ago - and the note claimed all 67
        were "not holding when this page was derived". A section that buries what it exists to
        surface has disclosed nothing."""
        self._log(("D0100", "waiver: old.lane", "long discharged", "accepted", "2026-01-15"),
                  ("D0214", "waiver: review.line_coverage", "in force", "accepted", "2026-07-22"))
        rows, _undated = sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)
        self.assertEqual(["D0214"], [r["waiver_id"]["value"] for r in rows])

    def test_an_unbounded_read_reports_NOT_MEASURED_not_a_clean_sheet(self) -> None:
        """AC3c. Fail-closed is only half of it. The first repair returned nothing AND emitted
        `the log was read and carries no accepted waiver` - so a read that REFUSED to run was
        word-for-word indistinguishable from one that ran and found nothing, on a signed page.
        That is this bug's own failure mode reproduced by its fix."""
        self._log(("D0214", "waiver: review.line_coverage", "in force", "accepted", "2026-07-22"))
        for end, start in ((None, self.WINDOW_START), (self.WINDOW_END, None), (None, None)):
            with self.subTest(end=end, start=start):
                self.assertEqual([], sr._waivers_in_force(self.root, end, start)[0])
                section = sr._waivers_section(self.root, end, start)
                self.assertIsNotNone(section["not_measured"],
                                     "an unbounded read must report NOT MEASURED")
                self.assertNotIn("waivers_note", section["figures"],
                                 "it must not also claim the log was read")

    def test_a_waiver_with_no_readable_date_is_disclosed_not_dropped(self) -> None:
        """AC3d. A waiver whose Date cell is blank cannot be placed in any window. Dropping it
        silently is the defect the sibling unit BG0715 built its undatable set to avoid."""
        self._log(("D0400", "waiver: some.lane", "why", "accepted", ""))
        rows, undated = sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)
        self.assertEqual([], rows)
        self.assertEqual(["D0400"], undated)
        note = sr._waivers_section(self.root, self.WINDOW_END,
                                   self.WINDOW_START)["figures"]["waivers_note"]["value"]
        self.assertIn("D0400", note)
        self.assertIn("UNKNOWN", note)

    def test_a_superseded_waiver_does_not_hold(self) -> None:
        """A waiver that was replaced is not in force, and reporting it would tell the signer a
        gate stood down that did not."""
        self._log(("D0214", "waiver: review.line_coverage", "why", "superseded", "2026-07-22"))
        self.assertEqual([], sr._waivers_in_force(self.root, self.WINDOW_END, self.WINDOW_START)[0])

    def test_the_section_reaches_the_report_of_record(self) -> None:
        """AC5, and the lesson two sibling units paid for in this same run: a derivation nothing
        calls is a claim nobody can read. The section must be IN the report, not merely
        derivable from it."""
        # DERIVED, not grepped. The first version of this test searched the source for the call
        # and was satisfied by a commented-out one; the mutant that dead-ended the call SURVIVED.
        self._log(("D0214", "waiver: review.line_coverage", "cannot be measured here",
                   "accepted", "2026-07-22"))
        state = {"schema": 1, "run_id": "RUN-TEST01", "batch": [], "goal": "done",
                 "sprint_goal": "prove the section reaches the page",
                 "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"},
                 "started_at": "2026-07-01T00:00:00Z", "ended_at": self.WINDOW_END}
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        rd = self.root / "sdlc-studio" / "retros"
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "RETRO0001-r.md").write_text(
            "# RETRO0001: a sprint\n\n> **Batch:** none\n\n## Delivered\n- nothing\n",
            encoding="utf-8")
        keys = {sec["key"] for sec in sr.build_report(self.root, "RETRO0001")["sections"]}
        self.assertIn("waivers", keys, "no report carries the section")
        self.assertIn("waivers", sr._ROW_LISTS,
                      "the renderer must know how to list this section's rows")
        self.assertEqual("waivers", sr._ROW_LISTS["waivers"],
                         "the row key must be the one the templates repeat over")
        for tmpl in ("templates/core/sprint-report.md", "templates/reports/sprint-report.html"):
            path = pathlib.Path(sr.__file__).parents[1] / tmpl
            with self.subTest(template=tmpl):
                self.assertIn("repeat: waivers", path.read_text(encoding="utf-8"),
                              "a section no template repeats over renders nothing")

    def test_the_not_measured_path_RENDERS(self) -> None:
        """AC5b. Three rounds running, a correct derivation shipped with a path nobody rendered.
        Both templates carried a bare `{{waivers_note}}` while the not_measured branch supplies
        no such figure, and `_render` refuses an unanswered placeholder - so the run that most
        needed the disclosure could not have its page produced at all."""
        self._log(("D0214", "waiver: review.line_coverage", "why", "accepted", "2026-07-22"))
        state = {"schema": 1, "run_id": "RUN-TEST01", "batch": [], "goal": "done",
                 "sprint_goal": "g", "sprint_goal_verdict": {"verdict": "achieved", "note": "n"},
                 "started_at": None, "ended_at": self.WINDOW_END}
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        rd = self.root / "sdlc-studio" / "retros"
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "RETRO0001-r.md").write_text(
            "# RETRO0001: a sprint\n\n> **Batch:** none\n\n## Delivered\n- nothing\n",
            encoding="utf-8")
        rep = sr.build_report(self.root, "RETRO0001")
        section = next(s for s in rep["sections"] if s["key"] == "waivers")
        self.assertIsNotNone(section["not_measured"])
        md = sr.render_markdown(rep)          # must not raise
        self.assertIn("NOT MEASURED", md)
        self.assertIn("could not be bounded", md,
                      "the reason is the only text the signer gets on this path")
        # BOTH twins. The HTML branch fails SILENTLY if it regresses - the `when:` guard means
        # no unanswered placeholder, so the page emits the heading and lede with nothing beneath,
        # which is the absent-section-reads-as-not-checked failure AC4 exists to prevent.
        self.assertIn("could not be bounded", sr.render_html(rep),
                      "the html twin must disclose it too, or it regresses without raising")

    def test_an_unreadable_decisions_log_returns_the_shape_the_caller_unpacks(self) -> None:
        """The import guard's own comment says a report must not die on a log read. When the
        return signature became a pair, the guard still returned a bare list, so the caller's
        unpack raised and the guard became the death it exists to prevent."""
        with unittest.mock.patch.dict("sys.modules", {"decisions": None}):
            self.assertEqual(([], []), sr._waivers_in_force(self.root, self.WINDOW_END,
                                                            self.WINDOW_START))

    def test_a_row_carries_its_date_and_a_populated_note(self) -> None:
        """The reviewer found four behaviours unpinned: the date cell, the `_ROW_LISTS` value, the
        non-empty note and row order. The first three are pinned here; order is pinned by the
        two-row fixture below."""
        self._log(("D0301", "waiver: lane.a", "reason a", "accepted", "2026-07-02"),
                  ("D0302", "waiver: lane.b", "reason b", "accepted", "2026-07-03"))
        section = sr._waivers_section(self.root, self.WINDOW_END, self.WINDOW_START)
        rows = section["rows"]
        self.assertEqual(["2026-07-02", "2026-07-03"], [r["waiver_date"]["value"] for r in rows],
                         "the date must be carried, and in log order")
        self.assertEqual(2, section["figures"]["waivers_count"]["value"])
        self.assertIn("2 gate(s) were not holding",
                      section["figures"]["waivers_note"]["value"])

    def test_a_run_with_no_waivers_renders_an_explicit_empty_set(self) -> None:
        """AC4. An absent section reads as `not checked`, and the whole point is that the signer
        can tell the difference between nothing waived and nobody looking."""
        self._log()
        section = sr._waivers_section(self.root, self.WINDOW_END, self.WINDOW_START)
        self.assertEqual("waivers", section["key"])
        self.assertEqual([], section["rows"])
        note = section["figures"]["waivers_note"]["value"].lower()
        self.assertIn("no gate stood down", note)
        self.assertIn("the log was read", note,
                      "the note must say the log WAS read - that is the whole distinction "
                      "between nothing waived and nobody looking")
        self.assertEqual(0, section["figures"]["waivers_count"]["value"])


if __name__ == "__main__":
    unittest.main()
