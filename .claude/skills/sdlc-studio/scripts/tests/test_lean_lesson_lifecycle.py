"""US0977: a lesson class finishes its lifecycle without a hand edit to `lessons.jsonl`.

Two ends the close never reached. A `graduating` class whose CR reached a terminal status stayed
`graduating` (the 2026-10-01 sweep edited four rows to `graduated` by hand), and an `active`
class whose recording and hit runs this clone's archive has never seen stayed active for ever,
because quiet was judged only on runs the archive knows to be old.

Each test writes a throwaway workspace, runs `lessons.close_pass` with the run state the close
passes it, and reads the result back through the shipped `lessons.py classes`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

lessons = loader.load_script("lessons")
SCRIPTS = Path(__file__).resolve().parent.parent

_CR = ("# {cid}: a graduation request\n\n> **Status:** {status}\n> **Priority:** Medium\n"
       "> **Type:** Enhancement\n\n## Summary\n\nFix the path.\n")


class LessonLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "sdlc-studio" / "change-requests").mkdir(parents=True)

    def _row(self, code: str, recorded: str, *hit_runs: str, state: str = "active",
             cr: str | None = None) -> dict:
        row = {"id": code, "class": f"class {code}", "rule": f"Rule of {code} holds.",
               "behaviour": f"Do {code} differently.", "inject": ["build"],
               "hits": [{"run": r, "unit": "US0001", "source": f"critic:{r}"} for r in hit_runs],
               "state": state, "recorded_run": recorded}
        if cr:
            row["cr"] = cr
        return row

    def _store(self, *rows: dict) -> None:
        (self.root / lessons.STORE_FILE).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def _cr(self, cid: str, status: str) -> None:
        (self.root / "sdlc-studio" / "change-requests" / f"{cid}-a-graduation-request.md"
         ).write_text(_CR.format(cid=cid, status=status), encoding="utf-8")

    def _archive(self, *runs: str) -> None:
        d = self.root / "sdlc-studio" / ".local" / "run-archive"
        d.mkdir(parents=True, exist_ok=True)
        for n, run in enumerate(runs, 1):
            (d / f"{run}.json").write_text(json.dumps(
                {"run_id": run, "started_at": f"2026-09-{n:02d}T08:00:00Z",
                 "outcome": "goal-reached"}), encoding="utf-8")

    def _close(self, run: str) -> dict:
        return lessons.close_pass(self.root, run, {"run_id": run, "batch": []})

    def _classes(self) -> dict[str, str]:
        """{code: state} as `lessons.py classes` prints it."""
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "lessons.py"), "--root", str(self.root),
             "classes"], capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        out = {}
        for ln in proc.stdout.splitlines():
            parts = ln.split()
            if len(parts) >= 2 and lessons.CLASS_CODE_RE.match(parts[0]):
                out[parts[0]] = parts[1]
        return out

    def test_a_class_graduates_when_its_cr_closes(self) -> None:
        """AC1. MUTANT: HEAD, which leaves both `graduating`. MUTANT: graduate on any CR that
        exists, whatever its status - LC-002, whose CR is still Proposed, graduates too."""
        self._cr("CR0001", "Complete")
        self._cr("CR0002", "Proposed")
        self._store(self._row("LC-001", "RUN-1", state="graduating", cr="CR0001"),
                    self._row("LC-002", "RUN-1", state="graduating", cr="CR0002"))
        res = self._close("RUN-2")
        self.assertEqual({"LC-001": "graduated", "LC-002": "graduating"}, self._classes())
        self.assertEqual(["LC-001"], res.get("graduated"))
        self.assertIn("LC-001 graduated (CR0001 Complete)", lessons.close_pass_line(res))
        # A re-run close finds nothing more to move.
        self.assertEqual([], self._close("RUN-2").get("graduated"))

    def test_a_class_recorded_in_another_clone_retires_when_quiet(self) -> None:
        """AC2. MUTANT: HEAD, which keeps LC-001 active because RUN-B1 is in no window this
        clone knows. MUTANT: retire on unknown runs alone, ignoring the window - LC-002, hit in
        RUN-6, which this clone knows and is one of its last five, retires too. MUTANT: judge
        before this clone has seen a full window - with five runs on record LC-001 retires."""
        self._store(self._row("LC-001", "RUN-B1", "RUN-B4"),
                    self._row("LC-002", "RUN-B1", "RUN-6"))
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4")
        self._close("RUN-5")
        self.assertEqual({"LC-001": "active", "LC-002": "active"}, self._classes(),
                         "five runs on record are one window, with no run yet older than it")
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4", "RUN-5", "RUN-6")
        res = self._close("RUN-7")
        self.assertEqual({"LC-001": "retired", "LC-002": "active"}, self._classes())
        self.assertEqual(["LC-001"], res["retired"])


if __name__ == "__main__":
    unittest.main()
