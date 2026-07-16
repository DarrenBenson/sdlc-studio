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
