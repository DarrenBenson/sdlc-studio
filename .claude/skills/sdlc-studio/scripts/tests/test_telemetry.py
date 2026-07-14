"""Unit tests for telemetry.py - run telemetry recorder (CR0050)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "telemetry.py"


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

    def test_writes_to_gitignored_state_dir(self) -> None:
        # Must land under sdlc-studio/.local/ (the gitignored state dir), not repo-root .local/.
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "X"})
            self.assertTrue((Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl").exists())
            self.assertFalse((Path(d) / ".local" / "telemetry.jsonl").exists())

    def test_unknown_field_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rec = tel.record(d, {"id": "U1", "secret": "hunter2", "cwd": "/x"})
            self.assertEqual(rec, {"id": "U1"})  # only whitelisted FIELDS are written
            self.assertNotIn("hunter2", (Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl").read_text())

    def test_read_all_skips_malformed_lines(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tel.record(d, {"id": "good"})
            p = Path(d) / "sdlc-studio" / ".local" / "telemetry.jsonl"
            with p.open("a", encoding="utf-8") as fh:
                fh.write("{ not json\n\n")
            tel.record(d, {"id": "good2"})
            self.assertEqual([r["id"] for r in tel.read_all(d)], ["good", "good2"])

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


if __name__ == "__main__":
    unittest.main()
