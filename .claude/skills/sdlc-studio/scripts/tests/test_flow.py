"""flow.py - deterministic flow metrics (cycle time, throughput, work-item age).

The instrument must be honest (LL0008): a unit whose dates cannot be resolved is
NAMED unmeasurable, never guessed; a pass never means "found nothing to measure".
"""
import datetime as dt
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repos below
import loader  # noqa: E402 - the canonical way to import a script under test (CR0317)

SCRIPT_PATH = pathlib.Path(__file__).resolve().parent.parent / "flow.py"
flow = loader.load_script("flow")


def _git(cwd, *args):
    gitutil.git(list(args), cwd=cwd)


def _repo_with_story(tmp, status_flow):
    """A tiny git repo whose one story walks status_flow, one commit per status."""
    root = pathlib.Path(tmp)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True)
    f = d / "US0001-example.md"
    for i, status in enumerate(status_flow):
        f.write_text(
            f"# US0001: example\n\n> **Status:** {status}\n> **Created:** 2026-07-01\n"
            f"> **Points:** 3\n\n## Acceptance Criteria\n\n- [ ] x\n",
            encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", f"step {i}: {status}",
             "--date", f"2026-07-{10 + i:02d}T12:00:00")
    return root, f


class CycleTimeTests(unittest.TestCase):
    def test_cycle_days_arithmetic(self):
        self.assertEqual(
            flow.cycle_days(dt.date(2026, 7, 1), dt.date(2026, 7, 11)), 10)

    def test_terminal_date_resolved_from_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, f = _repo_with_story(tmp, ["Draft", "In Progress", "Done"])
            when, source = flow.terminal_date(root, f, "story", "Done")
            self.assertEqual(source, "git")
            self.assertEqual(when.date(), dt.date(2026, 7, 12))

    def test_terminal_unit_reports_cycle_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = _repo_with_story(tmp, ["Draft", "Done"])
            report = flow.compute(root)
            unit = report["units"]["US0001"]
            self.assertEqual(unit["cycle_days"], 10)  # Created 07-01 -> Done 07-11

    def test_prose_mention_does_not_poison_terminal_date(self):
        # A later commit QUOTING the status literal in body prose must not move the
        # resolved transition date (the -S pickaxe failure the critic confirmed live).
        with tempfile.TemporaryDirectory() as tmp:
            root, f = _repo_with_story(tmp, ["Draft", "Done"])
            text = f.read_text(encoding="utf-8")
            f.write_text(text + "\nA body note quoting **Status:** Done in prose.\n",
                         encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "later prose edit",
                 "--date", "2026-07-20T12:00:00")
            when, source = flow.terminal_date(root, f, "story", "Done")
            self.assertEqual(source, "git")
            self.assertEqual(when.date(), dt.date(2026, 7, 11))

    def test_closed_undelivered_unit_gets_no_flow_metric(self):
        # Superseded closes the unit WITHOUT delivering it: no cycle time, no age,
        # no throughput contribution - the honesty contract of DELIVERED_STATUS.
        with tempfile.TemporaryDirectory() as tmp:
            root, f = _repo_with_story(tmp, ["Draft", "Superseded"])
            report = flow.compute(root)
            unit = report["units"]["US0001"]
            self.assertTrue(unit.get("closed_undelivered"))
            self.assertNotIn("cycle_days", unit)
            self.assertNotIn("age_days", unit)
            self.assertEqual(report["throughput"]["weekly"], {})

    def test_unresolvable_dates_are_named_not_guessed(self):
        # no git history and no revision row -> the unit appears as unmeasurable BY NAME
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0002-x.md").write_text(
                "# US0002: x\n\n> **Status:** Done\n> **Points:** 2\n", encoding="utf-8")
            report = flow.compute(root)
            self.assertIn("US0002", report["unmeasurable"])
            self.assertNotIn("cycle_days", report["units"].get("US0002", {}))

    def test_revision_history_fallback_without_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0003-x.md").write_text(
                "# US0003: x\n\n> **Status:** Done\n> **Created:** 2026-07-01\n"
                "> **Points:** 2\n\n## Revision History\n\n| Date | Author | Change |\n"
                "| --- | --- | --- |\n| 2026-07-05 | t | Created |\n"
                "| 2026-07-09 | t | Done |\n", encoding="utf-8")
            report = flow.compute(root)
            unit = report["units"]["US0003"]
            self.assertEqual(unit["cycle_days"], 8)
            self.assertEqual(unit["cycle_source"], "revision")


