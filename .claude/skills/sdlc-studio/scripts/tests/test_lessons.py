"""Unit tests for lessons.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import os
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

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


def _registry(d: Path) -> Path:
    """The registry files a skill-tier lessons directory must hold."""
    d.mkdir(parents=True, exist_ok=True)
    (d / "_template.md").write_text(TEMPLATE, encoding="utf-8")
    (d / "_index.md").write_text(INDEX, encoding="utf-8")
    (d / "LL0001-census-first.md").write_text("# LL0001\n", encoding="utf-8")
    (d / "LL0003-schema-alignment.md").write_text("# LL0003\n", encoding="utf-8")
    return d


def _make_skill_tier(root: Path, *, tracked: bool = True) -> Path:
    """A skill-tier lessons registry under `root`.

    `tracked=True` (the default) makes `root` a git work tree with the registry ADDED to
    the index, because a skill-tier write is only real when git actually version-controls
    the destination; `tracked=False` reproduces the untracked install the guard must refuse.
    """
    d = _registry(root / "lessons")
    if tracked:
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
    return d


def _make_source_checkout(root: Path) -> Path:
    """A git checkout shaped like the sdlc-studio SOURCE repo: the repo-only markers a
    release is cut from, plus the skill payload at its canonical path."""
    (root / "tools").mkdir(parents=True)
    (root / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (root / "tools" / "validate_skill.py").write_text("# guard\n", encoding="utf-8")
    d = _registry(root / ".claude" / "skills" / "sdlc-studio" / "lessons")
    gitutil.git(["init", "-q"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
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


class FixedDate:
    """Pin sdlc_md.now_date() for deterministic header/frontmatter assertions."""

    def __init__(self, date: str) -> None:
        self.date = date
        self._orig = None

    def __enter__(self) -> "FixedDate":
        self._orig = lessons.sdlc_md.now_date
        lessons.sdlc_md.now_date = lambda: self.date
        return self

    def __exit__(self, *exc) -> None:
        lessons.sdlc_md.now_date = self._orig


class ParseProjectLessonsTests(unittest.TestCase):
    def test_preamble_before_first_heading_is_ignored(self) -> None:
        text = ("preamble line\nignored too\n\n"
                "## L-0001: First\n\nbody one\n")
        entries = lessons.parse_project_lessons(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], "L-0001")
        self.assertEqual(entries[0]["body"], "body one")

    def test_fields_and_body_captured(self) -> None:
        text = ("## L-0001: Titled\n\n"
                "- **Epic:** EP0004\n- **Wave:** 3\nsome prose\n")
        e = lessons.parse_project_lessons(text)[0]
        self.assertEqual(e["fields"]["epic"], "EP0004")
        self.assertEqual(e["fields"]["wave"], "3")
        self.assertIn("some prose", e["body"])

    def test_field_keys_lowercased(self) -> None:
        text = "## L-0001: T\n\n- **TAGS:** schema, drift\n"
        e = lessons.parse_project_lessons(text)[0]
        self.assertIn("tags", e["fields"])
        self.assertEqual(e["fields"]["tags"], "schema, drift")

    def test_empty_text_yields_no_entries(self) -> None:
        self.assertEqual(lessons.parse_project_lessons(""), [])

    def test_malformed_file_does_not_crash(self) -> None:
        # Bullets and bold runs with no preceding heading must be tolerated.
        text = ("# Header only\n- **Epic:** EP0001\n"
                "**Lesson.** orphaned\n| not | a | table |\n")
        self.assertEqual(lessons.parse_project_lessons(text), [])


class ProjectHeaderTests(unittest.TestCase):
    def test_header_is_everything_before_first_entry(self) -> None:
        text = "# Project Lessons\n\nnotes\n\n## L-0001: First\nbody\n"
        self.assertEqual(lessons.project_header_of(text),
                         "# Project Lessons\n\nnotes\n")

    def test_no_entries_returns_whole_text(self) -> None:
        self.assertEqual(lessons.project_header_of("# Title\n\nbody\n"),
                         "# Title\n\nbody\n")

    def test_empty_text_returns_empty(self) -> None:
        self.assertEqual(lessons.project_header_of("   \n"), "")


class RefreshLastUpdatedTests(unittest.TestCase):
    def test_existing_marker_is_rewritten_to_today(self) -> None:
        with FixedDate("2026-01-15"):
            out = lessons.refresh_last_updated("# H\n\n**Last Updated:** 2020-01-01\n")
        self.assertIn("**Last Updated:** 2026-01-15", out)
        self.assertNotIn("2020-01-01", out)

    def test_missing_marker_left_unchanged(self) -> None:
        # NB: the docstring claims it adds the marker when absent; the code
        # only substitutes when present. This asserts the actual behaviour.
        with FixedDate("2026-01-15"):
            out = lessons.refresh_last_updated("# Header\n")
        self.assertEqual(out, "# Header\n")


class NextProjectIdTests(unittest.TestCase):
    def test_empty_starts_at_one(self) -> None:
        self.assertEqual(lessons.next_project_id([]), "L-0001")

    def test_uses_max_not_count_so_gaps_are_safe(self) -> None:
        entries = [{"id": "L-0001"}, {"id": "L-0005"}]
        self.assertEqual(lessons.next_project_id(entries), "L-0006")


class RenderEntryTests(unittest.TestCase):
    def test_renders_id_title_and_body(self) -> None:
        out = lessons.render_entry({"id": "L-0007", "title": "Cap", "body": "the body"})
        self.assertTrue(out.startswith("## L-0007: Cap"))
        self.assertIn("the body", out)
        self.assertTrue(out.endswith("\n"))

    def test_empty_body_omits_body(self) -> None:
        out = lessons.render_entry({"id": "L-0001", "title": "T", "body": ""})
        self.assertEqual(out, "## L-0001: T\n")


class ParseIndexRowsTests(unittest.TestCase):
    def test_missing_index_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(
                lessons.parse_index_rows(Path(d) / "_index.md"), [])

    def test_malformed_rows_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            idx = Path(d) / "_index.md"
            idx.write_text(
                "| ID | Title | Tags |\n| --- | --- | --- |\n"
                "| [LL0001](LL0001-a.md) | Good row | tag1, tag2 |\n"
                "| not-a-lesson-row | broken |\n"
                "| [LL0002](LL0002-b.md) | Second | tagx |\n",
                encoding="utf-8")
            rows = lessons.parse_index_rows(idx)
            self.assertEqual([r["id"] for r in rows], ["LL0001", "LL0002"])
            self.assertEqual(rows[0]["tags"], ["tag1", "tag2"])
            self.assertEqual(rows[0]["file"], "LL0001-a.md")


class RenderGlobalLessonTests(unittest.TestCase):
    def test_strips_leading_comment_and_fills_fields(self) -> None:
        out = lessons.render_global_lesson(
            TEMPLATE, "LL0009", "My Title", ["a", "b"], "Body here",
            "orig-proj", "2026-03-04")
        self.assertNotIn("<!--", out)
        self.assertIn("id: LL0009", out)
        self.assertIn("title: My Title", out)
        self.assertIn("tags: [a, b]", out)
        self.assertIn("added: 2026-03-04", out)
        self.assertIn("origin: orig-proj", out)
        self.assertIn("**Lesson.** Body here", out)

    def test_unfilled_placeholders_retained_for_author(self) -> None:
        out = lessons.render_global_lesson(
            TEMPLATE, "LL0009", "T", [], "B", "o", "2026-03-04")
        self.assertIn("{{the failure that taught it}}", out)
        self.assertIn("{{when to recall it}}", out)

    def test_template_without_comment_is_handled(self) -> None:
        tpl = ("id: LLxxxx\ntitle: T\ntags: []\nadded: D\norigin: O\n\n"
               "**Lesson.** placeholder\n")
        out = lessons.render_global_lesson(
            tpl, "LL0001", "Real Title", ["t"], "Real body", "o", "2026-01-01")
        self.assertIn("id: LL0001", out)
        self.assertIn("title: Real Title", out)
        self.assertIn("**Lesson.** Real body", out)


class AppendIndexRowTests(unittest.TestCase):
    def test_appends_after_separator_when_no_rows_yet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            idx = Path(d) / "_index.md"
            idx.write_text(
                "# X\n\n| ID | Title | Tags |\n| --- | --- | --- |\n",
                encoding="utf-8")
            lessons.append_index_row(idx, "LL0001", "LL0001-x.md", "Title", ["t1"])
            text = idx.read_text(encoding="utf-8")
            self.assertIn("| [LL0001](LL0001-x.md) | Title | t1 |", text)

    def test_no_table_raises_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            idx = Path(d) / "_index.md"
            idx.write_text("# X\n\njust prose, no table\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                lessons.append_index_row(idx, "LL0001", "f.md", "T", [])


class MatchesTests(unittest.TestCase):
    def test_tag_substring_match(self) -> None:
        self.assertTrue(lessons._matches("Title", ["reconcile"], ["recon"], None))

    def test_no_tag_match_fails(self) -> None:
        self.assertFalse(lessons._matches("Title", ["other"], ["recon"], None))

    def test_query_matches_tag_not_just_title(self) -> None:
        self.assertTrue(lessons._matches("Unrelated", ["drift"], [], "drif"))

    def test_query_and_tags_both_required(self) -> None:
        # tag matches but query does not -> overall no match.
        self.assertFalse(
            lessons._matches("Title", ["schema"], ["schema"], "nowhere"))

    def test_no_filters_matches_everything(self) -> None:
        self.assertTrue(lessons._matches("anything", [], [], None))


class CmdAddFormattingTests(unittest.TestCase):
    def test_tags_only_no_epic_or_wave(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            rc, _, _ = _run(["add", "--title", "Tagged", "--body", "the lesson",
                             "--tags", "a, b", "--project-file", pfile])
            self.assertEqual(rc, 0)
            text = Path(pfile).read_text(encoding="utf-8")
            self.assertIn("- **Tags:** a, b", text)
            self.assertNotIn("**Epic:**", text)
            self.assertNotIn("**Wave:**", text)
            self.assertIn("the lesson", text)

    def test_existing_header_preserved_on_append(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = Path(d) / "lessons.md"
            pfile.write_text(
                "# Project Lessons\n\nCustom note kept.\n\n"
                "## L-0001: Existing\n\nold body\n", encoding="utf-8")
            rc, out, _ = _run(["add", "--title", "Fresh", "--body", "new body",
                               "--project-file", str(pfile)])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote L-0002", out)
            text = pfile.read_text(encoding="utf-8")
            self.assertIn("Custom note kept.", text)
            self.assertLess(text.index("## L-0002"), text.index("## L-0001"))

    def test_wave_zero_is_recorded(self) -> None:
        # --wave uses `is not None`, so wave 0 must still be written.
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Zero wave", "--body", "x", "--wave", "0",
                  "--project-file", pfile])
            self.assertIn("- **Wave:** 0", Path(pfile).read_text(encoding="utf-8"))


class CmdAddGlobalErrorTests(unittest.TestCase):
    """A tracked destination whose registry is incomplete: each missing part reports itself."""

    def setUp(self) -> None:
        _requires_git(self)

    def test_missing_template_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = Path(d) / "lessons"
            ldir.mkdir()
            (ldir / "_index.md").write_text(INDEX, encoding="utf-8")
            gitutil.git(["init", "-q"], cwd=Path(d))
            rc, _, err = _run(["add", "--global", "--title", "T", "--body", "B",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 1)
            self.assertIn("template not found", err)

    def test_missing_index_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = Path(d) / "lessons"
            ldir.mkdir()
            (ldir / "_template.md").write_text(TEMPLATE, encoding="utf-8")
            gitutil.git(["init", "-q"], cwd=Path(d))
            rc, _, err = _run(["add", "--global", "--title", "T", "--body", "B",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 1)
            self.assertIn("index not found", err)

    def test_existing_higher_id_file_advances_allocation(self) -> None:
        # next_global_id scans LL files for the max, so an out-of-band file at a
        # higher number pushes the next id past it (no overwrite, no clash).
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            (ldir / "LL0009-orphan.md").write_text("existing\n", encoding="utf-8")
            rc, out, _ = _run(["add", "--global", "--title", "After orphan",
                               "--body", "B", "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote LL0010", out)
            self.assertEqual(
                (ldir / "LL0009-orphan.md").read_text(encoding="utf-8"),
                "existing\n")

    def test_global_add_uses_fixed_date(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            with FixedDate("2026-09-09"):
                rc, _, _ = _run(["add", "--global", "--title", "Dated",
                                 "--body", "B", "--origin", "proj",
                                 "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            content = (ldir / "LL0004-dated.md").read_text(encoding="utf-8")
            self.assertIn("added: 2026-09-09", content)


class CmdListGlobalTests(unittest.TestCase):
    def test_global_list_text(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["list", "--global", "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)
            self.assertIn("LL0003", out)
            self.assertIn("2 lesson(s)", out)

    def test_global_list_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["list", "--global", "--format", "json",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["tier"], "skill")
            self.assertEqual(data["count"], 2)
            self.assertEqual({r["id"] for r in data["lessons"]},
                             {"LL0001", "LL0003"})

    def test_global_list_empty_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = Path(d) / "lessons"
            ldir.mkdir()
            (ldir / "_index.md").write_text(
                "# Registry\n\n| ID | Title | Tags |\n| --- | --- | --- |\n",
                encoding="utf-8")
            rc, out, _ = _run(["list", "--global", "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("No skill-tier lessons found", out)

    def test_project_list_json_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out, _ = _run(["list", "--format", "json",
                               "--project-file", str(Path(d) / "none.md")])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data, {"tier": "project", "lessons": [], "count": 0})


class CmdRecallExtraTests(unittest.TestCase):
    def test_recall_json_format(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--tags", "reconcile", "--format", "json",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["count"], 1)
            self.assertEqual(data["matches"][0]["id"], "LL0001")
            self.assertEqual(data["matches"][0]["tier"], "skill")

    def test_recall_all_with_no_project_file_only_skill_tier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--query", "census", "--all",
                               "--lessons-dir", str(ldir),
                               "--project-file", str(Path(d) / "absent.md")])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)
            self.assertNotIn("(project tier)", out)

    def test_recall_query_matches_index_tag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            rc, out, _ = _run(["recall", "--query", "drift",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("LL0001", out)  # matched via its 'drift' tag
            self.assertNotIn("LL0003", out)


class CmdPruneExtraTests(unittest.TestCase):
    def test_invalid_epic_id_returns_code_two(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = Path(d) / "lessons.md"
            pfile.write_text("# Project Lessons\n\n## L-0001: T\n\n"
                             "- **Epic:** EP0001\n", encoding="utf-8")
            rc, _, err = _run(["prune", "--older", "not-an-epic",
                               "--project-file", str(pfile)])
            self.assertEqual(rc, 2)
            self.assertIn("not a valid epic ID", err)

    def test_no_matching_epic_reports_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Has epic", "--body", "x", "--epic", "EP0005",
                  "--project-file", pfile])
            rc, out, _ = _run(["prune", "--epic", "EP0001",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            self.assertIn("Nothing to prune", out)
            self.assertIn("Has epic", Path(pfile).read_text(encoding="utf-8"))

    def test_entries_without_epic_are_never_pruned(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Epic two", "--body", "x", "--epic", "EP0002",
                  "--project-file", pfile])
            _run(["add", "--title", "No epic", "--body", "x",
                  "--project-file", pfile])
            rc, out, _ = _run(["prune", "--older", "EP0009",
                               "--project-file", pfile])
            self.assertEqual(rc, 0)
            text = Path(pfile).read_text(encoding="utf-8")
            self.assertNotIn("Epic two", text)
            self.assertIn("No epic", text)


class RoundTripTests(unittest.TestCase):
    def test_add_then_list_round_trip_preserves_id_title_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pfile = str(Path(d) / "lessons.md")
            _run(["add", "--title", "Round trip", "--body", "keep this body",
                  "--epic", "EP0003", "--tags", "x, y", "--project-file", pfile])
            rc, out, _ = _run(["list", "--project-file", pfile, "--format", "json"])
            data = json.loads(out)
            self.assertEqual(rc, 0)
            e = data["lessons"][0]
            self.assertEqual(e["id"], "L-0001")
            self.assertEqual(e["title"], "Round trip")
            self.assertEqual(e["fields"]["epic"], "EP0003")
            self.assertEqual(e["fields"]["tags"], "x, y")
            self.assertIn("keep this body", e["body"])

    def test_global_add_index_row_reparses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d))
            _run(["add", "--global", "--title", "Parseable", "--body", "B",
                  "--tags", "alpha, beta", "--origin", "proj",
                  "--lessons-dir", str(ldir)])
            rows = lessons.parse_index_rows(ldir / "_index.md")
            new = [r for r in rows if r["id"] == "LL0004"]
            self.assertEqual(len(new), 1)
            self.assertEqual(new[0]["title"], "Parseable")
            self.assertEqual(new[0]["tags"], ["alpha", "beta"])
            self.assertEqual(new[0]["file"], "LL0004-parseable.md")


LESSONS_FIXTURE = """# Project Lessons

