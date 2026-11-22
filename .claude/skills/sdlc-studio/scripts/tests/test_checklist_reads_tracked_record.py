"""The sprint checklist reads the run record a commit holds, so a clean clone sees the run.

`sprint sign` (and the close) file the run's record at `sdlc-studio/reports/runs/<RUN>.json`,
committed beside the report. The checklist chose its run from `.local/run-state.json` and the
`.local` archive alone, so in any clone but the closing machine's every row that reads the run
said no run record could be read. These tests build a real clone and run the shipped CLI in it.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - the confined git helper
import sprint_report as sr  # noqa: E402
from lib import run_state  # noqa: E402

UNREAD = "no run record could be read"
RETRO = """# RETRO-9100: a sprint

> **Batch:** US0001, US0002

## Delivered
- shipped
"""


def _record(run_id: str, question: str, *, batch=("US0001", "US0002"),
            started_at: str = "2026-01-01T00:00:00Z") -> dict:
    """A run record whose one open operator question names which copy the checklist read."""
    return {"schema": 1, "run_id": run_id, "started_at": started_at, "outcome": "closed",
            "batch": list(batch), "batch_changes": [],
            "pending_decisions": [{"unit": "US0001", "question": question,
                                   "resolution": None}]}


class ChecklistTrackedRecordTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "origin"
        sd = self.root / "sdlc-studio"
        (sd / "retros").mkdir(parents=True)
        (sd / "retros" / "RETRO9100-t.md").write_text(RETRO, encoding="utf-8")
        (sd / "stories").mkdir()
        for sid in ("US0001", "US0002"):
            (sd / "stories" / f"{sid}-s.md").write_text(
                f"# {sid}: s\n\n> **Status:** Done\n> **Points:** 3\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")

    # -- fixture writers ------------------------------------------------------------------

    def _track(self, rec: dict, root: Path | None = None) -> Path:
        p = run_state.tracked_path(root or self.root, rec["run_id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec), encoding="utf-8")
        return p

    def _archive(self, rec: dict) -> None:
        p = run_state.archive_path(self.root, rec["run_id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec), encoding="utf-8")

    def _live(self, rec: dict) -> None:
        p = run_state.path(self.root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(rec), encoding="utf-8")

    def _clone(self) -> Path:
        """Commit the origin and clone it: the clone holds what git tracks and no `.local`."""
        gitutil.git(["init", "-q", "-b", "main"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "fixture"], self.root)
        clone = Path(self.tmp.name) / "clone"
        gitutil.git(["clone", "-q", str(self.root), str(clone)], Path(self.tmp.name))
        return clone

    def _checklist(self, root: Path) -> dict:
        """The checklist through the shipped CLI, as JSON."""
        cp = subprocess.run([sys.executable, str(SCRIPTS / "sprint_report.py"), "--root",
                             str(root), "checklist", "--id", "RETRO9100", "--format", "json"],
                            capture_output=True, text=True, env=gitutil.git_env(), timeout=120)
        self.assertNotIn("Traceback", cp.stderr, cp.stderr)
        return json.loads(cp.stdout)

    def _impediments(self, root: Path) -> dict:
        """The impediments row, read in-process: the criterion and its negative control go
        through the CLI, and the cases below judge which record and which copy is read."""
        return next(r for r in sr.checklist(root, "RETRO9100")["items"]
                    if r["id"] == "impediments")

    # -- the criterion --------------------------------------------------------------------

    def test_a_clean_clone_reads_the_committed_run(self) -> None:
        """The origin holds the run in its `.local` archive and commits the tracked record; the
        clone holds only the commit. Every row in the clone reads the committed record, and the
        impediments row carries the open question only that record states."""
        self._archive(_record("RUN-TEST01", "which schema wins?"))
        self._track(_record("RUN-TEST01", "which schema wins?"))
        row = next(r for r in self._checklist(self.root)["items"] if r["id"] == "impediments")
        self.assertIn("which schema wins?", row["detail"],
                      "the positive control: the closing clone reads its own archive")
        clone = self._clone()
        self.assertFalse((clone / "sdlc-studio" / ".local").exists(),
                         "the clone must hold no .local, or it proves nothing")
        ck = self._checklist(clone)
        unread = [r["id"] for r in ck["items"]
                  if UNREAD in f"{r.get('value')} {r.get('detail')}"]
        self.assertEqual(unread, [], f"rows that could not read the committed run: {unread}")
        row = next(r for r in ck["items"] if r["id"] == "impediments")
        self.assertIn("which schema wins?", row["detail"])
        self.assertIn("1 open question", row["value"])

    def test_a_clone_holding_no_record_still_says_it_could_not_read_one(self) -> None:
        """The negative control: with nothing committed, unknown stays unknown."""
        clone = self._clone()
        row = next(r for r in self._checklist(clone)["items"] if r["id"] == "impediments")
        self.assertEqual(row["state"], sr.UNMEASURABLE)
        self.assertIn(UNREAD, row["detail"])

    # -- which record, and which copy -----------------------------------------------------

    def test_a_committed_record_of_another_sprint_is_not_taken(self) -> None:
        self._track(_record("RUN-OTHER1", "not this sprint", batch=("US0999",)))
        row = self._impediments(self.root)
        self.assertIn(UNREAD, row["detail"])

    def test_the_closest_committed_record_wins(self) -> None:
        """An exact batch beats a superset among committed records, as among archived ones."""
        self._track(_record("RUN-AAAA01", "the superset",
                            batch=("US0001", "US0002", "US0999"),
                            started_at="2026-02-01T00:00:00Z"))
        self._track(_record("RUN-BBBB01", "the exact batch"))
        self.assertIn("the exact batch", self._impediments(self.root)["detail"])

    def test_a_tie_between_committed_records_goes_to_the_newest(self) -> None:
        """Equal closeness: the newest start wins, whatever the ids sort to."""
        self._track(_record("RUN-AAAA01", "the newer run", started_at="2026-02-01T00:00:00Z"))
        self._track(_record("RUN-BBBB01", "the older run", started_at="2026-01-01T00:00:00Z"))
        detail = self._impediments(self.root)["detail"]
        self.assertIn("the newer run", detail)
        self.assertNotIn("the older run", detail)

    def test_a_tie_between_a_committed_and_an_archived_run_goes_to_the_newest(self) -> None:
        """A run this clone archived and a run only committed are ordered by start together,
        so the same tie reads the same in a clean clone and on the closing machine. Both ways
        round: the committed run newer, then the archived one."""
        self._archive(_record("RUN-AAAA01", "the archived older run"))
        self._track(_record("RUN-BBBB01", "the committed newer run",
                            started_at="2026-02-01T00:00:00Z"))
        self.assertIn("the committed newer run", self._impediments(self.root)["detail"])
        run_state.archive_path(self.root, "RUN-AAAA01").unlink()
        run_state.tracked_path(self.root, "RUN-BBBB01").unlink()
        self._archive(_record("RUN-AAAA01", "the archived newer run",
                              started_at="2026-02-01T00:00:00Z"))
        self._track(_record("RUN-BBBB01", "the committed older run"))
        self.assertIn("the archived newer run", self._impediments(self.root)["detail"])

    def test_a_tie_in_start_keeps_the_archive_s_newest_cycle(self) -> None:
        """Two archived runs starting in the same second: the higher cycle index wins, as it
        did before committed records were read, because the archive orders a tie by it."""
        older = _record("RUN-BBBB01", "the earlier cycle")
        older["cycle"] = {"index": 1}
        newer = _record("RUN-AAAA01", "the later cycle")
        newer["cycle"] = {"index": 2}
        self._archive(older)
        self._archive(newer)
        detail = self._impediments(self.root)["detail"]
        self.assertIn("the later cycle", detail)
        self.assertNotIn("the earlier cycle", detail)

    def test_an_unreadable_live_record_falls_back_to_the_committed_one(self) -> None:
        """A live record that does not parse is passed over, as before, and the committed
        record is still read."""
        run_state.path(self.root).parent.mkdir(parents=True, exist_ok=True)
        run_state.path(self.root).write_text("{not json", encoding="utf-8")
        self._track(_record("RUN-TEST01", "the committed copy"))
        self.assertIn("the committed copy", self._impediments(self.root)["detail"])

    def test_the_live_record_wins_over_the_committed_copy_of_its_run(self) -> None:
        """One copy per run, the live one first. The committed copy here is the closer match,
        so a second copy of the live run would take the checklist from it."""
        self._live(_record("RUN-TEST01", "the live copy",
                           batch=("US0001", "US0002", "US0999")))
        self._track(_record("RUN-TEST01", "the committed copy"))
        self.assertIn("the live copy", self._impediments(self.root)["detail"])

    def test_the_committed_copy_stands_in_for_the_archived_one(self) -> None:
        """The record a commit holds is the one every clone reads, so it replaces this clone's
        archived copy of the same run even where the archived copy is the closer match."""
        self._archive(_record("RUN-TEST01", "the archived copy"))
        self._track(_record("RUN-TEST01", "the committed copy",
                            batch=("US0001", "US0002", "US0999")))
        self.assertIn("the committed copy", self._impediments(self.root)["detail"])

    def test_an_empty_committed_record_does_not_hide_the_archived_copy(self) -> None:
        self._archive(_record("RUN-TEST01", "the archived copy"))
        run_state.tracked_path(self.root, "RUN-TEST01").parent.mkdir(parents=True)
        run_state.tracked_path(self.root, "RUN-TEST01").write_text("{}", encoding="utf-8")
        self.assertIn("the archived copy", self._impediments(self.root)["detail"])

    def test_an_unreadable_committed_record_is_skipped_and_the_rest_still_read(self) -> None:
        """Bytes that are not UTF-8, an empty file, JSON that does not parse and JSON that is
        not an object: each is skipped, the checklist still renders, and a readable record
        beside it is still read."""
        bad = {"not-utf8": b"\xff\xfe\x00{", "empty": b"", "not-json": b"{not json",
               "not-an-object": b"[1, 2]"}
        for name, raw in bad.items():
            with self.subTest(record=name):
                d = self.root / run_state.TRACKED_REL
                d.mkdir(parents=True, exist_ok=True)
                for old in d.glob("*.json"):
                    old.unlink()
                (d / "RUN-BAD001.json").write_bytes(raw)
                row = self._impediments(self.root)
                self.assertEqual(row["state"], sr.UNMEASURABLE)
                self._track(_record("RUN-GOOD01", "the readable record"))
                self.assertIn("the readable record", self._impediments(self.root)["detail"])


if __name__ == "__main__":
    unittest.main()