class ThroughputTests(unittest.TestCase):
    def test_weekly_throughput_groups_by_iso_week(self):
        dates = [dt.date(2026, 7, 6), dt.date(2026, 7, 8),   # week 28
                 dt.date(2026, 7, 13)]                        # week 29
        weekly = flow.weekly_throughput(dates)
        self.assertEqual(weekly["2026-W28"], 2)
        self.assertEqual(weekly["2026-W29"], 1)

    def test_compute_reports_throughput_with_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = _repo_with_story(tmp, ["Draft", "Done"])
            report = flow.compute(root)
            self.assertEqual(sum(report["throughput"]["weekly"].values()), 1)
            w = report["throughput"]["window"]
            self.assertEqual((w["from"], w["to"], w["weeks"]),
                             ("2026-07-11", "2026-07-11", 1))

    def test_window_weeks_counts_iso_weeks_spanned(self):
        # Sunday -> Monday is 1 day apart but spans 2 ISO weeks
        self.assertEqual(flow.weekly_throughput([dt.date(2026, 7, 12),
                                                 dt.date(2026, 7, 13)]),
                         {"2026-W28": 1, "2026-W29": 1})


class BlockedAgeTests(unittest.TestCase):
    """US0181: a Blocked unit's blocked-age is reported distinctly from its total age."""

    def test_blocked_unit_reports_blocked_age_distinct_from_total_age(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = _repo_with_story(tmp, ["Draft", "In Progress", "Blocked"])
            report = flow.compute(root, today=dt.date(2026, 7, 16))
            unit = report["units"]["US0001"]
            self.assertEqual(unit["age_days"], 15)      # Created 07-01
            self.assertEqual(unit["blocked_days"], 4)   # Blocked 07-12 (3rd commit)
            self.assertEqual(unit["blocked_source"], "git")

    def test_unresolvable_blocked_transition_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0005-x.md").write_text(
                "# US0005: x\n\n> **Status:** Blocked\n> **Created:** 2026-07-01\n"
                "> **Points:** 2\n", encoding="utf-8")
            report = flow.compute(root, today=dt.date(2026, 7, 16))
            unit = report["units"]["US0005"]
            self.assertEqual(unit["age_days"], 15)
            self.assertIn("unmeasurable", unit["blocked_age"])


