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
            self.assertEqual(rec, {"id": "US0001", "type": "story", "iterations": 3})
            self.assertNotIn("tokens", rec)

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
            self.assertEqual(rec, {"id": "U1"})  # only whitelisted FIELDS are written
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
            rc = tel.main(["forecast", "--id", "CR0009", "--tokens", "67400", "--seed", "29",
                           "--base", "50000", "--per-cognitive", "600", "--root", d])
            self.assertEqual(rc, 0)
            got = tel.forecasts(d)["CR0009"]
            self.assertEqual(got["tokens"], 67_400)
            self.assertEqual(got["constants"]["TOKENS_PER_COGNITIVE"], 600)


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


if __name__ == "__main__":
    unittest.main()
