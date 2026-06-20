"""Unit tests for archive.py - index archival (RFC0012 WS3) + the census union (WS2).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "archive.py"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, SCRIPT.parent / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


arc = _load("archive", "archive.py")
rc = _load("reconcile", "reconcile.py")


def _repo(root: Path) -> Path:
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    for num, st in [(1, "Done"), (2, "Ready"), (3, "Done")]:
        (sd / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {st}\n"
            f"> **Epic:** [EP0001](../epics/EP0001-x.md)\n", encoding="utf-8")
    (sd / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Done | 2 |\n| Ready | 1 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Done |\n"
        "| [US0002](US0002-x.md) | s | Ready |\n"
        "| [US0003](US0003-x.md) | s | Done |\n", encoding="utf-8")
    return root


def _idx(root: Path) -> str:
    return (root / "sdlc-studio" / "stories" / "_index.md").read_text(encoding="utf-8")


class ArchiveTests(unittest.TestCase):
    def test_moves_terminal_rows_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = arc.archive(root, "story", "r1")
            self.assertEqual(sorted(res["archived"]), ["US0001", "US0003"])
            self.assertEqual(res["count"], 2)
            idx = _idx(root)
            self.assertNotIn("US0001-x.md) | s | Done", idx)   # moved out of active
            self.assertNotIn("US0003-x.md) | s | Done", idx)
            self.assertIn("US0002", idx)                        # active row stays
            self.assertIn("- **r1**", idx)                      # release pointer added
            arch = (root / "sdlc-studio" / "stories" / "archive" / "r1" / "story.md").read_text("utf-8")
            self.assertIn("US0001", arch)
            self.assertIn("US0003", arch)

    def test_census_correct_after_archive(self) -> None:
        # THE risk: archived files must not read as missing-row, and counts must hold.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            arc.archive(root, "story", "r1")
            drift = rc.detect_type("story", root)["drift"]
            self.assertEqual(drift, [], f"expected 0 drift after archive, got {drift}")
            rows = rc.parse_index("story", root)["rows"]
            self.assertEqual(set(rows), {"US0001", "US0002", "US0003"})  # all still counted

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before = _idx(root)
            res = arc.archive(root, "story", "r1", dry_run=True)
            self.assertEqual(res["count"], 2)
            self.assertEqual(_idx(root), before)
            self.assertFalse((root / "sdlc-studio" / "stories" / "archive").exists())

    def test_idempotent_second_run_noop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            arc.archive(root, "story", "r1")
            res2 = arc.archive(root, "story", "r1")  # nothing terminal left active
            self.assertEqual(res2["count"], 0)
            self.assertEqual(rc.detect_type("story", root)["drift"], [])

    def test_unknown_type_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                arc.archive(Path(d), "persona", "r1")

    def test_picks_master_table_not_secondary(self) -> None:
        # A secondary status table must not be selected/archived (the id-column guard).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            for num, st in [(1, "Done"), (2, "Done"), (3, "Ready")]:
                (sd / f"US{num:04d}-x.md").write_text(
                    f"# US{num:04d}: s\n\n> **Status:** {st}\n"
                    "> **Epic:** [EP0001](../epics/EP0001-x.md)\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 2 |\n| Ready | 1 |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | s | Done |\n| [US0002](US0002-x.md) | s | Done |\n"
                "| [US0003](US0003-x.md) | s | Ready |\n\n"
                "## Recently shipped\n\n| Note | Ref | Status |\n| --- | --- | --- |\n"
                "| fast | US0001 | Done |\n| fast | US0002 | Done |\n", encoding="utf-8")
            res = arc.archive(root, "story", "r1")
            self.assertEqual(sorted(res["archived"]), ["US0001", "US0002"])  # from MASTER
            idx = _idx(root)
            self.assertIn("| fast | US0001 | Done |", idx)   # secondary table untouched
            self.assertEqual(rc.detect_type("story", root)["drift"], [])

    def test_second_release_and_new_active(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            arc.archive(root, "story", "r1")  # US0001, US0003 (Done) -> archived
            # a new Done story arrives, then a second archive release
            sd = root / "sdlc-studio" / "stories"
            (sd / "US0004-x.md").write_text(
                "# US0004: s\n\n> **Status:** Done\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n",
                encoding="utf-8")
            lines = _idx(root).splitlines()
            hi = next(i for i, ln in enumerate(lines) if ln.strip().startswith("| ID |"))
            lines.insert(hi + 2, "| [US0004](US0004-x.md) | s | Done |")
            (sd / "_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            arc.archive(root, "story", "r2")
            self.assertEqual(rc.detect_type("story", root)["drift"], [])  # census still clean
            rows = rc.parse_index("story", root)["rows"]
            self.assertEqual(set(rows), {"US0001", "US0002", "US0003", "US0004"})

    def test_apply_idempotent_after_archive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            arc.archive(root, "story", "r1")
            before = _idx(root)
            res = rc.apply_type("story", root)  # must not move/dup/rewrite anything
            self.assertEqual(res["changes"], [])
            self.assertFalse(res["counts_updated"])
            self.assertEqual(_idx(root), before)


if __name__ == "__main__":
    unittest.main()
