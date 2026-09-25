"""BG0751: an open finding is placed in a report's window by the moment it was raised.

The known-issues section compared a finding's stamp with the window end inclusively, so a finding
stamped in the page's own generation second entered the re-derivation but not the page, and
`check` read INVALID on a page nobody touched. A finding filed with no batch open carried no
moment at all, only a date-level `Created`, so one filed at any time later on the page's day
entered the re-derivation the same way: RPT0008 was signed VALID and read INVALID once BG0762
was filed after the seal.

The second criterion files through the shipped `file_finding.py file` entry point, because the
moment the filer writes is half of the fix.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from lib import sdlc_md  # noqa: E402
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

sr = lean.sr
FILE_FINDING = HERE.parent / "file_finding.py"


def _utc(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _at(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


class FindingsWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        lean.lean_run(self.root)
        # An open run that started an hour ago, so the page's window ends at its generation.
        live = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(live.read_text(encoding="utf-8"))
        state["started_at"] = _utc(datetime.now(timezone.utc) - timedelta(hours=1))
        state.pop("ended_at")
        live.write_text(json.dumps(state), encoding="utf-8")

    def _stamped(self, fid: str, raised: str) -> None:
        lean._finding(self.root, fid, priority="High", status="Open", raised=raised)

    def _file(self, title: str) -> str:
        """File a bug through the shipped CLI with no batch open; its id."""
        proc = subprocess.run(
            [sys.executable, str(FILE_FINDING), "file", "--type", "bug", "--root",
             str(self.root), "--title", title, "--severity", "High", "--points", "2",
             "--summary", "a finding raised while the run was open", "--steps", "file it",
             "--fix", "fix it", "--affects", "x.py", "--format", "json"],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stderr)
        return json.loads(proc.stdout)["id"]

    def _created(self, fid: str) -> str:
        path = next((self.root / "sdlc-studio" / "bugs").glob(f"{fid}-*.md"))
        return (sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Created") or "")[:10]

    @staticmethod
    def _issues(report: dict) -> list[str]:
        section = next(s for s in report["sections"] if s["key"] == "known_issues")
        return [r["issue_id"]["value"] for r in section["rows"]]

    def _check(self, rid: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "check", "--report", rid])
        return rc, out.getvalue() + err.getvalue()

    def _assert_valid(self, rid: str) -> None:
        rc, out = self._check(rid)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {rid}", out)

    def test_a_finding_stamped_in_the_generation_second_leaves_the_page_valid(self) -> None:
        """AC1. MUTANT: the inclusive `when > hi` - the finding stamped in T's own second enters
        the re-derivation's known issues and not the page's, so `check` reads INVALID."""
        generated = datetime.now(timezone.utc) - timedelta(minutes=5)
        self._stamped("BG0950", _utc(generated - timedelta(seconds=1)))
        rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO,
                                                        as_of=_utc(generated)))
        page = sr.read_report(self.root, rid)
        self.assertIn("BG0950", self._issues(page),
                      "a finding raised one second before the page is not on it")
        self.assertIn("BG0950", sr.render_markdown(page))

        self._stamped("BG0951", _utc(generated))
        self._assert_valid(rid)
        # The positive control: BG0951 IS an open finding the section reads, once a window
        # covers its moment.
        later = sr.build_report(self.root, lean.RETRO,
                                as_of=_utc(generated + timedelta(seconds=1)))
        self.assertIn("BG0951", self._issues(later))

    def test_a_finding_filed_outside_a_batch_is_placed_by_its_moment_not_its_day(self) -> None:
        """AC2. MUTANTS: the date-level `Created` fallback, under which the finding filed after
        the page on its own day enters the re-derivation; and excluding every date-only stamp on
        the generation day, which drops the finding filed before the page."""
        before = self._file("filed before the page")
        # T is the second after the filing, so the first finding is strictly before it.
        generated = _utc(datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=1))
        rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO, as_of=generated))
        page = sr.read_report(self.root, rid)
        self.assertIn(before, self._issues(page),
                      "a finding filed outside a batch before the page is not on it")
        self.assertIn(before, sr.render_markdown(page))

        while datetime.now(timezone.utc) < _at(generated):
            time.sleep(0.05)
        after = self._file("filed after the page")
        if self._created(after) != generated[:10]:
            self.skipTest("the filing crossed UTC midnight; the premise is the page's own day")
        self._assert_valid(rid)
        # The positive control: the later finding IS an open finding the section reads.
        later = sr.build_report(self.root, lean.RETRO,
                                as_of=_utc(datetime.now(timezone.utc) + timedelta(seconds=2)))
        self.assertIn(after, self._issues(later))


if __name__ == "__main__":
    unittest.main()
