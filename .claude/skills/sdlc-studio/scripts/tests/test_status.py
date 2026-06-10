"""Unit tests for status.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "status.py"
_spec = importlib.util.spec_from_file_location("status", SCRIPT_PATH)
assert _spec and _spec.loader
status = importlib.util.module_from_spec(_spec)
sys.modules["status"] = status
_spec.loader.exec_module(status)


def _story(root: Path, num: int, st: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-x.md").write_text(f"# S{num}\n\n> **Status:** {st}\n", encoding="utf-8")


class CensusTests(unittest.TestCase):
    def test_count_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Done")
            _story(root, 3, "In Progress")
            census = status.count_by_status("story", root)
            self.assertEqual(census["total"], 3)
            self.assertEqual(census["by_status"]["Done"], 2)

    def test_decorated_status_collapses_to_canonical(self) -> None:
        # `Done (v2.66.0) · **CR:** CR-0088` must tally under `Done`, not as a
        # distinct bucket, so done-percentages stay correct.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done (v2.66.0) · **CR:** CR-0088")
            _story(root, 2, "Done")
            census = status.count_by_status("story", root)
            self.assertEqual(census["total"], 2)
            self.assertEqual(census["by_status"], {"Done": 2})

    def test_pct_done(self) -> None:
        census = {"total": 4, "by_status": {"Done": 1, "Draft": 3}}
        self.assertEqual(status._pct_done(census, ("Done",)), 25)
        self.assertEqual(status._pct_done({"total": 0, "by_status": {}}, ("Done",)), 0)


class GatherTests(unittest.TestCase):
    def test_gather_reports_artifacts_and_docs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            (root / "sdlc-studio" / "prd.md").write_text("# PRD\n", encoding="utf-8")
            data = status.gather(root)
            self.assertTrue(data["requirements"]["prd"])
            self.assertFalse(data["code"]["trd"])
            self.assertEqual(data["requirements"]["stories"]["total"], 1)
            self.assertEqual(data["requirements"]["stories_done_pct"], 100)


class HintTests(unittest.TestCase):
    def test_hint_no_prd_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            data = status.gather(Path(d))
            hint = status.compute_hint(data, Path(d))
            self.assertIn("prd", hint["next_command"])

    def test_hint_seeded_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = root / "sdlc-studio"
            base.mkdir(parents=True)
            for name in ("prd.md", "trd.md", "tsd.md", "personas.md"):
                (base / name).write_text("# x\n", encoding="utf-8")
            (base / "epics").mkdir()
            (base / "epics" / "EP0001-x.md").write_text("# E\n\n> **Status:** Done\n", encoding="utf-8")
            _story(root, 1, "Done")
            hint = status.compute_hint(status.gather(root), root)
            self.assertIn("story", hint["next_command"])


if __name__ == "__main__":
    unittest.main()
