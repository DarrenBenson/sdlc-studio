"""The sprint report (US0174) + its config gate (US0176).

The load-bearing properties are the honesty ones: cost sums over ATTEMPTS (rework counted), an
unpriced model is named not guessed, an interactive batch says so rather than reporting $0, and the
config switch gates RENDERING only - never recording.
"""
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock
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

    def test_an_equivalent_survivor_is_visible_in_the_report(self) -> None:
        mut = _mutation()
        rid = self._run(survived=2, elapsed=120.0)
        target = self.root / "thing.py"
        target.write_text("x = 1\n", encoding="utf-8")
        mut.register_mutant(self.root, target, "a no-op swap", None, "equivalent",
                            reason="unkillable by construction", run=rid)
        rep = sr.report(self.root, "RETRO9100")
        self.assertEqual(rep["mutation"]["current"]["equivalent"], 1)
        self.assertIn("1 equivalent", sr.render(rep))

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


class DisclosureTests(unittest.TestCase):
    """D0059 trades independence for DISCLOSURE, so the disclosure has to reach a reader who
    does not already know to look for it."""

    def test_every_delegated_signoff_is_named_with_its_delegate(self) -> None:
        """AC1. A count alone is not enough - which unit, and which delegate, is what lets a
        reader weigh the verdicts."""
        rep = {"ok": True, "id": "RETRO0001", "date": "2026-07-24", "units": [],
               "delivered_points": 0,
               "delegated_signoffs": [
                   {"unit": "US0001", "chain": "operator -> qa-seat (boundary: agent) "
                                               "[DELEGATED AGENT]"},
                   {"unit": "US0002", "chain": "operator -> qa-seat (boundary: agent) "
                                               "[DELEGATED AGENT]"}]}
        lines = sr._delegated_signoff_lines(rep)
        joined = "\n".join(lines)
        self.assertIn("2", joined, "the count must be stated")
        self.assertIn("US0001", joined)
        self.assertIn("US0002", joined)
        self.assertIn("qa-seat", joined, "the delegate must be named")
        self.assertIn("not by an independent reviewer", joined)

    def test_a_sprint_with_no_delegated_signoffs_says_nothing(self) -> None:
        """The negative control. A disclosure block that appears when there is nothing to
        disclose trains the reader to skip it."""
        self.assertEqual(
            sr._delegated_signoff_lines({"ok": True, "delegated_signoffs": []}), [])


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
                     "run-opened", "batch-boundary-review"}
        rows = {i["id"]: i for i in sr.CHECKLIST}
        self.assertTrue(pre_close <= set(rows), "a pre-close row was renamed or removed")
        for rid in pre_close:
            self.assertNotEqual(sr.CLOSE_WINDOW, sr._window(rows[rid]),
                                f"{rid} is enforced before the close, but declares the close as "
                                f"the last command that could satisfy it")
        drift = sr.cycle_drift()
        known = set(drift.get("covered") or []) | set(drift.get("verbs") or [])
        for item in sr.CHECKLIST:
            win = sr._window(item)
            self.assertTrue(win, f"{item['id']} declares no window")
            if known:
                self.assertIn(win, known | {sr.CLOSE_WINDOW},
                              f"{item['id']} names a window no shipped verb exposes")

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

    def test_a_pass_over_no_ticks_at_all_is_refused(self) -> None:
        """A pass over an empty set is not a pass - the affirmative-over-nothing shape the
        sibling rows refuse by design. Mutant: return RAN when nothing was examined."""
        for uid in ("US0001", "US0002"):
            self._unit(uid, "src/touched.py", ticked=False)
        row = self._resolve({"src/touched.py"})
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("nothing was checked", row["detail"])

    def test_an_unreadable_diff_is_unjudged_not_supported(self) -> None:
        """None is not an empty set. `could not be taken` and `nothing changed` lead to opposite
        verdicts, and collapsing them certifies what the row could not check."""
        self._unit("US0001", "src/a.py", ticked=True)
        self._unit("US0002", "src/b.py", ticked=True)
        row = self._resolve(None)
        self.assertEqual(sr.NOT_RUN, row["state"])
        self.assertIn("unjudged", row["detail"])


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

    def test_a_batch_span_OPENED_is_not_a_review_HELD(self) -> None:
        """Certifying the ceremony by the act of scheduling it is the failure mode: a span with
        no `reviewed_at` is a batch nobody reviewed, however many spans were opened."""
        unreviewed = self._ck(batches=[{"units": ["US0001"], "opened_at": "2026-01-01T01:00:00Z"}])
        row = self._row(unreviewed, "batch-boundary-review")
        # EXPIRED, not NOT RUN: its enforcer is `sprint review-batch`, which cannot be run at a
        # close where the batch has already been delivered (US0591). Still reported, and still
        # distinguishable from a batch that WAS reviewed - which is this test's subject.
        self.assertEqual(row["state"], sr.EXPIRED)
        self.assertIn("0/1", row["value"])
        self.assertIn("batch-boundary-review", unreviewed["expired"])
        # ... and the control, so the state depends on the review rather than being constant.
        reviewed = self._ck(batches=[{"units": ["US0001"], "opened_at": "2026-01-01T01:00:00Z",
                                      "reviewed_at": "2026-01-01T02:00:00Z"}])
        self.assertEqual(self._row(reviewed, "batch-boundary-review")["state"], sr.RAN)

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
        import retro as retro_mod
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
        self.assertEqual(blind["state"], sr.UNANSWERED)
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
            self.assertEqual(row["state"], sr.UNANSWERED)
            self.assertIn("unknown", row["value"])
            self.assertNotIn("0 filed against 0", row["value"])

    def test_every_compulsory_item_is_a_row_of_the_report(self) -> None:
        """One artefact, not two. Two close-time documents that both claim to record the run
        is the drift this repo keeps filing bugs about."""
        self._run()
        rep = sr.report(self.root, "RETRO9100")
        self.assertIn("checklist", rep)
        ids = {r["id"] for r in rep["checklist"]["items"]}
        self.assertEqual(ids, {i["id"] for i in sr.CHECKLIST})
        text = sr.render(rep)
        self.assertIn("## Sprint checklist", text)
        for item in sr.CHECKLIST:
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
        before = sr.checklist(self.root, "RETRO9100")["outstanding"]
        self.assertIn("cost", before)
        decisions.record_waiver(self.root, f"{sr.WAIVER_SUBJECT}:cost",
                                "interactive sprint: no per-unit telemetry exists to read",
                                authorised_by="the operator")
        row = self._row(sr.checklist(self.root, "RETRO9100"), "cost")
        self.assertEqual(row["state"], sr.WAIVED)
        self.assertTrue(row["waiver"], "the waiver's decision id is not recorded on the row")
        self.assertNotIn("cost", sr.checklist(self.root, "RETRO9100")["outstanding"])
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
        """The sign-off and the handoff are produced BY the close. Holding the chain on them
        makes the only exit the step it blocks, which is a deadlock, not a gate."""
        ck = self._ck(outcome="blocked", handoff=None)
        self.assertEqual(self._row(ck, "signoff")["state"], sr.NOT_RUN)
        self.assertNotIn("signoff", ck["outstanding"])
        self.assertIn("signoff", ck["pending_in_close"])
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


