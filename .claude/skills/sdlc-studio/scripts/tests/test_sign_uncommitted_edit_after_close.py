"""BG1582: once HEAD moves past the close commit, `sprint sign` still refuses an uncommitted edit
to a file a batch unit declares.

Once HEAD has moved past the commit that filed a waiting run's record, sign judges the run against
that commit rather than the working tree, so a later commit on top is not a change the report has
to describe. With no later run open, one empty commit after the close was then enough for an
uncommitted edit to a file the batch declared to be sealed over. Driven through the shipped
`sprint close` and `sprint sign` (the lean close and sign fixtures, the terminal transitions
stubbed) in a real git repository.

MUTANTS, each of which a test here fails on: (1) the committed-close path skips the declared-file
check, as before; (2) the check runs and sign seals anyway; (3) every uncommitted file is refused,
so scratch the batch never declared stops the seal; (4) the check is made while a later run is
open here, whose own work the working tree then holds.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import os
import subprocess
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
RECORD = "sdlc-studio/reports/runs/RUN-LEAN0001.json"


class SignRefusesUncommittedEditAfterCloseTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        stub = base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.root = base / "repo"
        self.root.mkdir()

    def _git(self, *argv: str) -> subprocess.CompletedProcess:
        return gitutil.git(list(argv), self.root, text=True,
                           env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _closed_with_a_commit_on_top(self) -> str:
        """Close the run, commit its paperwork, then one empty commit; the close commit."""
        lean._fixture(self.root)
        signing._git_repo(self.root)
        rc, _out, err = lean._close(self.root)
        self.assertEqual(0, rc, err)
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "close paperwork")
        filed = self._git("rev-parse", "HEAD").stdout.strip()
        self._git("commit", "-q", "--allow-empty", "-m", "later")
        return filed

    def _run_outcome(self) -> tuple[str, object]:
        record = json.loads((self.root / RECORD).read_text(encoding="utf-8"))
        live = lean._read(self.root)
        return live["outcome"], live.get("signature") or record.get("signature")

    def test_an_uncommitted_edit_to_a_declared_file_is_refused(self) -> None:
        filed = self._closed_with_a_commit_on_top()
        (self.root / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
        rc, out, err = signing._sign(self.root, REPORT)
        self.assertEqual(2, rc, out + err)
        self.assertIn(f"judged against {filed[:12]}", err,
                      "the fixture must take the committed-close path, or this tests the tree")
        self.assertIn("src/widget.py", err, "the refusal does not name the edited file")
        self.assertIn("US0101", err, "the refusal does not name the unit declaring it")
        self.assertEqual(("running", None), self._run_outcome(), "a refused sign sealed the run")

    def test_the_committed_close_still_signs_over_undeclared_scratch(self) -> None:
        filed = self._closed_with_a_commit_on_top()
        (self.root / "notes.txt").write_text("scratch\n", encoding="utf-8")
        (self.root / "README.md").write_text("an edit no batch unit declares\n", encoding="utf-8")
        rc, out, err = signing._sign(self.root, REPORT)
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"judged against {filed[:12]}", err)
        self.assertEqual("goal-reached", self._run_outcome()[0])

    def test_a_later_run_open_here_is_not_held_to_the_waiting_batch(self) -> None:
        """The later run's own work sits in the tree, judged by that run's own close."""
        sprint = lean._live("sprint")
        self._closed_with_a_commit_on_top()
        (self.root / "src" / "widget.py").write_text("x = 2\n", encoding="utf-8")
        state = lean._read(self.root)
        self.assertIn("src/widget.py", sprint._uncommitted_declared_refusal(self.root, state, ""))
        self.assertEqual("", sprint._uncommitted_declared_refusal(self.root, state, "RUN-LATER"))

if __name__ == "__main__":
    unittest.main()