**Last Updated:** 2026-01-01

## L-0002: Second lesson

- **Epic:** EP0005
- **Rule:** always do X
- **Applies to:** anything with X

## L-0001: First lesson

- **Epic:** EP0004
- **Fix:** did Y
"""


class RevalidateTests(unittest.TestCase):
    def _write(self, root: Path) -> Path:
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(LESSONS_FIXTURE, encoding="utf-8")
        return p

    def test_lessons_revalidate(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._write(root)
            # listing is read-only and shows both open
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                lessons.main(["revalidate", "--project-file", str(p), "--format", "json"])
            data = json.loads(out.getvalue())
            self.assertEqual(data["count"], 2)
            # closing L-0001 records the closure and removes it from open
            _quiet_main(["revalidate", "--project-file", str(p),
                         "--close", "L-0001", "--reason", "obsolete"])
            entries = lessons.parse_project_lessons(p.read_text(encoding="utf-8"))
            by_id = {e["id"]: e for e in entries}
            self.assertTrue(lessons.is_closed(by_id["L-0001"]))
            self.assertFalse(lessons.is_closed(by_id["L-0002"]))
            self.assertIn("obsolete", by_id["L-0001"]["body"])

    def test_lessons_revalidate_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._write(root)
            _quiet_main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            after_first = p.read_text(encoding="utf-8")
            _quiet_main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            self.assertEqual(p.read_text(encoding="utf-8"), after_first)  # no double-close


def _quiet_main(argv: list[str]) -> int:
    """Run the CLI with its progress line captured. A green suite must say nothing, or a
    real error hides in the scroll."""
    with contextlib.redirect_stdout(io.StringIO()):
        return lessons.main(argv)


class SummaryTests(unittest.TestCase):
    def _write(self, root: Path) -> Path:
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(LESSONS_FIXTURE, encoding="utf-8")
        return p

    def test_lessons_summary_generator(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._write(root)
            out = root / "summary.md"
            _quiet_main(["summary", "--project-file", str(p), "--out", str(out)])
            text = out.read_text(encoding="utf-8")
            self.assertIn("L-0001", text)
            self.assertIn("L-0002", text)
            self.assertIn("always do X", text)  # gist from the Rule field
            # closed lessons drop out of the summary
            _quiet_main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            _quiet_main(["summary", "--project-file", str(p), "--out", str(out)])
            text2 = out.read_text(encoding="utf-8")
            self.assertNotIn("L-0001", text2)
            self.assertIn("L-0002", text2)

    def test_lessons_summary_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._write(root)
            out = root / "summary.md"
            _quiet_main(["summary", "--project-file", str(p), "--out", str(out)])
            first = out.read_text(encoding="utf-8")
            _quiet_main(["summary", "--project-file", str(p), "--out", str(out)])
            self.assertEqual(out.read_text(encoding="utf-8"), first)  # byte-identical


def _requires_git(case: unittest.TestCase) -> None:
    if shutil.which("git") is None:
        case.skipTest("git not available")


class TrackedDestinationTests(unittest.TestCase):
    """A skill-tier lesson must land somewhere version-controlled, or the write is refused.

    The installed skill (`~/.claude/skills/sdlc-studio/`) is not a git work tree: a lesson
    written there is destroyed by the next skill update. Writing it and reporting success is
    the false-green failure LL0008 forbids.
    """

    def setUp(self) -> None:
        _requires_git(self)

    def test_global_add_into_untracked_dir_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d), tracked=False)
            before = (ldir / "_index.md").read_text(encoding="utf-8")
            rc, out, err = _run(["add", "--global", "--title", "Doomed lesson",
                                 "--body", "B", "--lessons-dir", str(ldir)])
            self.assertNotEqual(rc, 0, "writing to an untracked install must not exit 0")
            self.assertNotIn("Wrote", out)  # never report a success it did not achieve
            self.assertIn("git work tree", err)
            self.assertIn(str(ldir), err)
            self.assertIn("skill_source_repo", err)  # the remedy, not just the refusal
            # Nothing authored: no lesson file, and the index is byte-identical.
            self.assertEqual(list(ldir.glob("LL0004-*.md")), [])
            self.assertEqual((ldir / "_index.md").read_text(encoding="utf-8"), before)

    def test_global_add_into_git_work_tree_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = _make_skill_tier(Path(d), tracked=True)
            rc, out, _ = _run(["add", "--global", "--title", "Kept lesson",
                               "--body", "B", "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 0)
            self.assertIn("Wrote LL0004", out)
            self.assertTrue((ldir / "LL0004-kept-lesson.md").is_file())

    def test_global_add_into_a_gitignored_dir_inside_a_work_tree_fails_loud(self) -> None:
        # The install.sh --local case: the skill is vendored to `.claude/skills/` INSIDE the
        # consuming project's work tree, and that path is gitignored. Work-tree membership
        # says "tracked"; git never sees the file, and the next install deletes it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ldir = _registry(root / ".claude" / "skills" / "sdlc-studio" / "lessons")
            (root / ".gitignore").write_text(".claude/skills/\n", encoding="utf-8")
            gitutil.git(["init", "-q"], cwd=root)
            gitutil.git(["add", "-A"], cwd=root)
            before = (ldir / "_index.md").read_text(encoding="utf-8")

            rc, out, err = _run(["add", "--global", "--title", "Silently lost",
                                 "--body", "B", "--lessons-dir", str(ldir)])
            self.assertNotEqual(rc, 0, "a gitignored destination must not exit 0")
            self.assertNotIn("Wrote", out)
            self.assertIn("ignores", err)
            self.assertEqual(list(ldir.glob("LL0004-*.md")), [])
            self.assertEqual((ldir / "_index.md").read_text(encoding="utf-8"), before)

    def test_global_add_where_the_registry_is_not_version_controlled_fails_loud(self) -> None:
        # Inside a work tree, not ignored, but the registry was never added to the index:
        # git does not version-control it, so the write cannot be relied on to survive.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ldir = _make_skill_tier(root, tracked=False)
            gitutil.git(["init", "-q"], cwd=root)  # work tree, but nothing added
            rc, out, err = _run(["add", "--global", "--title", "T", "--body", "B",
                                 "--lessons-dir", str(ldir)])
            self.assertNotEqual(rc, 0)
            self.assertNotIn("Wrote", out)
            self.assertIn("does not track", err)
            self.assertEqual(list(ldir.glob("LL0004-*.md")), [])

    def test_running_skill_fallback_refuses_a_vendored_copy(self) -> None:
        # The fallback destination is the RUNNING skill's lessons/. A vendored copy committed
        # inside some consuming project is a tracked git work tree, but committing there ships
        # nothing with any release and the next install replaces the folder.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            vendored = _registry(root / ".claude" / "skills" / "sdlc-studio" / "lessons")
            gitutil.git(["init", "-q"], cwd=root)
            gitutil.git(["add", "-A"], cwd=root)
            proj = root / "project"
            proj.mkdir()
            orig = lessons.SKILL_LESSONS_DIR
            lessons.SKILL_LESSONS_DIR = vendored
            try:
                rc, out, err = _run(["add", "--global", "--title", "T", "--body", "B",
                                     "--root", str(proj)])
            finally:
                lessons.SKILL_LESSONS_DIR = orig
            self.assertNotEqual(rc, 0, "a vendored skill copy is not the skill source repo")
            self.assertNotIn("Wrote", out)
            self.assertNotIn("skill release", out)  # never claim a release it cannot reach
            self.assertIn("skill_source_repo", err)
            self.assertEqual(list(vendored.glob("LL0004-*.md")), [])

    def test_running_skill_fallback_accepts_the_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = _make_source_checkout(root / "sdlc-studio")
            proj = root / "project"
            proj.mkdir()
            orig = lessons.SKILL_LESSONS_DIR
            lessons.SKILL_LESSONS_DIR = src
            try:
                rc, out, err = _run(["add", "--global", "--title", "From source",
                                     "--body", "B", "--root", str(proj)])
            finally:
                lessons.SKILL_LESSONS_DIR = orig
            self.assertEqual(rc, 0, err)
            self.assertTrue((src / "LL0004-from-source.md").is_file())

    def test_global_add_resolves_skill_source_repo_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # The skill SOURCE checkout (a real git work tree), laid out as the repo is.
            src = root / "src-repo"
            skill = src / ".claude" / "skills" / "sdlc-studio"
            _make_source_checkout(src)
            # The consuming project, whose config points at that checkout.
            proj = root / "project"
            (proj / "sdlc-studio").mkdir(parents=True)
            (proj / "sdlc-studio" / ".config.yaml").write_text(
                f"skill_source_repo: {src}\n", encoding="utf-8")

            rc, out, err = _run(["add", "--global", "--title", "Promoted lesson",
                                 "--body", "B", "--tags", "process",
                                 "--root", str(proj)])
            self.assertEqual(rc, 0, err)
            dest = skill / "lessons" / "LL0004-promoted-lesson.md"
            self.assertTrue(dest.is_file(), "the lesson must land in the source checkout")
            self.assertIn(str(dest), out)
            # AC: `git status` in the source repo shows it.
            status = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all"], cwd=str(src),
                capture_output=True, text=True, env=gitutil.git_env())
            self.assertIn("LL0004-promoted-lesson.md", status.stdout)

    def test_skill_source_repo_without_a_registry_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "empty-repo"
            src.mkdir()
            gitutil.git(["init", "-q"], cwd=src)
            proj = root / "project"
            (proj / "sdlc-studio").mkdir(parents=True)
            (proj / "sdlc-studio" / ".config.yaml").write_text(
                f"skill_source_repo: {src}\n", encoding="utf-8")
            rc, out, err = _run(["add", "--global", "--title", "T", "--body", "B",
                                 "--root", str(proj)])
            self.assertNotEqual(rc, 0)
            self.assertNotIn("Wrote", out)
            self.assertIn("skill_source_repo", err)
            self.assertIn(str(src), err)

    def test_resolver_falls_back_to_the_running_skill_without_config(self) -> None:
        # No config key: the destination is the running skill's own lessons/ dir. The guard
        # then decides - tracked in a source checkout, refused in an installed copy.
        with tempfile.TemporaryDirectory() as d:
            path, source = lessons.resolve_global_dir(None, d)
            self.assertEqual(path, lessons.SKILL_LESSONS_DIR)
            self.assertIn("running skill", source)

    def test_untracked_reason_names_each_way_a_write_is_lost(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ldir = _make_skill_tier(root, tracked=False)
            # 1. No git at all: the installed skill.
            self.assertIn("work tree", lessons.untracked_reason(ldir) or "")
            # 2. A work tree, but the registry is not in the index.
            gitutil.git(["init", "-q"], cwd=root)
            self.assertIn("does not track", lessons.untracked_reason(ldir) or "")
            # 3. Registry version-controlled: safe.
            gitutil.git(["add", "-A"], cwd=root)
            self.assertIsNone(lessons.untracked_reason(ldir))
            self.assertTrue(lessons.is_tracked_destination(ldir))


class SummaryStalenessTests(unittest.TestCase):
    """The summary is DERIVED output of the lessons log. Staleness is decided by recomputing
    the digest from the log and comparing it with the digest parsed back out of the summary -
    the `index-derived` discipline, applied to LESSONS-SUMMARY.md. No stamp, no mtime."""

    def _seed(self, root: Path) -> tuple[Path, Path]:
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(LESSONS_FIXTURE, encoding="utf-8")
        s = root / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md"
        s.parent.mkdir(parents=True, exist_ok=True)
        return p, s

    def _regen(self, root: Path) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            lessons.main(["summary", "--project-file",
                          str(root / "sdlc-studio" / ".local" / "lessons.md")])

    def test_round_trip_summary_parses_back_to_the_expected_digest(self) -> None:
        entries = lessons.parse_project_lessons(LESSONS_FIXTURE)
        rendered = lessons.build_summary_text(entries)
        self.assertEqual(lessons.parse_summary_digest(rendered),
                         lessons.expected_digest(entries))

    # BG0216: the round trip must hold for a lesson whose OWN text carries emphasis.
    #
    # The renderer writes `- **{id}: {title}**` and SUMMARY_LINE_RE finds the title by scanning
    # to the first `**`, so a lesson starting with bold splits at the wrong marker and reads back
    # with the emphasis moved. `summary_status` then reported the SAME lesson as both added and
    # removed, and `lessons summary` regenerated a byte-identical file every time - a BLOCKING
    # gate lane with no satisfying state, which deadlocked a real sprint close.
    #
    # The fixture is the wording that actually caused it. Every prior fixture had a plain gist,
    # so none of them could tell a stable round trip from an unstable one.
    _BOLD_LEADING = (
        "## L-9001: **A drift kind whose advertised remedy cannot clear it is worse than no "
        "hint** - it sends the operator round a loop with no exit.\n\n"
        "- **Added:** 2026-07-20\n- **Review-by:** 2026-10-18\n"
    )

    def test_a_lesson_whose_text_starts_with_bold_round_trips(self) -> None:
        entries = lessons.parse_project_lessons(self._BOLD_LEADING)
        self.assertTrue(entries, "fixture did not parse as a lesson")
        rendered = lessons.build_summary_text(entries)
        self.assertEqual(lessons.parse_summary_digest(rendered),
                         lessons.expected_digest(entries),
                         "a bold-leading lesson does not survive the render/parse round trip")

    def test_a_bold_leading_lesson_does_not_report_as_added_and_removed(self) -> None:
        """The symptom as the gate saw it: one lesson counted on BOTH sides of the diff."""
        entries = lessons.parse_project_lessons(self._BOLD_LEADING)
        expected = lessons.expected_digest(entries)
        parsed = lessons.parse_summary_digest(lessons.build_summary_text(entries))
        self.assertEqual([e for e in expected if e not in parsed], [], "reported as added")
        self.assertEqual([p for p in parsed if p not in expected], [], "reported as removed")

    def test_summary_honours_root_from_a_different_cwd(self) -> None:
        """BG0219: `--project-file` defaults to a RELATIVE path, so every subcommand read and
        wrote relative to the CURRENT DIRECTORY and ignored `--root`, then reported success
        naming the path it had used. `sprint close` passes `--root` correctly and inherited it.

        Run from a cwd that is NOT the root - the only place the bug is visible. From the repo
        root cwd equals root and the broken code looks correct.
        """
        with tempfile.TemporaryDirectory() as t:
            base = Path(t)
            proj, elsewhere = base / "proj", base / "elsewhere"
            (proj / "sdlc-studio" / ".local").mkdir(parents=True)
            elsewhere.mkdir()
            (proj / "sdlc-studio" / ".local" / "lessons.md").write_text(
                "# Project Lessons\n\n**Last Updated:** 2026-07-20\n\n"
                "## L-0001: a lesson worth keeping\n\n- **Added:** 2026-07-20\n",
                encoding="utf-8")
            cwd = os.getcwd()
            os.chdir(elsewhere)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    lessons.main(["summary", "--root", str(proj)])
            finally:
                os.chdir(cwd)
            self.assertTrue((proj / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md").is_file(),
                            "the summary did not land under --root")
            self.assertFalse((elsewhere / "sdlc-studio").exists(),
                             "the summary was written beside the cwd instead of under --root")

    def test_underscores_and_backticks_are_not_stripped(self) -> None:
        """The normalisation must be no wider than the instability it corrects.

        Stripping `_` and `` ` `` as well as `*` made `two_role_after` compare EQUAL to
        `tworoleafter`, so the digest would have stopped noticing a real edit to the identifiers
        these lessons are mostly about. The renderer emits neither character, so neither can move
        in the round trip and neither earns its removal.
        """
        a = lessons.parse_project_lessons(
            "## L-9002: call `two_role_after` before the gate\n\n- **Added:** 2026-07-20\n")
        b = lessons.parse_project_lessons(
            "## L-9002: call tworoleafter before the gate\n\n- **Added:** 2026-07-20\n")
        self.assertNotEqual(lessons.expected_digest(a), lessons.expected_digest(b))

    def test_emphasis_is_the_only_thing_the_comparison_ignores(self) -> None:
        """The normalisation must not make the check blind to a real edit.

        Dropping markers to fix the round trip risks a digest that no longer notices a changed
        lesson, which would be a worse defect than the deadlock: the lane would pass on a stale
        summary. Same text but for one word must still compare unequal.
        """
        a = lessons.parse_project_lessons(self._BOLD_LEADING)
        b = lessons.parse_project_lessons(self._BOLD_LEADING.replace("no exit", "an exit"))
        self.assertNotEqual(lessons.expected_digest(a), lessons.expected_digest(b))

    def test_regenerated_summary_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._seed(root)
            self._regen(root)
            st = lessons.summary_status(root)
            self.assertTrue(st["applicable"])
            self.assertFalse(st["stale"], st["reason"])

    def test_an_added_lesson_makes_the_summary_stale(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p, _ = self._seed(root)
            self._regen(root)
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["add", "--project-file", str(p), "--title", "Third lesson",
                              "--body", "something new"])
            st = lessons.summary_status(root)
            self.assertTrue(st["stale"])
            self.assertTrue(any("Third lesson" in a for a in st["added"]))

    def test_a_closed_lesson_makes_the_summary_stale(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p, _ = self._seed(root)
            self._regen(root)
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            st = lessons.summary_status(root)
            self.assertTrue(st["stale"])
            self.assertTrue(any("L-0001" in r for r in st["removed"]))

    def test_close_one_add_one_is_caught_though_the_count_is_unchanged(self) -> None:
        """LL0015: a check that only catches the total case is not a check. A count or a
        count+mtime signal reads GREEN here - one out, one in, same total."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p, _ = self._seed(root)
            self._regen(root)
            before = lessons.summary_status(root)
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
                lessons.main(["add", "--project-file", str(p), "--title", "Replacement",
                              "--body", "b"])
            st = lessons.summary_status(root)
            self.assertEqual(before["open"], st["open"])  # the count signal is blind here
            self.assertTrue(st["stale"])

    def test_an_edited_gist_makes_the_summary_stale(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p, _ = self._seed(root)
            self._regen(root)
            p.write_text(p.read_text(encoding="utf-8").replace("always do X", "always do Z"),
                         encoding="utf-8")
            self.assertTrue(lessons.summary_status(root)["stale"])

    def test_whitespace_edits_to_the_summary_do_not_false_fire(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _, s = self._seed(root)
            self._regen(root)
            text = s.read_text(encoding="utf-8")
            # trailing spaces, extra blank lines, a reworded boilerplate header
            noisy = text.replace("# Lessons Summary", "# Lessons Summary\n\n<!-- generated -->")
            noisy = noisy.replace("\n- **", "  \n\n-  **")
            s.write_text(noisy + "\n\n", encoding="utf-8")
            st = lessons.summary_status(root)
            self.assertFalse(st["stale"], st["reason"])

    def test_a_missing_summary_beside_a_populated_log_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._seed(root)  # log written, summary never generated
            st = lessons.summary_status(root)
            self.assertTrue(st["applicable"])
            self.assertTrue(st["stale"])

    def test_no_lessons_log_and_no_summary_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            st = lessons.summary_status(Path(t))
            self.assertFalse(st["applicable"])
            self.assertFalse(st["stale"])

    def test_a_deleted_log_beside_a_populated_summary_is_stale_not_vacuous(self) -> None:
        """Review F2: deleting the log must not be the way to green. The summary and the log
        disagree - one lists lessons, the other does not exist - and a check that reads that
        as 'nothing to summarise' can be defeated with one `rm`."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            log, _ = self._seed(root)
            self._regen(root)
            log.unlink()
            st = lessons.summary_status(root)
            self.assertTrue(st["applicable"])
            self.assertTrue(st["stale"])
            self.assertIn("L-0002", st["reason"])

    def test_a_deleted_log_beside_an_empty_summary_stays_not_applicable(self) -> None:
        # the honest N/A: the summary agrees there is nothing to summarise.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            s = root / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md"
            s.parent.mkdir(parents=True)
            s.write_text(lessons.build_summary_text([]), encoding="utf-8")
            st = lessons.summary_status(root)
            self.assertFalse(st["applicable"])
            self.assertFalse(st["stale"])

    def test_a_hard_wrapped_bullet_does_not_false_fire(self) -> None:
        """Review F3: a consuming project with MD013 enabled wraps long lines. A wrapped
        digest bullet is the same lesson, so it must stay green - otherwise the project's own
        markdown linter and this gate would be in permanent, unfixable disagreement."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _, s = self._seed(root)
            self._regen(root)
            wrapped = s.read_text(encoding="utf-8").replace(
                "- **L-0002: Second lesson** - always do X",
                "- **L-0002: Second lesson** -\n  always do X")
            s.write_text(wrapped, encoding="utf-8")
            st = lessons.summary_status(root)
            self.assertFalse(st["stale"], st["reason"])

    def test_a_flush_left_paragraph_after_the_bullets_is_not_swallowed(self) -> None:
        # the join is indentation-anchored: a hand-added footer is not folded into the last
        # lesson's gist (which would corrupt the comparison instead of ignoring the footer).
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _, s = self._seed(root)
            self._regen(root)
            s.write_text(s.read_text(encoding="utf-8") + "\nSee also the retro index.\n",
                         encoding="utf-8")
            self.assertFalse(lessons.summary_status(root)["stale"])


class ValidityHorizonTests(unittest.TestCase):
    """An open lesson past its validity horizon must be closed or extended - the revalidate
    step, made mechanical. An open lesson with NO horizon is unprovable, not proven: it
    counts as a finding too, or the check would pass vacuously on every legacy log."""

    def _seed(self, root: Path, text: str = LESSONS_FIXTURE) -> Path:
        p = root / "sdlc-studio" / ".local" / "lessons.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_add_stamps_added_and_review_by(self) -> None:
        with tempfile.TemporaryDirectory() as t, FixedDate("2026-01-10"):
            p = Path(t) / "lessons.md"
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["add", "--project-file", str(p), "--title", "T", "--body", "b"])
            entry = lessons.parse_project_lessons(p.read_text(encoding="utf-8"))[0]
            self.assertEqual(entry["fields"]["added"], "2026-01-10")
            self.assertEqual(entry["fields"]["review-by"], "2026-04-10")  # +90 days

    def test_an_expired_open_lesson_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._seed(root, LESSONS_FIXTURE.replace(
                "- **Epic:** EP0005", "- **Epic:** EP0005\n- **Review-by:** 2026-01-01"))
            st = lessons.validity_status(root, today="2026-06-01")
            self.assertEqual([e["id"] for e in st["expired"]], ["L-0002"])

    def test_a_lesson_inside_its_horizon_is_not_expired(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._seed(root, LESSONS_FIXTURE.replace(
                "- **Epic:** EP0005", "- **Epic:** EP0005\n- **Review-by:** 2026-12-01"))
            st = lessons.validity_status(root, today="2026-06-01")
            self.assertEqual(st["expired"], [])

    def test_a_closed_lesson_never_expires(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._seed(root, LESSONS_FIXTURE.replace(
                "- **Epic:** EP0005", "- **Epic:** EP0005\n- **Review-by:** 2026-01-01"))
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0002"])
            st = lessons.validity_status(root, today="2026-06-01")
            self.assertEqual(st["expired"], [])

    def test_extend_pushes_the_horizon_forward(self) -> None:
        with tempfile.TemporaryDirectory() as t, FixedDate("2026-06-01"):
            root = Path(t)
            p = self._seed(root, LESSONS_FIXTURE.replace(
                "- **Epic:** EP0005", "- **Epic:** EP0005\n- **Review-by:** 2026-01-01"))
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--extend", "L-0002"])
            entry = {e["id"]: e for e in
                     lessons.parse_project_lessons(p.read_text(encoding="utf-8"))}["L-0002"]
            self.assertEqual(entry["fields"]["review-by"], "2026-08-30")  # +90 days
            self.assertEqual(lessons.validity_status(root, today="2026-06-01")["expired"], [])

    def test_an_undated_open_lesson_is_unstamped_and_stamp_fixes_it(self) -> None:
        with tempfile.TemporaryDirectory() as t, FixedDate("2026-06-01"):
            root = Path(t)
            p = self._seed(root)  # the fixture carries no Added/Review-by (a legacy log)
            st = lessons.validity_status(root, today="2026-06-01")
            self.assertEqual(sorted(st["unstamped"]), ["L-0001", "L-0002"])
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--stamp"])
            st2 = lessons.validity_status(root, today="2026-06-01")
            self.assertEqual(st2["unstamped"], [])
            self.assertEqual(st2["expired"], [])

    def test_stamping_a_prose_only_entry_keeps_it_parseable(self) -> None:
        """Review F4: an entry whose body is a paragraph (no leading bullets) must not get a
        bullet glued to the prose - that reads as a lazy list continuation and the field is
        then unparseable, i.e. still horizon-less after a --stamp that reported success."""
        with tempfile.TemporaryDirectory() as t, FixedDate("2026-06-01"):
            root = Path(t)
            p = self._seed(root, "# Project Lessons\n\n## L-0001: Prose only\n\n"
                                 "A paragraph with no field bullets at all.\n")
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--stamp"])
            entry = lessons.parse_project_lessons(p.read_text(encoding="utf-8"))[0]
            self.assertEqual(entry["fields"]["review-by"], "2026-08-30")
            self.assertEqual(lessons.validity_status(root, today="2026-06-01")["unstamped"], [])
            self.assertIn("A paragraph with no field bullets", entry["body"])

    def test_an_unknown_id_is_refused_not_silently_no_opped(self) -> None:
        """Review F5: `--close L-9999` on a typo'd id printed '0 closed' and exited 0 - a
        no-op wearing a success. The operator believes the lesson is closed; the close gate
        then fails on it, or worse, does not."""
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._seed(root)
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = lessons.main(["revalidate", "--project-file", str(p), "--close", "L-9999"])
            self.assertEqual(rc, 2)
            self.assertIn("L-9999", err.getvalue())
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                rc = lessons.main(["revalidate", "--project-file", str(p), "--extend", "L-9999"])
            self.assertEqual(rc, 2)

    def test_extending_a_closed_lesson_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._seed(root)
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                rc = lessons.main(["revalidate", "--project-file", str(p), "--extend", "L-0001"])
            self.assertEqual(rc, 2)

    def test_closing_an_already_closed_lesson_stays_idempotent(self) -> None:
        # the id EXISTS, so this is not the unknown-id case: re-closing is a no-op that
        # reports 0 and exits 0 (the existing idempotence contract).
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._seed(root)
            with contextlib.redirect_stdout(io.StringIO()):
                lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
                rc = lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            self.assertEqual(rc, 0)

    def test_a_malformed_horizon_counts_as_unstamped_not_as_proven(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            self._seed(root, LESSONS_FIXTURE.replace(
                "- **Epic:** EP0005", "- **Epic:** EP0005\n- **Review-by:** soon"))
            st = lessons.validity_status(root, today="2026-06-01")
            self.assertIn("L-0002", st["unstamped"])


class ValidityDefaultDriftTests(unittest.TestCase):
    """lessons.py reads the config key with the override-only reader (no PyYAML dependency on a
    parser-critical path), so its fallback constant is a SECOND copy of the default. Guard it: a
    change to config-defaults.yaml that leaves the constant behind would silently give projects
    without an override a different horizon from the documented one."""

    def test_constant_matches_config_defaults_yaml(self) -> None:
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        defaults = (Path(__file__).resolve().parents[2] / "templates" / "config-defaults.yaml")
        data = yaml.safe_load(defaults.read_text(encoding="utf-8"))
        self.assertEqual(data["lessons"]["validity_days"], lessons.DEFAULT_VALIDITY_DAYS)

    def test_project_override_wins(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "lessons:\n  validity_days: 30\n", encoding="utf-8")
            days = lessons.resolve_validity_days(root)
            self.assertIn(days, (30, lessons.DEFAULT_VALIDITY_DAYS))  # 90 only without PyYAML
            if days == 30:
                self.assertEqual(lessons.resolve_validity_days(root, 7), 7)  # flag beats config

    def test_a_junk_config_value_degrades_to_the_default(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "lessons:\n  validity_days: soon\n", encoding="utf-8")
            self.assertEqual(lessons.resolve_validity_days(root), lessons.DEFAULT_VALIDITY_DAYS)


class PlanDigestTests(unittest.TestCase):
    """The sprint plan must CONTAIN the lessons, not point at a file."""

    def test_digest_comes_from_the_log_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = root / "sdlc-studio" / ".local" / "lessons.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(LESSONS_FIXTURE, encoding="utf-8")
            d = lessons.plan_digest(root)
            self.assertEqual(d["source"], "log")
            self.assertEqual([x["id"] for x in d["lessons"]], ["L-0002", "L-0001"])

    def test_digest_falls_back_to_the_committed_summary_when_the_log_is_absent(self) -> None:
        # the log is gitignored: a fresh clone has only the summary, and the plan must still
        # carry the lessons rather than silently carrying none.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            s = root / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md"
            s.parent.mkdir(parents=True, exist_ok=True)
            s.write_text(lessons.build_summary_text(
                lessons.parse_project_lessons(LESSONS_FIXTURE)), encoding="utf-8")
            d = lessons.plan_digest(root)
            self.assertEqual(d["source"], "summary")
            self.assertEqual([x["id"] for x in d["lessons"]], ["L-0002", "L-0001"])

    def test_no_lessons_anywhere_is_an_empty_digest(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            d = lessons.plan_digest(Path(t))
            self.assertEqual(d["source"], "none")
            self.assertEqual(d["lessons"], [])


class SummaryOutRootAnchoringTests(unittest.TestCase):
    """`summary --out` writes under the PROJECT ROOT, never beside the cwd.

    BG0219 anchored the READS on `--root`; this write was left taking `Path(args.out)`
    verbatim, so a relative `--out` landed next to whatever directory the agent happened to
    be in while the log it summarised was read from the root - the digest and its source
    could come from two different projects. The default `--root .` was taken as the cwd as
    well, so `summary` from a subdirectory summarised nothing and said so with exit 0.

    Every test runs from a cwd that is NOT the root: from the root the two paths coincide
    and the broken code looks correct. The read/write pair uses DIFFERENT directories,
    because two equally cwd-relative paths agree with each other while both are wrong.
    """

    LOG = ("# Project Lessons\n\n**Last Updated:** 2026-07-20\n\n"
           "## L-0001: a lesson worth keeping\n\n- **Added:** 2026-07-20\n")
    DEFAULT_OUT = Path("sdlc-studio") / "retros" / "LESSONS-SUMMARY.md"

    def setUp(self) -> None:
        self._prev_cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="lessons_root_"))
        self.root = self.tmp / "proj"
        # `sdlc-studio/stories` is one of the project-root markers discovery looks for.
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local" / "lessons.md").write_text(
            self.LOG, encoding="utf-8")
        self.inner = self.root / "scripts"      # a subdirectory inside the project
        self.inner.mkdir()
        self.outside = self.tmp / "elsewhere"   # a cwd with no project above it
        self.outside.mkdir()

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, argv: list[str]) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = lessons.main(argv)
        return rc, out.getvalue()

    def test_a_relative_out_lands_under_the_named_root(self) -> None:
        os.chdir(self.outside)
        self._run(["summary", "--root", str(self.root), "--out", "summary-out.md"])
        self.assertTrue((self.root / "summary-out.md").is_file(),
                        "the summary did not land under the root that was named")
        self.assertEqual(sorted(p.name for p in self.outside.iterdir()), [],
                         "the summary was written beside the cwd")

    def test_summary_without_a_root_discovers_the_project_from_a_subdirectory(self) -> None:
        """The default `--root .` means 'work it out from here', not 'assume the cwd is
        the project'."""
        os.chdir(self.inner)
        self._run(["summary"])
        self.assertTrue((self.root / self.DEFAULT_OUT).is_file(),
                        "the summary did not land under the discovered project root")
        self.assertEqual(sorted(p.name for p in self.inner.iterdir()), [],
                         "the summary was written beside the cwd")

    def test_the_log_it_read_and_the_summary_it_wrote_share_one_root(self) -> None:
        """Written from inside the project on the default root, read back from OUTSIDE it.
        A summary anchored on the cwd while the log is anchored on the root reports zero
        open lessons over a log that holds one, and exits 0 saying so."""
        os.chdir(self.inner)
        self._run(["summary"])
        os.chdir(self.outside)
        written = (self.root / self.DEFAULT_OUT).read_text(encoding="utf-8")
        self.assertIn("L-0001", written,
                      "the digest was built from a log the writer never found")

    def test_it_prints_the_resolved_path_it_wrote(self) -> None:
        """A relative string could not distinguish the root from the cwd, which is what
        hid the misplaced write."""
        os.chdir(self.outside)
        _rc, out = self._run(["summary", "--root", str(self.root), "--out", "summary-out.md"])
        self.assertIn(str(self.root / "summary-out.md"), out)

    def test_an_absolute_out_is_honoured_verbatim(self) -> None:
        """Anchoring must not capture a path the caller chose deliberately."""
        os.chdir(self.outside)
        chosen = self.tmp / "chosen.md"
        self._run(["summary", "--root", str(self.root), "--out", str(chosen)])
        self.assertTrue(chosen.is_file(), "an absolute --out was re-anchored under the root")

    def test_a_named_root_is_not_re_pointed_by_discovery(self) -> None:
        """Discovery widens the default `.` only. A root the caller NAMED is where the
        summary goes, even with a bigger project above it."""
        os.chdir(self.outside)
        self._run(["summary", "--root", str(self.inner), "--out", "summary-out.md"])
        self.assertTrue((self.inner / "summary-out.md").is_file(),
                        "the named root was overridden by discovery")
        self.assertFalse((self.root / "summary-out.md").exists())

    def test_discovery_does_not_escape_a_cwd_with_no_project_above_it(self) -> None:
        """With no project anywhere above, the cwd is the honest answer."""
        os.chdir(self.outside)
        self._run(["summary", "--out", "summary-out.md"])
        self.assertTrue((self.outside / "summary-out.md").is_file())
        self.assertFalse((self.root / "summary-out.md").exists())

    def test_dry_run_still_writes_nothing(self) -> None:
        """Anchoring the path must not have turned a preview into a write."""
        os.chdir(self.outside)
        self._run(["summary", "--root", str(self.root), "--out", "summary-out.md",
                   "--dry-run"])
        self.assertFalse((self.root / "summary-out.md").exists())
        self.assertFalse((self.outside / "summary-out.md").exists())


class CarriedSetBase(unittest.TestCase):
    """A workspace with a lessons log and a carried set."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)

    def log(self, n: int) -> Path:
        p = lessons.default_project_file(self.root)
        body = "# Project Lessons\n\n**Last Updated:** 2026-07-28\n"
        for i in range(1, n + 1):
            body += (f"\n## L-{i:04d}: lesson number {i}\n\n"
                     f"- **Added:** 2026-07-28\n- **Rule:** do the {i}th thing\n")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def fill(self) -> list[str]:
        """Carry exactly `carried_max` lessons, so the set is full."""
        ids = [f"L-{i:04d}" for i in range(1, lessons.carried_max(self.root) + 1)]
        for lid in ids:
            lessons.carry(self.root, lid)
        return ids

    def carried_text(self) -> str:
        return lessons.default_carried_path(self.root).read_text(encoding="utf-8")


class DisplacementTests(CarriedSetBase):
    """US0519/CR0464: a set that can GROW is the 252-entry summary again. The size is held by
    construction - a lesson earns a place only by displacing one, named with the reason - so the
    judgement 'is this more important than what is already carried' is forced rather than
    avoided. Displaced is not deleted: the lesson stays in the full registry."""

    def test_adding_without_displacing_is_refused(self) -> None:
        self.log(20)
        self.fill()
        limit = lessons.carried_max(self.root)
        before = lessons.parse_carried(self.carried_text())
        with self.assertRaises(ValueError) as ctx:
            lessons.carry(self.root, f"L-{limit + 1:04d}")
        msg = str(ctx.exception)
        self.assertIn("displac", msg.lower())
        self.assertIn(str(limit), msg)
        # nothing was written: a refusal that half-applies is worse than one that blocks
        self.assertEqual(lessons.parse_carried(self.carried_text()), before)

    def test_the_displaced_lesson_is_named_and_retained(self) -> None:
        log = self.log(20)
        self.fill()
        limit = lessons.carried_max(self.root)
        new, gone = f"L-{limit + 1:04d}", "L-0002"
        res = lessons.carry(self.root, new, displaces=gone,
                            reason="the repeat it warns about has a guard now")
        self.assertEqual(res["displaced"], gone)
        ids = [c["id"] for c in lessons.parse_carried(self.carried_text())]
        self.assertIn(new, ids)
        self.assertNotIn(gone, ids)
        self.assertEqual(len(ids), limit, "the set must stay fixed size")
        # the displacement is on the record, with WHY
        row = [d for d in lessons.parse_displaced(self.carried_text()) if d["id"] == gone]
        self.assertEqual(len(row), 1, self.carried_text())
        self.assertIn("guard now", row[0]["reason"])
        self.assertEqual(row[0]["by"], new)
        # ... and the lesson itself is still in the full registry - displaced is not deleted
        entries = lessons.parse_project_lessons(log.read_text(encoding="utf-8"))
        self.assertIn(gone, [e["id"] for e in entries])

    def test_a_displacement_without_a_reason_is_refused(self) -> None:
        self.log(20)
        self.fill()
        limit = lessons.carried_max(self.root)
        with self.assertRaises(ValueError) as ctx:
            lessons.carry(self.root, f"L-{limit + 1:04d}", displaces="L-0002")
        self.assertIn("reason", str(ctx.exception).lower())

    def test_displacing_a_lesson_that_is_not_carried_is_refused(self) -> None:
        self.log(20)
        self.fill()
        limit = lessons.carried_max(self.root)
        with self.assertRaises(ValueError) as ctx:
            lessons.carry(self.root, f"L-{limit + 1:04d}", displaces="L-0019", reason="why")
        self.assertIn("L-0019", str(ctx.exception))

    def test_an_unknown_lesson_cannot_be_carried(self) -> None:
        self.log(3)
        with self.assertRaises(ValueError) as ctx:
            lessons.carry(self.root, "L-0099")
        self.assertIn("L-0099", str(ctx.exception))

    def test_room_in_the_set_needs_no_displacement(self) -> None:
        self.log(20)
        res = lessons.carry(self.root, "L-0001")
        self.assertTrue(res["changed"])
        self.assertEqual([c["id"] for c in lessons.parse_carried(self.carried_text())], ["L-0001"])

    def test_carrying_the_same_lesson_twice_is_a_no_op(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        res = lessons.carry(self.root, "L-0001")
        self.assertFalse(res["changed"])
        self.assertEqual(len(lessons.parse_carried(self.carried_text())), 1)


class RepeatTests(CarriedSetBase):
    """US0521/CR0464: a lesson violated AGAIN after being carried is evidence that it needs a
    guard, not a louder note. It is reported at the close naming the unit that repeated it, so
    the evidence attaches to the work that produced it instead of dissolving into the next retro.

    Scoped to what was CARRIED on purpose. The claim is 'this was put in front of you and it
    happened anyway'; a violation of one of the other 247 lessons nobody was asked to hold is a
    finding, not a repeat, and counting it would make the repeat number mean nothing."""

    def test_a_repeat_after_carrying_is_reported_with_its_unit(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        lessons.record_violation(self.root, "L-0001", "US0512",
                                 note="renamed a test and left four ACs pointing at nothing")
        found = lessons.repeats(self.root)
        self.assertEqual([r["id"] for r in found], ["L-0001"])
        self.assertEqual(found[0]["units"], ["US0512"])
        report = lessons.repeat_report(self.root)
        self.assertIn("L-0001", report)
        self.assertIn("US0512", report)

    def test_an_uncarried_lesson_is_not_a_repeat(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        lessons.record_violation(self.root, "L-0007", "US0512", note="not a carried lesson")
        found = lessons.repeats(self.root)
        self.assertEqual(found, [], "a lesson nobody was asked to carry is not a repeat")
        self.assertEqual(lessons.repeat_report(self.root), "")

    def test_every_unit_that_repeated_it_is_named(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        for unit in ("US0512", "US0513", "US0512"):
            lessons.record_violation(self.root, "L-0001", unit)
        found = lessons.repeats(self.root)
        self.assertEqual(found[0]["count"], 3)
        self.assertEqual(found[0]["units"], ["US0512", "US0513"])   # named once each, in order

    def test_a_violation_of_an_unknown_lesson_is_refused(self) -> None:
        self.log(3)
        with self.assertRaises(ValueError) as ctx:
            lessons.record_violation(self.root, "L-0099", "US0512")
        self.assertIn("L-0099", str(ctx.exception))

    def test_a_violation_needs_the_unit_that_produced_it(self) -> None:
        self.log(3)
        with self.assertRaises(ValueError) as ctx:
            lessons.record_violation(self.root, "L-0001", "")
        self.assertIn("unit", str(ctx.exception).lower())

    def test_the_close_reports_repeats(self) -> None:
        """The mechanism must reach the CALLER: `sprint close` prints this, or it is inert."""
        import sprint  # noqa: PLC0415 - the close is the caller under test
        self.log(20)
        lessons.carry(self.root, "L-0001")
        lessons.record_violation(self.root, "L-0001", "US0512")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            sprint._close_lesson_repeats(self.root)
        self.assertIn("L-0001", out.getvalue())
        self.assertIn("US0512", out.getvalue())


class ProposalTests(CarriedSetBase):
    """US0522/CR0464: a lesson violated over and over is not a memory problem, it is a MISSING
    GUARD. The loop should end in work rather than in a longer list - so a repeatedly violated
    carried lesson proposes a change request or a bug for the operator to accept or decline.

    Nothing is filed without acceptance, and a decline is RECORDED against the lesson so the same
    proposal cannot come back on the same evidence. New evidence re-opens it; the old evidence
    does not."""

    def setUp(self) -> None:
        super().setUp()
        self._seed_workspace()

    def _seed_workspace(self) -> None:
        """A workspace a CR can actually be filed into: an index, and a real file to declare."""
        d = self.root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "_index.md").write_text(
            "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 0 |\n"
            "| **Total** | **0** |\n\n## All\n\n"
            "| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
        (self.root / "scripts").mkdir(parents=True, exist_ok=True)
        (self.root / "scripts" / "guard.py").write_text("x\n", encoding="utf-8")

    def _repeat(self, lesson: str, times: int) -> None:
        for i in range(times):
            lessons.record_violation(self.root, lesson, f"US05{i:02d}",
                                     note=f"repeated it in wave {i}")

    def _filed(self) -> list[Path]:
        return [p for p in (self.root / "sdlc-studio" / "change-requests").glob("*.md")
                if p.name != "_index.md"]

    def test_a_repeated_lesson_proposes_a_unit(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        self._repeat("L-0001", lessons.repeat_threshold(self.root) + 1)
        found = lessons.proposals(self.root)
        self.assertEqual([p["id"] for p in found], ["L-0001"])
        prop = found[0]
        self.assertIn(prop["type"], ("cr", "bug"))
        self.assertIn("L-0001", prop["title"])
        # the violations travel WITH the proposal as evidence, not as a count to take on trust
        self.assertTrue(all(u in prop["evidence"] for u in prop["units"]), prop["evidence"])
        # the operator accepts it, and only THEN is an artefact created
        self.assertEqual(self._filed(), [])
        res = lessons.accept_proposal(self.root, "L-0001", affects="scripts/guard.py", size="M")
        body = Path(res["path"]).read_text(encoding="utf-8")
        self.assertIn("L-0001", body)
        self.assertIn("US0500", body)
        self.assertEqual(len(self._filed()), 1)

    def test_a_declined_proposal_files_nothing_and_is_recorded(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        count = lessons.repeat_threshold(self.root) + 1
        self._repeat("L-0001", count)
        res = lessons.decline_proposal(self.root, "L-0001",
                                       reason="the guard belongs in the reviewer, not the tool")
        self.assertEqual(self._filed(), [], "a declined proposal must file nothing")
        # ... recorded against the lesson, with the evidence it was declined on
        declines = lessons.parse_declines(self.carried_text())
        self.assertEqual([d["id"] for d in declines], ["L-0001"])
        self.assertEqual(declines[0]["count"], count)
        self.assertIn("reviewer", declines[0]["reason"])
        self.assertEqual(res["count"], count)
        # ... and it does not come back on the same evidence
        self.assertEqual(lessons.proposals(self.root), [])

    def test_new_evidence_re_opens_a_declined_proposal(self) -> None:
        """A decline settles the evidence it was made on, not the lesson for ever."""
        self.log(20)
        lessons.carry(self.root, "L-0001")
        self._repeat("L-0001", lessons.repeat_threshold(self.root) + 1)
        lessons.decline_proposal(self.root, "L-0001", reason="not worth a guard yet")
        self.assertEqual(lessons.proposals(self.root), [])
        lessons.record_violation(self.root, "L-0001", "US0599", note="and again")
        self.assertEqual([p["id"] for p in lessons.proposals(self.root)], ["L-0001"])

    def test_a_lesson_under_the_threshold_proposes_nothing(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        self._repeat("L-0001", lessons.repeat_threshold(self.root))
        self.assertEqual(lessons.proposals(self.root), [])

    def test_an_uncarried_lesson_proposes_nothing(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        self._repeat("L-0007", 9)
        self.assertEqual(lessons.proposals(self.root), [])

    def test_a_decline_needs_a_reason(self) -> None:
        self.log(20)
        lessons.carry(self.root, "L-0001")
        self._repeat("L-0001", lessons.repeat_threshold(self.root) + 1)
        with self.assertRaises(ValueError) as ctx:
            lessons.decline_proposal(self.root, "L-0001", reason="  ")
        self.assertIn("reason", str(ctx.exception).lower())


class CarriedSetOneTruthTests(unittest.TestCase):
    """BG0365. The carried set was held in three places: a constant in `lessons`, a different
    constant in `sprint`, and the file on disk. `lessons.CARRIED_FILE` named CARRIED-LESSONS.md
    while `sprint` named - and the tree carried - LESSONS-TOP.md, so a curation written by a
    retro and the set a lane was briefed on were two different files. On top of that the writer
    parsed a bullet list the file does not use, so it read [] over a file the readers were
    reading five lessons out of."""

    FILE = ("# The carried lessons\n\n---\n\n"
            "## 1. A mechanism that reaches no caller is inert\n\nbody\n\n"
            "## 2. An absence is not an answer\n\nbody\n")

    def test_the_writer_and_the_readers_name_one_file(self) -> None:
        import sprint
        self.assertEqual("/".join(sprint.CARRIED_LESSONS_REL), lessons.CARRIED_FILE)

    def test_the_constant_names_the_file_the_tree_actually_carries(self) -> None:
        """Agreement between two constants is not enough - they agreed on the WRONG name and
        both read nothing. `sprint` derives its path from `lessons.CARRIED_FILE`, so a test
        comparing the two passes whatever that constant says. The check that can fail is
        against the tree: the file has to be there."""
        repo = Path(__file__).resolve().parents[5]
        if not (repo / "sdlc-studio").is_dir():
            self.skipTest("no dogfooded workspace here")
        carried = repo / lessons.CARRIED_FILE
        self.assertTrue(carried.is_file(),
                        f"{lessons.CARRIED_FILE} does not exist - the constant names a file "
                        f"nothing writes, so every read of the carried set returns nothing")
        self.assertTrue(lessons.parse_carried(carried.read_text(encoding="utf-8")),
                        "the carried file exists but the writer's parser reads no lesson from "
                        "it - two parsers over one file is the same defect as two paths")

    def test_the_writer_and_the_readers_read_one_file_the_same_way(self) -> None:
        """Asserted as AGREEMENT rather than as two expected counts, so an edit to one parser
        cannot pass while the other disagrees."""
        import sprint
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / lessons.CARRIED_FILE
            path.parent.mkdir(parents=True)
            path.write_text(self.FILE, encoding="utf-8")
            writer = len(lessons.read_carried_file(lessons.default_carried_path(root))[0])
            reader = sprint.carried_lessons(root)["count"]
            self.assertEqual(writer, reader)
            self.assertEqual(writer, 2)

    def test_the_older_bullet_shape_is_still_read(self) -> None:
        """A file written in the previous shape must not become unreadable - the repair is a
        widening, not a replacement."""
        older = ("# The carried lessons\n\n## Carried\n\n"
                 "- **L-0001: A thing** - because of a reason\n")
        self.assertEqual(len(lessons.parse_carried(older)), 1)

    def test_an_empty_file_reads_as_no_lessons_for_both(self) -> None:
        import sprint
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / lessons.CARRIED_FILE
            path.parent.mkdir(parents=True)
            path.write_text("# The carried lessons\n\nnothing curated yet\n", encoding="utf-8")
            self.assertEqual(lessons.parse_carried(path.read_text()), [])
            # And the reader says so as an UNANSWERED question, never as a set with nothing in
            # it - a brief that silently omits the set reads like one with nothing to carry.
            self.assertFalse(sprint.carried_lessons(root)["available"])


class RepeatReadIsPinnedTests(unittest.TestCase):
    """BG0371. The close reports a carried lesson violated again, and the proposal path acts on
    the same repeat counts - each taking its OWN read. A violation recorded between the two
    answered one question two ways, and the proposal inherited whichever view it happened to
    see. The violations file is genuinely append-only and accumulates, which was the half of
    the finding that did not reproduce; the unpinned pair was the half that did."""

    def _root(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="repeats_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        (d / "sdlc-studio" / "retros").mkdir(parents=True)
        # The project log the carried set and the violation recorder both read: an id naming no
        # still-valid lesson is refused, which is the right refusal and makes the log part of
        # the fixture rather than an optional extra.
        (d / lessons.DEFAULT_PROJECT_FILE).write_text(
            "# Project lessons\n\n## L-0001: a lesson worth carrying\n\n"
            "- **Gist:** do not do the thing\n", encoding="utf-8")
        # The BULLET shape under `## Carried`, which is the form that carries an ID - the
        # numbered-section shape parses a title only, so `repeats` could never match it.
        (d / lessons.CARRIED_FILE).write_text(
            "# Carried lessons\n\n## Carried\n\n"
            "- **L-0001: a lesson worth carrying** - do not do the thing\n", encoding="utf-8")
        for _ in range(3):
            lessons.record_violation(d, "L-0001", "US0001", note="violated again")
        return d

    def test_the_report_and_the_proposals_read_the_same_counts(self) -> None:
        root = self._root()
        found = lessons.repeats(root)
        self.assertTrue(found, "the fixture must produce a repeat, or this proves nothing")
        before = lessons.repeat_report(root, found=found)
        # A violation lands BETWEEN the two consumers - the race the pin exists for.
        lessons.record_violation(root, "L-0001", "US0002", note="one more")
        pinned = lessons.proposals(root, found=found)
        unpinned = lessons.proposals(root)
        self.assertIn(str(found[0]["count"]), before)
        for row in pinned:
            with self.subTest(lesson=row["id"]):
                self.assertEqual(found[0]["count"], row["count"],
                                 "the pinned proposal read a count the report never saw")
        if unpinned:
            self.assertNotEqual(unpinned[0]["count"], found[0]["count"],
                                "the unpinned read must see the later violation - otherwise "
                                "this test cannot tell a pin from a coincidence")

    def test_an_unpinned_call_still_reads_the_accumulated_record(self) -> None:
        """The half that did not reproduce, pinned so it stays true: the violations file is
        append-only, so a count is the run's history and not one call's view."""
        root = self._root()
        self.assertEqual(3, lessons.repeats(root)[0]["count"])
        lessons.record_violation(root, "L-0001", "US0003")
        self.assertEqual(4, lessons.repeats(root)[0]["count"])


if __name__ == "__main__":
    unittest.main()
