"""Unit tests for transition.py - status transition + index/epic cascade (CR0042).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tr = _load("transition", "transition.py")
rc = _load("reconcile", "reconcile.py")


def _repo(root: Path) -> Path:
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    (sd / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
        "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n", encoding="utf-8")
    (sd / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Ready | 1 |\n| In Progress | 0 |\n| Done | 0 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
    ed = root / "sdlc-studio" / "epics"
    ed.mkdir(parents=True)
    (ed / "EP0001-e.md").write_text(
        "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
        "- [ ] [US0001: s](../stories/US0001-x.md)\n", encoding="utf-8")
    return root


def _read(root, *parts):
    return (root.joinpath("sdlc-studio", *parts)).read_text(encoding="utf-8")


class TransitionTests(unittest.TestCase):
    def test_sets_status_syncs_index_and_ticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual((res["from"], res["to"]), ("Ready", "Done"))
            self.assertIn("> **Status:** Done", _read(root, "stories", "US0001-x.md"))
            idx = _read(root, "stories", "_index.md")
            self.assertIn("| [US0001](US0001-x.md) | s | Done |", idx)   # row synced
            self.assertIn("| Done | 1 |", idx)                          # counts recomputed
            self.assertIn("| Ready | 0 |", idx)
            self.assertIn("- [x] [US0001: s]", _read(root, "epics", "EP0001-e.md"))  # epic ticked
            self.assertEqual(res["epic"], "EP0001")
            self.assertEqual(rc.detect_type("story", root)["drift"], [])  # 0 drift after

    def test_reopen_unticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            tr.transition(root, "US0001", "Done")
            tr.transition(root, "US0001", "In Progress")
            self.assertIn("- [ ] [US0001: s]", _read(root, "epics", "EP0001-e.md"))
            self.assertIn("> **Status:** In Progress", _read(root, "stories", "US0001-x.md"))
            self.assertEqual(rc.detect_type("story", root)["drift"], [])

    def test_invalid_status_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Frozen")

    def test_unknown_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US9099", "Done")

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before_story = _read(root, "stories", "US0001-x.md")
            before_idx = _read(root, "stories", "_index.md")
            before_epic = _read(root, "epics", "EP0001-e.md")
            res = tr.transition(root, "US0001", "Done", dry_run=True)
            self.assertEqual(res["to"], "Done")
            self.assertEqual(_read(root, "stories", "US0001-x.md"), before_story)
            self.assertEqual(_read(root, "stories", "_index.md"), before_idx)
            self.assertEqual(_read(root, "epics", "EP0001-e.md"), before_epic)

    def test_inline_status_field_preserved(self) -> None:
        # House inline `· **Status:** X · **Epic:** Y` form: only the Status value changes.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text("# US0001: s\n\n> **Status:** Ready · **Epic:** EP0001 · **Points:** 3\n\n"
                          "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
                          encoding="utf-8")
            tr.transition(root, "US0001", "Done")
            line = next(ln for ln in sp.read_text(encoding="utf-8").splitlines() if "Status" in ln)
            self.assertIn("**Status:** Done", line)
            self.assertIn("**Epic:** EP0001", line)   # neighbours intact
            self.assertIn("**Points:** 3", line)


class HonestSyncTests(unittest.TestCase):
    """index_synced reflects the real post-transition state (critic CR0042)."""

    def test_archived_row_reports_not_synced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
                "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n",
                encoding="utf-8")  # empty active table - the row lives in archive
            ad = sd / "archive" / "r1"
            ad.mkdir(parents=True)
            (ad / "story.md").write_text(
                "# story archive - r1\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](../../US0001-x.md) | s | Ready |\n", encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")
            self.assertFalse(res["index_synced"])      # archive row not synced - honest
            self.assertIsNotNone(res["warning"])

    def test_status_without_summary_row_reports_not_synced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Status:** Ready\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")  # no Done summary row
            res = tr.transition(root, "US0001", "Done")
            self.assertFalse(res["index_synced"])

    def test_no_status_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Epic:** EP0001\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_non_story_type_no_epic_cascade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text("# CR-0001: c\n\n> **Status:** Proposed\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n"
                "| Complete | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0001](CR0001-x.md) | c | Proposed |\n", encoding="utf-8")
            res = tr.transition(root, "CR0001", "Complete")
            self.assertTrue(res["index_synced"])
            self.assertIsNone(res["epic"])
            self.assertEqual(rc.detect_type("cr", root)["drift"], [])

    def test_epic_absent_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            # point the story at a non-existent epic
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "[EP0001: e](../epics/EP0001-e.md)", "[EP0099: gone](../epics/EP0099-gone.md)"),
                encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")  # must not crash
            self.assertIsNone(res["epic"])
            self.assertTrue(res["index_synced"])


if __name__ == "__main__":
    unittest.main()
