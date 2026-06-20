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
        # must be read against its own header, not the first table's (agent-crew).
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


if __name__ == "__main__":
    unittest.main()
