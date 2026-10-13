"""BG0944: pins for three behaviours BG0940 and BG0943 shipped with no test that fails when
they break. Found by the QA reviews of RUN-01M45FV6; no production change.

MUTANTS, one per test, each of which survived every related module before this one:
(1) `config._deep_merge` skips every null rather than a null SECTION, so a project's deliberate
leaf null (`review.max_rounds:`) is ignored and the shipped default read instead (AC1);
(2) `run_state.record_ruling` asks `state.get("report")` instead of `_page_filed(state)`, so a
ruling logged after reopening a SEALED run is withheld, because a reopen keeps the broken page's
id on the run (AC2); (3) `sprint._page_no_longer_matches` loses its ReportError catch, so sign
crashes on a page it cannot re-derive instead of signing on the report alone (AC3).
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
import loader  # noqa: E402
import test_lean_sign as signing  # noqa: E402 - BG0848's close-and-sign fixture, shared

SCRIPTS = Path(__file__).resolve().parent.parent


class S12PinTests(unittest.TestCase):
    def _tmp(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def _project(self, config: str) -> Path:
        root = self._tmp()
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
        return root

    def _show(self, root: Path) -> str:
        r = subprocess.run([sys.executable, str(SCRIPTS / "config.py"), "show", "--key",
                            "review.max_rounds", "--root", str(root)],
                           capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(0, r.returncode, r.stderr)
        return r.stdout.strip()

    def test_a_leaf_null_still_overrides(self) -> None:
        config = loader.load_script("config")
        leaf = self._project("review:\n  max_rounds:\n")
        section = self._project("review:\n  # only comments under this section\n")
        self.assertIsNone(config.get(leaf, "review.max_rounds", "unset"),
                          "a project's deliberate leaf null was replaced by the default")
        self.assertEqual("null", self._show(leaf))
        self.assertEqual(2, config.get(section, "review.max_rounds", "unset"),
                         "a section holding only comments overrode the defaults under it")
        self.assertEqual("2", self._show(section))

    def _run(self) -> signing._SignMovesRun:
        run = signing._SignMovesRun(str(self._tmp()))
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        return run

    def test_a_ruling_after_reopening_a_sealed_run_counts(self) -> None:
        run = self._run()
        run.sign(run.close())
        rc, out, err = signing._run(run.root, "reopen", "--reason", "a pin for BG0944")
        self.assertEqual(0, rc, out + err)
        rulings = signing.run_state.RULINGS
        before = len(signing.run_state.read(run.root).get(rulings) or [])
        r = subprocess.run([sys.executable, str(SCRIPTS / "decisions.py"), "add", "--decision",
                            "a ruling after the reopen", "--rationale", "the pin",
                            "--by", "operator", "--root", str(run.root)],
                           capture_output=True, text=True, timeout=60, check=False, env=run.env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("was not counted", r.stderr)
        after = len(signing.run_state.read(run.root).get(rulings) or [])
        self.assertEqual(before + 1, after, "a ruling after reopening a sealed run was withheld")

    def test_an_unjudgeable_page_signs_with_its_note(self) -> None:
        run = self._run()
        report = run.close()
        sprint_report = run.lean._live("sprint_report")
        with unittest.mock.patch.object(sprint_report, "revalidate",
                                        side_effect=sprint_report.ReportError("unreadable here")), \
                unittest.mock.patch.object(signing.run_state, "_unit_clock",
                                           lambda: "2026-09-30T10:00:00Z"), \
                unittest.mock.patch.object(signing.sprint, "_principal_refusals",
                                           lambda *a, **k: []):
            rc, out, err = signing._run(run.root, "sign", "--report", report, "--principal",
                                        "Darren")
        self.assertEqual(0, rc, out + err)
        self.assertIn("could not be re-derived", err)
        self.assertIn("signing on the report alone", err)
        self.assertTrue(signing.run_state.read(run.root).get("signature"), "nothing was signed")


if __name__ == "__main__":
    unittest.main()
