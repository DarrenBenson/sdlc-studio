"""Unit tests for reconcile.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
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
            self.assertIn(("orphan-row", "US0099"), kinds)        # row, no file
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
        # orphan-row stays report-only - removing history is never mechanical
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            res = reconcile.apply_type("story", root)
            self.assertEqual(res["appended"], ["US0002"])
            kinds = {dd["kind"] for dd in reconcile.detect_type("story", root)["drift"]}
            self.assertNotIn("missing-row", kinds)  # US0002 appended
            self.assertIn("orphan-row", kinds)       # US0099 not removed


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


if __name__ == "__main__":
    unittest.main()


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
        orphan = self.BASE + "| [CR-0099](CR0099-gone.md) | gone | Complete |\n"
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, orphan)
            reconcile.apply_type("cr", repo)
            text = (repo / "sdlc-studio" / "change-requests" / "_index.md").read_text(
                encoding="utf-8")
            self.assertIn("CR-0099", text)                   # never removed
            kinds = [x["kind"] for x in reconcile.detect_type("cr", repo)["drift"]]
            self.assertIn("orphan-row", kinds)               # still reported
