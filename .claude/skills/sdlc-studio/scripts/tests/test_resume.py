"""Unit tests for resume.py - epic implement --resume (CR0007). RED first."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "resume.py"


def _load():
    spec = importlib.util.spec_from_file_location("resume", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["resume"] = mod
    spec.loader.exec_module(mod)
    return mod


def _story(root, num, status, epic="EP0001"):
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-x.md").write_text(
        f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Epic:** [link](../epics/{epic}-x.md)\n",
        encoding="utf-8")


class ResumePointTests(unittest.TestCase):
    def test_first_non_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Done")
            _story(root, 3, "Ready")
            _story(root, 4, "Ready")
            self.assertEqual(_load().resume_point(root, "EP0001"), "US0003")

    def test_all_done_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Done")
            self.assertIsNone(_load().resume_point(root, "EP0001"))

    def test_only_target_epic_counted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done", epic="EP0001")
            _story(root, 2, "Ready", epic="EP0002")   # other epic
            _story(root, 3, "Ready", epic="EP0001")
            self.assertEqual(_load().resume_point(root, "EP0001"), "US0003")

    def test_skips_terminal_statuses(self) -> None:
        # Superseded / Won't Implement / Deferred are terminal - never a resume point.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Superseded")
            _story(root, 3, "Ready")
            self.assertEqual(_load().resume_point(root, "EP0001"), "US0003")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Won't Implement")
            _story(root, 3, "Deferred")
            self.assertIsNone(_load().resume_point(root, "EP0001"))

    def test_primary_epic_id_only(self) -> None:
        # A "(was EP0002)" annotation must not pull the story into EP0002's run.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0009-x.md").write_text(
                "# US0009: s\n\n> **Status:** Ready\n> **Epic:** EP0001 (was EP0002)\n", encoding="utf-8")
            self.assertEqual(_load().resume_point(root, "EP0001"), "US0009")
            self.assertIsNone(_load().resume_point(root, "EP0002"))


class StateTests(unittest.TestCase):
    def test_write_state_persists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "In Progress")
            mod = _load()
            state, path = mod.write_state(root, "EP0001")
            self.assertEqual(state["resume_at"], "US0002")
            self.assertFalse(state["complete"])
            self.assertEqual(len(state["stories"]), 2)
            on_disk = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(on_disk["resume_at"], "US0002")

    def test_cli_resume(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Ready")
            self.assertEqual(_load().main(["resume", "--epic", "EP0001", "--root", str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
