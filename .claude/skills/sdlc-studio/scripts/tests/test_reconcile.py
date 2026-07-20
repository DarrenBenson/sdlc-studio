"""Unit tests for reconcile.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "reconcile.py"
_spec = importlib.util.spec_from_file_location("reconcile", SCRIPT_PATH)
assert _spec and _spec.loader
reconcile = importlib.util.module_from_spec(_spec)
sys.modules["reconcile"] = reconcile
_spec.loader.exec_module(reconcile)

INDEX = (
    "# Stories\n\n"
    "| Status | Count |\n|---|---|\n| Done | 1 |\n| In Progress | 0 |\n\n"
    "| ID | Title | Status |\n|---|---|---|\n"
    "| [US0001](US0001-login.md) | Login | Draft |\n"
    "| [US0099](US0099-ghost.md) | Ghost | Done |\n"
)


def _fixture(root: Path) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / "US0001-login.md").write_text("# Login\n\n> **Status:** Done\n", encoding="utf-8")
    (d / "US0002-logout.md").write_text("# Logout\n\n> **Status:** In Progress\n", encoding="utf-8")
    (d / "_index.md").write_text(INDEX, encoding="utf-8")


class CensusTests(unittest.TestCase):
    def test_file_census(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            census = reconcile.file_census("story", root)
            self.assertEqual(
                census,
                {"US0001": ("US0001", "Done"), "US0002": ("US0002", "In Progress")},
            )


class UnreadableArtefactTests(unittest.TestCase):
    """A non-UTF-8 / corrupted artefact (a half-written file from a crashed session) must be NAMED
    (censused Unknown), never crash the census or the drift gate that run on every commit."""

    def test_census_survives_a_non_utf8_artefact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = root / "sdlc-studio" / "bugs"
            b.mkdir(parents=True)
            (b / "BG0001-x.md").write_bytes(b"# BG0001: x\n\xff\xfe not utf-8\n")
            census = reconcile.file_census("bug", root)   # must not raise
            self.assertEqual(census.get("BG0001"), ("BG0001", "Unknown"))

    def test_detect_type_survives_a_non_utf8_artefact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = root / "sdlc-studio" / "bugs"
            b.mkdir(parents=True)
            (b / "BG0001-x.md").write_bytes(b"# BG0001: x\n\xff\xfe\n")
            (b / "_index.md").write_text(
                "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 0 |\n"
                "| **Total** | **0** |\n\n## All\n\n| ID | Title | Status | Severity | Created | "
                "Updated |\n| --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
            self.assertIsInstance(reconcile.detect_type("bug", root), dict)  # the drift gate survives


class IndexParseTests(unittest.TestCase):
    def test_parse_index_rows_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            idx = reconcile.parse_index("story", root)
            self.assertTrue(idx["exists"])
            self.assertEqual(
                idx["rows"],
                {"US0001": ("US0001", "Draft"), "US0099": ("US0099", "Done")},
            )
            self.assertEqual(idx["summary"], {"Done": 1, "In Progress": 0})

    def test_table_cells_respects_escaped_pipe(self) -> None:
        # A cell containing an escaped pipe must not split into extra columns.
        cells = reconcile._table_cells(r"| US0161 | `string \| string[]` match | CR-0045 | 2 | Done |")
        self.assertEqual(len(cells), 5)
        self.assertEqual(cells[0], "US0161")
        self.assertEqual(cells[1], "`string | string[]` match")
        self.assertEqual(cells[4], "Done")

    def test_table_cells_skips_separator(self) -> None:
        self.assertIsNone(reconcile._table_cells("|---|---|"))
        self.assertEqual(reconcile._table_cells("| a | b |"), ["a", "b"])
        self.assertIsNone(reconcile._table_cells("not a row"))


class StatusWordTitleTests(unittest.TestCase):
    def test_title_starting_with_status_word_not_misread(self) -> None:
        # BG0018: a title beginning with a status word must not become the status.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n"
                "| ID | Title | Status |\n|---|---|---|\n"
                "| [US0001](US0001-x.md) | Review the login flow | Done |\n",
                encoding="utf-8")
            idx = reconcile.parse_index("story", root)
            self.assertEqual(idx["rows"]["US0001"], ("US0001", "Done"))

    def test_cr_title_complete_read_positionally(self) -> None:
        # The live CR0023 case: title "Complete the gate" must not read as Complete.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True, exist_ok=True)
            (cd / "CR0001-x.md").write_text("# CR\n\n> **Status:** Proposed\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n"
                "| ID | Title | Status | Priority |\n|---|---|---|---|\n"
                "| [CR-0001](CR0001-x.md) | Complete the gate | Proposed | High |\n",
                encoding="utf-8")
            idx = reconcile.parse_index("cr", root)
            self.assertEqual(idx["rows"]["CR0001"][1], "Proposed")  # not "Complete"


class TwoLayoutIndexTests(unittest.TestCase):
    def test_status_col_repins_per_header(self) -> None:
        # A second table with a different layout (Status in a different column)
        # must be read against its own header, not the first table's (consuming repo A).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "US0002-x.md").write_text("# US0002: b\n\n> **Status:** Proposed\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n"
                "| Story | Title | Epic | Status | Points | Dependencies |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| US0001 | a | EP0001 | Done | 5 | None |\n\n"
                "## CR-0001 breakdown\n\n"
                "| Story | Title | CR | Points | Status |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| US0002 | b | CR-0001 | 3 | Proposed |\n", encoding="utf-8")
            idx = reconcile.parse_index("story", root)
            self.assertEqual(idx["rows"]["US0001"][1], "Done")      # master: Status @ col 3
            self.assertEqual(idx["rows"]["US0002"][1], "Proposed")  # breakdown: Status @ col 4 (re-pinned)


class DriftTests(unittest.TestCase):
    def test_detects_all_three_classes_plus_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            result = reconcile.detect_type("story", root)
            kinds = {(x["kind"], x["id"]) for x in result["drift"]}
            self.assertIn(("status-mismatch", "US0001"), kinds)  # Done vs Draft
            self.assertIn(("missing-row", "US0002"), kinds)       # file, no row
            # US0099's row LINKS US0099-ghost.md, which does not exist: still a phantom
            # row with no file, now diagnosed precisely (BG0135) - it names the dead link
            # rather than inferring the absence from the row's status.
            self.assertIn(("dead-row-link", "US0099"), kinds)     # row, no file
            self.assertTrue(any(k[0] == "count-mismatch" for k in kinds))

    def test_clean_when_index_matches(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Done | 1 |\n\n"
                "| ID | Status |\n|---|---|\n| [US0001](US0001-x.md) | Done |\n",
                encoding="utf-8",
            )
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])

    def test_missing_index_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            kinds = {x["kind"] for x in reconcile.detect_type("story", root)["drift"]}
            self.assertIn("missing-index", kinds)


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)  # yields status-mismatch + missing-row + orphan-row
            buf = io.StringIO()
            with redirect_stdout(buf):
                reconcile.main(["detect", "--scope", "stories", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("status-mismatch ->", out)


class RefactorGuardTests(unittest.TestCase):
    """apply_type was decomposed from cognitive 56 (CR0030, acting on RFC0009's own
    refactor-first signal); guard it from silently regrowing."""

    def test_apply_type_stays_decomposed(self) -> None:
        import ast
        import inspect
        cx_spec = importlib.util.spec_from_file_location(
            "complexity", SCRIPT_PATH.parent / "complexity.py")
        cx = importlib.util.module_from_spec(cx_spec)
        cx_spec.loader.exec_module(cx)
        fn = ast.parse(inspect.getsource(reconcile.apply_type)).body[0]
        self.assertLess(cx.cognitive_complexity(fn), 15)


class MissingIndexCreationTests(unittest.TestCase):
    """CR0277 / US0158: reconcile apply CREATES a missing index from the template."""

    def _bug(self, root: Path) -> None:
        p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n", encoding="utf-8")

    def test_dry_run_reports_would_create_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            res = reconcile.apply_type("bug", root, dry_run=True)
            self.assertTrue(res.get("would_create_index"))
            self.assertFalse((root / "sdlc-studio" / "bugs" / "_index.md").exists())

    def test_apply_creates_the_index_populates_it_and_clears_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            # missing-index drift present before
            self.assertIn("missing-index",
                          {x["kind"] for x in reconcile.detect_type("bug", root)["drift"]})
            res = reconcile.apply_type("bug", root)
            self.assertTrue(res.get("created_index"))
            idx = root / "sdlc-studio" / "bugs" / "_index.md"
            self.assertTrue(idx.exists())
            self.assertIn("BG0001", idx.read_text())              # census row appended
            # drift cleared, and a subsequent apply is idempotent (no re-create)
            self.assertEqual(reconcile.detect_type("bug", root)["drift"], [])
            self.assertFalse(reconcile.apply_type("bug", root).get("created_index"))

    def test_meta_index_created_from_template(self) -> None:
        # the homelab case: a first dated review file, no reviews/_index.md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rv = root / "sdlc-studio" / "reviews" / "RV0001-unified.md"
            rv.parent.mkdir(parents=True, exist_ok=True)
            rv.write_text("# RV0001 - Unified Review\n\n> **Date:** 2026-07-15\n", encoding="utf-8")
            res = reconcile.apply_meta(root)
            self.assertTrue(res.get("created"))
            self.assertTrue((root / "sdlc-studio" / "reviews" / "_index.md").exists())

    def test_no_census_no_creation(self) -> None:
        # an empty type (no files) is not seeded a phantom index
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            res = reconcile.apply_type("bug", root)
            self.assertFalse(res.get("created_index"))
            self.assertFalse((root / "sdlc-studio" / "bugs" / "_index.md").exists())


class ApplyTests(unittest.TestCase):
    def test_apply_fixes_status_and_counts_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)  # US0001 file Done / index Draft; summary Done=1
            res = reconcile.apply_type("story", root)
            self.assertIn("US0001", [c["id"] for c in res["changes"]])  # Draft -> Done
            self.assertTrue(res["counts_updated"])
            kinds = {dd["kind"] for dd in reconcile.detect_type("story", root)["drift"]}
            self.assertNotIn("status-mismatch", kinds)
            self.assertNotIn("count-mismatch", kinds)
            res2 = reconcile.apply_type("story", root)  # idempotent
            self.assertEqual(res2["changes"], [])
            self.assertFalse(res2["counts_updated"])

    def test_apply_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            idx = root / "sdlc-studio" / "stories" / "_index.md"
            before = idx.read_text(encoding="utf-8")
            res = reconcile.apply_type("story", root, dry_run=True)
            self.assertTrue(res["changes"])           # still reports
            self.assertEqual(idx.read_text(encoding="utf-8"), before)  # but no write

    def test_apply_preserves_escaped_pipe_and_is_byte_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n| Status | Count |\n| --- | --- |\n| Done | 0 |\n\n"
                "| ID | Title | Status |\n| --- | --- | --- |\n"
                "| US0001 | `a \\| b` | Draft |\n", encoding="utf-8")
            idx = sd / "_index.md"
            reconcile.apply_type("story", root)
            after1 = idx.read_text(encoding="utf-8")
            self.assertIn("`a \\| b`", after1)  # escaped pipe survived (re-escaped)
            self.assertEqual(reconcile.parse_index("story", root)["rows"]["US0001"][1], "Done")
            reconcile.apply_type("story", root)
            self.assertEqual(idx.read_text(encoding="utf-8"), after1)  # byte-identical

    def test_apply_two_col_data_table_summary_not_zeroed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n| Status | Count |\n| --- | --- |\n| Done | 1 |\n\n"
                "| ID | Status |\n| --- | --- |\n| US0001 | Done |\n", encoding="utf-8")
            res = reconcile.apply_type("story", root)
            self.assertEqual(res["changes"], [])
            self.assertFalse(res["counts_updated"])  # correct summary not zeroed

    def test_apply_leaves_stray_two_col_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n| Status | Count |\n| --- | --- |\n| Done | 1 |\n\n"
                "| ID | Title | Status |\n| --- | --- | --- |\n| US0001 | a | Done |\n\n"
                "## Points by status\n\n| Done | 5 |\n", encoding="utf-8")
            reconcile.apply_type("story", root)
            self.assertIn("| Done | 5 |", (sd / "_index.md").read_text(encoding="utf-8"))

    def test_apply_ignores_row_shorter_than_status_col(self) -> None:
        # A ragged data row with fewer cells than the Status column is a no-op,
        # not a crash (the status_col >= len(cells) guard).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n| Status | Count |\n| --- | --- |\n| Done | 1 |\n\n"
                "| ID | Title | Status |\n| --- | --- | --- |\n"
                "| US0001 | a | Done |\n| US0002 |\n", encoding="utf-8")  # ragged last row
            res = reconcile.apply_type("story", root)  # must not raise
            self.assertIn("| US0002 |", (sd / "_index.md").read_text(encoding="utf-8"))
            self.assertEqual(res["changes"], [])

    def test_apply_appends_missing_but_never_removes_orphans(self) -> None:
        # missing-row is now mechanically applied (header-driven append);
        # a phantom row stays report-only - removing history is never mechanical
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            res = reconcile.apply_type("story", root)
            self.assertEqual(res["appended"], ["US0002"])
            kinds = {dd["kind"] for dd in reconcile.detect_type("story", root)["drift"]}
            self.assertNotIn("missing-row", kinds)   # US0002 appended
            self.assertIn("dead-row-link", kinds)    # US0099 not removed, still reported
            self.assertIn("US0099", (root / "sdlc-studio" / "stories" / "_index.md")
                          .read_text(encoding="utf-8"))


class NormalisationTests(unittest.TestCase):
    """Regression cover for the four false-positive classes fixed 2026-06-10."""

    def test_id_format_hyphen_insensitive(self) -> None:
        # File `CR0001` (no hyphen) vs index row `CR-0001` (hyphen) must MATCH,
        # not double-count as missing-row + orphan-row.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text("# X\n\n> **Status:** Complete\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Complete | 1 |\n\n"
                "| ID | Status |\n|---|---|\n| [CR-0001](CR0001-x.md) | Complete |\n",
                encoding="utf-8",
            )
            kinds = {x["kind"] for x in reconcile.detect_type("cr", root)["drift"]}
            self.assertNotIn("missing-row", kinds)
            self.assertNotIn("orphan-row", kinds)

    def test_decorated_status_canonicalised(self) -> None:
        # File `Done (v2.83.0) · **CR:** CR-0088` vs index `Done` is NOT drift.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# X\n\n> **Status:** Done (v2.83.0) · **CR:** CR-0088 · **Points:** 8\n",
                encoding="utf-8",
            )
            (sd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Done | 1 |\n\n"
                "| ID | Status |\n|---|---|\n| [US0001](US0001-x.md) | Done |\n",
                encoding="utf-8",
            )
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])

    def test_status_less_namesake_does_not_clobber(self) -> None:
        # `EP0001-consultations.md` (no status) must not overwrite EP0001's Done.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0001-real.md").write_text("# Real\n\n> **Status:** Done\n", encoding="utf-8")
            (ed / "EP0001-consultations.md").write_text("# Consults\n\nno status here\n", encoding="utf-8")
            census = reconcile.file_census("epic", root)
            self.assertEqual(census["EP0001"][1], "Done")

    def test_file_without_status_field_not_flagged(self) -> None:
        # A legacy file with no `> **Status:**` line asserts nothing to compare,
        # so it must not status-mismatch against the index every run.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text("# CR-0001\n\n**Requester:** Op\n\nbody only\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Complete | 1 |\n\n"
                "| ID | Status |\n|---|---|\n| [CR-0001](CR0001-x.md) | Complete |\n",
                encoding="utf-8",
            )
            kinds = {x["kind"] for x in reconcile.detect_type("cr", root)["drift"]}
            self.assertNotIn("status-mismatch", kinds)

    def test_reserved_row_is_not_an_orphan(self) -> None:
        # A `Proposed` (or custom `Retired`) index row with no file is an
        # intentional reservation, not an orphan; an active `Done` row with no
        # file IS an orphan.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "_index.md").write_text(
                "| ID | Status |\n|---|---|\n"
                "| EP0050 | Proposed |\n"      # reserved future epic, no file
                "| EP0051 | Retired |\n"        # documented retirement, no file
                "| EP0052 | Done |\n",          # shipped but file vanished -> orphan
                encoding="utf-8",
            )
            orphans = {x["id"] for x in reconcile.detect_type("epic", root)["drift"]
                       if x["kind"] == "orphan-row"}
            self.assertEqual(orphans, {"EP0052"})

    def test_count_checked_against_index_rows_not_file_census(self) -> None:
        # CR files carry no status; the summary must reconcile against the index
        # ROW tally, so a correct summary is clean even though the file census
        # is all-Unknown.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text("# CR-0001\n\nno status line\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Complete | 1 |\n\n"
                "| ID | Status |\n|---|---|\n| [CR-0001](CR0001-x.md) | Complete |\n",
                encoding="utf-8",
            )
            kinds = {x["kind"] for x in reconcile.detect_type("cr", root)["drift"]}
            self.assertNotIn("count-mismatch", kinds)


class DuplicateRowTests(unittest.TestCase):
    def _idx(self, repo, body):
        d = repo / "sdlc-studio" / "stories"; d.mkdir(parents=True, exist_ok=True)
        (d / "_index.md").write_text(
            "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n" + body, encoding="utf-8")

    def test_duplicate_row_detected(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._idx(repo, "| US0001 | a | Done |\n| US0001 | dupe | Open |\n| US0002 | b | Done |\n")
            r = reconcile.detect_duplicate_rows(repo)
            self.assertEqual(r["count"], 1)
            self.assertEqual(r["duplicates"][0]["id"], reconcile._norm_id("US0001"))
            self.assertEqual(r["duplicates"][0]["count"], 2)

    def test_norm_id_collapses_dash_variant(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            d2 = repo / "sdlc-studio" / "change-requests"; d2.mkdir(parents=True)
            (d2 / "_index.md").write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR0007 | a | Done |\n| CR-0007 | dash | Done |\n", encoding="utf-8")
            self.assertEqual(reconcile.detect_duplicate_rows(repo)["count"], 1)  # CR0007 == CR-0007

    def test_clean_index_no_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._idx(repo, "| US0001 | a | Done |\n| US0002 | b | Done |\n")
            self.assertEqual(reconcile.detect_duplicate_rows(repo)["count"], 0)

    def test_two_view_index_not_flagged(self):  # BG0035
        """The canonical story index ships a per-epic view + an All Stories table; each id
        appears once per view, which is not a duplicate."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "stories"; dd.mkdir(parents=True)
            (dd / "_index.md").write_text(
                "# Story Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 2 |\n\n"
                "## Stories by Epic\n\n### EP0001\n\n| ID | Title | Status | Points | Owner |\n"
                "| --- | --- | --- | --- | --- |\n| US0001 | a | Done | 3 | x |\n"
                "| US0002 | b | Done | 2 | x |\n\n"
                "## All Stories\n\n| ID | Title | Epic | Status | Points | Persona |\n"
                "| --- | --- | --- | --- | --- | --- |\n| US0001 | a | EP0001 | Done | 3 | p |\n"
                "| US0002 | b | EP0001 | Done | 2 | p |\n", encoding="utf-8")
            self.assertEqual(reconcile.detect_duplicate_rows(repo)["count"], 0)

    def test_within_table_dup_in_two_view_index_still_flagged(self):  # BG0035 guard preserved
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "stories"; dd.mkdir(parents=True)
            (dd / "_index.md").write_text(
                "# Story Index\n\n## Stories by Epic\n\n### EP0001\n\n| ID | Title | Status |\n"
                "| --- | --- | --- |\n| US0001 | a | Done |\n\n"
                "## All Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| US0001 | a | Done |\n| US0001 | dupe-in-same-table | Open |\n", encoding="utf-8")
            r = reconcile.detect_duplicate_rows(repo)
            self.assertEqual(r["count"], 1)
            self.assertEqual(r["duplicates"][0]["count"], 2)

    def test_dependencies_table_not_flagged(self):  # BG0046
        """The shipped cr.md index shape: All CRs table + a Dependencies table whose
        header (`| CR | Depends On | Dependency Status |`) has no bare `Status` cell.
        Each id once per table is not a duplicate - the reset must be structural."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            (dd / "_index.md").write_text(
                "# Change Request Registry\n\n## All Change Requests\n\n"
                "| ID | Title | Priority | Status | Type | Linked Epics | Date |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0001](CR0001-a.md) | a | P1 | Proposed | f | -- | d |\n"
                "| [CR-0007](CR0007-b.md) | b | P2 | Proposed | f | -- | d |\n\n"
                "## Dependencies\n\n"
                "| CR | Depends On | Dependency Status |\n"
                "| --- | --- | --- |\n"
                "| CR-0001 | CR-0003 | Complete |\n"
                "| CR-0007 | CR-0001 | Proposed |\n", encoding="utf-8")
            r = reconcile.detect_duplicate_rows(repo)
            self.assertEqual(r["count"], 0, r["duplicates"])

    def test_dup_within_dependencies_style_table_still_flagged(self):  # BG0046 true-positive guard
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            (dd / "_index.md").write_text(
                "# Index\n\n## Dependencies\n\n"
                "| CR | Depends On | Dependency Status |\n"
                "| --- | --- | --- |\n"
                "| CR-0001 | CR-0003 | Complete |\n"
                "| CR-0001 | CR-0004 | Proposed |\n", encoding="utf-8")
            r = reconcile.detect_duplicate_rows(repo)
            self.assertEqual(r["count"], 1)
            self.assertEqual(r["duplicates"][0]["count"], 2)


class DependenciesTableStatusPoisonTests(unittest.TestCase):
    """The shipped Dependencies table must not poison status parsing either:
    a `| CR-0001 | CR-0003 | Complete |` row is not a status assertion about
    CR-0001, and a fully-templated, fully-consistent index has zero drift."""

    def _repo(self, d):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        (dd / "CR0001-a.md").write_text(
            "# CR-0001: a\n\n> **Status:** Proposed\n", encoding="utf-8")
        (dd / "CR0002-b.md").write_text(
            "# CR-0002: b\n\n> **Status:** Proposed\n", encoding="utf-8")
        (dd / "_index.md").write_text(
            "# Registry\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
            "| Proposed | 2 |\n\n"
            "## All Change Requests\n\n"
            "| ID | Title | Priority | Status | Type | Linked Epics | Date |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| [CR-0001](CR0001-a.md) | a | P1 | Proposed | f | -- | d |\n"
            "| [CR-0002](CR0002-b.md) | b | P2 | Proposed | f | -- | d |\n\n"
            "## Dependencies\n\n"
            "| CR | Depends On | Dependency Status |\n"
            "| --- | --- | --- |\n"
            "| CR-0001 | CR-0003 | Complete |\n", encoding="utf-8")
        return repo

    def test_fully_templated_index_has_zero_drift(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d))
            self.assertEqual(r["drift"], [])

    def test_dependency_row_does_not_overwrite_row_status(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            idx = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(encoding="utf-8")
            rows, _ = reconcile._index_rows_and_summary(
                idx, reconcile.sdlc_md.status_vocab("cr", repo))
            self.assertEqual(rows[reconcile._norm_id("CR0001")][1], "Proposed")

    def test_short_dash_separator_is_a_boundary(self):
        # GFM accepts |--| separators; the structural reset must too.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            (dd / "_index.md").write_text(
                "# I\n\n## All\n\n| ID | Title | Status |\n|--|--|--|\n"
                "| CR-0001 | a | Proposed |\n\n"
                "## Dependencies\n\n| CR | Depends On | Dependency Status |\n|--|--|--|\n"
                "| CR-0001 | CR-0002 | Complete |\n", encoding="utf-8")
            self.assertEqual(reconcile.detect_duplicate_rows(repo)["count"], 0)


class DegenerateStatusHeaderTests(unittest.TestCase):
    """An index whose data table mis-names (or lacks) its Status column parses
    every row as Unknown. That is ONE structural defect, not N status drifts:
    detect must emit a single diagnostic naming the offending header, and apply
    must refuse rather than rewrite summary counts it cannot reconcile."""

    def _repo(self, d, status_header="Effective Status"):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        for i, st in ((1, "Proposed"), (2, "Proposed"), (3, "Complete")):
            (dd / f"CR000{i}-x.md").write_text(
                f"# CR-000{i}: x\n\n> **Status:** {st}\n", encoding="utf-8")
        (dd / "_index.md").write_text(
            "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
            "| Proposed | 2 |\n| Complete | 1 |\n"
            f"\n## All\n\n| ID | Title | {status_header} |\n| --- | --- | --- |\n"
            "| CR-0001 | x | Proposed |\n| CR-0002 | x | Proposed |\n"
            "| CR-0003 | x | Complete |\n",
            encoding="utf-8")
        return repo

    def test_misnamed_header_one_diagnostic_not_a_storm(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d))
            kinds = [x["kind"] for x in r["drift"]]
            self.assertEqual(kinds.count("index-status-column"), 1, r["drift"])
            self.assertNotIn("status-mismatch", kinds)
            self.assertNotIn("count-mismatch", kinds)
            f = next(x for x in r["drift"] if x["kind"] == "index-status-column")
            self.assertIn("Effective Status", f["fix"])   # offender named
            self.assertIn("rename", f["fix"].lower())      # remedy named

    def test_absent_status_column_still_one_diagnostic(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d, status_header="State"))
            kinds = [x["kind"] for x in r["drift"]]
            self.assertEqual(kinds.count("index-status-column"), 1, r["drift"])
            self.assertNotIn("status-mismatch", kinds)

    def test_healthy_index_single_drift_unchanged(self):
        # the pre-check must not swallow a real one-row drift on a well-formed index
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, status_header="Status")
            idx = repo / "sdlc-studio" / "change-requests" / "_index.md"
            idx.write_text(idx.read_text(encoding="utf-8").replace(
                "| CR-0003 | x | Complete |", "| CR-0003 | x | Proposed |"),
                encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            kinds = [x["kind"] for x in r["drift"]]
            self.assertNotIn("index-status-column", kinds)
            self.assertIn("status-mismatch", kinds)

    def test_all_rows_out_of_vocab_is_not_misdiagnosed_as_header(self):
        # a proper Status header whose every row carries an out-of-vocab token is
        # a vocab problem (count-mismatch self-diagnosis), not a header problem
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            (dd / "CR0001-x.md").write_text(
                "# CR-0001: x\n\n> **Status:** Shipped\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
                "| Proposed | 1 |\n"
                "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0001 | x | Shipped |\n", encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            self.assertNotIn("index-status-column",
                             [x["kind"] for x in r["drift"]])

    def test_apply_refuses_degenerate_index_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            idx = repo / "sdlc-studio" / "change-requests" / "_index.md"
            before = idx.read_text(encoding="utf-8")
            res = reconcile.apply_type("cr", repo)
            self.assertEqual(res["changes"], [])
            self.assertFalse(res["counts_updated"])
            self.assertEqual(idx.read_text(encoding="utf-8"), before)

    def test_declared_status_alias_parses_cleanly(self):
        # RFC-0023: a project that declares its house header under
        # conventions.status_column gets a clean parse - no diagnostic, no drift
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - conventions degrade to defaults")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  status_column:\n    - Effective Status\n",
                encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            self.assertEqual(r["drift"], [])

    def test_declared_alias_apply_rewrites_the_aliased_column(self):
        # writer parity: an alias the READ side accepts must be rewritable by
        # apply, else apply recomputes counts against rows it cannot fix and
        # detect-after shows MORE drift than before
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - conventions degrade to defaults")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, status_header="Effective Status")
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  status_column:\n    - Effective Status\n",
                encoding="utf-8")
            idx = repo / "sdlc-studio" / "change-requests" / "_index.md"
            # seed one genuine drift: CR0003's file says Complete, row says Proposed
            idx.write_text(idx.read_text(encoding="utf-8").replace(
                "| CR-0003 | x | Complete |", "| CR-0003 | x | Proposed |"),
                encoding="utf-8")
            before = reconcile.detect_type("cr", repo)["drift"]
            self.assertEqual([x["kind"] for x in before if x["id"]],
                             ["status-mismatch"])
            res = reconcile.apply_type("cr", repo)
            self.assertEqual([c["id"] for c in res["changes"]], ["CR-0003"])
            self.assertEqual(res["unapplied"], [])
            self.assertEqual(reconcile.detect_type("cr", repo)["drift"], [])

    def test_diagnostic_names_the_conventions_knob(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d))
            f = next(x for x in r["drift"] if x["kind"] == "index-status-column")
            self.assertIn("conventions.status_column", f["fix"])

    def test_archive_row_does_not_defeat_the_diagnosis(self):
        # one healthy archived row must not mask a degenerate LIVE index:
        # degeneracy is a property of the live table, judged before the
        # archive census merge
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            arch = repo / "sdlc-studio" / "change-requests" / "archive"
            arch.mkdir()
            (arch / "2025.md").write_text(
                "# Archived\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0099 | old | Superseded |\n", encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            kinds = [x["kind"] for x in r["drift"]]
            self.assertEqual(kinds.count("index-status-column"), 1, r["drift"])
            self.assertNotIn("status-mismatch", kinds)
            self.assertNotIn("count-mismatch", kinds)
            # and apply still refuses - no half-written summary
            idx = repo / "sdlc-studio" / "change-requests" / "_index.md"
            before = idx.read_text(encoding="utf-8")
            res = reconcile.apply_type("cr", repo)
            self.assertTrue(res.get("refused"))
            self.assertEqual(idx.read_text(encoding="utf-8"), before)

    def test_apply_command_reports_refusal_and_exits_nonzero(self):
        # L-0004: the wiring, not only the helper - the CLI must say REFUSED
        # and exit 1, never print a clean "changed 0 row(s)" success
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = reconcile.main(["apply", "--root", str(repo)])
            self.assertEqual(rc, 1)
            self.assertIn("REFUSED", buf.getvalue())
            self.assertIn("Effective Status", buf.getvalue())


class SeparatorLessHeaderTests(unittest.TestCase):
    def test_vocab_header_repins_case_insensitively(self):
        # A separator-less table is re-pinned by the vocabulary-header
        # predicate, which must case-fold: without the header pin the row
        # would be scavenged and 'Done deal' would win over the Status cell
        rows, _ = reconcile._index_rows_and_summary(
            "| ID | Notes | Status |\n| US0001 | Done deal | Draft |\n",
            ["Draft", "Done"])
        self.assertEqual(rows["US0001"][1], "Draft")


class SummaryRowInsertionTests(unittest.TestCase):
    """A status flip into a status ABSENT from the summary must not leave apply
    exiting 0 over a count-mismatch it just created: the writer inserts the
    missing in-vocab row into the reconcile-managed global summary block
    (before Total), touches no scoped per-epic table, and exits non-zero
    naming the residual when no managed block can take the row."""

    def _repo(self, d, index_text):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        (dd / "CR0001-a.md").write_text(
            "# CR-0001: a\n\n> **Status:** Approved\n", encoding="utf-8")
        (dd / "_index.md").write_text(index_text, encoding="utf-8")
        return repo

    GLOBAL = ("# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
              "| Proposed | 1 |\n| **Total** | **1** |\n"
              "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
              "| CR-0001 | a | Proposed |\n")

    def test_missing_row_inserted_before_total_and_clean_after(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, self.GLOBAL)
            res = reconcile.apply_type("cr", repo)
            self.assertEqual([c["id"] for c in res["changes"]], ["CR-0001"])
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            lines = [ln.strip() for ln in text.splitlines()]
            self.assertIn("| Approved | 1 |", lines)
            self.assertLess(lines.index("| Approved | 1 |"),
                            lines.index("| **Total** | **1** |"))
            self.assertIn("| Proposed | 0 |", lines)
            self.assertEqual(reconcile.detect_type("cr", repo)["drift"], [])

    def test_scoped_per_epic_summary_never_gains_rows(self):
        scoped = (self.GLOBAL +
                  "\n## EP0001 roll-up\n\n| Status | Count |\n| --- | --- |\n"
                  "| Proposed | 1 |\n")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, scoped)
            reconcile.apply_type("cr", repo)
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            rollup = text.split("## EP0001 roll-up")[1]
            self.assertNotIn("Approved", rollup)   # author-maintained block untouched

    def test_no_summary_block_at_all_is_not_drift(self):
        # zero Status|Count blocks = no summary contract: nothing asserts
        # counts, so apply must exit 0 untouched - detect's count-mismatch
        # only fires when a summary exists, and apply mirrors that authority
        bare = ("# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0001 | a | Approved |\n")
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, bare)
            before = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = reconcile.main(["apply", "--root", str(repo)])
            self.assertEqual(rc, 0, err.getvalue())
            self.assertNotIn("could not insert", err.getvalue())
            self.assertEqual((repo / "sdlc-studio" / "change-requests" /
                              "_index.md").read_text(encoding="utf-8"), before)

    def test_unplaceable_names_only_statuses_absent_everywhere(self):
        # a status that already has a row in an UNMANAGED block is not
        # "missing" - the warning must name only statuses absent from every
        # summary block
        twin = ("# Index\n\n## A\n\n| Status | Count |\n| --- | --- |\n"
                "| Approved | 1 |\n"
                "\n## B\n\n| Status | Count |\n| --- | --- |\n"
                "| Proposed | 0 |\n"
                "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0001 | a | Approved |\n")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, twin)
            res = reconcile.apply_type("cr", repo)
            self.assertEqual(res["summary_missing"], [])  # Approved has a row in A

    def test_unplaceable_missing_row_exits_nonzero_named(self):
        # two Total-less summaries: neither is the managed block, so the row
        # cannot be placed - apply must say so and exit 1, never a clean 0
        twin = ("# Index\n\n## A\n\n| Status | Count |\n| --- | --- |\n"
                "| Proposed | 1 |\n"
                "\n## B\n\n| Status | Count |\n| --- | --- |\n"
                "| Proposed | 1 |\n"
                "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| CR-0001 | a | Proposed |\n")
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, twin)
            buf = io.StringIO()
            err = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = reconcile.main(["apply", "--root", str(repo)])
            self.assertEqual(rc, 1)
            self.assertIn("Approved", buf.getvalue() + err.getvalue())


class SelfDiagnosingCountMismatchTests(unittest.TestCase):
    """count-mismatch findings carry their own diagnosis: the mismatched status
    tokens with both numbers, and - when out-of-vocab statuses are the cause -
    the offending status, its artifacts, and the status_vocab remedy."""

    def _repo(self, d, cr2_status="Built", summary="| Proposed | 2 |\n"):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        (dd / "CR0001-a.md").write_text(
            "# CR-0001: a\n\n> **Status:** Proposed\n", encoding="utf-8")
        (dd / "CR0002-b.md").write_text(
            f"# CR-0002: b\n\n> **Status:** {cr2_status}\n", encoding="utf-8")
        (dd / "_index.md").write_text(
            "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n" + summary +
            "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| CR-0001 | a | Proposed |\n| CR-0002 | b | {cr2_status} |\n",
            encoding="utf-8")
        return repo

    def test_out_of_vocab_cause_is_named_with_remedy(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d))
            finds = [x for x in r["drift"] if x["kind"] == "count-mismatch"]
            self.assertEqual(len(finds), 1)
            f = finds[0]
            self.assertIn("Proposed rows=1 summary=2", f["fix"])       # numbers travel
            self.assertIn("'Built'", f["fix"])                          # offender named
            self.assertIn("CR0002", f["fix"])                           # carrier named
            self.assertIn("status_vocab.cr", f["fix"])                  # the config remedy
            self.assertIn("validate", f["fix"])                         # sibling tool routed
            self.assertEqual(f["mismatches"],
                             [{"status": "Proposed", "rows": 1, "summary": 2}])
            self.assertEqual(f["out_of_vocab"], {"Built": ["CR0002"]})

    def test_arithmetic_only_keeps_recompute_hint(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type(
                "cr", self._repo(d, cr2_status="Complete", summary="| Proposed | 2 |\n"))
            finds = [x for x in r["drift"] if x["kind"] == "count-mismatch"]
            self.assertEqual(len(finds), 1)
            f = finds[0]
            self.assertIn("recompute the summary counts", f["fix"])     # generic hint kept
            self.assertNotIn("status_vocab", f["fix"])                  # no false vocab blame
            self.assertIsNone(f["out_of_vocab"])
            self.assertIn({"status": "Proposed", "rows": 1, "summary": 2}, f["mismatches"])

    def test_declaring_the_status_in_config_clears_it(self):
        try:
            import yaml  # noqa: F401 - soft dependency, mirrors project_override
        except ImportError:
            self.skipTest("PyYAML absent - project_override degrades to defaults")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, summary="| Proposed | 1 |\n| Built | 1 |\n")
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "status_vocab:\n  cr:\n    - Built\n", encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            self.assertEqual([x for x in r["drift"] if x["kind"] == "count-mismatch"], [])


class CountBlockScopeTests(unittest.TestCase):
    def test_per_epic_count_table_not_corrupted(self):
        # BG0026: per-epic Status|Count tables (no Total) must survive; only the global summary
        # (the block with a Total, or the sole summary) is recomputed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "US0002-b.md").write_text("# US0002: b\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-a.md) | a | Done |\n| [US0002](US0002-b.md) | b | Done |\n\n"
                "### EP0001\n\n| Status | Count |\n| --- | --- |\n| Done | 6 |\n\n"
                "## Status summary\n\n| Status | Count |\n| --- | --- |\n| Done | 99 |\n| **Total** | **99** |\n",
                encoding="utf-8")
            reconcile.apply_type("story", root)
            out = (sd / "_index.md").read_text()
            self.assertIn("| Done | 6 |", out)        # per-epic preserved (the BG0026 corruption)
            self.assertIn("| Done | 2 |", out)        # global recomputed (was 99 -> 2)
            self.assertIn("**Total** | **2**", out)   # global total recomputed

    def test_sole_summary_without_total_still_recomputed(self):
        # no regression: a single summary (even Total-less) is still managed
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-a.md) | a | Done |\n\n"
                "## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 5 |\n", encoding="utf-8")
            reconcile.apply_type("story", root)
            self.assertIn("| Done | 1 |", (sd / "_index.md").read_text())  # recomputed (sole summary)


    def test_adjacent_blocks_no_scan_bleed(self):
        # the Total-scan must stop at the block boundary: a per-epic block (no Total) directly
        # before the global block (with Total) must NOT inherit the global's Total.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# S\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-a.md) | a | Done |\n\n"
                "### EP0001\n\n| Status | Count |\n| --- | --- |\n| Done | 6 |\n\n"
                "## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 9 |\n| **Total** | **9** |\n",
                encoding="utf-8")
            reconcile.apply_type("story", root)
            out = (sd / "_index.md").read_text()
            self.assertIn("| Done | 6 |", out)        # per-epic untouched (no scan-bleed)
            self.assertIn("**Total** | **1**", out)   # global recomputed to 1

    def test_multiple_summaries_none_with_total_left_alone(self):
        # documented boundary: 2+ summaries, none with a Total -> none recomputed (don't-corrupt
        # beats don't-recompute). Both per-epic-style counts are preserved verbatim.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# S\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-a.md) | a | Done |\n\n"
                "### EP0001\n\n| Status | Count |\n| --- | --- |\n| Done | 6 |\n\n"
                "### EP0002\n\n| Status | Count |\n| --- | --- |\n| Done | 8 |\n",
                encoding="utf-8")
            reconcile.apply_type("story", root)
            out = (sd / "_index.md").read_text()
            self.assertIn("| Done | 6 |", out)
            self.assertIn("| Done | 8 |", out)        # both preserved; neither stamped


class MultiSchemaStatusTests(unittest.TestCase):
    def _bug(self, d, id_, status):
        (d / f"{id_}-x.md").write_text(f"# {id_}: x\n\n> **Status:** {status}\n", encoding="utf-8")

    def test_offschema_row_status_read_by_vocab_not_position(self):
        # BG0032: a stacked/off-schema row (extra column) must have its Status found by vocab token,
        # not the pinned column - else it reads "Unknown" -> phantom status-mismatch.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0001", "Fixed"); self._bug(bd, "BG0002", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| BG0001 | a | Fixed |\n| BG0002 | b | note | Fixed |\n", encoding="utf-8")
            drift = reconcile.detect_type("bug", root)["drift"]
            self.assertEqual([x for x in drift if x["kind"] == "status-mismatch"], [])

    def test_perblock_header_multischema_rewrites_correct_column(self):
        # real stacked-schema case: each block has its own header, so status_col re-pins per block
        # and apply rewrites the right column (block 2 has Status at col1).
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0001", "Fixed"); self._bug(bd, "BG0002", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n| BG0001 | a | Fixed |\n\n"
                "## Older\n\n| ID | Status | Severity |\n| --- | --- | --- |\n| BG0002 | Open | High |\n",
                encoding="utf-8")
            reconcile.apply_type("bug", root)
            out = (bd / "_index.md").read_text()
            self.assertIn("| BG0002 | Fixed | High |", out)   # col1 (re-pinned) corrected, severity intact

    def test_offschema_extra_column_row_not_clobbered_on_apply(self):
        # BG0032 safety: when the pinned column is NOT a status (off-schema extra-column row), apply
        # declines rather than guess - it must never overwrite the title/another field.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0002", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| BG0002 | b | note | Open |\n", encoding="utf-8")
            reconcile.apply_type("bug", root)
            out = (bd / "_index.md").read_text()
            self.assertIn("| BG0002 | b | note | Open |", out)  # left intact - no clobber, no guess

    def test_orphan_row_never_deleted_by_apply(self):
        # BG0031: an inline-only record (index row, no file) is report-only - apply must not remove it.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0001", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| BG0001 | a | Fixed |\n| BG0081 | inline-only | Fixed |\n", encoding="utf-8")
            reconcile.apply_type("bug", root)
            self.assertIn("| BG0081 | inline-only | Fixed |", (bd / "_index.md").read_text())

    def test_apply_never_clobbers_title_starting_with_status_word(self):
        # critic edge: pinned col is a non-vocab value AND the title leads with a status word. apply
        # must NOT relocate the status into the title (data loss) - it declines.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0003", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| BG0003 | Open the dialog on load | TBD |\n", encoding="utf-8")  # title leads 'Open'; col2 non-vocab
            reconcile.apply_type("bug", root)
            self.assertIn("| BG0003 | Open the dialog on load | TBD |", (bd / "_index.md").read_text())

    def test_headerless_block_status_read_by_vocab(self):
        # the legitimate fallback: a block with no Status header -> status found by vocab token.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            self._bug(bd, "BG0005", "Fixed")
            (bd / "_index.md").write_text(
                "# Bugs\n\n- prose, no table header\n\n| BG0005 | x | Fixed |\n", encoding="utf-8")
            drift = reconcile.detect_type("bug", root)["drift"]
            self.assertEqual([x for x in drift if x["kind"] == "status-mismatch"], [])


class FieldProjectionTests(unittest.TestCase):
    """CR0082: reconcile projects file-owned index cells (title, points) from the files."""

    def _setup(self, root: Path) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / "US0001-login.md").write_text(
            "# US0001: Login flow\n\n> **Status:** Draft\n\n**Story Points:** 5\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Stories\n\n## All Stories\n\n"
            "| ID | Title | Epic | Status | Points | Persona |\n"
            "|---|---|---|---|---|---|\n"
            "| [US0001](US0001-login.md) | Login | EP0001 | Draft | -- | Priya |\n",
            encoding="utf-8")

    def test_detect_reports_title_and_points_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._setup(root)
            r = reconcile.project_fields(root, dry_run=True)
            fields = {x["field"]: x for x in r["drift"]}
            self.assertEqual(fields["title"]["file"], "Login flow")
            self.assertEqual(fields["points"]["file"], "5")
            # dry-run wrote nothing
            self.assertIn("| Login |", (root / "sdlc-studio" / "stories" / "_index.md").read_text())

    def test_apply_syncs_cells_then_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._setup(root)
            reconcile.project_fields(root, dry_run=False)
            text = (root / "sdlc-studio" / "stories" / "_index.md").read_text()
            self.assertIn("| Login flow | EP0001 | Draft | 5 | Priya |", text)
            self.assertEqual(reconcile.project_fields(root, dry_run=True)["drift"], [])  # idempotent

    def test_persona_projected_from_canonical_field(self) -> None:  # CR0097
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: Login\n\n> **Status:** Draft\n> **Persona:** Priya\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status | Persona |\n|---|---|---|---|\n"
                "| [US0001](US0001-x.md) | Login | Draft | -- |\n", encoding="utf-8")
            reconcile.project_fields(root, dry_run=False)
            self.assertIn("| Priya |", (sd / "_index.md").read_text())

    def test_absent_file_field_left_untouched(self) -> None:
        # Persona has no canonical file field, and a file without Points must not blank the cell.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._setup(root)
            # remove the Points field from the file -> the index Points cell must stay as-is
            f = root / "sdlc-studio" / "stories" / "US0001-login.md"
            f.write_text("# US0001: Login\n\n> **Status:** Draft\n", encoding="utf-8")
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status | Points |\n|---|---|---|---|\n"
                "| [US0001](US0001-login.md) | Login | Draft | 8 |\n", encoding="utf-8")
            reconcile.project_fields(root, dry_run=False)
            self.assertIn("| 8 |", (root / "sdlc-studio" / "stories" / "_index.md").read_text())


class WriterFidelityTests(unittest.TestCase):
    """The reconcile writer must persist what it claims and report what it could not -
    never present a no-op as a clean apply (the fail-loud discipline)."""

    def test_claimed_edit_that_does_not_persist_is_not_reported_as_changed(self) -> None:
        # The sharpest field defect: a row whose Status the reader finds by vocab fallback
        # (off-schema, status not in the pinned column) is planned as a fix, but the writer
        # declines to guess the cell - so nothing persists. apply must NOT report it as a
        # change; it must surface it as unapplied. Buffer-diff is the contract.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0265-x.md").write_text("# CR-0265: t\n\n> **Status:** Complete\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0265](CR0265-x.md) | t | extra | **Proposed** |\n", encoding="utf-8")
            before = (cd / "_index.md").read_text(encoding="utf-8")
            res = reconcile.apply_type("cr", root)
            after = (cd / "_index.md").read_text(encoding="utf-8")
            self.assertEqual(after, before)  # nothing actually changed on disk
            # the claimed-but-unapplied fix must not be reported as a landed change
            self.assertEqual(res["changes"], [])
            self.assertIn("CR-0265", [u["id"] for u in res["unapplied"]])

    def test_apply_command_warns_on_unapplied_edit(self) -> None:
        # The text command must warn (stderr) and return non-zero, never a clean "set ... -> ...".
        import io
        from contextlib import redirect_stderr, redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0265-x.md").write_text("# CR-0265: t\n\n> **Status:** Complete\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0265](CR0265-x.md) | t | extra | **Proposed** |\n", encoding="utf-8")
            out_buf, err_buf = io.StringIO(), io.StringIO()
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                rc = reconcile.main(["apply", "--scope", "crs", "--root", str(root)])
            out, err = out_buf.getvalue(), err_buf.getvalue()
            self.assertEqual(rc, 1)  # non-zero: an edit could not be made
            self.assertIn("could not apply", err)
            self.assertNotIn("set cr CR-0265", out)  # not reported as a landed flip
            self.assertIn("could not be applied", out)  # summary line is honest

    def test_bold_wrapped_status_persisted_with_emphasis_preserved(self) -> None:
        # BG0043 (a): a bold-wrapped status cell is rewritten AND keeps its emphasis on write,
        # mirroring the reader's tolerant canonicalisation rather than flattening to plain text.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0265-x.md").write_text("# CR-0265: t\n\n> **Status:** Complete\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n| ID | Title | Status | Priority |\n| --- | --- | --- | --- |\n"
                "| [CR-0265](CR0265-x.md) | t | **Proposed** | High |\n", encoding="utf-8")
            res = reconcile.apply_type("cr", root)
            out = (cd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("CR-0265", [c["id"] for c in res["changes"]])
            self.assertIn("| **Complete** |", out)  # re-wrapped, not flattened to | Complete |
            self.assertNotIn("| Complete |", out)


class FixOrderSignpostTests(unittest.TestCase):
    """CR0122 (a): when both status drift and count drift are present, the detect output must
    state the recommended order - resolve status mismatches first, recompute counts/summaries last."""

    def test_signpost_emitted_when_status_and_count_both_drift(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)  # US0001 status-mismatch + a count-mismatch
            buf = io.StringIO()
            with redirect_stdout(buf):
                reconcile.main(["detect", "--scope", "stories", "--root", str(root)])
            out = buf.getvalue().lower()
            self.assertIn("recommended order", out)
            # counts/summaries recomputed last
            self.assertIn("last", out)

    def test_no_signpost_when_only_count_drift(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "| Status | Count |\n|---|---|\n| Done | 9 |\n\n"
                "| ID | Status |\n|---|---|\n| [US0001](US0001-x.md) | Done |\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                reconcile.main(["detect", "--scope", "stories", "--root", str(root)])
            self.assertNotIn("recommended order", buf.getvalue().lower())


class MissingRowFilenameTests(unittest.TestCase):
    """CR0122 (b): a missing/mismatched index-row finding emits the artifact's actual filename
    / relative path on disk, not just the bare id, so the index link can be wired without guessing."""

    def test_missing_row_fix_carries_filename(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir(parents=True)
            (bd / "BG0136-suspense-csr-bail.md").write_text(
                "# BG0136: x\n\n> **Status:** Open\n", encoding="utf-8")
            (bd / "_index.md").write_text(
                "# Bugs\n\n| ID | Status |\n|---|---|\n", encoding="utf-8")
            drift = reconcile.detect_type("bug", root)["drift"]
            missing = [x for x in drift if x["kind"] == "missing-row"]
            self.assertEqual(len(missing), 1)
            self.assertEqual(missing[0]["file"], "BG0136-suspense-csr-bail.md")
            self.assertIn("BG0136-suspense-csr-bail.md", missing[0]["fix"])


class BG0044RegressionTests(unittest.TestCase):
    """BG0044: the per-epic count sub-tables must survive the global summary recompute -
    the count recompute is scoped to the canonical global summary (its Total-row signature)."""

    def test_per_epic_done_block_survives_global_recompute(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-a.md").write_text("# US0001: a\n\n> **Status:** Done\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-a.md) | a | Done |\n\n"
                "### EP0001\n\n| Status | Count |\n| --- | --- |\n| Done | 6 |\n\n"
                "## Status summary\n\n| Status | Count |\n| --- | --- |\n"
                "| Done | 99 |\n| **Total** | **99** |\n", encoding="utf-8")
            reconcile.apply_type("story", root)
            out = (sd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("| Done | 6 |", out)        # per-epic block unchanged
            self.assertIn("**Total** | **1**", out)   # global summary recomputed only


class IndexBloatAdvisoryTests(unittest.TestCase):
    """The archive process must be RECOMMENDED, not just shipped: when live
    terminal rows exceed indexes.archive_after the detect result carries an
    advisory naming the count, the threshold, and the archive command - and
    it never blocks (not a drift item, exit code unaffected)."""

    def _repo(self, d, n_terminal, archived=0):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        rows = []
        for i in range(1, n_terminal + 1):
            (dd / f"CR{i:04d}-x.md").write_text(
                f"# CR-{i:04d}: x\n\n> **Status:** Complete\n", encoding="utf-8")
            rows.append(f"| CR-{i:04d} | x | Complete |")
        (dd / "_index.md").write_text(
            "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            + "\n".join(rows) + "\n", encoding="utf-8")
        if archived:
            ad = dd / "archive" / "r1"; ad.mkdir(parents=True)
            arows = []
            for i in range(900, 900 + archived):
                (dd / f"CR{i:04d}-y.md").write_text(
                    f"# CR-{i:04d}: y\n\n> **Status:** Complete\n", encoding="utf-8")
                arows.append(f"| CR-{i:04d} | y | Complete |")
            (ad / "cr.md").write_text(
                "# archive\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                + "\n".join(arows) + "\n", encoding="utf-8")
        return repo

    def test_over_threshold_fires_named_advisory(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d, 35))
            advs = r.get("advisories") or []
            self.assertEqual(len(advs), 1, r)
            self.assertIn("35", advs[0])
            self.assertIn("30", advs[0])                       # threshold named
            self.assertIn("archive.py archive --type cr", advs[0])
            self.assertNotIn("index-bloat", [x["kind"] for x in r["drift"]])

    def test_under_threshold_silent(self):
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d, 10))
            self.assertEqual(r.get("advisories") or [], [])

    def test_archived_rows_do_not_count(self):
        # 40 archived terminal rows + 5 live: the live index is bounded - silent
        with tempfile.TemporaryDirectory() as d:
            r = reconcile.detect_type("cr", self._repo(d, 5, archived=40))
            self.assertEqual(r.get("advisories") or [], [])
            self.assertEqual(r["drift"], [])                   # census union intact

    def test_config_threshold_respected(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, 10)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "indexes:\n  archive_after: 5\n", encoding="utf-8")
            r = reconcile.detect_type("cr", repo)
            self.assertEqual(len(r.get("advisories") or []), 1)

    def test_detect_command_exit_zero_on_advisory_only(self):
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, 35)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = reconcile.main(["detect", "--root", str(repo)])
            self.assertEqual(rc, 0, buf.getvalue())
            self.assertIn("advisory", buf.getvalue())
            self.assertIn("drift_items=0", buf.getvalue())


class MissingRowAppendTests(unittest.TestCase):
    """apply appends missing index rows mechanically (header-driven, matching
    the table's own column order) - a consuming project hand-authored 23 rows
    because missing-row was report-only. Orphans stay report-only; a table the
    writer cannot pin reports the rows unapplied and exits non-zero."""

    def _repo(self, d, index_text, files=(1, 2, 3)):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        for i in files:
            (dd / f"CR{i:04d}-thing-{i}.md").write_text(
                f"# CR-{i:04d}: thing {i}\n\n> **Status:** Proposed\n", encoding="utf-8")
        (dd / "_index.md").write_text(index_text, encoding="utf-8")
        return repo

    BASE = ("# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
            "| Proposed | 1 |\n| **Total** | **1** |\n"
            "\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [CR-0001](CR0001-thing-1.md) | thing 1 | Proposed |\n")

    def test_missing_rows_appended_and_clean_after(self):
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, self.BASE)
            res = reconcile.apply_type("cr", repo)
            self.assertEqual(sorted(res.get("appended", [])), ["CR0002", "CR0003"])
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertIn("thing 2", text)
            self.assertIn("(CR0003-thing-3.md)", text)     # link to the real file
            self.assertIn("| Proposed | 3 |", text)         # counts include appends
            self.assertEqual(reconcile.detect_type("cr", repo)["drift"], [])

    def test_custom_column_order_respected(self):
        custom = ("# Index\n\n## All\n\n| Status | ID | Title |\n| --- | --- | --- |\n"
                  "| Proposed | [CR-0001](CR0001-thing-1.md) | thing 1 |\n")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, custom, files=(1, 2))
            res = reconcile.apply_type("cr", repo)
            self.assertEqual(res.get("appended", []), ["CR0002"])
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            row = next(ln for ln in text.splitlines() if "CR0002" in ln)
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            self.assertEqual(cells[0], "Proposed")          # status in column 0
            self.assertIn("CR-0002", cells[1])              # id in column 1
            self.assertEqual(reconcile.detect_type("cr", repo)["drift"], [])

    def test_unpinnable_table_reports_unapplied_nonzero(self):
        # no ID-column data header anywhere: the writer must not guess
        weird = ("# Index\n\n## All\n\n| Ref | Title | Status |\n| --- | --- | --- |\n"
                 "| CR-0001 | thing 1 | Proposed |\n")
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, weird, files=(1, 2))
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = reconcile.main(["apply", "--root", str(repo)])
            self.assertEqual(rc, 1)
            self.assertIn("CR0002", buf.getvalue() + err.getvalue())
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertNotIn("CR0002", text)                 # nothing guessed in

    def test_orphan_rows_stay_report_only(self):
        # the row LINKS CR0099-gone.md, so the phantom is diagnosed as a dead-row-link
        # (BG0135). The invariant is unchanged: apply never removes it, detect always
        # reports it - only an explicit --prune-orphans may cut it.
        orphan = self.BASE + "| [CR-0099](CR0099-gone.md) | gone | Complete |\n"
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, orphan)
            reconcile.apply_type("cr", repo)
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertIn("CR-0099", text)                   # never removed
            kinds = [x["kind"] for x in reconcile.detect_type("cr", repo)["drift"]]
            self.assertIn("dead-row-link", kinds)            # still reported


class AppendTargetingTests(unittest.TestCase):
    """Critic round: the append must honour an aliased status column and pin
    the MASTER table (where the census rows live), never a trailing view."""

    def test_aliased_status_column_gets_the_status_not_dashes(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  status_column: [State]\n", encoding="utf-8")
            for i in (1, 2):
                (dd / f"CR{i:04d}-t{i}.md").write_text(
                    f"# CR-{i:04d}: t{i}\n\n> **Status:** Proposed\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                "# I\n\n## All\n\n| ID | Title | State |\n| --- | --- | --- |\n"
                "| [CR-0001](CR0001-t1.md) | t1 | Proposed |\n", encoding="utf-8")
            res = reconcile.apply_type("cr", repo)
            self.assertEqual(res["appended"], ["CR0002"])
            row = next(ln for ln in (dd / "_index.md").read_text(encoding="utf-8")
                       .splitlines() if "CR0002" in ln)
            self.assertIn("Proposed", row)      # status lands in the aliased column
            self.assertNotIn("--", row)
            self.assertEqual(reconcile.detect_type("cr", repo)["drift"], [])
            # idempotent: second apply plants nothing new
            self.assertEqual(reconcile.apply_type("cr", repo)["appended"], [])

    def _view_repo(self, d, master_rows, view_rows):
        repo = Path(d)
        dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
        for i in (1, 2, 3):
            (dd / f"CR{i:04d}-t{i}.md").write_text(
                f"# CR-{i:04d}: t{i}\n\n> **Status:** Proposed\n", encoding="utf-8")
        (dd / "_index.md").write_text(
            "# I\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            + "".join(f"| [CR-000{i}](CR000{i}-t{i}.md) | t{i} | Proposed |\n"
                      for i in master_rows)
            + "\n## Blocked view\n\n| ID | Blocker | Status |\n| --- | --- | --- |\n"
            + "".join(f"| [CR-000{i}](CR000{i}-t{i}.md) | none | Proposed |\n"
                      for i in view_rows), encoding="utf-8")
        return repo, dd

    def _assert_master_append(self, dd, res, expect=("CR0003",)):
        self.assertEqual(res["appended"], list(expect))
        text = (dd / "_index.md").read_text(encoding="utf-8")
        master, view = text.split("## Blocked view")
        for rid in expect:
            self.assertIn(rid, master)       # appended to the master table
            self.assertNotIn(rid, view)      # the view is author-maintained

    def test_append_pins_the_master_table_not_a_trailing_view(self):
        with tempfile.TemporaryDirectory() as d:
            repo, dd = self._view_repo(d, master_rows=(1, 2), view_rows=(1,))
            self._assert_master_append(dd, reconcile.apply_type("cr", repo))

    def test_append_pins_the_master_even_on_a_census_id_tie(self):
        # Sam's battery case D: master and view each hold ONE census id - a
        # tie must not hand the append to the trailing view (the id would
        # parse from the view and certify the incomplete master as clean)
        with tempfile.TemporaryDirectory() as d:
            repo, dd = self._view_repo(d, master_rows=(1,), view_rows=(1,))
            self._assert_master_append(dd, reconcile.apply_type("cr", repo),
                                       expect=("CR0002", "CR0003"))

    def test_single_epic_story_tie_still_resolves_to_the_master(self):
        # the shipped story layout ALSO ties (per-epic view first, All
        # Stories master LAST) - the disambiguator must keep that green
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            for i in (1, 2):
                (sd / f"US000{i}-s{i}.md").write_text(
                    f"# US000{i}: s{i}\n\n> **Status:** Draft\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# S\n\n## Stories by Epic\n\n"
                "| Story | Title | CR | Points | Status |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| [US0001](US0001-s1.md) | s1 | CR-1 | 3 | Draft |\n"
                "\n## All Stories\n\n"
                "| ID | Title | Epic | Status | Points | Dependencies |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| [US0001](US0001-s1.md) | s1 | EP1 | Draft | 3 | None |\n",
                encoding="utf-8")
            res = reconcile.apply_type("story", repo)
            self.assertEqual(res["appended"], ["US0002"])
            text = (sd / "_index.md").read_text(encoding="utf-8")
            by_epic, master = text.split("## All Stories")
            self.assertIn("US0002", master)
            self.assertNotIn("US0002", by_epic)

    def test_identical_mirror_tables_refuse_loudly(self):
        # two indistinguishable ID tables: appending to either is a guess -
        # report unapplied and exit 1, never fabricate a choice
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            for i in (1, 2):
                (dd / f"CR{i:04d}-t{i}.md").write_text(
                    f"# CR-{i:04d}: t{i}\n\n> **Status:** Proposed\n", encoding="utf-8")
            table = ("| ID | Title | Status |\n| --- | --- | --- |\n"
                     "| [CR-0001](CR0001-t1.md) | t1 | Proposed |\n")
            (dd / "_index.md").write_text(
                "# I\n\n## A\n\n" + table + "\n## B (mirror)\n\n" + table,
                encoding="utf-8")
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = reconcile.main(["apply", "--root", str(repo)])
            self.assertEqual(rc, 1)
            self.assertIn("CR0002", buf.getvalue() + err.getvalue())
            self.assertNotIn("CR0002",
                             (dd / "_index.md").read_text(encoding="utf-8"))

    def test_display_form_mirrors_existing_rows(self):
        # a house table using undashed CR ids gets an undashed append
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            dd = repo / "sdlc-studio" / "change-requests"; dd.mkdir(parents=True)
            for i in (1, 2):
                (dd / f"CR{i:04d}-t{i}.md").write_text(
                    f"# CR-{i:04d}: t{i}\n\n> **Status:** Proposed\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                "# I\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR0001](CR0001-t1.md) | t1 | Proposed |\n", encoding="utf-8")
            reconcile.apply_type("cr", repo)
            row = next(ln for ln in (dd / "_index.md").read_text(encoding="utf-8")
                       .splitlines() if "t2" in ln)
            self.assertIn("[CR0002]", row)       # undashed, matching the house rows


class ApplyJsonFormatTests(unittest.TestCase):
    """US0080/CR0187: `reconcile apply --format json` emits the per-type result structures."""

    def test_apply_json(self) -> None:
        import argparse
        import io
        import json
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            sd = repo / "sdlc-studio" / "bugs"; sd.mkdir(parents=True)
            (sd / "_index.md").write_text(
                "# B\n\n## All\n\n| ID | Title | Status | Severity | Created | Updated |\n"
                "| --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                reconcile.cmd_apply(argparse.Namespace(root=str(repo), scope=None,
                                                       dry_run=True, format="json"))
            j = json.loads(buf.getvalue())
            self.assertIn("by_type", j)
            self.assertIn("applied", j)
            self.assertTrue(j["dry_run"])


class FormatJsonParityTests(unittest.TestCase):
    """US0102/CR0187: every reconcile subcommand speaks --format json (parity locked so a
    new subcommand cannot ship text-only)."""

    _SUBS = ("detect", "apply", "fields")

    def test_every_subparser_exposes_format_json(self) -> None:
        import argparse
        parser = reconcile.build_parser()
        sub = next(a for a in parser._actions
                   if isinstance(a, argparse._SubParsersAction))
        for name in self._SUBS:
            self.assertIn(name, sub.choices, f"{name} subcommand missing")
            fmt = next((ac for ac in sub.choices[name]._actions
                        if ac.dest == "format"), None)
            self.assertIsNotNone(fmt, f"{name} has no --format")
            self.assertIn("json", fmt.choices, f"{name} --format lacks json")

    def test_each_subcommand_emits_valid_json(self) -> None:
        import io
        import json
        import contextlib
        argv = {
            "detect": ["detect"],
            "apply": ["apply", "--dry-run"],
            "fields": ["fields"],
        }
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            for name in self._SUBS:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    reconcile.main(argv[name] + ["--root", str(root), "--format", "json"])
                json.loads(buf.getvalue())  # raises if not valid JSON


class ReopenedArchiveDriftTests(unittest.TestCase):
    """BG0081: a live row must win over an archive row for the same id - a reopened
    (archived-then-live-again) artefact was shadowed by its archive row, giving permanent
    un-clearable status-mismatch + count drift."""

    def _seed(self, root: Path) -> None:
        d = root / "sdlc-studio" / "stories"
        (d / "archive" / "2026-06").mkdir(parents=True)
        (d / "US0001-x.md").write_text(
            "# US0001: x\n\n> **Status:** In Progress\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
            "| In Progress | 1 |\n| **Total** | **1** |\n\n## All\n\n"
            "| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | x | In Progress |\n", encoding="utf-8")
        (d / "archive" / "2026-06" / "story.md").write_text(
            "# Archived\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](../../US0001-x.md) | x | Done |\n", encoding="utf-8")

    def test_live_row_wins_over_archive_row(self) -> None:
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._seed(root)
            self.assertEqual(reconcile.parse_index("story", root)["rows"]["US0001"][1],
                             "In Progress")

    def test_reopened_artefact_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._seed(root)
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])


class IndexRewriterColumnBleedTests(unittest.TestCase):
    """BG0082: an unclassifiable header (e.g. a Dependencies table) must RESET the tracked
    status/id columns - otherwise the previous data table's column index bleeds forward and
    the rewriter clobbers an author-maintained cell that happens to be status-shaped."""

    def test_status_col_does_not_bleed_into_a_following_table(self) -> None:
        vocab = ["Proposed", "In Progress", "Complete", "Blocked"]
        lines = (
            "## All\n\n"
            "| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [CR-0001](CR0001-x.md) | x | Proposed |\n\n"
            "## Dependencies\n\n"
            "| CR | Depends on | Notes |\n| --- | --- | --- |\n"
            "| CR-0001 | CR-0003 | Blocked until review lands |\n"
        ).splitlines()
        # a fix for CR-0001's real Status (Proposed -> Complete) must NOT touch the
        # Dependencies row's 3rd cell (which starts with the vocab word 'Blocked')
        fixes = {"CR0001": "Complete"}
        _cu, applied = reconcile._rewrite_index_lines(lines, fixes, {}, vocab)
        joined = "\n".join(lines)
        self.assertIn("| [CR-0001](CR0001-x.md) | x | Complete |", joined)
        self.assertIn("| CR-0001 | CR-0003 | Blocked until review lands |", joined)


class JsonExitCodeTests(unittest.TestCase):
    """BG0088: --format json must signal failure with the same exit code as the text path."""

    def test_apply_json_exit_matches_text_on_unapplied(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True)
            (d / "US0001-x.md").write_text("# US0001: x\n\n> **Status:** Done\n", encoding="utf-8")
            # an index with no rewritable ID-column data table -> the fix is unapplied
            (d / "_index.md").write_text(
                "# Stories\n\n## All\n\nno data table here\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                rc_json = reconcile.main(["apply", "--scope", "stories", "--root", str(root),
                                          "--format", "json"])
                rc_text = reconcile.main(["apply", "--scope", "stories", "--root", str(root)])
            self.assertEqual(rc_json, rc_text)


class MasterHeaderTieBreakTests(unittest.TestCase):
    """_master_data_header must compare ALL equally-ranked winners, not just the first and
    last. With two identical mirrors bracketing a distinct table, the old first-vs-last check
    saw winners[0]==winners[-1] and wrongly declared them indistinguishable (returned None)."""

    def test_distinct_table_between_mirrors_still_resolves(self) -> None:
        census = {"US0001": ("US-0001", "Done")}  # _master_data_header needs 3+ column tables
        lines = (
            "| ID | Col | Foo |\n| --- | --- | --- |\n| US0001 | a | x |\n\n"
            "| ID | Col | Bar |\n| --- | --- | --- |\n| US0001 | a | y |\n\n"
            "| ID | Col | Foo |\n| --- | --- | --- |\n| US0001 | a | z |\n"
        ).splitlines()
        hdr = reconcile._master_data_header(lines, census)
        self.assertIsNotNone(hdr)                       # old code returned None here
        self.assertEqual(hdr[1], ["ID", "Col", "Foo"])  # LAST equally-ranked table wins

    def test_all_identical_mirrors_return_none(self) -> None:
        census = {"US0001": ("US-0001", "Done")}
        lines = (
            "| ID | Col | Foo |\n| --- | --- | --- |\n| US0001 | a | x |\n\n"
            "| ID | Col | Foo |\n| --- | --- | --- |\n| US0001 | a | z |\n"
        ).splitlines()
        self.assertIsNone(reconcile._master_data_header(lines, census))


class EpicBreakdownTests(unittest.TestCase):
    """BG0101: an epic's Story Breakdown checkboxes must be reconciled for EVERY unit type
    listed (bug/CR/story), not only stories - a terminal unit behind an unchecked box (or a
    checked box over a live unit) is drift, and apply syncs it mechanically."""

    @staticmethod
    def _fixture(root: Path) -> Path:
        for rel, fname, body in [
            ("epics", "EP0001-alpha.md",
             "# EP0001: Alpha\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
             "- [ ] [BG0001](../bugs/BG0001-x.md) - fixed bug, box unchecked (drift)\n"
             "- [x] [CR0001](../change-requests/CR0001-y.md) - live CR, box checked (drift)\n"
             "- [ ] [US0001](../stories/US0001-z.md) - live story, box unchecked (clean)\n"
             "- [ ] US9999 - placeholder stub with no backing file (skipped, never drift)\n"),
            ("bugs", "BG0001-x.md", "# BG0001: x\n\n> **Status:** Fixed\n"),
            ("change-requests", "CR0001-y.md", "# CR0001: y\n\n> **Status:** In Progress\n"),
            ("stories", "US0001-z.md", "# US0001: z\n\n> **Status:** In Progress\n"),
        ]:
            d = root / "sdlc-studio" / rel
            d.mkdir(parents=True, exist_ok=True)
            (d / fname).write_text(body, encoding="utf-8")
        return root

    def test_detect_flags_both_directions_and_skips_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            drift = reconcile.epic_breakdown_drift(self._fixture(Path(d)))
            kinds = {(x["id"], x["kind"]) for x in drift}
            self.assertIn(("BG0001", "breakdown-unticked"), kinds)   # terminal, box empty
            self.assertIn(("CR0001", "breakdown-ticked-early"), kinds)  # live, box checked
            self.assertEqual(len(drift), 2)  # US0001 clean, US9999 placeholder skipped

    def test_apply_syncs_boxes_both_ways(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d))
            res = reconcile.apply_breakdown(root)
            self.assertEqual(sorted(res["synced"]), ["BG0001", "CR0001"])
            text = (root / "sdlc-studio" / "epics" / "EP0001-alpha.md").read_text(encoding="utf-8")
            self.assertIn("- [x] [BG0001]", text)
            self.assertIn("- [ ] [CR0001]", text)
            self.assertEqual(reconcile.epic_breakdown_drift(root), [])  # now clean
            self.assertEqual(reconcile.apply_breakdown(root)["synced"], [])  # idempotent

    def test_checkboxes_outside_the_breakdown_are_never_touched(self) -> None:
        # Critic repro: a Definition of Done item mentioning a Fixed unit must not be
        # ticked - a box outside the Story Breakdown does not mean "unit delivered".
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text("# BG0001: x\n\n> **Status:** Fixed\n",
                                            encoding="utf-8")
            (ed / "EP0001-a.md").write_text(
                "# EP0001: A\n\n> **Status:** In Progress\n\n"
                "## Story Breakdown\n\n- [ ] [BG0001](../bugs/BG0001-x.md) - the unit\n\n"
                "## Definition of Done\n\n"
                "- [ ] Verify BG0001 fix is documented in the README\n",
                encoding="utf-8")
            drift = reconcile.epic_breakdown_drift(root)
            self.assertEqual(len(drift), 1)          # ONLY the breakdown box
            res = reconcile.apply_breakdown(root)
            self.assertEqual(res["synced"], ["BG0001"])
            text = (ed / "EP0001-a.md").read_text(encoding="utf-8")
            self.assertIn("- [x] [BG0001]", text)                       # breakdown synced
            self.assertIn("- [ ] Verify BG0001 fix is documented", text)  # DoD untouched

    def test_status_less_unit_asserts_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG0002-y.md").write_text("# BG0002: y\n\nno status field\n",
                                            encoding="utf-8")
            (ed / "EP0001-a.md").write_text(
                "# EP0001: A\n\n> **Status:** In Progress\n\n"
                "## Story Breakdown\n\n- [x] [BG0002](../bugs/BG0002-y.md)\n",
                encoding="utf-8")
            self.assertEqual(reconcile.epic_breakdown_drift(root), [])
            self.assertEqual(reconcile.apply_breakdown(root)["synced"], [])

    def test_detect_runs_in_the_default_sweep(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d))
            rc = reconcile.main(["detect", "--root", str(root)])
            self.assertEqual(rc, 1)  # breakdown drift alone must make detect non-zero


class EraDivergenceTests(unittest.TestCase):
    """Multi-user era warning: config says v2 but v3 ULID ids exist in the workspace -
    another writer is on v3 (or config is stale). Advisory only, one direction only."""

    def test_v2_config_with_v3_ids_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG-01JQK3F8-x.md").write_text("# BG-01JQK3F8: x\n\n> **Status:** Open\n",
                                                 encoding="utf-8")
            note = reconcile.era_divergence_advisory(root)  # no config -> schema 2
            self.assertIsNotNone(note)
            self.assertIn("era divergence", note)
            self.assertIn("BG-01JQK3F8", note)

    def test_v3_config_with_mixed_ids_is_silent(self) -> None:
        # forward-only adopt keeps sequential ids beside ULIDs - NOT divergence
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir()
            (bd / "BG0001-old.md").write_text("# BG0001: old\n\n> **Status:** Open\n",
                                              encoding="utf-8")
            (bd / "BG-01JQK3F8-new.md").write_text("# BG-01JQK3F8: new\n\n> **Status:** Open\n",
                                                   encoding="utf-8")
            self.assertIsNone(reconcile.era_divergence_advisory(root))

    def test_pure_v2_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text("# BG0001: x\n\n> **Status:** Open\n",
                                            encoding="utf-8")
            self.assertIsNone(reconcile.era_divergence_advisory(root))


class MetaIndexTests(unittest.TestCase):
    """retros/ and reviews/ coverage: row presence only, house columns tolerated, the meta id
    namespace (RETRO/RV) that the pipeline id regexes exclude."""

    @staticmethod
    def _reviews(root: Path, files: list[str], rows: list[str]) -> None:
        d = root / "sdlc-studio" / "reviews"
        d.mkdir(parents=True, exist_ok=True)
        for f in files:
            (d / f).write_text(f"# {f}\n\n> **Date:** 2026-07-01\n", encoding="utf-8")
        body = "| ID | Title | Date |\n| --- | --- | --- |\n" + "".join(rows)
        (d / "_index.md").write_text("# Review Index\n\n" + body, encoding="utf-8")

    def test_clean_when_every_file_has_a_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md", "RV0002-b.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n",
                           "| [RV-0002](RV0002-b.md) | B | 2026-07-01 |\n"])
            self.assertEqual(reconcile.meta_index_drift(root), [])

    def test_missing_row_detected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md", "RV0002-b.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n"])
            drift = reconcile.meta_index_drift(root)
            self.assertEqual([(x["kind"], x["id"]) for x in drift], [("missing-row", "RV-0002")])

    def test_orphan_row_detected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n",
                           "| [RV-0009](RV0009-gone.md) | Gone | 2026-07-01 |\n"])
            drift = reconcile.meta_index_drift(root)
            self.assertEqual([(x["kind"], x["id"]) for x in drift], [("orphan-row", "RV-0009")])

    def test_non_numbered_neighbours_are_not_census(self) -> None:
        # LATEST.md, prompts and rehearsal notes live in reviews/ but are not numbered
        # artefacts - they must never be flagged as a missing row.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n"])
            rv = root / "sdlc-studio" / "reviews"
            (rv / "LATEST.md").write_text("# latest\n", encoding="utf-8")
            (rv / "repo-review-prompt.md").write_text("# prompt\n", encoding="utf-8")
            self.assertEqual(reconcile.meta_index_drift(root), [])

    def test_second_non_id_table_cannot_phantom_a_row(self) -> None:
        # iter_tables yields every separator table; a summary/second table whose prose
        # matches RV-?0*\d+ must NOT be read as an index row (it would mask real drift).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rv = root / "sdlc-studio" / "reviews"
            rv.mkdir(parents=True, exist_ok=True)
            (rv / "RV0001-a.md").write_text("# a\n> **Date:** 2026-07-01\n", encoding="utf-8")
            (rv / "RV0002-b.md").write_text("# b\n> **Date:** 2026-07-01\n", encoding="utf-8")
            (rv / "_index.md").write_text(
                "# Review Index\n\n"
                "| Bucket | Note |\n| --- | --- |\n| misc | see RV0002 for context |\n\n"
                "| ID | Title | Date |\n| --- | --- | --- |\n"
                "| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n",
                encoding="utf-8")
            # RV-0002 is genuinely missing its row; the phantom 'RV0002' in the note table
            # must not suppress that finding.
            drift = reconcile.meta_index_drift(root)
            self.assertEqual([(x["kind"], x["id"]) for x in drift], [("missing-row", "RV-0002")])

    def test_missing_index_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rv = root / "sdlc-studio" / "reviews"
            rv.mkdir(parents=True, exist_ok=True)
            (rv / "RV0001-a.md").write_text("# a\n", encoding="utf-8")
            drift = reconcile.meta_index_drift(root)
            self.assertIn(("missing-index", "review"),
                          [(x["kind"], x["type"]) for x in drift])

    def test_apply_appends_missing_row_header_driven(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md", "RV0002-b.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n"])
            res = reconcile.apply_meta(root)
            self.assertEqual(res["appended"], ["RV-0002"])
            self.assertEqual(reconcile.meta_index_drift(root), [])  # now clean
            text = (root / "sdlc-studio" / "reviews" / "_index.md").read_text(encoding="utf-8")
            self.assertIn("[RV-0002](RV0002-b.md)", text)

    def test_detect_scope_meta_and_all_include_meta(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._reviews(root, ["RV0001-a.md", "RV0002-b.md"],
                          ["| [RV-0001](RV0001-a.md) | A | 2026-07-01 |\n"])
            # scope 'meta' runs ONLY the meta lane (exit 1 on drift)
            self.assertEqual(reconcile.main(["detect", "--scope", "meta", "--root", str(root)]), 1)
            # a single pipeline scope must NOT drag meta drift in
            self.assertEqual(reconcile.main(["detect", "--scope", "bugs", "--root", str(root)]), 0)


class DeadRowLinkTests(unittest.TestCase):
    """BG0135: the index is DERIVED, and reconcile is what makes that true - in BOTH
    directions. An index row that LINKS an artefact file is asserting that file exists;
    when the file is gone the row is a phantom, whatever its status.

    The blind spot was the status gate: a freshly-filed CR is `Proposed`, and a
    `Proposed` row with no file was read as an intentional reservation, so deleting the
    file left a phantom row that `detect` (drift_items=0), `apply` ("changed 0 row(s)")
    and `validate` (errors=0) all called clean. A reservation has no link; a link is a
    promise. Drive the public CLI - a guard that cannot fail is not a guard.
    """

    BASE = ("# CRs\n\n"
            "| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n| **Total** | **1** |\n\n"
            "## All Changes\n\n"
            "| ID | Title | Status |\n| --- | --- | --- |\n")

    def _repo(self, d: str, rows: str) -> Path:
        root = Path(d)
        cd = root / "sdlc-studio" / "change-requests"
        cd.mkdir(parents=True)
        (cd / "_index.md").write_text(self.BASE + rows, encoding="utf-8")
        return root

    def _detect(self, root: Path):
        return reconcile.detect_type("cr", root)["drift"]

    def test_proposed_row_linking_a_deleted_file_is_drift(self) -> None:
        # The exact BG0135 repro: file a CR (Proposed), delete its file, keep the row.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            drift = self._detect(root)
            kinds = {x["kind"] for x in drift}
            self.assertIn("dead-row-link", kinds)
            item = next(x for x in drift if x["kind"] == "dead-row-link")
            self.assertEqual(item["id"], "CR-0261")
            self.assertIn("CR0261-probe.md", item["file"])       # names the missing file
            # and the CLI must FAIL, not merely mention it
            self.assertEqual(reconcile.main(["detect", "--root", str(root)]), 1)

    def test_row_whose_file_exists_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            (root / "sdlc-studio" / "change-requests" / "CR0261-probe.md").write_text(
                "# CR-0261: Probe\n\n> **Status:** Proposed\n", encoding="utf-8")
            self.assertEqual(self._detect(root), [])
            self.assertEqual(reconcile.main(["detect", "--root", str(root)]), 0)

    def test_unlinked_reservation_row_is_still_not_drift(self) -> None:
        # The reservation exemption survives: a Proposed row with NO link claims no file.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| CR-0262 | Reserved | Proposed |\n")
            self.assertEqual(self._detect(root), [])

    def test_dead_link_and_orphan_row_are_not_double_counted(self) -> None:
        # A Complete row with a dead link is ONE finding (the precise one), not two.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0263](CR0263-gone.md) | Gone | Complete |\n")
            kinds = [x["kind"] for x in self._detect(root) if x["kind"] in
                     ("dead-row-link", "orphan-row")]
            self.assertEqual(kinds, ["dead-row-link"])

    def test_apply_never_prunes_a_dead_row_by_default(self) -> None:
        # A missing file can be a bad checkout, an in-flight rename or an unstaged file.
        # apply must NOT silently delete the row; detect must keep reporting it.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            reconcile.main(["apply", "--root", str(root)])
            text = (root / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertIn("CR-0261", text)
            self.assertIn("dead-row-link", {x["kind"] for x in self._detect(root)})

    def test_apply_warns_loudly_about_the_row_it_will_not_prune(self) -> None:
        # "changed 0 row(s)" over a phantom is how this survived the whole gate. apply
        # declines to prune, but it must never be SILENT about what it left behind.
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                reconcile.main(["apply", "--root", str(root)])
            self.assertIn("CR-0261", err.getvalue())
            self.assertIn("CR0261-probe.md", err.getvalue())

    def test_prune_orphans_flag_removes_the_row_and_recomputes_counts(self) -> None:
        # ...and only when the operator explicitly asks for it.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            reconcile.main(["apply", "--prune-orphans", "--root", str(root)])
            text = (root / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertNotIn("CR-0261", text)
            self.assertIn("| **Total** | **0** |", text)   # summary follows the rows
            self.assertEqual(self._detect(root), [])

    def test_archived_row_resolves_file_relative(self) -> None:
        # archive.py moves the ROW to `<type>/archive/<release>/` and leaves the FILE in the type
        # dir, so the archived row carries a `../../`-relative link back to it (BG0137). It
        # resolves file-relative to the sub-index - not a phantom. (BG0142 removed the old type-dir
        # fallback that tolerated a bare-name link; the correct form is the relative one.)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "")
            cd = root / "sdlc-studio" / "change-requests"
            (cd / "CR0100-shipped.md").write_text(
                "# CR-0100: Shipped\n\n> **Status:** Complete\n", encoding="utf-8")
            arch = cd / "archive" / "v1.0.0"
            arch.mkdir(parents=True)
            (arch / "cr.md").write_text(
                "| ID | Status |\n| --- | --- |\n"
                "| [CR-0100](../../CR0100-shipped.md) | Complete |\n",
                encoding="utf-8")
            self.assertNotIn("dead-row-link", {x["kind"] for x in self._detect(root)})

    def test_archived_row_with_no_file_is_reported_but_never_pruned_here(self) -> None:
        # A phantom in an archive sub-index is reported - but archive.py is the ONE archive
        # writer, so reconcile refuses to edit its files and says so (exit 1, nothing lost).
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "")
            arch = root / "sdlc-studio" / "change-requests" / "archive" / "v1.0.0"
            arch.mkdir(parents=True)
            sub = arch / "cr.md"
            sub.write_text(
                "| ID | Status |\n| --- | --- |\n| [CR-0101](CR0101-gone.md) | Complete |\n",
                encoding="utf-8")
            self.assertIn("dead-row-link", {x["kind"] for x in self._detect(root)})
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = reconcile.main(["apply", "--prune-orphans", "--root", str(root)])
            self.assertEqual(rc, 1)                               # asked, could not comply
            self.assertIn("CR-0101", sub.read_text(encoding="utf-8"))   # row untouched
            self.assertIn("archive", err.getvalue())

    def test_prune_leaves_an_unlinked_orphan_row_alone(self) -> None:
        # An inline-only record (no link) holds its ONLY copy in that row - never prune it.
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, "| CR-0264 | inline-only | Complete |\n")
            reconcile.main(["apply", "--prune-orphans", "--root", str(root)])
            text = (root / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertIn("inline-only", text)
            self.assertIn("orphan-row", {x["kind"] for x in self._detect(root)})


class EpicDerivedPointTotalTests(unittest.TestCase):
    """CR0268: an epic's point total is DERIVED - the sum of its stories' points, recomputed by
    reconcile so it can never drift from the stories beneath it. An epic is T-shirt sized (Size),
    never pointed, and a Size is never summed into the roll-up."""

    @staticmethod
    def _fixture(root: Path, declared: str = "0", points=(3, 5, 2)) -> Path:
        ed = root / "sdlc-studio" / "epics"
        ed.mkdir(parents=True, exist_ok=True)
        (ed / "EP0001-alpha.md").write_text(
            "# EP0001: Alpha\n\n> **Status:** In Progress\n\n## Sizing\n\n"
            "**Size:** L\n\n"
            "_T-shirt estimate, made before decomposition._\n\n"
            f"**Derived Point Total:** {declared}\n\n"
            "_DERIVED - recomputed by reconcile._\n", encoding="utf-8")
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(points, 1):
            (sd / f"US000{i}-s{i}.md").write_text(
                f"# US000{i}: Story {i}\n\n> **Status:** Draft\n"
                f"> **Epic:** EP0001\n> **Points:** {p}\n", encoding="utf-8")
        return root

    def test_roll_up_is_the_sum_of_story_points(self) -> None:
        # Three stories of 3+5+2 have a DERIVED total of 10; a stale declared 0 is drift, and
        # apply writes the computed 10. The load-bearing behaviour.
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d), declared="0")
            self.assertEqual([(x["id"], x["kind"]) for x in reconcile.epic_points_drift(root)],
                             [("EP0001", "epic-points-stale")])
            reconcile.apply_epic_points(root)
            text = (root / "sdlc-studio" / "epics" / "EP0001-alpha.md").read_text(encoding="utf-8")
            self.assertIn("**Derived Point Total:** 10", text)
            self.assertIn("_DERIVED - recomputed by reconcile._", text)  # the note survives
            self.assertEqual(reconcile.epic_points_drift(root), [])          # now clean
            self.assertEqual(reconcile.apply_epic_points(root)["synced"], [])  # idempotent

    def test_changing_a_story_updates_the_epic_total(self) -> None:
        # In sync at 10, then a story goes 3 -> 8: the roll-up must follow to 15.
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d), declared="10")
            self.assertEqual(reconcile.epic_points_drift(root), [])
            s1 = root / "sdlc-studio" / "stories" / "US0001-s1.md"
            s1.write_text(s1.read_text(encoding="utf-8").replace(
                "**Points:** 3", "**Points:** 8"), encoding="utf-8")
            self.assertEqual([x["kind"] for x in reconcile.epic_points_drift(root)],
                             ["epic-points-stale"])
            reconcile.apply_epic_points(root)
            text = (root / "sdlc-studio" / "epics" / "EP0001-alpha.md").read_text(encoding="utf-8")
            self.assertIn("**Derived Point Total:** 15", text)

    def test_a_size_is_never_summed_and_a_legacy_epic_never_drifts(self) -> None:
        # An epic that declares only a T-shirt Size (no Derived Point Total field) asserts no
        # roll-up: it is never flagged, and its Size is never read as a number to sum.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0002-beta.md").write_text(
                "# EP0002: Beta\n\n> **Status:** In Progress\n\n## Sizing\n\n**Size:** XL\n",
                encoding="utf-8")
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0009-x.md").write_text(
                "# US0009: X\n\n> **Status:** Draft\n> **Epic:** EP0002\n> **Points:** 8\n",
                encoding="utf-8")
            self.assertEqual(reconcile.epic_points_drift(root), [])
            self.assertEqual(reconcile.apply_epic_points(root)["synced"], [])

    def test_detect_surfaces_the_roll_up_on_the_epics_scope(self) -> None:
        # The public path: `detect --scope epics` must carry the stale roll-up in its drift list.
        import argparse
        import io
        import json
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture(Path(d), declared="4")  # declared 4, stories sum to 10
            buf = io.StringIO()
            with redirect_stdout(buf):
                reconcile.cmd_detect(argparse.Namespace(
                    root=str(root), scope="epics", format="json",
                    write_report=False, blocker_sweep=False))
            report = json.loads(buf.getvalue())
            kinds = {x["kind"] for x in report["drift"]}
            self.assertIn("epic-points-stale", kinds)


class ArchiveLinkFallbackTests(unittest.TestCase):
    """BG0142: `_link_exists` resolves a row's link ONLY file-relative to the index that carries
    it - no type-dir fallback. An archived row carries a `../../`-relative link and resolves; a
    regressed BARE-name archive link (the old wrong-depth form the fallback used to tolerate) is
    now reported as a dead link, agreeing with `check_links`."""

    def _fixture(self, repo: Path) -> None:
        sd = repo / "sdlc-studio" / "stories"
        (sd / "archive" / "v1").mkdir(parents=True)
        # two real files live in the type dir (archive moves the ROW, not the FILE)
        (sd / "US0001-good.md").write_text("# US0001: g\n\n> **Status:** Done\n", encoding="utf-8")
        (sd / "US0002-bare.md").write_text("# US0002: b\n\n> **Status:** Done\n", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n| Status | Count |\n|---|---|\n| Done | 2 |\n", encoding="utf-8")

    def test_correct_relative_archive_link_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._fixture(repo)
            (repo / "sdlc-studio" / "stories" / "archive" / "v1" / "story.md").write_text(
                "# Archived\n\n| ID | Title | Status |\n|---|---|---|\n"
                "| [US0001](../../US0001-good.md) | g | Done |\n", encoding="utf-8")
            dead = [x["id"] for x in reconcile._dead_row_links("story", repo)]
            self.assertNotIn("US0001", dead)   # ../../ resolves file-relative

    def test_bare_name_archive_link_is_now_reported_dead(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            self._fixture(repo)
            # the regressed form: a bare filename. The file exists in the TYPE DIR, so the old
            # type-dir fallback tolerated it; file-relative from archive/v1 it does not resolve.
            (repo / "sdlc-studio" / "stories" / "archive" / "v1" / "story.md").write_text(
                "# Archived\n\n| ID | Title | Status |\n|---|---|---|\n"
                "| [US0002](US0002-bare.md) | b | Done |\n", encoding="utf-8")
            dead = [x["id"] for x in reconcile._dead_row_links("story", repo)]
            self.assertIn("US0002", dead)      # no fallback: the regression is caught


class DriftKindVocabularyTests(unittest.TestCase):
    """DRIFT_KINDS must be the true emission vocabulary, not a restated answer key.

    The remediation guard (test_sdlc_md) derives its expected reconcile key set from
    reconcile.DRIFT_KINDS; if that tuple could silently drift from the detectors, the
    guard would inherit the same blind spot the bug exists to kill. This ties the
    tuple to what the module actually emits by scanning the source for `"kind":`
    literals - so a detector that emits a new kind not in DRIFT_KINDS reddens here.
    """

    def test_drift_kinds_matches_kinds_emitted_in_source(self) -> None:
        src = SCRIPT_PATH.read_text(encoding="utf-8")
        emitted = set(re.findall(r'"kind":\s*"([a-z-]+)"', src))
        self.assertEqual(
            emitted, set(reconcile.DRIFT_KINDS),
            "DRIFT_KINDS drifted from the `\"kind\":` literals the detectors emit")


CR_INDEX_HEADER = (
    "# Change Requests\n\n"
    "| Status | Count |\n|---|---|\n| Complete | 1 |\n\n"
    "| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
    "|---|---|---|---|---|---|---|\n")


def _cr_fixture(root: Path, decomposed: str | None = "EP0007",
                cell: str = "--") -> Path:
    """A CR whose file names its epic while the index row shows a placeholder."""
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    body = "# CR-0001: c\n\n> **Status:** Complete\n"
    if decomposed:
        body += f"> **Decomposed-into:** {decomposed}\n"
    body += "\n## Summary\n\nx\n"
    (d / "CR0001-c.md").write_text(body, encoding="utf-8")
    (d / "_index.md").write_text(
        CR_INDEX_HEADER
        + f"| [CR-0001](CR0001-c.md) | c | Complete | Medium | Improvement | 2026-07-19 | {cell} |\n",
        encoding="utf-8")
    return d / "_index.md"


class LinkedEpicsCensusTests(unittest.TestCase):
    """US0256 AC1: a Linked Epics cell that contradicts the file is drift.

    The column shipped as a placeholder and stayed one: across this workspace all 63 CRs
    carrying a real `Decomposed-into` showed `--`. A column nothing derives is a column
    nobody can trust, so the census reads the files and reports the disagreement.
    """

    def test_a_placeholder_cell_over_a_decomposed_cr_is_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_fixture(root)
            drift = reconcile.detect_linked_epics(root)["drift"]
            self.assertEqual(len(drift), 1, drift)
            self.assertEqual(drift[0]["id"], "CR0001")
            self.assertEqual(drift[0]["expected"], "EP0007")

    def test_a_cell_that_already_matches_is_not_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_fixture(root, cell="EP0007")
            self.assertEqual(reconcile.detect_linked_epics(root)["drift"], [])

    def test_a_cr_that_was_never_decomposed_is_not_drift(self) -> None:
        """An undecomposed CR has no epic to name; a placeholder is the honest cell."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_fixture(root, decomposed=None)
            self.assertEqual(reconcile.detect_linked_epics(root)["drift"], [])

    def test_multiple_epics_are_compared_whole(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_fixture(root, decomposed="EP0041, EP0081", cell="EP0041")
            drift = reconcile.detect_linked_epics(root)["drift"]
            self.assertEqual(len(drift), 1)
            self.assertEqual(drift[0]["expected"], "EP0041, EP0081")


class LinkedEpicsApplyTests(unittest.TestCase):
    """US0256 AC2: apply writes the column from the files, and only that column."""

    def test_apply_syncs_the_cell_from_the_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _cr_fixture(root)
            res = reconcile.apply_linked_epics(root)
            self.assertEqual(res["synced"], ["CR0001"])
            row = [l for l in idx.read_text(encoding="utf-8").splitlines()
                   if l.startswith("| [CR-0001]")][0]
            self.assertTrue(row.rstrip().endswith("| EP0007 |"), row)
            self.assertIn("| Complete |", row)   # the other cells survive
            self.assertIn("| 2026-07-19 |", row)

    def test_apply_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr_fixture(root)
            reconcile.apply_linked_epics(root)
            self.assertEqual(reconcile.apply_linked_epics(root)["synced"], [])

    def test_a_pipe_inside_a_cell_does_not_shift_the_columns(self) -> None:
        """An escaped pipe in a cell must not move every cell after it.

        Splitting on every `|` counts an escaped one as a separator, so the header-located
        column index then addresses the WRONG cell: the epic id was written over the Date,
        destroying it, while the Linked Epics cell stayed `--` so the next run re-drifted.
        Locating the column by header does not help once the cell count is wrong.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cr = root / "sdlc-studio" / "change-requests"
            cr.mkdir(parents=True)
            (cr / "CR0001-x.md").write_text(
                "# CR-0001: x\n\n> **Status:** Complete\n> **Decomposed-into:** EP0078\n",
                encoding="utf-8")
            row = (r"| [CR-0001](CR0001-x.md) | Support the a \| b operator | Complete "
                   r"| P2 | Improvement | 2026-07-14 | -- |")
            idx = cr / "_index.md"
            idx.write_text(CR_INDEX_HEADER + row + "\n", encoding="utf-8")

            drift = reconcile.detect_linked_epics(root)["drift"]
            self.assertEqual(drift[0]["found"], "--",
                             "detect read the wrong cell: it is reporting the Date column")

            reconcile.apply_linked_epics(root)
            after = [l for l in idx.read_text(encoding="utf-8").splitlines()
                     if l.startswith("| [CR-0001]")][0]
            self.assertIn("2026-07-14", after, "the Date cell was destroyed")
            self.assertIn(r"\|", after, "the escaped pipe was broken apart")
            self.assertTrue(after.rstrip().endswith("| EP0078 |"), after)

    def test_apply_is_idempotent_with_an_escaped_pipe(self) -> None:
        """The re-drift half: a corrupted write leaves the real cell untouched, so the
        next run finds the same drift and corrupts the row again."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cr = root / "sdlc-studio" / "change-requests"
            cr.mkdir(parents=True)
            (cr / "CR0001-x.md").write_text(
                "# CR-0001: x\n\n> **Status:** Complete\n> **Decomposed-into:** EP0078\n",
                encoding="utf-8")
            idx = cr / "_index.md"
            idx.write_text(CR_INDEX_HEADER + (
                r"| [CR-0001](CR0001-x.md) | a \| b | Complete | P2 | Improvement "
                r"| 2026-07-14 | -- |") + "\n", encoding="utf-8")
            reconcile.apply_linked_epics(root)
            self.assertEqual(reconcile.apply_linked_epics(root)["synced"], [],
                             "still drifting after apply - the wrong cell was written")

    def test_dry_run_reports_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _cr_fixture(root)
            before = idx.read_text(encoding="utf-8")
            res = reconcile.apply_linked_epics(root, dry_run=True)
            self.assertEqual(res["synced"], ["CR0001"])
            self.assertEqual(idx.read_text(encoding="utf-8"), before)


sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import loader  # noqa: E402  - the shared script importer, used by the sweep tests below

NOT_UTF8 = b"# US0003: corrupt\n\n> **Status:** Draft\n\xff\xfe not utf8\n"


def _corrupt_workspace(root: Path) -> None:
    """A workspace holding one healthy artefact and one non-UTF-8 artefact per scanned type,
    plus a non-UTF-8 deploy ledger - the half-written wreckage a crashed session leaves."""
    ws = root / "sdlc-studio"
    for sub, healthy, corrupt in (
        ("stories", "US0001-login.md", "US0003-corrupt.md"),
        ("bugs", "BG0001-x.md", "BG0003-corrupt.md"),
        ("epics", "EP0001-e.md", "EP0003-corrupt.md"),
        ("test-specs", "TS0001-s.md", "TS0003-corrupt.md"),
        ("change-requests", "CR0001-c.md", "CR0003-corrupt.md"),
        ("rfcs", "RFC0001-r.md", "RFC0003-corrupt.md"),
        ("issues", "IS0001-i.md", "IS0003-corrupt.md"),
    ):
        d = ws / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / healthy).write_text(
            f"# {healthy.split('-')[0]}: ok\n\n> **Status:** Draft\n> **Epic:** EP0001\n"
            "\n## Acceptance Criteria\n\n### AC1: ok\n\n- **Verify:** manual eyeball\n",
            encoding="utf-8",
        )
        (d / corrupt).write_bytes(NOT_UTF8)
    (ws / "deploy-log.md").write_bytes(NOT_UTF8)


class NonUtf8ScannerRegressionTests(unittest.TestCase):
    """Every swept scanner completes over a workspace holding a non-UTF-8 artefact.

    Before the sweep each of these raised UnicodeDecodeError and aborted the whole pass - one
    corrupt file from a crashed session took the entire workspace scan down with it.
    """

    def test_status_scanners_survive(self) -> None:
        status = loader.load_script("status")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corrupt_workspace(root)
            census = status.backlog(root)
            self.assertTrue(census, "backlog censused nothing - the scan did not reach the tree")
            self.assertIsInstance(status.discovery_awaiting(root), dict)
            self.assertIsInstance(status.tranche_members(root, "T1"), list)

    def test_verify_ac_scanners_survive(self) -> None:
        verify_ac = loader.load_script("verify_ac")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corrupt_workspace(root)
            stories = sorted((root / "sdlc-studio" / "stories").glob("*.md"))
            self.assertEqual(len(stories), 2)
            self.assertIsInstance(verify_ac.duplicate_verifiers(stories), list)
            self.assertIsInstance(verify_ac.epic_stories(root, "EP0001"), list)
            self.assertIn("AC Coverage Matrix", verify_ac.scaffold_ac_matrix(root, "EP0001"))
            self.assertIsInstance(verify_ac.epic_test_spec_check(root, "EP0001"), dict)
            corrupt = root / "sdlc-studio" / "stories" / "US0003-corrupt.md"
            self.assertIsInstance(verify_ac.ts_check(corrupt), list)

    def test_verify_story_survives_and_names_the_file(self) -> None:
        """A body that reads back empty must be NAMED, not counted as a clean zero-AC pass -
        the whole point of the default is that something downstream says so."""
        verify_ac = loader.load_script("verify_ac")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corrupt_workspace(root)
            corrupt = root / "sdlc-studio" / "stories" / "US0003-corrupt.md"
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                report = verify_ac.verify_story(corrupt, True, 5, root, allow_shell=False)
            self.assertEqual(report.ac_count, 0)
            self.assertIn("US0003-corrupt.md", buf.getvalue())
            self.assertIn("unreadable", buf.getvalue().lower())

    def test_deploy_metrics_survives(self) -> None:
        deploy = loader.load_script("deploy")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corrupt_workspace(root)
            out = deploy.metrics(root)
            self.assertTrue(out["applicable"], "an unreadable ledger must not read as absent")


class LoudIndexReadTests(unittest.TestCase):
    """The opposite direction: an index read stays bare and loud.

    A missing or corrupt `_index.md` is a real error. Defaulting it to an empty body would
    report "no rows" and mask exactly the derived-index drift reconcile exists to catch, so
    these reads must keep raising. If a future sweep makes everything safe, this goes red.
    """

    def test_corrupt_index_raises_rather_than_reading_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            (root / "sdlc-studio" / "stories" / "_index.md").write_bytes(NOT_UTF8)
            with self.assertRaises(UnicodeDecodeError):
                reconcile.parse_index("story", root)

    def test_a_healthy_index_still_parses(self) -> None:
        """Guards the test above: it must fail on the corruption, not on a broken call."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            parsed = reconcile.parse_index("story", root)
            self.assertTrue(parsed["exists"])
            self.assertIn("US0001", parsed["rows"])

    def test_a_missing_index_is_reported_not_defaulted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            (root / "sdlc-studio" / "stories" / "_index.md").unlink()
            self.assertFalse(reconcile.parse_index("story", root)["exists"])

class DerivableRequestDriftTests(unittest.TestCase):
    """CR0364: G2 was a gate with no counterpart.

    `transition._request_terminal_gate` REFUSES a request reaching its successful terminal until
    every child resolves. Nothing ever performed the closure once it was earned, so on this repo
    34 of 59 open CRs sat In Progress with every delivering epic already Done, and the discovery
    backlog over-reported remaining work by roughly 44 per cent while reconcile reported zero
    drift.

    The detector must ask the GATE rather than reimplement "are the children resolved". Two
    answers to one question is how BG0207 and BG0211 both happened.
    """

    def _repo(self, enforce=True):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        root = Path(d.name)
        (root / "sdlc-studio").mkdir(parents=True)
        if enforce:
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "two_backlog:\n  enforce: true\n", encoding="utf-8")
        return root

    def _cr(self, root, cid="CR0001", status="In Progress", children=("US0001",), parent=None):
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        into = f"> **Decomposed-into:** {', '.join(children)}\n" if children else ""
        par = f"> **Parent:** {parent}\n" if parent else ""
        (d / f"{cid}-x.md").write_text(
            f"# CR-{cid[2:]}: c\n\n> **Status:** {status}\n> **Size:** M\n{par}{into}\n"
            "## Summary\n\nx\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# CRs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [{cid}]({cid}-x.md) | c | {status} |\n", encoding="utf-8")

    def _story(self, root, sid, status, parent="CR0001"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}-s.md").write_text(
            f"# {sid}: s\n\n> **Status:** {status}\n> **Parent:** {parent}\n> **Points:** 2\n",
            encoding="utf-8")
        # The row carries the story's REAL status. A placeholder here is not inert: the sweep
        # cannot rewrite it, so every apply in this class reported a spurious unapplied row and
        # any count assertion had to be loosened around noise the fixture invented.
        rows = "".join(
            f"| [{p.stem.split('-')[0]}]({p.name}) | s | "
            f"{reconcile.sdlc_md.extract_field(p.read_text(encoding='utf-8'), 'Status')} |\n"
            for p in sorted(d.glob("US*.md")))
        (d / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n" + rows, encoding="utf-8")

    def _kinds(self, root):
        return reconcile.derivable_request_drift(root)

    def test_a_request_with_all_children_resolved_is_reported(self):
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        got = self._kinds(root)
        self.assertEqual(len(got), 1, got)
        self.assertEqual(got[0]["id"], "CR0001")
        self.assertIn(got[0]["kind"], reconcile.DRIFT_KINDS)

    def test_the_derivable_kind_is_registered(self):
        """Registered in BOTH places a kind has to appear, which is what makes this test carry
        weight the reporting tests do not: as a known kind, and with a fix hint. A kind missing
        from the remediation registry reports drift an operator has no documented route to
        clear."""
        self.assertIn("request-derivable", reconcile.DRIFT_KINDS)
        hint = reconcile.sdlc_md.REMEDIATION["reconcile"].get("request-derivable", "")
        self.assertIn("reconcile apply", hint)
        self.assertIn("CANNOT clear", hint)   # the blocked case is documented, not just the happy one

    def test_detector_delegates_to_the_g2_gate(self):
        """AC2: swap the gate's verdict and the detector must follow.

        A detector carrying its own child-resolution logic would keep reporting the request as
        derivable and pass every other test in this class.
        """
        import transition
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        self.assertEqual(len(self._kinds(root)), 1)      # derivable via the real gate
        original = transition._request_terminal_gate
        try:
            transition._request_terminal_gate = lambda *a, **k: "SENTINEL refusal"
            self.assertEqual(self._kinds(root), [],
                             "the detector reimplements the gate instead of calling it")
        finally:
            transition._request_terminal_gate = original

    def test_a_childless_request_is_never_derivable(self):
        root = self._repo()
        self._cr(root, children=())
        self.assertEqual(self._kinds(root), [])

    def test_one_unresolved_child_blocks_derivation(self):
        root = self._repo()
        self._cr(root, children=("US0001", "US0002"))
        self._story(root, "US0001", "Done")
        self._story(root, "US0002", "In Progress")
        self.assertEqual(self._kinds(root), [])

    def test_a_dropped_child_counts_as_resolved(self):
        root = self._repo()
        self._cr(root, children=("US0001", "US0002"))
        self._story(root, "US0001", "Done")
        self._story(root, "US0002", "Won't Implement")
        self.assertEqual(len(self._kinds(root)), 1)

    def test_unenforced_project_reports_no_derivable_requests(self):
        root = self._repo(enforce=False)
        self._cr(root)
        self._story(root, "US0001", "Done")
        # Through the CLI sweep, which is where the two_backlog gating lives - calling the
        # detector directly would bypass the very condition under test.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "detect"])
        self.assertNotIn("request-derivable", buf.getvalue())
        # ...and the same workspace WITH enforcement does report it, so this is not vacuous.
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "two_backlog:\n  enforce: true\n", encoding="utf-8")
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "detect"])
        self.assertIn("request-derivable", buf2.getvalue())

    def test_apply_derives_the_request_terminal(self):
        """Through `reconcile apply`, the COMMAND - not the function it calls.

        The first version of this test called `apply_derivable_requests` directly and passed
        while the CLI did nothing at all, because the function was never wired into `cmd_apply`.
        The AC says "when reconcile apply runs"; testing the helper tests a different claim.
        """
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "apply"])
        body = (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text(encoding="utf-8")
        self.assertIn("> **Status:** Complete", body)
        self.assertIn("derived CR0001", buf.getvalue())

    def test_apply_dry_run_changes_nothing(self):
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "apply", "--dry-run"])
        body = (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text(encoding="utf-8")
        self.assertIn("> **Status:** In Progress", body)
        self.assertIn("WOULD derive CR0001", buf.getvalue())

    def test_apply_goes_through_transition(self):
        # AC2: not a direct file write - the index cascade and telemetry must still run.
        import transition
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        seen = []
        original = transition.transition
        try:
            def spy(r, aid, status, **kw):
                seen.append((aid, status))
                return original(r, aid, status, **kw)
            transition.transition = spy
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                reconcile.apply_derivable_requests(root)
        finally:
            transition.transition = original
        self.assertEqual(seen, [("CR0001", "Complete")])
        idx = (root / "sdlc-studio" / "change-requests" / "_index.md").read_text(encoding="utf-8")
        self.assertIn("Complete", idx)

    def test_apply_is_idempotent(self):
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            reconcile.apply_derivable_requests(root)
            again = reconcile.derivable_request_drift(root)
        self.assertEqual(again, [])

    # --- A request whose G2 gate passes but which a LATER gate still refuses. ---------------
    # G2 is not the only gate on the road to a terminal, and every fixture above uses a CR with
    # a clean ladder, so none of them can tell an honest preflight from a dishonest one. This is
    # the production shape: RFC0046's children were all resolved and its accept gate still
    # refused on an open decision.

    def _rfc_with_open_decision(self, root, rid="RFC0001", status="In Review"):
        d = root / "sdlc-studio" / "rfcs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{rid}-r.md").write_text(
            f"# {rid}: r\n\n> **Status:** {status}\n> **Decomposed-into:** CR0001\n\n"
            "## Decisions\n\n| ID | Question | Status |\n| --- | --- | --- |\n"
            "| D1 | should we | Open |\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [{rid}]({rid}-r.md) | r | {status} |\n", encoding="utf-8")

    def _resolved_rfc_child(self, root, rid="RFC0001"):
        """The RFC's only child CR, already Complete - so G2 itself is satisfied and the only
        thing left standing between the RFC and Accepted is the accept gate."""
        self._cr(root, status="Complete", children=("US0001",), parent=rid)
        self._story(root, "US0001", "Done")

    def test_dry_run_reports_the_refusal_a_real_run_would_hit(self):
        """The preflight must not promise a derivation the real sweep refuses.

        The first cut appended the id and skipped `transition` entirely on a dry run, so only
        the G2 gate was ever consulted: `apply --dry-run` said 36 where `apply` delivered 35.
        """
        root = self._repo()
        self._rfc_with_open_decision(root)
        self._resolved_rfc_child(root)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            dry = reconcile.apply_derivable_requests(root, dry_run=True)
            real = reconcile.apply_derivable_requests(root, dry_run=False)
        self.assertEqual(dry["synced"], [], "dry run promised a derivation the gate refuses")
        self.assertEqual([u["id"] for u in dry["unapplied"]], ["RFC0001"])
        # The whole point: preflight and real run agree.
        self.assertEqual(dry["synced"], real["synced"])
        self.assertEqual([u["id"] for u in dry["unapplied"]],
                         [u["id"] for u in real["unapplied"]])
        # ...and the dry run wrote nothing.
        body = (root / "sdlc-studio" / "rfcs" / "RFC0001-r.md").read_text(encoding="utf-8")
        self.assertIn("> **Status:** In Review", body)

    def test_a_refused_derivation_is_returned_as_data_not_only_printed(self):
        root = self._repo()
        self._rfc_with_open_decision(root)
        self._resolved_rfc_child(root)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            res = reconcile.apply_derivable_requests(root)
        self.assertEqual(len(res["unapplied"]), 1, res)
        u = res["unapplied"][0]
        self.assertEqual((u["id"], u["target"]), ("RFC0001", "Accepted"))
        self.assertIn("Open decision", u["reason"])

    def test_a_refused_derivation_drives_a_non_zero_exit(self):
        """Every other unapplied path in `cmd_apply` fails the command; this one exited 0, so a
        CI running `reconcile apply` could not see that a derivation had been refused."""
        root = self._repo()
        self._rfc_with_open_decision(root)
        self._resolved_rfc_child(root)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = reconcile.main(["--root", str(root), "apply"])
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("could NOT derive RFC0001", buf.getvalue())
        self.assertIn("1 could not be applied", buf.getvalue())

    def test_the_json_path_surfaces_a_refusal(self):
        """A programmatic caller saw `{"synced": [...]}` only, so a blocked run read as clean."""
        root = self._repo()
        self._rfc_with_open_decision(root)
        self._resolved_rfc_child(root)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = reconcile.main(["--root", str(root), "apply", "--format", "json"])
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["unapplied"], 1)
        self.assertEqual(
            [u["id"] for u in payload["by_type"]["derivable_requests"]["unapplied"]], ["RFC0001"])

    def test_the_fix_hint_does_not_advertise_a_command_that_cannot_work(self):
        """A drift item whose remedy is guaranteed to refuse is a loop with no exit."""
        root = self._repo()
        self._rfc_with_open_decision(root)
        self._resolved_rfc_child(root)
        got = [d for d in reconcile.derivable_request_drift(root) if d["id"] == "RFC0001"]
        self.assertEqual(len(got), 1, got)
        self.assertTrue(got[0]["blocked_by"], "the blocking gate was not recorded")
        self.assertIn("CANNOT clear", got[0]["fix"])

    def test_an_unblocked_request_still_advertises_apply(self):
        """The counterpart to the test above - otherwise 'never advertise apply' would pass it."""
        root = self._repo()
        self._cr(root)
        self._story(root, "US0001", "Done")
        d = self._kinds(root)[0]
        self.assertIsNone(d["blocked_by"])
        self.assertIn("`reconcile apply` sets it Complete", d["fix"])

    def test_apply_is_gated_by_two_backlog_not_only_detect(self):
        """The apply-side guard had no test: mutating BOTH `cmd_apply` guards to drop the
        `two_backlog_enforced` clause left this class entirely green. An unenforced project
        closes its requests by assertion, so nothing here may move them."""
        root = self._repo(enforce=False)
        self._cr(root)
        self._story(root, "US0001", "Done")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "apply"])
        body = (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text(encoding="utf-8")
        self.assertIn("> **Status:** In Progress", body)
        self.assertNotIn("derived CR0001", buf.getvalue())
        # ...and the same workspace WITH enforcement does derive it, so this is not vacuous.
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "two_backlog:\n  enforce: true\n", encoding="utf-8")
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "apply"])
        body2 = (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text(encoding="utf-8")
        self.assertIn("> **Status:** Complete", body2)

    def test_apply_is_gated_by_two_backlog_in_the_json_path_too(self):
        """Both `cmd_apply` guards are real: the JSON path has its own."""
        root = self._repo(enforce=False)
        self._cr(root)
        self._story(root, "US0001", "Done")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            reconcile.main(["--root", str(root), "apply", "--format", "json"])
        payload = json.loads(buf.getvalue())
        self.assertNotIn("derivable_requests", payload["by_type"])

if __name__ == "__main__":
    unittest.main()