class SignoffProvenanceTests(unittest.TestCase):
    """The close report must not hide WHO accepted the batch behind a single count."""

    def test_the_report_splits_panel_from_operator(self) -> None:
        """MUTANT: report `len(signed)` alone, as it did before.

        A combined total reads as complete whether a human or a panel accepted every unit, and
        those are different facts about who took responsibility.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sprint_report", SCRIPT if "SCRIPT" in globals()
            else Path(__file__).resolve().parent.parent / "sprint_report.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["sprint_report"] = mod
        spec.loader.exec_module(mod)
        import critic as _c  # noqa: F401
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            for uid, slug in (("US0001", "a"), ("US0002", "b")):
                (root / "sdlc-studio" / "stories" / f"{uid}-{slug}.md").write_text(
                    f"# {uid}: x\n\n> **Status:** Review\n> **Points:** 3\n"
                    f"> **Affects:** src/{slug}.py\n", encoding="utf-8")
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  signoff: panel\n", encoding="utf-8")
            import critic
            # Briefed verdicts first: the panel interlock refuses to ratify a review carrying
            # no provenance, so a fixture without them tests the interlock, not the report.
            for uid in ("US0001", "US0002"):
                critic.record_verdict(root, uid, "APPROVE", "qa seat", "auth",
                                      issues="none blocking", brief="abcdef123456")
            critic.record_signoff(root, "US0001", "Lena Marsh", "auth",
                                  panel=["qa", "engineering"])
            critic.record_signoff(root, "US0002", "Darren Benson", "auth")
            state, value, _detail = mod._ck_signoff(
                {"units": ["US0001", "US0002"], "root": root})
        self.assertEqual("ran", state)
        self.assertIn("1 panel", value, f"the row does not report the panel count: {value}")
        self.assertIn("1 operator", value, f"the row does not report the operator count: {value}")


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
        import critic
        self._verdict("US0001", "REJECT", issues="the test could not fail")
        critic.record_signoff(self.root, "US0002", principal="product", author="dev",
                              capacity=critic.CAPACITY_SEAT)
        with contextlib.redirect_stderr(io.StringIO()):
            s = sr.operator_summary(self.root, "RETRO9100")
        why = {r["unit"]: r["why"] for r in s["reversal_candidates"]}
        self.assertIn("US0001", why)
        self.assertIn("rejected", why["US0001"])
        self.assertIn("US0002", why)
        self.assertIn("SEAT", why["US0002"])
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

    def test_the_summary_is_generated_for_a_human_signoff_too(self) -> None:
        """Mutant: generate it only on the panel path - the human close and the seat close
        diverge, and a second code path is one that drifts."""
        import critic
        self._verdict("US0001", "APPROVE")
        critic.record_signoff(self.root, "US0001", principal="darren", author="dev")
        with contextlib.redirect_stderr(io.StringIO()):
            s = sr.operator_summary(self.root, "RETRO9100")
        shipped = {r["unit"]: r["signed_by"] for r in s["shipped"]}
        self.assertEqual(shipped.get("US0001"), critic.CAPACITY_HUMAN)
        self.assertNotIn("US0001", [r["unit"] for r in s["reversal_candidates"]],
                         "a human sign-off is not a thing to overturn on those grounds")

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

if __name__ == "__main__":
    unittest.main()
