"""Unit tests for autosprint.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "autosprint.py"


def _load():
    spec = importlib.util.spec_from_file_location("autosprint", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["autosprint"] = mod
    spec.loader.exec_module(mod)
    return mod


def _bug(root, num, status="Open", severity="Medium"):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** {severity}\n", encoding="utf-8")


def _cr(root, num, status="Proposed", priority="Medium"):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Priority:** {priority}\n", encoding="utf-8")


class SelectTests(unittest.TestCase):
    def test_selects_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, status="Open")
            _bug(root, 2, status="Fixed")
            batch = _load().select_batch(root, "bug", "Open")
            ids = [b["id"] for b in batch]
            self.assertEqual(ids, ["BG0001"])
            self.assertEqual(batch[0]["status"], "Open")


class OrderTests(unittest.TestCase):
    def test_priority_order(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, severity="Low")
            _bug(root, 2, severity="Critical")
            _bug(root, 3, severity="Medium")
            batch = _load().select_batch(root, "bug", "Open", order="priority")
            self.assertEqual([b["priority"] for b in batch], ["Critical", "Medium", "Low"])


class CliTests(unittest.TestCase):
    def test_plan_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, priority="High")
            mod = _load()
            rc = mod.main(["plan", "--crs", "Proposed", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            data = mod.build_plan(root, "cr", "Proposed", "priority")
            self.assertIn("batch", data)
            self.assertEqual(data["count"], 1)


if __name__ == "__main__":
    unittest.main()