class AgeingFlagTests(unittest.TestCase):
    """US0181: status flags an In Progress unit older than flow.ageing_days -
    off entirely when the config is absent (L-0043: gates on live workflows opt in)."""

    def _workspace(self, tmp, *, config_days=None, created="2026-07-01",
                   status="In Progress"):
        root = pathlib.Path(tmp)
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True)
        (d / "US0009-x.md").write_text(
            f"# US0009: x\n\n> **Status:** {status}\n> **Created:** {created}\n"
            "> **Points:** 2\n", encoding="utf-8")
        if config_days is not None:
            (root / "sdlc-studio" / ".config.yaml").write_text(
                f"flow:\n  ageing_days: {config_days}\n", encoding="utf-8")
        return root

    def test_ageing_flag_over_threshold_flagged_in_report_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._workspace(tmp, config_days=5)
            rep = flow.ageing_report(root, today=dt.date(2026, 7, 16))
            self.assertEqual([f[0] for f in rep["flagged"]], ["US0009"])
            import importlib.util as _ilu
            spec = _ilu.spec_from_file_location(
                "status", SCRIPT_PATH.parent / "status.py")
            status_mod = _ilu.module_from_spec(spec)
            sys.modules["status"] = status_mod
            spec.loader.exec_module(status_mod)
            adv = status_mod.ageing_advisory(root, today=dt.date(2026, 7, 16))
            self.assertIn("US0009", adv)
            self.assertIn("15d", adv)

    def test_ageing_flag_at_exact_threshold_is_quiet(self):
        # "older than" is strict: age == ageing_days does not flag (kills a >= mutant)
        with tempfile.TemporaryDirectory() as tmp:
            root = self._workspace(tmp, config_days=15)  # age is exactly 15 on 07-16
            rep = flow.ageing_report(root, today=dt.date(2026, 7, 16))
            self.assertEqual(rep["flagged"], [])

    def test_blocked_without_git_is_named_unresolvable_not_guessed(self):
        # the revision-row fallback is refused for a TRANSIENT status: a post-block
        # edit's row must never masquerade as the Blocked transition
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0006-x.md").write_text(
                "# US0006: x\n\n> **Status:** Blocked\n> **Created:** 2026-07-01\n"
                "> **Points:** 2\n\n## Revision History\n\n| Date | Author | Change |\n"
                "| --- | --- | --- |\n| 2026-07-14 | t | edited AFTER blocking |\n",
                encoding="utf-8")
            report = flow.compute(root, today=dt.date(2026, 7, 16))
            unit = report["units"]["US0006"]
            self.assertNotIn("blocked_days", unit)
            self.assertIn("unmeasurable", unit["blocked_age"])

    def test_ageing_flag_quiet_under_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._workspace(tmp, config_days=30)
            rep = flow.ageing_report(root, today=dt.date(2026, 7, 16))
            self.assertEqual(rep["flagged"], [])

    def test_ageing_flag_off_without_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._workspace(tmp)
            self.assertIsNone(flow.ageing_report(root, today=dt.date(2026, 7, 16)))


class MonteCarloTests(unittest.TestCase):
    """US0182: seeded, reproducible probabilistic completion forecast over measured
    weekly throughput. Zero-weeks INSIDE the window are real samples - dropping them
    is silent optimism."""

    SAMPLES = [2, 0, 3, 1, 0, 2, 4, 1]  # 8 measured weeks, mean ~1.6/week

    def test_monte_carlo_is_seeded_and_reproducible(self):
        a = flow.monte_carlo_forecast(self.SAMPLES, 10, seed=7,
                                      today=dt.date(2026, 7, 16))
        b = flow.monte_carlo_forecast(self.SAMPLES, 10, seed=7,
                                      today=dt.date(2026, 7, 16))
        self.assertEqual(a, b)
        self.assertEqual(set(a["confidence"]), {"50", "85", "95"})

    def test_monte_carlo_percentiles_are_ordered_dates(self):
        f = flow.monte_carlo_forecast(self.SAMPLES, 10, seed=7,
                                      today=dt.date(2026, 7, 16))
        d50 = dt.date.fromisoformat(f["confidence"]["50"])
        d85 = dt.date.fromisoformat(f["confidence"]["85"])
        d95 = dt.date.fromisoformat(f["confidence"]["95"])
        self.assertLessEqual(d50, d85)
        self.assertLessEqual(d85, d95)
        self.assertGreater(d50, dt.date(2026, 7, 16))

    def test_monte_carlo_zero_weeks_push_dates_out(self):
        # the same totals WITHOUT the zero weeks must forecast earlier - proving the
        # zero samples are genuinely in the distribution
        with_zeros = flow.monte_carlo_forecast(self.SAMPLES, 12, seed=7,
                                               today=dt.date(2026, 7, 16))
        without = flow.monte_carlo_forecast([s for s in self.SAMPLES if s], 12, seed=7,
                                            today=dt.date(2026, 7, 16))
        self.assertGreater(with_zeros["confidence"]["85"], without["confidence"]["85"])


