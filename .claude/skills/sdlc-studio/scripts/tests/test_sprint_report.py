"""The sprint report (US0174) + its config gate (US0176).

The load-bearing properties are the honesty ones: cost sums over ATTEMPTS (rework counted), an
unpriced model is named not guessed, an interactive batch says so rather than reporting $0, and the
config switch gates RENDERING only - never recording.
"""
import contextlib
import io
import json
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
        self.assertNotIn("Sprint Goal", sr.render(rep))


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


if __name__ == "__main__":
    unittest.main()
