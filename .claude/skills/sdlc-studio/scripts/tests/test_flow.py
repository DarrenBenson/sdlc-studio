"""flow.py - deterministic flow metrics (cycle time, throughput, work-item age).

The instrument must be honest (LL0008): a unit whose dates cannot be resolved is
NAMED unmeasurable, never guessed; a pass never means "found nothing to measure".
"""
import datetime as dt
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT_PATH = pathlib.Path(__file__).resolve().parent.parent / "flow.py"
_spec = importlib.util.spec_from_file_location("flow", SCRIPT_PATH)
assert _spec and _spec.loader
flow = importlib.util.module_from_spec(_spec)
sys.modules["flow"] = flow
_spec.loader.exec_module(flow)


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


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


if __name__ == "__main__":
    unittest.main()