class MinimumSampleTests(unittest.TestCase):
    """US0182: too little history is REFUSED with the sample size named - never a
    guessed date."""

    def test_refuses_under_minimum_weeks(self):
        f = flow.monte_carlo_forecast([2, 3], 10, seed=1, today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)
        self.assertIn("2 week(s)", f["refused"])
        self.assertNotIn("confidence", f)

    def test_refuses_when_confidence_rank_hits_the_horizon(self):
        # a batch the measured throughput cannot finish inside the simulation horizon
        # must REFUSE - a capped week count reported as a date is a truncation
        f = flow.monte_carlo_forecast([2, 0, 3, 1, 0, 2, 4, 1], 5000, seed=7,
                                      today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)
        self.assertIn("horizon", f["refused"])
        self.assertNotIn("confidence", f)

    def test_refuses_non_positive_batch(self):
        f = flow.monte_carlo_forecast([2, 0, 3, 1, 0], 0, seed=1,
                                      today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)

    def test_seed_parameter_is_live(self):
        # deterministic given the algorithm: two seeds must yield different dates
        # (a mutant hardwiring Random(0) collapses them to equal)
        a = flow.monte_carlo_forecast([9, 0, 0, 0, 1], 25, seed=1, sims=200,
                                      today=dt.date(2026, 7, 16))
        b = flow.monte_carlo_forecast([9, 0, 0, 0, 1], 25, seed=99, sims=200,
                                      today=dt.date(2026, 7, 16))
        self.assertNotEqual(a["confidence"], b["confidence"])

    def test_refuses_zero_throughput_history(self):
        f = flow.monte_carlo_forecast([0, 0, 0, 0, 0], 5, seed=1,
                                      today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)
        self.assertIn("zero", f["refused"].lower())

    def test_workspace_glue_refuses_short_window(self):
        # one delivered unit = a 1-week window < the 4-week minimum
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = _repo_with_story(tmp, ["Draft", "Done"])
            f = flow.forecast(root, 5, seed=1)
            self.assertIn("refused", f)
            self.assertIn("1 week(s)", f["refused"])

    def test_workspace_glue_fills_zero_weeks_in_the_window(self):
        # two deliveries ~6 ISO weeks apart: the sample set must span every week in
        # the window (gap weeks as zeros), not just the weeks with data - a
        # values-only mutant reports history_weeks 2 and forecasts optimistically
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _git(root, "init", "-q")
            _git(root, "config", "user.email", "t@t")
            _git(root, "config", "user.name", "t")
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            for sid, day in (("US0001", "2026-06-01"), ("US0002", "2026-07-10")):
                (d / f"{sid}-x.md").write_text(
                    f"# {sid}: x\n\n> **Status:** Done\n> **Created:** 2026-05-20\n"
                    f"> **Points:** 2\n", encoding="utf-8")
                _git(root, "add", "-A")
                _git(root, "commit", "-q", "-m", f"done {sid}",
                     "--date", f"{day}T12:00:00")
            f = flow.forecast(root, 3, seed=1, today=dt.date(2026, 7, 16))
            self.assertEqual(f["history_weeks"], 6)  # W23..W28 inclusive, zeros filled


class LeadTimeTests(unittest.TestCase):
    """flow.lead_times bucketing (used by deploy metrics): a commit exactly AT an event
    time belongs to that event and is never double-counted into the next."""

    def test_boundary_commit_counted_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _git(root, "init", "-q")
            _git(root, "config", "user.email", "t@t")
            _git(root, "config", "user.name", "t")
            (root / "a.txt").write_text("1", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "c1", "--date", "2026-07-05T10:00:00")
            events = [dt.datetime(2026, 7, 5, 10, 0), dt.datetime(2026, 7, 10, 10, 0)]
            leads = flow.lead_times(root, events)
            self.assertEqual(leads, [0.0])  # first event only; mutants (<, >=) break this

    def test_non_repo_root_refuses_rather_than_reading_enclosing_repo(self):
        # a plain subdirectory INSIDE a git repo must not inherit the enclosing
        # repo's history (git walks up from cwd - wrong-repo lead times look real)
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _git(root, "init", "-q")
            _git(root, "config", "user.email", "t@t")
            _git(root, "config", "user.name", "t")
            (root / "a.txt").write_text("1", encoding="utf-8")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "c1")
            sub = root / "workspace"
            sub.mkdir()
            self.assertIsNone(flow.commit_author_times(sub))
            self.assertEqual(len(flow.commit_author_times(root)), 1)


