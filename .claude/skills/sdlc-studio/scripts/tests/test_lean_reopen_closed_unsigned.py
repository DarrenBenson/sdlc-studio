"""BG0937: a run closed and not yet signed can be reopened.

`sprint close` leaves the outcome `running` until `sprint sign`, and `reopen_run` refused every
run whose outcome is running as already open. Since BG0926 a filed page also refuses every late
total, so work added between the close and the sign could neither reopen the run nor record its
cost. A run whose page is filed and unsigned now reopens, recording the page it breaks as a
sealed run's reopen does; a run with no page filed is still already open.

The close and the seal are the real `sprint close` and `sprint sign` (only the chain's steps and
the terminal transitions are stubbed, as `test_lean_closed_run_late_total` drives them).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/run_state.py
from __future__ import annotations

import contextlib
import io
import json
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


class ReopenClosedUnsignedTests(unittest.TestCase):

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

    def _run(self, *argv: str) -> tuple[int, str]:
        import sprint  # noqa: PLC0415
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                rc = sprint.main([*argv, "--root", str(self.root)])
            except SystemExit as exc:
                rc = exc.code
        return rc, out.getvalue()

    def _state(self) -> dict:
        from lib import run_state  # noqa: PLC0415
        return run_state.read(self.root)

    def _close(self) -> None:
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._commit("close paperwork")

    def _tokens(self) -> list:
        from lib import run_state  # noqa: PLC0415
        return [r.get("tokens") for r in self._state().get(run_state.DELEGATED) or []]

    def test_a_closed_unsigned_run_reopens(self) -> None:
        """AC1. MUTANT: HEAD's guard, which refuses every run whose outcome is running - the
        close leaves it running, so the reopen is refused as already open and the late total
        records nothing."""
        from lib import run_state  # noqa: PLC0415
        self._close()
        state = self._state()
        self.assertEqual(run_state.RUNNING, state.get("outcome"),
                         "premise: the close leaves the outcome running until the sign")
        self.assertEqual(REPORT, state.get("report"), "premise: the close filed the page")
        self.assertIsNone(state.get("signature"), "premise: the page is not signed")

        rc, said = self._run("reopen", "--reason", "D0334: work added before the sign")

        self.assertEqual(0, rc, said)
        reopens = self._state().get("reopened") or []
        self.assertEqual(1, len(reopens), reopens)
        self.assertEqual(REPORT, reopens[-1].get("report"),
                         "the reopen does not name the page it breaks")
        self.assertEqual(run_state.RUNNING, reopens[-1].get("from_outcome"))
        self.assertEqual("D0334: work added before the sign", reopens[-1].get("reason"))

        _rc, said = self._run("lane", "return", "--units", "US0101", "--tokens", "7000")
        self.assertEqual([7000], self._tokens(), f"the late total was not recorded:\n{said}")

        self.assertFalse(self._state().get("report"),
                         "the broken page is still the run's, so sign would seal it")
        self._commit("work added before the sign")
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self.assertEqual(REPORT, self._state().get("report"),
                         "the next close filed no page (an unsigned page re-files in place)")
        page = json.loads((self.root / "sdlc-studio" / "reports" / f"{REPORT}.json")
                          .read_text(encoding="utf-8"))
        import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
        delegated = [f.get("value") for _s, key, f in sprint_report.leaf_figures(page)
                     if key == "tokens_delegated"]
        self.assertEqual([7000], delegated, "the re-filed page omits the late total")

        _rc, said = self._run("lane", "return", "--units", "US0101", "--tokens", "500")
        self.assertEqual([7000], self._tokens(),
                         f"a total after the re-close was recorded into its filed page:\n{said}")

    def test_an_open_run_with_no_page_is_still_already_open(self) -> None:
        """Control. MUTANT: accept every running run - one never closed has no page to break,
        so a reopen of it is a record of nothing."""
        state = self._state()
        self.assertFalse(state.get("report"), "premise: no page is filed")

        rc, said = self._run("reopen", "--reason", "nothing to reopen")

        self.assertEqual(2, rc, said)
        self.assertIn("already open", said)
        self.assertFalse(self._state().get("reopened"))

    def test_a_reopened_unclosed_run_is_already_open(self) -> None:
        """Control. MUTANT: key on the report marker alone - a run reopened since its page was
        filed still carries that id, and a second reopen would record the same page twice."""
        self._close()
        rc, said = self._run("reopen", "--reason", "first")
        self.assertEqual(0, rc, said)

        rc, said = self._run("reopen", "--reason", "second")

        self.assertEqual(2, rc, said)
        self.assertIn("already open", said)
        self.assertEqual(1, len(self._state().get("reopened") or []))

    def test_a_signed_run_still_reopens(self) -> None:
        """Control. MUTANT: accept only the filed-unsigned shape - the sealed run's reopen, the
        one the close's refusal names, is unchanged."""
        self._close()
        rc, _out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, err)
        self._commit("seal")
        sealed = self._state().get("outcome")
        self.assertNotEqual("running", sealed, "premise: the sign seals the run")

        rc, said = self._run("reopen", "--reason", "a late review belongs to this run")

        self.assertEqual(0, rc, said)
        reopens = self._state().get("reopened") or []
        self.assertEqual([sealed, REPORT],
                         [reopens[-1].get("from_outcome"), reopens[-1].get("report")])
        self.assertEqual("running", self._state().get("outcome"))


if __name__ == "__main__":
    unittest.main()
