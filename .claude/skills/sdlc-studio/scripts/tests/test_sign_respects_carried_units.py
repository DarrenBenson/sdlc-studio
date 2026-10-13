"""BG1025: `sprint sign` leaves a batch unit the close's retro carries with a ruling at its
status, and a sealed run's unit still changes status only through `sprint.py reopen` (D0367).

A consuming project's operator ruled a bug not-stop-ship and left it Open on purpose; the retro
carried it; `sprint sign` moved it to Fixed anyway, and the seal then refused every route back
but a hand edit. These run the real `sprint sign` and `revalidate` on BG0848's close-and-sign
fixture (`test_lean_sign._SignMovesRun`), whose close runs with its chain steps stubbed green,
after `sprint close --retro RETRO0001`. The batch is a story and two bugs: BG0101, which the
retro carries and which stays Open, and BG0102, which nothing carries.

MUTANTS, each of which a test here fails on: (1) sign moves every non-terminal batch unit, as it
did (AC1); (2) sign keeps every bug, or every unit at one status, without reading the retro
(AC2: BG0102 must still reach Fixed); (3) sign reads the latest retro naming the run instead of
the one the filed page records, so a retro whose Run line does not name the run, or a later one
that does, decides; (4) sign honours a carried row the close reads as no ruling; (5) the sealed
refusal stops naming `sprint.py reopen`, or `--force` waives it (AC3).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_sign as signing  # noqa: E402 - BG0848's close-and-sign fixture, shared

SCRIPTS = Path(__file__).resolve().parent.parent
RETRO = "RETRO0001"


class _CarriedRun(signing._SignMovesRun):
    """BG0848's run plus an uncarried bug, whose retro carries BG0101 (left Open) under
    `ruling`. Its Run line does not name the run unless `names_run`: the close names the retro
    with `--retro`, as `artifact.py new --type retro` leaves it."""

    UNITS = {"US0101": ("stories", "Ready", "Review"), "BG0101": ("bugs", "Open", "Open"),
             "BG0102": ("bugs", "Open", "In Progress")}

    def __init__(self, d: str, ruling: str = "not-stop-ship", names_run: bool = False) -> None:
        super().__init__(d)
        self.ruling, self.names_run = ruling, names_run

    def build(self) -> None:
        super().build()
        run_id = signing.run_state.read(self.root)["run_id"]
        path = self.root / "sdlc-studio" / "retros" / f"{RETRO}-lean.md"
        run_line = f"> **Run:** {run_id}\n" if self.names_run else "> **Run:** -\n"
        text = path.read_text(encoding="utf-8").replace(
            "> **Date:** 2026-09-23\n",
            f"> **Date:** 2026-09-23\n{run_line}> **Batch:** US0101, BG0101, BG0102\n", 1)
        path.write_text(text + "\n## Known issues carried\n\n"
                        "| ID | Ruling | Ruled by | Date |\n| --- | --- | --- | --- |\n"
                        f"| BG0101 | {self.ruling} | Maya | 2026-09-30 |\n", encoding="utf-8")
        self._commit("the retro carries BG0101")

    def later_retro(self) -> None:
        """An untracked RETRO0002 naming the run and carrying nothing, added after the close."""
        run_id = signing.run_state.read(self.root)["run_id"]
        (self.root / "sdlc-studio" / "retros" / "RETRO0002-later.md").write_text(
            f"# RETRO-0002: later\n\n> **Date:** 2026-09-30\n> **Run:** {run_id}\n\n"
            "## Known issues carried\n\n| ID | Ruling | Ruled by | Date |\n"
            "| --- | --- | --- | --- |\n", encoding="utf-8")


class SignRespectsCarriedUnitsTests(unittest.TestCase):
    def _sealed(self, **kw) -> tuple[_CarriedRun, str, str]:
        """Build, close and sign: `(the run, the report id, sign's output)`."""
        later = kw.pop("later", False)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = _CarriedRun(tmp.name, **kw)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        report = run.close()
        if later:
            run.later_retro()
        return run, report, run.sign(report)

    def test_a_carried_unit_keeps_its_status(self) -> None:
        run, report, out = self._sealed()
        self.assertEqual("Open", run.status("BG0101"),
                         f"sign moved the unit its retro carried:\n{out}")
        self.assertRegex(out, r"BG0101 is carried as a known issue by RETRO0001 - it stays Open, "
                              r"not moved", out)
        check = run.lean._live("sprint_report").revalidate(run.root, report)
        self.assertTrue(check["valid"], (check["changes"], check["edited"]))

    def test_the_close_s_retro_decides_not_a_later_one(self) -> None:
        for kw in ({"later": True}, {"later": True, "names_run": True}):
            with self.subTest(**kw):
                run, _report, out = self._sealed(**kw)
                self.assertEqual("Open", run.status("BG0101"), out)

    def test_uncarried_units_are_still_moved(self) -> None:
        run, _report, out = self._sealed()
        self.assertEqual("Done", run.status("US0101"), out)
        self.assertEqual("Fixed", run.status("BG0102"),
                         f"a bug nothing carries was held back:\n{out}")

    def test_a_row_the_close_reads_as_no_ruling_carries_nothing(self) -> None:
        run, _report, out = self._sealed(ruling="fixed")
        self.assertEqual("Fixed", run.status("BG0101"),
                         f"a carried row nobody validly ruled held the unit back:\n{out}")
        self.assertNotIn("carried as a known issue", out)

    def test_the_sealed_refusal_names_reopen(self) -> None:
        run, _report, _out = self._sealed()
        for extra in ([], ["--force"]):
            with self.subTest(extra=extra):
                r = subprocess.run(
                    [sys.executable, str(SCRIPTS / "transition.py"), "set", "--id", "BG0101",
                     "--status", "Fixed", *extra, "--root", str(run.root)],
                    capture_output=True, text=True, timeout=120, check=False, env=run.env)
                self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn("sprint.py reopen", r.stdout + r.stderr)
                self.assertEqual("Open", run.status("BG0101"))


if __name__ == "__main__":
    unittest.main()
