"""Unit tests for telemetry.py - the project's measured evidence, and the forecasts it judges.

The evidence logs are COMMITTED. They record observations of runs that already happened, no
tool can regenerate them, and a log kept in the gitignored `.local/` state dir is one machine's
private memory: on a fresh clone every forecast reads UNFORECAST and the whole estimate-vs-actual
history reads as no-evidence. Several tests below exist only to hold that line.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "telemetry.py"
sys.path.insert(0, str(SCRIPT.parent))
from lib import sdlc_md  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("telemetry", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["telemetry"] = mod
    spec.loader.exec_module(mod)
    return mod


tel = _load()


class RecordTests(unittest.TestCase):
    def test_record_omits_none_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "US0001", "type": "story", "iterations": 3,
                                 "wall_time_s": None, "tokens": None})
            self.assertEqual({k: v for k, v in rec.items() if k != "project"},
                             {"id": "US0001", "type": "story", "iterations": 3})
            self.assertNotIn("tokens", rec)
            self.assertIn("project", rec)  # every record is stamped with its project

    def test_appends_not_overwrites(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "US0001"})
            tel.record(d, {"id": "US0002"})
            recs = tel.read_all(d)
            self.assertEqual([r["id"] for r in recs], ["US0001", "US0002"])

    def test_the_measurement_is_written_where_git_can_see_it(self) -> None:
        """A measurement kept in the gitignored `.local/` state dir is one machine's private
        memory: on a fresh clone it does not exist, and evidence the team cannot read is not
        evidence. It lands in the committed evidence dir, never under any `.local/`."""
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "X"})
            p = tel.actuals_path(d)
            self.assertTrue(p.exists())
            self.assertNotIn(".local", p.parts)
            self.assertEqual(p.parent, Path(d) / "sdlc-studio" / "retros" / "evidence")
            self.assertFalse((Path(d) / "sdlc-studio" / ".local").exists())

    def test_the_log_is_sharded_by_day_so_two_branches_do_not_collide(self) -> None:
        """The merge story. Append-only JSONL merges badly, so each day is its own file: two
        sprints closed on different days, on different branches, touch different files and merge
        cleanly. Same day is the same file, and git raises a conflict a human resolves."""
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "X"})
            self.assertEqual(tel.actuals_path(d).name, f"actuals-{tel.shard_id()}.jsonl")
            other = tel.actuals_path(d, "2020-01-01")
            self.assertNotEqual(other, tel.actuals_path(d))
            other.write_text('{"id": "OLD", "tokens": 1}\n', encoding="utf-8")
            # both shards are read, oldest (by name) first
            self.assertEqual([r["id"] for r in tel.read_all(d)], ["OLD", "X"])

    def test_unknown_field_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "U1", "secret": "hunter2", "cwd": "/x"})
            # only whitelisted FIELDS are written (plus the stamped project)
            self.assertEqual({k: v for k, v in rec.items() if k != "project"}, {"id": "U1"})
            self.assertNotIn("hunter2", tel.actuals_path(d).read_text(encoding="utf-8"))

    def test_read_all_skips_malformed_lines(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "good"})
            with tel.actuals_path(d).open("a", encoding="utf-8") as fh:
                fh.write("{ not json\n\n")
            tel.record(d, {"id": "good2"})
            self.assertEqual([r["id"] for r in tel.read_all(d)], ["good", "good2"])

    def test_the_evidence_log_is_never_rolled(self) -> None:
        """A bounded roll drops the OLDEST records first. On a committed evidence log that means
        deleting history out of git - and the oldest forecast is the authoritative one."""
        with tempfile.TemporaryDirectory() as d:
            for n in range(sdlc_md.DEFAULT_LOG_MAX_LINES + 50):
                tel.record(d, {"id": f"U{n:05d}"})
            self.assertEqual(len(tel.read_all(d)), sdlc_md.DEFAULT_LOG_MAX_LINES + 50)
            self.assertEqual(tel.read_all(d)[0]["id"], "U00000")

    def test_read_all_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tel.read_all(d), [])

    def test_record_never_raises_on_unwritable(self) -> None:
        # telemetry is advisory - a write failure must be swallowed, returning the record.
        rec = tel.record("/proc/nonexistent-rootlevel-xyz", {"id": "Z"})
        self.assertEqual(rec["id"], "Z")

    def test_tokens_recorded_when_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "T", "tokens": 1234})
            self.assertEqual(rec["tokens"], 1234)


class SummaryTests(unittest.TestCase):
    """show --summary aggregates the jsonl into readable per-type stats."""

    def _seed(self, d):
        for rec in ({"id": "US0001", "type": "story", "iterations": 2, "wall_time_s": 100,
                     "critic_verdict": "approve", "reopened": "no"},
                    {"id": "US0002", "type": "story", "iterations": 4, "wall_time_s": 300,
                     "critic_verdict": "reject", "reopened": "yes"},
                    {"id": "CR0001", "type": "cr", "iterations": 1,
                     "critic_verdict": "approve"}):
            tel.record(d, rec)

    def test_summarise_per_type(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            s = tel.summarise(tel.read_all(d))
            self.assertEqual(s["story"]["count"], 2)
            self.assertEqual(s["story"]["mean_iterations"], 3.0)
            self.assertEqual(s["story"]["mean_wall_time_s"], 200.0)
            self.assertEqual(s["story"]["reopen_rate"], 0.5)
            self.assertEqual(s["story"]["verdicts"], {"approve": 1, "reject": 1})
            self.assertEqual(s["cr"]["count"], 1)
            self.assertIsNone(s["cr"]["mean_wall_time_s"])  # absent field -> None, not 0

    def test_summary_empty_is_empty(self) -> None:
        self.assertEqual(tel.summarise([]), {})

    def test_cli_summary_flag(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = tel.main(["show", "--summary", "--root", d])
            self.assertEqual(rc, 0)
            out = buf.getvalue()
            self.assertIn("story", out)
            self.assertIn("mean_iterations", out.replace(" ", "").replace("=", "_")
                          if "mean_iterations" not in out else out)


class TierFieldsTests(unittest.TestCase):
    """RFC0026 / CR0191: routing tier fields recorded + summarised per delivered tier."""

    def test_tier_fields_recorded_and_absent_fields_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "US0001", "type": "story",
                                  "tier_recommended": "small",
                                  "tier_delivered": "medium",
                                  "model": "model-m", "escalated": "true"})
            self.assertEqual(rec["tier_recommended"], "small")
            self.assertEqual(rec["tier_delivered"], "medium")
            self.assertEqual(rec["model"], "model-m")
            self.assertEqual(rec["escalated"], "true")
            plain = tel.record(d, {"id": "US0002", "type": "story"})
            self.assertNotIn("tier_delivered", plain)  # whitelist discipline unchanged

    def test_cli_record_accepts_tier_flags(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = tel.main(["record", "--id", "US0001", "--type", "story",
                               "--tier-recommended", "small",
                               "--tier-delivered", "small",
                               "--model", "model-s", "--escalated", "false",
                               "--root", d])
            self.assertEqual(rc, 0)
            recs = tel.read_all(d)
            self.assertEqual(recs[0]["tier_delivered"], "small")

    def test_cli_record_accepts_attempts_writer(self) -> None:
        # BG0152: the record CLI must be able to WRITE a per-attempt list, not only the
        # reader (attempts_of) being able to read one. A cheap-first unit that escalated
        # carries both attempts, and unit_cost sums them - flat --tokens cannot express it.
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = tel.main(["record", "--id", "US0001", "--type", "story",
                               "--attempt", "haiku:1000", "--attempt", "opus:5000",
                               "--root", d])
            self.assertEqual(rc, 0)
            rec = tel.read_all(d)[0]
            self.assertEqual(rec["attempts"],
                             [{"model": "haiku", "tokens": 1000},
                              {"model": "opus", "tokens": 5000}])
            self.assertEqual(tel.attempts_of(rec),
                             [{"model": "haiku", "tokens": 1000},
                              {"model": "opus", "tokens": 5000}])

    def test_cli_record_accepts_attempts_json(self) -> None:
        # BG0152: a JSON form for callers that already hold the structured list.
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = tel.main(["record", "--id", "US0002", "--type", "story",
                               "--attempts",
                               json.dumps([{"model": "sonnet", "tokens": 2000}]),
                               "--root", d])
            self.assertEqual(rc, 0)
            self.assertEqual(tel.read_all(d)[0]["attempts"],
                             [{"model": "sonnet", "tokens": 2000}])

    def test_summary_groups_per_delivered_tier(self) -> None:
        rows = [
            {"id": "A", "type": "story", "critic_verdict": "approve",
             "tier_delivered": "small", "reopened": "no"},
            {"id": "B", "type": "story", "critic_verdict": "reject",
             "tier_delivered": "small", "reopened": "yes"},
            {"id": "C", "type": "cr", "critic_verdict": "approve",
             "tier_delivered": "large"},
        ]
        s = tel.summarise(rows)
        self.assertIn("by_tier", s)
        self.assertEqual(s["by_tier"]["small"]["count"], 2)
        self.assertEqual(s["by_tier"]["small"]["verdicts"], {"approve": 1, "reject": 1})
        self.assertEqual(s["by_tier"]["small"]["reopen_rate"], 0.5)
        self.assertEqual(s["by_tier"]["large"]["count"], 1)
        self.assertIsNone(s["by_tier"]["large"]["reopen_rate"])  # no data -> None, not 0

    def test_no_per_tier_block_when_no_record_carries_a_tier(self) -> None:
        rows = [{"id": "A", "type": "story", "critic_verdict": "approve"}]
        s = tel.summarise(rows)
        self.assertNotIn("by_tier", s)


class PlanReviewEventTests(unittest.TestCase):
    """US0091: plan-review events are their own block and never pollute the unit aggregates."""

    def test_event_excluded_from_type_aggregate(self) -> None:
        rows = [{"id": "US0001", "type": "story", "iterations": 2},
                {"event": "plan-review", "phase": "plan-review", "id": "US0001",
                 "verdict": "APPROVE", "reviewer": "qa", "author": "dev", "independent": True}]
        s = tel.summarise(rows)
        self.assertEqual(s["story"]["count"], 1)
        self.assertNotIn("unknown", s)                 # no phantom bucket
        self.assertEqual(s["plan_review"]["count"], 1)
        self.assertEqual(s["plan_review"]["verdicts"], {"APPROVE": 1})
        self.assertEqual(s["plan_review"]["independent_rate"], 1.0)

    def test_record_plan_review_independence_matches_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # `-` sentinel and empty author read as NOT independent (same as critic.is_independent)
            self.assertFalse(tel.record_plan_review(d, "US1", "APPROVE", "qa", "-")["independent"])
            self.assertFalse(tel.record_plan_review(d, "US1", "APPROVE", "qa", "")["independent"])
            self.assertFalse(tel.record_plan_review(d, "US1", "APPROVE", "dev", "dev")["independent"])
            self.assertTrue(tel.record_plan_review(d, "US1", "APPROVE", "qa", "dev")["independent"])

    def test_record_plan_review_never_raises(self) -> None:
        rec = tel.record_plan_review("/proc/nonexistent-xyz", "US1", "APPROVE", "qa", "dev")
        self.assertEqual(rec["id"], "US1")             # best-effort, returns the record

    def test_event_record_carries_phase(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record_plan_review(d, "US1", "reject", "qa", "dev")
            self.assertEqual(rec["phase"], "plan-review")
            self.assertEqual(rec["verdict"], "REJECT")


class ActualsTests(unittest.TestCase):
    """The measured actuals a retro's estimate-vs-actual report reads."""

    def test_the_last_non_null_value_wins_not_the_last_record(self) -> None:
        """The loop appends a bare close record after the instrumented one. Taking the last
        record wholesale would erase a measurement that was genuinely taken."""
        got = tel.latest_actuals([
            {"id": "BG0126", "type": "bug", "tokens": 46792, "wall_time_s": 272},
            {"id": "BG0126", "type": "bug"},
        ])
        self.assertEqual(got["BG0126"]["tokens"], 46792)
        self.assertEqual(got["BG0126"]["wall_time_s"], 272)

    def test_a_field_no_record_carried_is_absent_not_zero(self) -> None:
        """An unmeasured unit must be reportable as unmeasured. A fabricated 0 would read as
        a unit that cost nothing."""
        got = tel.latest_actuals([{"id": "CR0001", "type": "cr", "wall_time_s": 10}])
        self.assertNotIn("tokens", got["CR0001"])

    def test_plan_review_events_are_not_unit_actuals(self) -> None:
        got = tel.latest_actuals([{"event": "plan-review", "id": "CR0001", "verdict": "APPROVE"}])
        self.assertEqual(got, {})

    def test_actuals_reads_the_projects_log(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "CR0002", "type": "cr", "tokens": 1234})
            self.assertEqual(tel.actuals(d)["CR0002"]["tokens"], 1234)


