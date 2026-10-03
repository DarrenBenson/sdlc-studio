"""BG0926: a lane return between the close and the sign records nothing into the run.

BG0902 stopped a late total landing in a SEALED run, but its guard keys on the run's outcome,
and `sprint close` leaves the outcome `running` until `sprint sign`. A `sprint lane return
--tokens` made in that window still recorded, so the filed page re-derived INVALIDATED before
anyone signed it. The guard now also reads the filed-page marker `sign` reads (the run's
`report`), unless a `sprint reopen` has since broken that page's seal.

The close and the seal are the real `sprint close` and `sprint sign` (only the chain's steps and
the terminal transitions are stubbed, as `test_lean_sealed_run_late_total` drives them). Every
VALID is read live, by `sprint_report check`, after the return (LC-016).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

REPORT = "RPT0001"
LATER = "2099-01-01T00:00:00Z"


class ClosedRunLateTotalTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        bin_ = base / "bin"
        bin_.mkdir()
        gh = bin_ / "gh"
        gh.write_text("#!/bin/sh\necho '[]'\n", encoding="utf-8")
        gh.chmod(0o755)
        (base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{bin_}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.root = base / "closer"
        self.root.mkdir()
        lean._fixture(self.root)
        signing._git_repo(self.root)

    def _commit(self, message: str) -> None:
        for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
            gitutil.git(argv, self.root, text=True,
                        env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _check(self) -> tuple[int, str]:
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = sprint_report.main(["--root", str(self.root), "check", "--report", REPORT])
        return rc, out.getvalue()

    def _run(self, *argv: str) -> tuple[int, str]:
        import sprint  # noqa: PLC0415
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = sprint.main([*argv, "--root", str(self.root)])
            except SystemExit as exc:
                rc = exc.code
        return rc, out.getvalue()

    def _delegated(self) -> list:
        from lib import run_state  # noqa: PLC0415
        return list(run_state.read(self.root).get(run_state.DELEGATED) or [])

    def _close(self) -> None:
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._commit("close paperwork")

    def test_a_return_after_the_close_records_nothing(self) -> None:
        """AC1. MUTANT: HEAD's guard, which reads only the outcome - the close leaves it
        `running`, so the 7000 lands in the run's delegated records and the filed page reads
        INVALIDATED. The positive control is the filed page itself, VALID before the return."""
        from lib import run_state  # noqa: PLC0415
        self._close()
        state = run_state.read(self.root)
        self.assertEqual(run_state.RUNNING, state.get("outcome"),
                         "premise: the close leaves the outcome running until the sign")
        self.assertEqual(REPORT, state.get("report"), "premise: the close filed the page")
        rc, out = self._check()
        self.assertEqual(0, rc, f"premise: the filed page checks VALID\n{out}")
        before = self._delegated()

        _rc, said = self._run("lane", "return", "--units", "US0101", "--tokens", "7000")

        self.assertEqual(before, self._delegated(),
                         f"the late total was recorded into the closed run:\n{said}")
        self.assertRegex(said, rf"{state['run_id']}\b.*\bclosed\b", said)
        rc, out = self._check()
        self.assertEqual(0, rc, f"the late return moved the filed page:\n{out}")
        self.assertNotIn("INVALIDATED", out)

    def test_a_return_before_the_close_still_records(self) -> None:
        """Control. MUTANT: refuse every return on a run that has a report key at all, or key on
        anything the open run already carries - the total before the close is the run's own."""
        _rc, said = self._run("lane", "return", "--units", "US0101", "--tokens", "7000")
        self.assertEqual([7000], [r.get("tokens") for r in self._delegated()], said)

    def test_a_return_after_a_reopen_still_records(self) -> None:
        """Control. MUTANT: key on the report marker alone - `sprint reopen` leaves the signed
        page's id on the run, so a reopened run would refuse every total the reopen exists to
        let it record."""
        self._close()
        rc, _out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, err)
        self._commit("seal")
        rc, said = self._run("reopen", "--reason", "a late review belongs to this run")
        self.assertEqual(0, rc, said)

        _rc, said = self._run("lane", "return", "--units", "US0101", "--tokens", "7000")

        self.assertEqual([7000], [r.get("tokens") for r in self._delegated()], said)


if __name__ == "__main__":
    unittest.main()