class AgeTests(unittest.TestCase):
    def test_non_terminal_unit_reports_age(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0004-x.md").write_text(
                "# US0004: x\n\n> **Status:** In Progress\n> **Created:** 2026-07-01\n"
                "> **Points:** 2\n", encoding="utf-8")
            report = flow.compute(root, today=dt.date(2026, 7, 16))
            self.assertEqual(report["units"]["US0004"]["age_days"], 15)

    def test_non_terminal_without_created_is_unmeasurable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            d = root / "sdlc-studio" / "bugs"
            d.mkdir(parents=True)
            (d / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** Open\n> **Points:** 2\n", encoding="utf-8")
            report = flow.compute(root, today=dt.date(2026, 7, 16))
            self.assertIn("BG0001", report["unmeasurable"])

    def test_terminal_unit_has_no_age(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = _repo_with_story(tmp, ["Draft", "Done"])
            report = flow.compute(root)
            self.assertNotIn("age_days", report["units"]["US0001"])


def _velocity_fixture(root: pathlib.Path, rows: list[str]) -> None:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    header = ("| Retro | Date | Units | Measured | Wall (s) |\n"
              "| --- | --- | --- | --- | --- |\n")
    (d / "VELOCITY.md").write_text(header + "\n".join(rows) + "\n", encoding="utf-8")


class DayBucketTests(unittest.TestCase):
    """CR0314: days replace ISO weeks as the calendar floor - an agent-speed project's
    median cycle time is 0 days, and a week bucket quantises the answer to uselessness."""

    def test_day_samples_include_zero_days(self):
        dates = [dt.date(2026, 7, 1), dt.date(2026, 7, 1), dt.date(2026, 7, 3)]
        self.assertEqual(flow.day_samples(dates), [2, 0, 1])

    def test_day_bucket_reports_day_precision_dates(self):
        samples = [1, 0, 2, 1, 0, 3, 1]  # 7 measured days
        f = flow.mc_bucket_forecast(samples, 6, bucket="day", seed=7,
                                    today=dt.date(2026, 7, 16))
        self.assertEqual(f["bucket"], "day")
        d50 = dt.date.fromisoformat(f["confidence"]["50"])
        d95 = dt.date.fromisoformat(f["confidence"]["95"])
        self.assertGreater(d50, dt.date(2026, 7, 16))
        self.assertLessEqual(d95, dt.date(2026, 7, 16) + dt.timedelta(days=60))
        self.assertLessEqual(d50, d95)

    def test_day_is_the_default_bucket_week_stays_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            self.assertEqual(flow.resolve_bucket(None, root), "day")
            self.assertEqual(flow.resolve_bucket("week", root), "week")

    def test_unknown_config_bucket_refused_not_guessed(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("config override reads .config.yaml (needs PyYAML)")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "flow:\n  forecast_bucket: fortnight\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                flow.resolve_bucket(None, root)

    def test_horizon_refusal_names_the_bucket(self):
        f = flow.monte_carlo_forecast([2, 0, 3, 1, 0, 2, 4, 1], 5000, seed=7,
                                      today=dt.date(2026, 7, 16))
        self.assertIn("weeks", f["refused"])   # not the vague "periods"
        g = flow.mc_bucket_forecast([0, 0, 0, 0, 0, 0, 1], 100000, bucket="day",
                                    seed=1, sims=50, today=dt.date(2026, 7, 16))
        self.assertIn("days", g["refused"])

    def test_config_can_prefer_week(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("config override reads .config.yaml (needs PyYAML)")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "flow:\n  forecast_bucket: week\n", encoding="utf-8")
            self.assertEqual(flow.resolve_bucket(None, root), "week")
            self.assertEqual(flow.resolve_bucket("day", root), "day")  # flag wins


class SprintDenominatorTests(unittest.TestCase):
    """CR0314: the primary denominator is the SPRINT-SESSION - measured per-sprint
    throughput from the velocity history, with hours at the measured elapsed median."""

    ROWS = ["| RETRO0001 | 2026-07-01 | 5 | 5 | 3600 |",
            "| RETRO0002 | 2026-07-02 | 5 | 4 | 7200 |",
            "| RETRO0003 | 2026-07-03 | 3 | 3 | 5400 |"]

    def test_sprint_forecast_samples_measured_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _velocity_fixture(root, self.ROWS)
            f = flow.sprint_forecast(root, 8, seed=7)
            self.assertEqual(f["bucket"], "sprint")
            self.assertEqual(f["history_sprints"], 3)
            self.assertGreaterEqual(f["confidence_sprints"]["50"], 2)   # 8 units at 3-5/sprint
            self.assertLessEqual(f["confidence_sprints"]["95"], 6)
            # hours = sprints x the measured median elapsed (5400s = 1.5h)
            self.assertAlmostEqual(f["median_sprint_hours"], 1.5)
            self.assertAlmostEqual(
                f["confidence_hours"]["50"], f["confidence_sprints"]["50"] * 1.5)

    def test_sprint_refusal_under_minimum_history_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _velocity_fixture(root, self.ROWS[:2])
            f = flow.sprint_forecast(root, 8, seed=7)
            self.assertIn("refused", f)
            self.assertIn("sprint", f["refused"])
            self.assertIn(str(flow.MC_MIN_SPRINTS), f["refused"])   # the minimum, named

    def test_unmeasured_hours_are_named_not_zeroed(self):
        rows = ["| RETRO0001 | 2026-07-01 | 5 | 5 | - |",
                "| RETRO0002 | 2026-07-02 | 5 | 4 | - |",
                "| RETRO0003 | 2026-07-03 | 3 | 3 | - |"]
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _velocity_fixture(root, rows)
            f = flow.sprint_forecast(root, 8, seed=7)
            self.assertIsNone(f["median_sprint_hours"])
            self.assertIsNone(f["confidence_hours"])
            self.assertIn("unmeasured", f["note"])


class BucketGuardTests(unittest.TestCase):
    """CR0314: the refusal guards (seeded, min-history, all-zero, non-positive,
    horizon) hold in EVERY bucket, not only the week one."""

    def test_day_min_history_refused(self):
        f = flow.mc_bucket_forecast([1, 2], 5, bucket="day", seed=1,
                                    today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)
        self.assertIn(str(flow.MC_MIN_DAYS), f["refused"])

    def test_day_all_zero_refused(self):
        f = flow.mc_bucket_forecast([0] * 10, 5, bucket="day", seed=1,
                                    today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)

    def test_day_non_positive_batch_refused(self):
        f = flow.mc_bucket_forecast([1, 0, 2, 1, 0, 3, 1], 0, bucket="day", seed=1,
                                    today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)

    def test_day_horizon_hit_refused_not_truncated(self):
        f = flow.mc_bucket_forecast([0, 0, 0, 0, 0, 0, 1], 100000, bucket="day",
                                    seed=1, sims=50, today=dt.date(2026, 7, 16))
        self.assertIn("refused", f)
        self.assertIn("horizon", f["refused"])

    def test_day_bucket_is_seeded_and_reproducible(self):
        samples = [1, 0, 2, 1, 0, 3, 1]
        a = flow.mc_bucket_forecast(samples, 6, bucket="day", seed=7,
                                    today=dt.date(2026, 7, 16))
        b = flow.mc_bucket_forecast(samples, 6, bucket="day", seed=7,
                                    today=dt.date(2026, 7, 16))
        self.assertEqual(a, b)

    def test_sprint_non_positive_and_all_zero_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _velocity_fixture(root, ["| RETRO0001 | 2026-07-01 | 0 | 0 | 3600 |",
                                     "| RETRO0002 | 2026-07-02 | 0 | 0 | 3600 |",
                                     "| RETRO0003 | 2026-07-03 | 0 | 0 | 3600 |"])
            self.assertIn("refused", flow.sprint_forecast(root, 0, seed=1))
            self.assertIn("refused", flow.sprint_forecast(root, 8, seed=1))


if __name__ == "__main__":
    unittest.main()
