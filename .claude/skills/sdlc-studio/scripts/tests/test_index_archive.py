"""Unit tests for the index-archive writer (US0040 / CR0125).

The writer is `archive.py` - the single archive path. `reconcile.py` keeps only the shared
read helper; its duplicate write path (a flat, pointerless `archive/_index.md`) is gone.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS / "lib"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


reconcile = _load("reconcile")
archive = _load("archive")
import sdlc_md  # noqa: E402  (on sys.path via lib)

INDEX = (
    "# Stories\n\n"
    "## Summary\n\n"
    "| Status | Count |\n| --- | --- |\n"
    "| Draft | 1 |\n| In Progress | 1 |\n| Done | 1 |\n| Superseded | 1 |\n"
    "| **Total** | **4** |\n\n"
    "## All Stories\n\n"
    "| ID | Title | Status |\n| --- | --- | --- |\n"
    "| [US0001](US0001-a.md) | A | Draft |\n"
    "| [US0002](US0002-b.md) | B | In Progress |\n"
    "| [US0003](US0003-c.md) | C | Done |\n"
    "| [US0004](US0004-d.md) | D | Superseded |\n"
)


def _fixture(root: Path, index: str = INDEX) -> Path:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    for sid, st in [("US0001", "Draft"), ("US0002", "In Progress"),
                    ("US0003", "Done"), ("US0004", "Superseded")]:
        slug = {"US0001": "a", "US0002": "b", "US0003": "c", "US0004": "d"}[sid]
        (d / f"{sid}-{slug}.md").write_text(
            f"# {sid}: t\n\n> **Status:** {st}\n", encoding="utf-8")
    (d / "_index.md").write_text(index, encoding="utf-8")
    return d


class TerminalVocabTests(unittest.TestCase):
    def test_terminal_status_from_vocab(self) -> None:
        # terminal sets are vocab-derived, not hardcoded at call sites
        self.assertEqual(sdlc_md.terminal_statuses("story"),
                         {"Done", "Won't Implement", "Superseded"})
        self.assertTrue(sdlc_md.is_terminal_status("story", "Done"))
        self.assertFalse(sdlc_md.is_terminal_status("story", "Draft"))
        self.assertFalse(sdlc_md.is_terminal_status("story", "Blocked"))  # re-activatable
        self.assertTrue(sdlc_md.is_terminal_status("cr", "Complete"))
        self.assertFalse(sdlc_md.is_terminal_status("cr", "Proposed"))
        # a CR "Built" is not a default-vocab status here, so it is never terminal (stays active)
        self.assertFalse(sdlc_md.is_terminal_status("cr", "Built"))


class WriterTests(unittest.TestCase):
    def test_index_archive_writer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = _fixture(root)
            res = archive.archive(root, "story", "r1")
            self.assertEqual(res["count"], 2)
            self.assertCountEqual(res["archived"], ["US0003", "US0004"])
            live = (sd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("US0001", live)
            self.assertNotIn("US0003-c.md", live)  # terminal row gone from live
            self.assertNotIn("US0004-d.md", live)
            self.assertIn("| **Total** | **4** |", live)  # census union keeps the total whole
            # the live index points at the release it was archived into (the range bullet)
            self.assertIn("- **r1** (US0003-US0004, 2 archived) -> "
                          "sdlc-studio/stories/archive/r1/story.md", live)
            arch = (sd / "archive" / "r1" / "story.md").read_text(encoding="utf-8")
            self.assertIn("US0003", arch)
            self.assertIn("US0004", arch)
            # idempotent: a second run moves nothing and leaves the live index byte-identical
            before = (sd / "_index.md").read_text(encoding="utf-8")
            res2 = archive.archive(root, "story", "r1")
            self.assertEqual(res2["count"], 0)
            self.assertEqual((sd / "_index.md").read_text(encoding="utf-8"), before)

    def test_index_archive_dryrun_and_unknown_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = _fixture(root)
            before = (sd / "_index.md").read_text(encoding="utf-8")
            # dry-run writes nothing
            res = archive.archive(root, "story", "r1", dry_run=True)
            self.assertEqual(res["count"], 2)
            self.assertEqual((sd / "_index.md").read_text(encoding="utf-8"), before)
            self.assertFalse((sd / "archive").exists())
            # a row whose status is not in the vocab is never archived - it stays live
            bad = before.replace("| A | Draft |", "| A | Bogus |")
            (sd / "_index.md").write_text(bad, encoding="utf-8")
            res = archive.archive(root, "story", "r1")
            self.assertCountEqual(res["archived"], ["US0003", "US0004"])
            self.assertIn("| [US0001](US0001-a.md) | A | Bogus |",
                          (sd / "_index.md").read_text(encoding="utf-8"))

    def test_index_archive_reconcile_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])
            archive.archive(root, "story", "r1")
            # census still complete (archived rows unioned by parse_index), summary intact
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])


if __name__ == "__main__":
    unittest.main()
