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

    def test_apply_leaves_structural_classes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            reconcile.apply_type("story", root)
            kinds = {dd["kind"] for dd in reconcile.detect_type("story", root)["drift"]}
            self.assertIn("missing-row", kinds)   # US0002 not added
            self.assertIn("orphan-row", kinds)    # US0099 not removed


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


if __name__ == "__main__":
    unittest.main()
