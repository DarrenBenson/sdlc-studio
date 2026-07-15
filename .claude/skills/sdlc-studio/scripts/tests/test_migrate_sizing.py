"""Tests for the RFC0038 sizing migration (migrate_v3.py sizing) - EP0037 / RFC0040.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


migrate_v3 = _load("migrate_v3")


def _w(root: Path, rel: str, text: str) -> None:
    p = root / "sdlc-studio" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class SizingConversionTests(unittest.TestCase):
    """US0134: deterministic conversions for a request/container."""

    def test_effort_becomes_size_for_a_cr(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0001-x.md",
               "# CR-0001: X\n\n> **Status:** Approved\n> **Effort:** M\n")
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertEqual(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text()), "M")
            self.assertEqual([c["id"] for c in res["converted"]], ["CR0001"])

    def test_pointed_cr_gets_size_from_the_point_band(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0002-y.md",
               "# CR-0002: Y\n\n> **Status:** Proposed\n> **Points:** 5\n")   # 5 -> M
            migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertEqual(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0002-y.md").read_text()), "M")

    def test_already_sized_is_skipped_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0003-z.md",
               "# CR-0003: Z\n\n> **Status:** Approved\n> **Size:** L\n> **Effort:** S\n")
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertEqual(res["converted"], [])                 # already has Size
            self.assertEqual(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0003-z.md").read_text()), "L")

    def test_status_less_artefact_is_needs_manual_not_converted(self) -> None:
        # review finding: a convertible cr with NO Status line cannot be wired (the Size write
        # no-ops), so it must be reported as needs_manual, never counted as converted.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0005-m.md", "# CR-0005: M\n\n> **Effort:** M\n")
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertEqual(res["converted"], [])
            self.assertIn("CR0005", [n["id"] for n in res["needs_manual"]])
            self.assertIsNone(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0005-m.md").read_text()))

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0004-a.md",
               "# CR-0004: A\n\n> **Status:** Approved\n> **Effort:** M\n")
            res = migrate_v3.migrate_sizing(root, dry_run=True)
            self.assertEqual([c["id"] for c in res["converted"]], ["CR0004"])   # reported
            self.assertIsNone(sdlc_md.read_size(                                 # but not written
                (root / "sdlc-studio" / "change-requests" / "CR0004-a.md").read_text()))


class SizingReportTests(unittest.TestCase):
    """US0135: what cannot be converted safely is reported, never guessed."""

    def test_story_bug_with_effort_needs_resize_not_converted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "bugs/BG0001-b.md",
               "# BG0001: b\n\n> **Status:** Open\n> **Effort:** S\n> **Severity:** Low\n")
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertIn("BG0001", [n["id"] for n in res["needs_resize"]])
            # NOT auto-converted: Effort has no honest Points map
            self.assertIsNone(sdlc_md.read_points(
                (root / "sdlc-studio" / "bugs" / "BG0001-b.md").read_text()))
            self.assertIsNone(sdlc_md.read_size(
                (root / "sdlc-studio" / "bugs" / "BG0001-b.md").read_text()))

    def test_a_pointed_bug_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "bugs/BG0002-c.md",
               "# BG0002: c\n\n> **Status:** Open\n> **Points:** 2\n> **Severity:** Low\n")
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertEqual(res["needs_resize"], [])

    def test_accepted_childless_request_needs_refine(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "change-requests/CR0010-x.md",
               "# CR-0010: X\n\n> **Status:** Approved\n> **Size:** M\n")   # accepted, childless
            _w(root, "change-requests/CR0011-y.md",
               "# CR-0011: Y\n\n> **Status:** Proposed\n> **Size:** M\n")   # intake - not flagged
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            refine_ids = [n["id"] for n in res["needs_refine"]]
            self.assertIn("CR0010", refine_ids)
            self.assertNotIn("CR0011", refine_ids)

    def test_accepted_childless_issue_needs_triage_not_refine(self) -> None:
        # An Issue is triaged, not refined: the report must steer it to the right ceremony.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "issues/IS0001-x.md",
               "# IS0001: X\n\n> **Status:** Triaging\n> **Size:** M\n")   # accepted, childless
            res = migrate_v3.migrate_sizing(root, dry_run=False)
            self.assertIn("IS0001", [n["id"] for n in res["needs_triage"]])
            self.assertNotIn("IS0001", [n["id"] for n in res["needs_refine"]])


if __name__ == "__main__":
    unittest.main()
