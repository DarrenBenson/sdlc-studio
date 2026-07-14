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


def _cr_repo(root: Path) -> Path:
    sd = root / "sdlc-studio" / "change-requests"
    sd.mkdir(parents=True)
    (sd / "_index.md").write_text(
        "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Complete | 1 |\n| Deferred | 1 |\n\n"
        "## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| [CR-0001](CR0001-x.md) | done thing | Complete | Medium | Feature | 2026-01-01 | - |\n"
        "| [CR-0002](CR0002-x.md) | paused thing | Deferred | Medium | Feature | 2026-01-01 | - |\n",
        encoding="utf-8")
    return root


class DeferredNotTerminalTests(unittest.TestCase):
    def test_deferred_cr_not_archived_by_default(self) -> None:
        # BG0061: Deferred is re-activatable, NOT terminal (sdlc_md.terminal_statuses is the
        # single source). archive.py must not treat it as closed and move it out of the index.
        with tempfile.TemporaryDirectory() as d:
            root = _cr_repo(Path(d))
            res = arc.archive(root, "cr", "r1")
            self.assertEqual(res["archived"], ["CR-0001"])         # only the Complete row
            self.assertNotIn("CR-0002", res["archived"])           # Deferred stays live
            idx = (root / "sdlc-studio" / "change-requests" / "_index.md").read_text("utf-8")
            self.assertIn("CR-0002", idx)                          # still in the live index

    def test_statuses_override_can_still_include_deferred(self) -> None:
        # The explicit --statuses override is honoured (operator opt-in).
        with tempfile.TemporaryDirectory() as d:
            root = _cr_repo(Path(d))
            res = arc.archive(root, "cr", "r1", statuses={"Deferred"})
            self.assertEqual(res["archived"], ["CR-0002"])


class MultiViewNoDoubleArchiveTests(unittest.TestCase):
    """US0078/CR0182: a multi-view index (master + a trailing view table sharing a row) must
    archive each terminal row exactly once - the master row moves, the view row is kept."""

    def _multiview(self, root: Path) -> Path:
        sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            "# US0001: x\n\n> **Status:** Done\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n",
            encoding="utf-8")
        idx = sd / "_index.md"
        idx.write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 1 |\n\n"
            "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | x | Done |\n\n"
            "## Stories by Epic\n\n| Epic | Story | Status |\n| --- | --- | --- |\n"
            "| EP0001 | [US0001](US0001-x.md) | Done |\n", encoding="utf-8")
        return idx

    def test_release_archiver_moves_master_row_once(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); idx = self._multiview(root)
            arc.archive(root, "story", "r1")
            archived = (root / "sdlc-studio" / "stories" / "archive" / "r1" / "story.md").read_text("utf-8")
            self.assertEqual(archived.count("US0001-x.md"), 1)   # archived exactly once
            self.assertEqual(idx.read_text("utf-8").count("US0001-x.md"), 1)  # view row kept

    def _multiview_full_header(self, root: Path) -> Path:
        """A view sub-table with the SAME full `| ID | Title | Status |` header as the master -
        the shape that made an older archiver move the shared row TWICE (this fixture fails on
        pre-refactor code, so it genuinely locks the double-archive regression)."""
        sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
        for n in (1, 2):
            (sd / f"US000{n}-x.md").write_text(
                f"# US000{n}: x\n\n> **Status:** Done\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n",
                encoding="utf-8")
        idx = sd / "_index.md"
        idx.write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Done | 2 |\n\n"
            "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | x | Done |\n| [US0002](US0002-x.md) | x | Done |\n\n"
            "## Recently closed\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | x | Done |\n", encoding="utf-8")  # view subset, full header
        return idx

    def test_no_double_archive_with_full_header_view(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); idx = self._multiview_full_header(root)
            arc.archive(root, "story", "r1")
            archived = (root / "sdlc-studio" / "stories" / "archive" / "r1" / "story.md").read_text("utf-8")
            self.assertEqual(archived.count("US0001-x.md"), 1)   # once (an older writer moved it twice)
            self.assertEqual(archived.count("US0002-x.md"), 1)
            self.assertEqual(idx.read_text("utf-8").count("US0001-x.md"), 1)   # view row kept


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


