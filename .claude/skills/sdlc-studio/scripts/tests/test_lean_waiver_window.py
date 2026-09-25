"""BG0750: a waiver is placed in a report's window by the moment it was recorded.

The waivers section compared the Date cell with the window by date only, and the Date cell held
the LOCAL date. A waiver recorded later on the page's own day entered the re-derivation but not
the page, so `check` read INVALID on a page nobody touched; and near midnight the local date and
the window's UTC date disagree, so a waiver inside the window could fall a day outside it.

Each waiver here is recorded through the shipped `decisions.py waive` entry point, in a process
whose clock zone the test chooses, because the local date is half of the defect.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import decisions  # noqa: E402
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

sr = lean.sr
DECISIONS = HERE.parent / "decisions.py"


def _utc(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _zone_past_local_midnight() -> str:
    """A POSIX TZ whose local date is one day AHEAD of the UTC date: the clock has passed local
    midnight while the window, stored in UTC, is still on the day before. At 00:xx UTC no offset
    under a day can do that, so the zone sits a day BEHIND instead - the dates still disagree."""
    hour = datetime.now(timezone.utc).hour
    return f"<+{24 - hour:02d}>-{24 - hour}" if hour else "<-12>+12"


class WaiverWindowTests(unittest.TestCase):
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

    def _waive(self, zone: str) -> dict:
        """Record a waiver through the shipped CLI with the clock in `zone`; the row it wrote."""
        proc = subprocess.run(
            [sys.executable, str(DECISIONS), "waive", "--subject", "rule:engagement-floor",
             "--rationale", "the floor is out of scope for this fixture",
             "--root", str(self.root)],
            capture_output=True, text=True, timeout=60, env={**os.environ, "TZ": zone})
        self.assertEqual(0, proc.returncode, proc.stderr)
        return decisions.list_decisions(self.root)[-1]

    @staticmethod
    def _waivers(report: dict) -> dict:
        return next(s for s in report["sections"] if s["key"] == "waivers")

    def _check(self, rid: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "check", "--report", rid])
        return rc, out.getvalue() + err.getvalue()

    def test_a_waiver_recorded_after_the_page_leaves_it_valid(self) -> None:
        """AC1. MUTANT: compare the waiver's date with the window end's date - the waiver is
        dated the page's own day, so the re-derivation counts it and `check` reads INVALID."""
        generated = datetime.now(timezone.utc) - timedelta(minutes=5)
        rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO,
                                                        as_of=_utc(generated)))
        filed = sr.read_report(self.root, rid)
        self.assertEqual(0, self._waivers(filed)["figures"]["waivers_count"]["value"])

        row = self._waive("UTC")
        self.assertEqual(_utc(generated)[:10], row["date"][:10],
                         "the waiver must be dated the page's own day, or this proves nothing")

        rc, out = self._check(rid)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {rid}", out)
        again = sr.build_report(self.root, lean.RETRO, as_of=filed["generated_at"],
                                window_end=filed["window_end"])
        self.assertEqual(0, self._waivers(again)["figures"]["waivers_count"]["value"],
                         "the page's waiver count moved after the page was generated")
        # The positive control: the row IS a waiver the section reads, once a window covers it.
        later = sr.build_report(self.root, lean.RETRO,
                                as_of=_utc(datetime.now(timezone.utc) + timedelta(minutes=1)))
        self.assertEqual([row["id"]], [r["waiver_id"]["value"]
                                       for r in self._waivers(later)["rows"]])

    def test_a_waiver_recorded_before_the_page_on_its_day_is_disclosed(self) -> None:
        """AC2. MUTANTS: exclude every waiver dated the generation day (the cheap fix to AC1),
        and compare the local Date cell with the window's UTC date."""
        for zone in ("UTC", _zone_past_local_midnight()):
            with self.subTest(zone=zone):
                row = self._waive(zone)
                moment = datetime.fromisoformat(row["date"].replace("Z", "+00:00"))
                generated = _utc(moment + timedelta(minutes=1))
                if zone == "UTC":
                    self.assertEqual(generated[:10], row["date"][:10],
                                     "the waiver must be dated the generation day")
                else:
                    self.assertNotEqual(_utc(moment)[:10], row["date"][:10],
                                        "the local date must disagree with the UTC window")
                report = sr.build_report(self.root, lean.RETRO, as_of=generated)
                self.assertIn(row["id"], [r["waiver_id"]["value"]
                                          for r in self._waivers(report)["rows"]])
                self.assertIn(row["id"], sr.render_markdown(report),
                              "the waiver is derived but not on the page")


if __name__ == "__main__":
    unittest.main()
