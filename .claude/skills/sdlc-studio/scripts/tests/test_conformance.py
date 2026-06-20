"""Unit tests for conformance.py (RED first - the script does not exist yet).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "conformance.py"


def _load():
    spec = importlib.util.spec_from_file_location("conformance", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conformance"] = mod
    spec.loader.exec_module(mod)
    return mod


def _story(root, num, *, epic=True, ac=True, verify=True, status="Ready", verified="yes"):
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# US{num:04d}: sample", "", f"> **Status:** {status}"]
    if epic:
        lines.append("> **Epic:** [EP0001: x](../epics/EP0001-x.md)")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing"]
        if verify:
            lines.append("- **Verify:** shell echo ok")
        if status == "Done":
            lines.append(f"- **Verified:** {verified} (2026-01-01)")
    (d / f"US{num:04d}-sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _units(root):
    return {u["id"]: u for u in _load().detect_conformance(root)["units"]}


class StageTests(unittest.TestCase):
    def test_full_story_all_stages_true(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            u = _units(root)["US0001"]
            self.assertTrue(u["conformant"])
            self.assertEqual(u["missing"], [])
            self.assertTrue(all(u["stages"][s] for s in ("decomposed", "specified", "verifiable")))

    def test_missing_stage_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("decomposed", u["missing"])

    def test_done_must_be_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="no")
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("verified", u["missing"])


class CliTests(unittest.TestCase):
    def test_exit_and_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            _story(root, 2, epic=False)
            mod = _load()
            rc = mod.main(["check", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 1)  # US0002 is non-conformant
            data = mod.detect_conformance(root)
            self.assertIn("units", data)
            self.assertEqual(set(data["summary"]), {"total", "conformant", "nonconformant"})


if __name__ == "__main__":
    unittest.main()