class SingleArchiverTests(unittest.TestCase):
    """US0098/CR0182 AC1: one shared table walker; archive.py keeps no private walker."""

    def test_archive_py_has_no_private_table_walker(self):
        for name in ("_master_header", "_terminal_rows", "_table_end", "_id_col"):
            self.assertFalse(hasattr(arc, name), f"{name} should be removed (delegates to reconcile)")

    def test_the_archiver_delegates_to_the_shared_helper(self):
        self.assertTrue(hasattr(rc, "master_terminal_rows"))   # the shared READ side stays
        arc_src = (SCRIPT.parent / "archive.py").read_text(encoding="utf-8")
        self.assertIn("master_terminal_rows", arc_src)         # the one archiver delegates


class OneArchiveWriterTests(unittest.TestCase):
    """One archive layout, one writer: archive.py. reconcile must not ship a second archive
    write path - two writers with different on-disk layouts (release sub-index + live pointer
    vs a flat, pointerless archive/_index.md) split a type's terminal rows silently."""

    def test_reconcile_registers_no_archive_subcommand(self):
        actions = [a for a in rc.build_parser()._subparsers._group_actions]
        names = sorted({n for a in actions for n in a.choices})
        self.assertNotIn("archive", names, "reconcile must not re-register an archive subcommand")
        self.assertEqual(names, ["apply", "detect", "fields"])

    def test_reconcile_has_no_archive_writer(self):
        for name in ("archive_plan", "archive_type", "cmd_archive"):
            self.assertFalse(hasattr(rc, name), f"reconcile.{name} is the duplicate archive writer")
        rec_src = (SCRIPT.parent / "reconcile.py").read_text(encoding="utf-8")
        self.assertNotIn('add_parser("archive"', rec_src)

    def test_archive_py_still_registers_archive(self):
        sub = [a for a in arc.build_parser()._subparsers._group_actions]
        self.assertIn("archive", {n for a in sub for n in a.choices})


class IterTablesOnlyTests(unittest.TestCase):
    """US0098/CR0182 AC4: the shared walker parses via iter_tables; no hand-rolled walker."""

    def test_shared_walker_uses_iter_tables(self):
        import inspect
        self.assertIn("iter_tables", inspect.getsource(rc.master_terminal_rows))

    def test_archive_path_has_no_hand_rolled_walker(self):
        import inspect
        arc_src = (SCRIPT.parent / "archive.py").read_text(encoding="utf-8")
        self.assertNotIn("_table_end", arc_src)             # the removed walker is gone
        src = inspect.getsource(arc.archive)                # the one writer delegates the read
        self.assertIn("master_terminal_rows", src)
        self.assertNotIn("in_table", src)


class CrashResumeIdempotentTests(unittest.TestCase):
    """BG0091: archive appends moved rows before it trims the live index. A crash between
    the two writes, then a re-run, must NOT duplicate the rows in the archive file."""

    def test_rerun_after_partial_archive_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            # simulate the crash: step 1 (archive write) completed, step 2 (live trim) did not.
            adir = root / "sdlc-studio" / "stories" / "archive" / "r1"
            adir.mkdir(parents=True)
            (adir / "story.md").write_text(
                "# story archive - r1\n\nx\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | s | Done |\n", encoding="utf-8")
            # US0001/US0003 are still Done in the live index (step 2 never ran)
            arc.archive(root, "story", "r1")
            atext = (adir / "story.md").read_text(encoding="utf-8")
            self.assertEqual(atext.count("[US0001]"), 1, "US0001 archive row duplicated")
            self.assertEqual(atext.count("[US0003]"), 1)


if __name__ == "__main__":
    unittest.main()

