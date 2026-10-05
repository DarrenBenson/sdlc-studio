"""BG0940: a ruling between the close and the sign leaves the filed page as it was filed.

`decisions.py add --by operator` counted the ruling into the run's `rulings` while the close had
filed the page and left the outcome `running` until the sign, so the page's Rulings figure
re-derived differently; `sprint sign` then sealed it without re-deriving it, and RPT0017 was
signed already INVALIDATED (`operator_rulings` signed 1, now 2). The count now reads the
filed-page marker BG0926's late-total guard reads, and the sign re-derives the page through
`sprint_report.revalidate` - the check's own reading - before it writes the seal.

The close, the ruling, the reopen and the seal are the real `sprint close`, `decisions.py add`,
`sprint reopen` and `sprint sign` (only the chain's steps and the terminal transitions are
stubbed, as `test_lean_closed_run_late_total` drives them). Every VALID is read live, by
`sprint_report check` (LC-016).
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
import test_lean_sign as signing  # noqa: E402 - the git fixture, shared

REPORT = "RPT0001"
LATER = "2099-01-01T00:00:00Z"
#: The run's one ruling before the close, so the page's Rulings figure is measured: 1.
BEFORE = [{"id": "D0001", "by": "operator", "seat": None, "subject": None, "kind": "ruling"}]


class RulingAfterCloseTests(unittest.TestCase):

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
        lean._fixture(self.root, rulings=list(BEFORE))
        signing._git_repo(self.root)

    def _commit(self, message: str) -> None:
        for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
            gitutil.git(argv, self.root, text=True,
                        env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _cli(self, name: str, *argv: str) -> tuple[int, str]:
        mod = lean._live(name)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                # `sprint_report` takes `--root` before its verb; the others after it.
                rc = mod.main(["--root", str(self.root), *argv] if name == "sprint_report"
                              else [*argv, "--root", str(self.root)])
            except SystemExit as exc:
                rc = exc.code
        return rc, out.getvalue()

    def _check(self) -> tuple[int, str]:
        return self._cli("sprint_report", "check", "--report", REPORT)

    def _rule(self, text: str) -> str:
        rc, said = self._cli("decisions", "add", "--decision", text,
                             "--rationale", "the operator said so", "--by", "operator")
        self.assertEqual(0, rc, said)
        return said

    def _rulings(self) -> list:
        from lib import run_state  # noqa: PLC0415
        return list(run_state.read(self.root).get(run_state.RULINGS) or [])

    def _close(self) -> None:
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._commit("close paperwork")

    def _sign(self) -> tuple[int, str]:
        # The terminal transitions stubbed green on the module the CLI resolves NOW, as
        # `test_lean_sign._seal_stubbed` stubs them: these tests judge the page check.
        mod = lean._live("sprint")
        with unittest.mock.patch.object(mod, "_principal_refusals", lambda *a, **k: []), \
                unittest.mock.patch.object(mod, "_seal_units", lambda *a, **k: 0), \
                unittest.mock.patch.object(mod, "_cascade_after_signature", lambda *a, **k: None):
            return self._cli("sprint", "sign", "--report", REPORT, "--principal", "Darren")

    def test_a_ruling_after_the_close_leaves_the_page_valid(self) -> None:
        """AC1. MUTANT: HEAD's `record_ruling`, which reads only the outcome - the close leaves
        it `running`, so the ruling lands in the run's rulings and the filed page reads
        INVALIDATED (`operator_rulings` 1, now 2). The positive controls are the filed page,
        VALID before the ruling, and the ruling after a reopen, which is counted."""
        from lib import run_state  # noqa: PLC0415
        self._close()
        state = run_state.read(self.root)
        self.assertEqual(run_state.RUNNING, state.get("outcome"),
                         "premise: the close leaves the outcome running until the sign")
        self.assertEqual(REPORT, state.get("report"), "premise: the close filed the page")
        rc, out = self._check()
        self.assertEqual(0, rc, f"premise: the filed page checks VALID\n{out}")
        decisions = self.root / "sdlc-studio" / "decisions.md"

        said = self._rule("a ruling logged after the close")

        self.assertIn("a ruling logged after the close", decisions.read_text(encoding="utf-8"),
                      "the ruling itself must still be written to the log")
        self.assertEqual(BEFORE, self._rulings(),
                         f"the ruling was counted into the closed run:\n{said}")
        self.assertRegex(said, rf"{state['run_id']}\b.*\bclosed\b", said)
        self._commit("the late ruling")
        rc, out = self._check()
        self.assertEqual(0, rc, f"the late ruling moved the filed page:\n{out}")
        self.assertNotIn("INVALIDATED", out)

        # the control: a reopen breaks the filed page, so the run counts rulings again
        rc, said = self._cli("sprint", "reopen", "--reason", "the ruling belongs to this run")
        self.assertEqual(0, rc, said)
        said = self._rule("a ruling logged after the reopen")
        self.assertEqual(["operator", "operator"], [r.get("by") for r in self._rulings()], said)

    def test_sign_refuses_a_page_that_no_longer_matches(self) -> None:
        """AC2. MUTANT: HEAD's sign, which compares the tree and never re-derives the page, so a
        run state moved since the close (here the count a pre-BG0940 ruling made) is sealed over
        a page already INVALIDATED. The positive control is the same page once the run state is
        back as the close left it: it seals, and the sealed page checks VALID - the page is
        judged before the seal is written, so the signature never refuses itself."""
        from lib import run_state  # noqa: PLC0415
        self._close()
        rc, out = self._check()
        self.assertEqual(0, rc, f"premise: the filed page checks VALID\n{out}")
        moved = [*BEFORE, {**BEFORE[0], "id": "D0002"}]
        run_state.update(self.root, **{run_state.RULINGS: moved})
        rc, out = self._check()
        self.assertEqual(1, rc, f"premise: the moved run state invalidates the page\n{out}")

        rc, said = self._sign()

        self.assertEqual(2, rc, f"sign sealed a page that no longer matches:\n{said}")
        self.assertIn("operator_rulings", said)
        state = run_state.read(self.root)
        self.assertEqual(run_state.RUNNING, state.get("outcome"), "the run was sealed")
        self.assertIsNone(state.get("signature"), "a signature was written")

        # the control: the run state as the close left it seals
        run_state.update(self.root, **{run_state.RULINGS: list(BEFORE)})
        rc, said = self._sign()
        self.assertEqual(0, rc, said)
        self.assertEqual("Darren", (run_state.read(self.root).get("signature") or {})
                         .get("principal"))
        self._commit("seal")
        rc, out = self._check()
        self.assertEqual(0, rc, f"the sealed page does not check VALID:\n{out}")


if __name__ == "__main__":
    unittest.main()
