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
    def test_missing_template_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = Path(d) / "lessons"
            ldir.mkdir()
            (ldir / "_index.md").write_text(INDEX, encoding="utf-8")
            rc, _, err = _run(["add", "--global", "--title", "T", "--body", "B",
                               "--lessons-dir", str(ldir)])
            self.assertEqual(rc, 1)
            self.assertIn("template not found", err)

    def test_missing_index_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ldir = Path(d) / "lessons"
            ldir.mkdir()
            (ldir / "_template.md").write_text(TEMPLATE, encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()


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
            lessons.main(["revalidate", "--project-file", str(p),
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
            lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            after_first = p.read_text(encoding="utf-8")
            lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            self.assertEqual(p.read_text(encoding="utf-8"), after_first)  # no double-close


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
            lessons.main(["summary", "--project-file", str(p), "--out", str(out)])
            text = out.read_text(encoding="utf-8")
            self.assertIn("L-0001", text)
            self.assertIn("L-0002", text)
            self.assertIn("always do X", text)  # gist from the Rule field
            # closed lessons drop out of the summary
            lessons.main(["revalidate", "--project-file", str(p), "--close", "L-0001"])
            lessons.main(["summary", "--project-file", str(p), "--out", str(out)])
            text2 = out.read_text(encoding="utf-8")
            self.assertNotIn("L-0001", text2)
            self.assertIn("L-0002", text2)

    def test_lessons_summary_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = self._write(root)
            out = root / "summary.md"
            lessons.main(["summary", "--project-file", str(p), "--out", str(out)])
            first = out.read_text(encoding="utf-8")
            lessons.main(["summary", "--project-file", str(p), "--out", str(out)])
            self.assertEqual(out.read_text(encoding="utf-8"), first)  # byte-identical
