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


def _record_verdict(root, unit, verdict="approve"):
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = m
    spec.loader.exec_module(m)
    m.record_verdict(root, unit, verdict)


class CritiqueStageTests(unittest.TestCase):
    def test_done_without_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")  # no critic verdict
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("critiqued", u["missing"])

    def test_done_with_approve_verdict_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            u = _units(root)["US0001"]
            self.assertNotIn("critiqued", u["missing"])
            self.assertTrue(u["stages"]["critiqued"])

    def test_done_with_reject_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "reject")
            u = _units(root)["US0001"]
            self.assertIn("critiqued", u["missing"])  # unresolved REJECT


class ReconciledStageTests(unittest.TestCase):
    def test_done_with_index_drift_not_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")  # isolate the reconciled stage
            # index says Ready while the file says Done -> status-mismatch
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n"
                "| [US0001](US0001-sample.md) | sample | Ready |\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])
            self.assertFalse(u["stages"]["reconciled"])

    def test_done_absent_from_index_not_reconciled(self) -> None:
        # A Done story missing from the index (missing-row) is not reconciled.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])


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