class ForecastLogTests(unittest.TestCase):
    """The estimate side of the ratio. A forecast is a RECORD of what was predicted, kept so
    that judging it later cannot mean recomputing it from the model being judged."""

    CONSTANTS = {"BASE_TOKEN_BUDGET": 50_000, "TOKENS_PER_COGNITIVE": 600}

    def rec(self, uid: str, tokens: int, constants: dict | None = None) -> dict:
        return {"id": uid, "tokens": tokens, "seed": 10, "seed_source": "complexity",
                "constants": constants or self.CONSTANTS, "planned_at": "2026-07-14T09:00:00Z"}

    def test_a_forecast_is_written_and_read_back_whole(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            got = tel.forecasts(d)["CR0001"]
            self.assertEqual(got["tokens"], 56_000)
            self.assertEqual(got["seed"], 10)
            self.assertEqual(got["constants"], self.CONSTANTS,
                             "a forecast that does not record its estimator cannot say which "
                             "model its error belongs to")

    def test_the_first_forecast_for_a_unit_wins(self) -> None:
        """Hindsight is not a forecast. Re-planning after the work is done must not be able to
        rewrite what was predicted before it started."""
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            tel.record_forecasts(d, [self.rec("CR0001", 999_000)])
            self.assertEqual(tel.forecasts(d)["CR0001"]["tokens"], 56_000)
            self.assertEqual(len(tel.read_forecasts(d)), 2, "the later one is kept as history")

    def test_recording_the_same_forecast_twice_does_not_grow_the_log(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            res = tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            self.assertEqual(res["recorded"], [])
            self.assertEqual(res["already"], ["CR0001"])
            self.assertEqual(len(tel.read_forecasts(d)), 1)

    def test_a_unit_never_forecast_is_absent_not_zero(self) -> None:
        """The mirror of the actuals rule. An absent forecast must be reportable as absent -
        a 0, or a number derived on the spot, would read as a prediction nobody made."""
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            self.assertNotIn("CR0002", tel.forecasts(d))

    def test_a_corrupt_line_does_not_break_the_read(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            p = tel.forecasts_path(d)
            p.write_text(p.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
            self.assertEqual(tel.forecasts(d)["CR0001"]["tokens"], 56_000)

    def test_a_forecast_lives_beside_the_actuals_not_inside_them(self) -> None:
        """Two logs, so neither can evict or overwrite the other, and a unit's forecast and its
        actual can be read back independently."""
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            tel.record(d, {"id": "CR0001", "type": "cr", "tokens": 40_000})
            self.assertEqual(tel.actuals(d)["CR0001"]["tokens"], 40_000)
            self.assertEqual(tel.forecasts(d)["CR0001"]["tokens"], 56_000)
            self.assertNotEqual(tel.forecasts_path(d), tel.actuals_path(d))

    def test_the_forecast_is_written_where_git_can_see_it(self) -> None:
        """The whole point of recording it. A forecast that only exists on the machine that
        planned the sprint cannot be used to falsify the estimator by anyone else."""
        with tempfile.TemporaryDirectory() as d:
            tel.record_forecasts(d, [self.rec("CR0001", 56_000)])
            p = tel.forecasts_path(d)
            self.assertTrue(p.exists())
            self.assertNotIn(".local", p.parts)
            self.assertEqual(p.parent, Path(d) / "sdlc-studio" / "retros" / "evidence")

    def test_the_first_forecast_wins_across_shards_not_just_within_one(self) -> None:
        """First-wins is what stops hindsight rewriting a prediction, and it must hold when the
        two records land in different day shards - which is the normal case for a re-plan."""
        with tempfile.TemporaryDirectory() as d:
            tel.forecasts_path(d, "2020-01-01").parent.mkdir(parents=True, exist_ok=True)
            tel.forecasts_path(d, "2020-01-01").write_text(
                json.dumps(self.rec("CR0001", 56_000)) + "\n", encoding="utf-8")
            tel.record_forecasts(d, [self.rec("CR0001", 999_000)])  # today's shard
            self.assertEqual(tel.forecasts(d)["CR0001"]["tokens"], 56_000)
            self.assertEqual(len(tel.read_forecasts(d)), 2, "the later one is kept as history")

    def test_the_cli_records_a_forecast(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc = tel.main(["forecast", "--id", "CR0009", "--tokens", "75000", "--points", "3",
                           "--constant", "TOKENS_PER_POINT=25000", "--root", d])
            self.assertEqual(rc, 0)
            got = tel.forecasts(d)["CR0009"]
            self.assertEqual(got["tokens"], 75_000)
            self.assertEqual(got["points"], 3, "the SIZE is on the record, not just the tokens")
            self.assertEqual(got["constants"]["TOKENS_PER_POINT"], 25_000)

    def test_the_estimator_is_recorded_whatever_shape_it_has(self) -> None:
        """The estimator has already changed twice. A recorder that only knows today's field
        names cannot record yesterday's forecast, and the history is what falsifies the model."""
        with tempfile.TemporaryDirectory() as d:
            tel.main(["forecast", "--id", "CR0010", "--tokens", "50000",
                      "--constant", "BASE_TOKEN_BUDGET=50000",
                      "--constant", "TOKENS_PER_COGNITIVE=600", "--root", d])
            self.assertEqual(tel.forecasts(d)["CR0010"]["constants"],
                             {"BASE_TOKEN_BUDGET": 50_000, "TOKENS_PER_COGNITIVE": 600})

    def test_a_size_off_the_fibonacci_scale_is_refused_not_rounded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                tel.main(["forecast", "--id", "CR0011", "--tokens", "50000", "--points", "7",
                          "--constant", "TOKENS_PER_POINT=25000", "--root", d])
            self.assertEqual(tel.forecasts(d), {}, "nothing was written")


class MigrationLosesNothing(unittest.TestCase):
    """A project whose evidence predates the logs being committed still has it in `.local/`.
    It is READ from there regardless, and `migrate` moves it into the repository.

    A migration that silently drops a record is the worst possible outcome: a measured run
    cannot be re-measured. So the move is attacked, not assumed.
    """

    ACTUALS = [{"id": "BG0001", "type": "bug", "tokens": 46_792, "wall_time_s": 272,
                "model": "m-1"},
               {"id": "CR0001", "type": "cr", "tokens": 98_513, "wall_time_s": 475,
                "model": "m-1"}]
    FORECASTS = [{"id": "BG0001", "tokens": 245_000, "seed": 39,
                  "constants": {"BASE_TOKEN_BUDGET": 50_000, "TOKENS_PER_COGNITIVE": 5_000}}]

    def legacy(self, d) -> Path:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (root / tel.LEGACY_ACTUALS).write_text(
            "".join(json.dumps(r) + "\n" for r in self.ACTUALS), encoding="utf-8")
        (root / tel.LEGACY_FORECASTS).write_text(
            "".join(json.dumps(r) + "\n" for r in self.FORECASTS), encoding="utf-8")
        return root

    def test_an_unmigrated_local_log_is_still_read(self) -> None:
        """Upgrading the skill must not make a project's existing evidence vanish."""
        with tempfile.TemporaryDirectory() as d:
            root = self.legacy(d)
            self.assertEqual(tel.actuals(root)["BG0001"]["tokens"], 46_792)
            self.assertEqual(tel.forecasts(root)["BG0001"]["tokens"], 245_000)

    def test_migrate_moves_every_record_and_changes_none(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self.legacy(d)
            before_a, before_f = tel.read_all(root), tel.read_forecasts(root)
            tel.migrate(root)
            self.assertEqual(tel.read_all(root), before_a, "an actual was lost or altered")
            self.assertEqual(tel.read_forecasts(root), before_f, "a forecast was lost or altered")
            self.assertFalse((root / tel.LEGACY_ACTUALS).exists())
            self.assertFalse((root / tel.LEGACY_FORECASTS).exists())

    def test_the_migrated_evidence_is_no_longer_under_a_local_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self.legacy(d)
            tel.migrate(root)
            landed = sorted((root / tel.EVIDENCE).glob("*.jsonl"))
            self.assertEqual([p.name for p in landed],
                             ["actuals-0000-migrated.jsonl", "forecasts-0000-migrated.jsonl"])
            for p in landed:
                self.assertNotIn(".local", p.parts)

    def test_the_migrated_shard_reads_before_todays(self) -> None:
        """Chronology. The migrated records predate every dated shard, so first-wins on the
        forecast side must still pick the one that was actually predicted first."""
        with tempfile.TemporaryDirectory() as d:
            root = self.legacy(d)
            tel.migrate(root)
            tel.record_forecasts(root, [{"id": "BG0001", "tokens": 1,
                                         "constants": {"BASE_TOKEN_BUDGET": 1,
                                                       "TOKENS_PER_COGNITIVE": 1}}])
            self.assertEqual(tel.forecasts(root)["BG0001"]["tokens"], 245_000)

    def test_migrating_twice_does_not_duplicate_a_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self.legacy(d)
            tel.migrate(root)
            after = tel.read_all(root)
            self.legacy(d)          # a stale .local log turns up again
            tel.migrate(root)
            self.assertEqual(tel.read_all(root), after)

    def test_migrate_with_nothing_to_move_is_a_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tel.migrate(d)["moved"], [])


class ProjectStampTests(unittest.TestCase):
    """CR0270: every evidence record carries the project it was produced in, stamped at write
    time from the repo, so records pooled from several projects stay attributable. A measurement
    is taken once and cannot be backfilled, and neither can its attribution - so it lands when the
    record is written, not when it is later read."""

    def _repo(self, d, name):
        from gitutil import git
        git(["init", "-q"], cwd=d)
        git(["remote", "add", "origin", f"git@github.com:acme/{name}.git"], cwd=d)

    def test_project_resolves_from_the_git_remote(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, "widget")
            self.assertEqual(tel.project_name(d), "widget",
                             "the canonical name survives a directory rename or a different clone "
                             "path on another machine")

    def test_project_falls_back_to_the_directory_name_without_a_remote(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # not a git repo at all - the resolved root directory's own name is the answer
            self.assertEqual(tel.project_name(d), Path(d).resolve().name)

    def test_a_forecast_and_an_actual_written_today_carry_the_resolved_project(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, "widget")
            tel.record(d, {"id": "US0001", "type": "story", "tokens": 1_000, "model": "m1"})
            tel.record_forecasts(d, [{"id": "US0001", "tokens": 1_200, "points": 3,
                                      "constants": {"TOKENS_PER_POINT": 400}}])
            self.assertEqual(tel.actuals(d)["US0001"]["project"], "widget")
            self.assertEqual(tel.forecasts(d)["US0001"]["project"], "widget")

    def test_the_write_time_stamp_ignores_any_project_the_caller_passes(self) -> None:
        """The stamp is the repo's, always - a forecast cannot claim to belong to a project it
        was not recorded in."""
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, "widget")
            tel.record_forecasts(d, [{"id": "US0001", "tokens": 1_200, "points": 3,
                                      "project": "somewhere-else", "constants": {}}])
            self.assertEqual(tel.forecasts(d)["US0001"]["project"], "widget")

    def test_an_old_record_with_no_project_still_reads_and_is_never_invented(self) -> None:
        """Additive: a record written before the field existed must still read, so history is not
        invalidated - the same tolerance the size_gate rename used."""
        with tempfile.TemporaryDirectory() as d:
            p = tel.actuals_path(d)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{"id": "OLD", "type": "bug", "tokens": 5}\n', encoding="utf-8")
            got = tel.actuals(d)["OLD"]
            self.assertEqual(got["tokens"], 5)
            self.assertIsNone(got.get("project"), "an absent project is absent, never guessed")


class BackfillProjectTests(unittest.TestCase):
    """CR0270: evidence recorded before the project field has a KNOWN project - the repo it lives
    in - so it can be stamped now. The stamp is attacked, not assumed (LL0028): every record must
    survive value-for-value, or the write is refused."""

    ACTUALS = [{"id": "BG0001", "type": "bug", "tokens": 46_792, "wall_time_s": 272,
                "model": "m-1"},
               {"id": "CR0001", "type": "cr", "tokens": 98_513, "model": "m-1"}]
    FORECASTS = [{"id": "BG0001", "tokens": 245_000, "points": 5,
                  "constants": {"TOKENS_PER_POINT": 40_000}, "planned_at": "2026-07-14"}]

    def _seed(self, d):
        ap = tel.actuals_path(d, "0000-migrated")
        ap.parent.mkdir(parents=True, exist_ok=True)
        ap.write_text("".join(json.dumps(r) + "\n" for r in self.ACTUALS), encoding="utf-8")
        tel.forecasts_path(d, "0000-migrated").write_text(
            "".join(json.dumps(r) + "\n" for r in self.FORECASTS), encoding="utf-8")

    @staticmethod
    def _strip(recs):
        return [{k: v for k, v in r.items() if k != "project"} for r in recs]

    def test_backfill_stamps_the_project_and_changes_no_other_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            before_a, before_f = tel.read_all(d), tel.read_forecasts(d)
            res = tel.backfill_project(d, project="legacy-proj")
            after_a, after_f = tel.read_all(d), tel.read_forecasts(d)
            # every record survives value-for-value once the added project is set aside
            self.assertEqual(self._strip(after_a), self._strip(before_a),
                             "an actual's measured value changed under backfill")
            self.assertEqual(self._strip(after_f), self._strip(before_f),
                             "a forecast changed under backfill")
            self.assertTrue(all(r["project"] == "legacy-proj" for r in after_a))
            self.assertTrue(all(r["project"] == "legacy-proj" for r in after_f))
            self.assertEqual(res["stamped"], len(self.ACTUALS) + len(self.FORECASTS))

    def test_backfill_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d)
            tel.backfill_project(d, project="p")
            snap_a, snap_f = tel.read_all(d), tel.read_forecasts(d)
            res = tel.backfill_project(d, project="p")
            self.assertEqual(res["stamped"], 0, "a second run has nothing left to stamp")
            self.assertEqual(tel.read_all(d), snap_a)
            self.assertEqual(tel.read_forecasts(d), snap_f)

    def test_backfill_leaves_a_record_that_already_names_a_project_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ap = tel.actuals_path(d, "0000-migrated")
            ap.parent.mkdir(parents=True, exist_ok=True)
            ap.write_text('{"id": "US0001", "type": "story", "tokens": 9, "project": "keep"}\n',
                          encoding="utf-8")
            tel.backfill_project(d, project="new")
            self.assertEqual(tel.actuals(d)["US0001"]["project"], "keep")


class AttemptsAndCostTests(unittest.TestCase):
    """US0172/US0173: per-attempt telemetry (non-destructive) + true cost summed over attempts."""

    def test_legacy_record_reads_as_one_attempt(self) -> None:
        self.assertEqual(tel.attempts_of({"model": "opus", "tokens": 100}),
                         [{"model": "opus", "tokens": 100}])

    def test_attempts_list_is_preserved_in_order(self) -> None:
        rec = {"attempts": [{"model": "haiku", "tokens": 50}, {"model": "opus", "tokens": 200}]}
        self.assertEqual([a["model"] for a in tel.attempts_of(rec)], ["haiku", "opus"])

    def test_empty_attempts_falls_back_to_flat_fields(self) -> None:
        self.assertEqual(tel.attempts_of({"attempts": [], "model": "sonnet", "tokens": 80}),
                         [{"model": "sonnet", "tokens": 80}])

    def test_no_measurement_yields_no_fabricated_attempt(self) -> None:
        self.assertEqual(tel.attempts_of({"id": "US0001"}), [])

    def test_true_cost_sums_over_attempts_including_rework(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = {"attempts": [{"model": "claude-haiku-4-5", "tokens": 50000},
                                {"model": "claude-opus-4-8", "tokens": 200000}]}
            c = tel.unit_cost(d, rec)  # 50k*1 + 200k*30 per 1e6 = 0.05 + 6.0
            self.assertEqual(c["tokens"], 250000)
            self.assertAlmostEqual(c["cost"], 6.05, places=4)
            self.assertEqual(c["unpriced"], [])

    def test_unpriced_model_is_named_not_guessed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            c = tel.unit_cost(d, {"model": "some-other-model", "tokens": 100000})
            self.assertEqual(c["cost"], 0.0)          # no dollars invented
            self.assertEqual(c["tokens"], 100000)      # tokens still counted
            self.assertEqual(c["unpriced"], ["some-other-model"])

    def test_config_price_overrides_the_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir(parents=True)
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text("pricing:\n  opus: 15.0\n")
            c = tel.unit_cost(d, {"model": "claude-opus-4-8", "tokens": 1000000})
            self.assertAlmostEqual(c["cost"], 15.0, places=4)

    def test_record_persists_an_attempts_list(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "US0001", "type": "story",
                           "attempts": [{"model": "haiku", "tokens": 10}]})
            rec = tel.read_all(d)[0]
            self.assertEqual(rec["attempts"], [{"model": "haiku", "tokens": 10}])


    def test_model_less_attempt_is_unpriced_unrecorded_not_a_crash(self) -> None:
        # MAJOR-1: a tokens-only attempt has no model to name; it must price as UNPRICED "unrecorded",
        # never leave a None in the unpriced list that a join() downstream would crash on.
        with tempfile.TemporaryDirectory() as d:
            c = tel.unit_cost(d, {"attempts": [{"tokens": 50000}]})
            self.assertEqual(c["tokens"], 50000)
            self.assertEqual(c["unpriced"], ["unrecorded"])
            self.assertNotIn(None, c["unpriced"])

    def test_negative_configured_price_is_refused(self) -> None:
        # MAJOR-2: a negative price would SUBTRACT from the total - a flattering figure. Refuse it.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir(parents=True)
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text("pricing:\n  opus: -6\n")
            c = tel.unit_cost(d, {"model": "claude-opus-4-8", "tokens": 1000000})
            self.assertEqual(c["cost"], 0.0)
            self.assertIn("claude-opus-4-8", c["unpriced"])

    def test_zero_configured_price_reads_as_unpriced(self) -> None:
        # MINOR-3: $0 is indistinguishable from "could not price"; treat it as UNPRICED.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir(parents=True)
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text("pricing:\n  opus: 0\n")
            self.assertIsNone(tel.model_price(d, "claude-opus-4-8"))

    def test_foreign_model_containing_a_family_string_is_not_mispriced(self) -> None:
        # MINOR-1: the defaults are Claude rates; a non-Claude model must not inherit one by substring.
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tel._model_family("gpt-opus-mini"), "gpt-opus-mini")
            self.assertIsNone(tel.model_price(d, "gpt-opus-mini"))
            self.assertEqual(tel._model_family("claude-opus-4-8"), "opus")  # a real Claude model still keys


if __name__ == "__main__":
    unittest.main()
