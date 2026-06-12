"""Unit tests for lessons.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "lessons.py"
_spec = importlib.util.spec_from_file_location("lessons", SCRIPT_PATH)
assert _spec and _spec.loader
lessons = importlib.util.module_from_spec(_spec)
sys.modules["lessons"] = lessons
_spec.loader.exec_module(lessons)

TEMPLATE = """<!--
Template: Cross-project lesson learned
-->
---
id: LL{NNNN}
title: {{short title}}
tags: [{{e.g. reconcile, schema}}]
added: {{date}}
origin: {{project that surfaced it}}
---

**Lesson.** {{the generalisable rule}}

**Why / what it cost.** {{the failure that taught it}}

**How to apply.** {{the concrete check}}

**Generalises to.** {{when to recall it}}
"""

INDEX = """# Cross-Project Lessons-Learned Registry

## All Lessons

| ID | Title | Tags |
| --- | --- | --- |
| [LL0001](LL0001-census-first.md) | Reconcile from a file census | reconcile, drift |
| [LL0003](LL0003-schema-alignment.md) | Config-schema vs type alignment | schema, validation |

## Notes

- IDs are global and zero-padded.
"""


def _run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = lessons.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _make_skill_tier(root: Path) -> Path:
    d = root / "lessons"
    d.mkdir(parents=True)
    (d / "_template.md").write_text(TEMPLATE, encoding="utf-8")
    (d / "_index.md").write_text(INDEX, encoding="utf-8")
    (d / "LL0001-census-first.md").write_text("# LL0001\n", encoding="utf-8")
    (d / "LL0003-schema-alignment.md").write_text("# LL0003\n", encoding="utf-8")
    return d


class ProjectAddListTests(unittest.TestCase):
    def test_add_creates_file_and_allocates_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            rc, out, _ = _run(["add", "--title", "First lesson",
                               "--body", "Read hub files first.",
                               "--epic", "EP0001", "--wave", "2",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote L-0001", out)
            rc, out, _ = _run(["add", "--title", "Second lesson",
                               "--body", "Run typecheck after merge.",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote L-0002", out)
            text = Path(pfile).read_text(encoding="utf-8")
            self.assertIn("# Project Lessons", text)
            self.assertIn("**Last Updated:**", text)
            # Newest first: L-0002 appears before L-0001.
            self.assertLess(text.index("## L-0002"), text.index("## L-0001"))
            self.assertIn("- **Epic:** EP0001", text)
            self.assertIn("- **Wave:** 2", text)

    def test_list_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Older", "--body", "x", "--project-file", pfile])
            _run(["add", "--title", "Newer", "--body", "y", "--project-file", pfile])
            rc, out, _ = _run(["list", "--project-file", pfile, "--format", "json"])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual([e["title"] for e in data["lessons"]],
                             ["Newer", "Older"])

    def test_list_missing_file_is_friendly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out, _ = _run(["list", "--project-file", str(Path(d) / "none.md")])
            self.assertEqual(rc, 0)
            self.assertIn("No lessons recorded yet", out)


class GlobalAddTests(unittest.TestCase):
    def test_global_add_allocates_next_id_and_appends_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["add", "--global",
                               "--title", "Ship paperwork in the same commit",
                               "--body", "Docs travel with the change.",
                               "--tags", "process, docs",
                               "--origin", "demo-project",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote LL0004", out)
            new_file = ldir / "LL0004-ship-paperwork-in-the-same-commit.md"
            self.assertTrue(new_file.is_file())
            content = new_file.read_text(encoding="utf-8")
            self.assertIn("id: LL0004", content)
            self.assertIn("title: Ship paperwork in the same commit", content)
            self.assertIn("tags: [process, docs]", content)
            self.assertIn("origin: demo-project", content)
            self.assertIn("**Lesson.** Docs travel with the change.", content)
            self.assertNotIn("<!--", content)
            index = (ldir / "_index.md").read_text(encoding="utf-8")
            row = ("| [LL0004](LL0004-ship-paperwork-in-the-same-commit.md) "
                   "| Ship paperwork in the same commit | process, docs |")
            self.assertIn(row, index)
            # Row lands inside the table, before the Notes section.
            self.assertLess(index.index(row), index.index("## Notes"))

    def test_global_id_scans_files_for_max(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            # LL0003 exists on disk even though LL0002 is missing.
            self.assertEqual(lessons.next_global_id(ldir), "LL0004")


class PruneTests(unittest.TestCase):
    def _seed(self, pfile: str) -> None:
        for n, title in ((1, "From epic one"), (2, "From epic two"),
                         (3, "From epic three")):
            _run(["add", "--title", title, "--body", "x",
                  "--epic", f"EP{n:04d}", "--project-file", pfile])
        _run(["add", "--title", "No epic context", "--body", "x",
              "--project-file", pfile])

    def test_prune_older_drops_at_or_below(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            self._seed(pfile)
            rc, out, _ = _run(["prune", "--older", "EP0002",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("2 pruned, 2 kept", out)
            text = Path(pfile).read_text(encoding="utf-8")
            self.assertNotIn("From epic one", text)
            self.assertNotIn("From epic two", text)
            self.assertIn("From epic three", text)
            self.assertIn("No epic context", text)

    def test_prune_epic_drops_only_that_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            self._seed(pfile)
            rc, out, _ = _run(["prune", "--epic", "EP0002",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("From epic two", out)
            self.assertIn("1 pruned, 3 kept", out)
            text = Path(pfile).read_text(encoding="utf-8")
            self.assertIn("From epic one", text)
            self.assertNotIn("## L-0002", text)

    def test_prune_missing_file_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out, _ = _run(["prune", "--older", "EP0009",
                               "--project-file", str(Path(d) / "none.md")])
            self.assertEqual(rc, 0)
            self.assertIn("nothing to prune", out.lower())


class RecallTests(unittest.TestCase):
    def test_recall_no_args_prints_whole_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)
            self.assertIn("LL0003", out)
            self.assertIn("2 match(es)", out)

    def test_recall_tag_match_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--tags", "RECONCILE",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)
            self.assertNotIn("LL0003", out)

    def test_recall_query_matches_title(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--query", "census",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)
            self.assertNotIn("LL0003", out)

    def test_recall_all_searches_project_tier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Schema naming pitfall", "--body", "x",
                  "--tags", "schema", "--project-file", pfile])
            rc, out, _ = _run(["recall", "--tags", "schema", "--all",
                               "--lessons-dir", str(ldir),
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("LL0003", out)
            self.assertIn("Schema naming pitfall", out)
            self.assertIn("(project tier)", out)

    def test_recall_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--tags", "zzz-no-such-tag",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("No matching lessons", out)


if __name__ == "__main__":
    unittest.main()
