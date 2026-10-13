"""BG1025: `sprint sign` leaves a batch unit the run's retro carries as a known issue at its
status, and a sealed run's unit still changes status only through `sprint.py reopen` (D0367).

A consuming project's operator ruled a bug not-stop-ship and left it Open on purpose; the retro
carried it; `sprint sign` moved it to Fixed anyway, and the seal then refused every route back
but a hand edit. These run the real `sprint close`, `sprint sign` and `revalidate` on BG0848's
close-and-sign fixture (`test_lean_sign._SignMovesRun`), with BG0101 carried by the run's retro.

MUTANTS, each of which a test here fails on: (1) sign moves every non-terminal batch unit, as it
did (AC1); (2) sign skips EVERY batch unit once any is carried, or moves none (AC2); (3) the
sealed refusal stops naming `sprint.py reopen`, or a `--force` waives it (AC3).
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
    """BG0848's run, whose retro names the run and carries BG0101 as not-stop-ship."""

    def build(self) -> None:
        super().build()
        run_id = signing.run_state.read(self.root)["run_id"]
        path = self.root / "sdlc-studio" / "retros" / f"{RETRO}-lean.md"
        text = path.read_text(encoding="utf-8").replace(
            "> **Date:** 2026-09-23\n",
            f"> **Date:** 2026-09-23\n> **Run:** {run_id}\n> **Batch:** US0101, BG0101\n", 1)
        path.write_text(text + "\n## Known issues carried\n\n"
                        "| ID | Ruling | Ruled by | Date |\n| --- | --- | --- | --- |\n"
                        "| BG0101 | not-stop-ship | Maya | 2026-09-30 |\n", encoding="utf-8")
        self._commit("the retro carries BG0101")


class SignRespectsCarriedUnitsTests(unittest.TestCase):
    def _sealed(self) -> tuple[_CarriedRun, str, str]:
        """Build, close and sign: `(the run, the report id, sign's output)`."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = _CarriedRun(tmp.name)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        report = run.close()
        return run, report, run.sign(report)

    def test_a_carried_unit_keeps_its_status(self) -> None:
        run, report, out = self._sealed()
        self.assertEqual("In Progress", run.status("BG0101"),
                         f"sign moved the unit its retro carried:\n{out}")
        self.assertRegex(out, r"BG0101[^\n]*carried", out)
        check = run.lean._live("sprint_report").revalidate(run.root, report)
        self.assertTrue(check["valid"], (check["changes"], check["edited"]))

    def test_uncarried_units_are_still_moved(self) -> None:
        run, _report, out = self._sealed()
        self.assertEqual("Done", run.status("US0101"), out)

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
                self.assertEqual("In Progress", run.status("BG0101"))


if __name__ == "__main__":
    unittest.main()
