"""BG0902: a lane return made after the seal records nothing into the sealed run.

`run_state.record_delegated_tokens` checked only that the run had an id, so a late
`sprint lane return --tokens` wrote a delegated record into a sealed run and the signed page,
re-derived, read INVALIDATED. It now records nothing into a run whose outcome is no longer
running and says the run is sealed - a warning, not a refusal.

The close and the seal are the real `sprint close` and `sprint sign` (only the chain's steps and
the terminal transitions are stubbed, as `test_lean_frozen_report_inputs` drives them).
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


class SealedRunLateTotalTests(unittest.TestCase):

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
        self.root = base / "signer"
        self.root.mkdir()

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

    def _lane_return(self, *argv: str) -> tuple[int, str]:
        import sprint  # noqa: PLC0415
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = sprint.main(["lane", "return", *argv, "--root", str(self.root)])
            except SystemExit as exc:
                rc = exc.code
        return rc, out.getvalue()

    def test_a_late_total_leaves_the_sealed_page_valid(self) -> None:
        """AC1. MUTANT: HEAD's `record_delegated_tokens`, which checks only the run id - the
        late 7000 lands in the sealed run's delegated records and the page reads INVALIDATED.
        The positive control is the seal itself: the page checks VALID before the late return."""
        from lib import run_state  # noqa: PLC0415
        lean._fixture(self.root)
        signing._git_repo(self.root)
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._commit("close paperwork")
        rc, _out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, err)
        self._commit("seal")
        rc, out = self._check()
        self.assertEqual(0, rc, f"premise: the sealed page checks VALID\n{out}")
        before = run_state.read(self.root).get(run_state.DELEGATED)

        _rc, said = self._lane_return("--units", "US0101", "--tokens", "7000")

        self.assertEqual(before, run_state.read(self.root).get(run_state.DELEGATED),
                         f"the late total was recorded into the sealed run:\n{said}")
        self.assertRegex(said, r"(?i)\bsealed\b", said)
        rc, out = self._check()
        self.assertEqual(0, rc, f"the late return moved the signed page:\n{out}")
        self.assertNotIn("INVALIDATED", out)


if __name__ == "__main__":
    unittest.main()
