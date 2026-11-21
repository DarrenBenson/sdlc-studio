"""BG1590: once HEAD has moved past the close commit, `sprint sign` re-derives the page from that
commit, as it already takes the tree check from it.

A waiting run is judged against its committed close once HEAD moves past it, and a later change
belongs in a commit on top (D0524). Sign took the tree check from the close commit but re-derived
the page from the working tree, so a ruling the operator wrote into the retro's Known issues
carried table after the close moved the page's issue detail and sign refused the run with 'no
longer matches what it re-derives to'. Driven through the shipped `sprint close` and `sprint sign`
(the lean close and sign fixtures, the terminal transitions stubbed) in a closing checkout and a
fresh clone of it, with one open finding the run raised and the close left unruled.

MUTANTS, each of which a test here fails on: (1) the page is re-derived from the working tree,
as before (the ruling refuses the seal); (2) the page check is dropped whenever sign judges
against the close commit (the control's page, which its own close commit does not derive, is
sealed); (3) the close commit's tree is left checked out beside the repository after sign.
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
FINDING = "BG0201"
STALE = "no longer matches what it re-derives to"


class SignJudgesPageFromCloseCommitTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        stub = self.base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (self.base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(self.base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.closer = self.base / "closer"
        self.closer.mkdir()

    def _git(self, root: Path, *argv: str) -> subprocess.CompletedProcess:
        return gitutil.git(list(argv), root, text=True,
                           env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})

    def _commit(self, message: str) -> None:
        self._git(self.closer, "add", "-A")
        self._git(self.closer, "commit", "-q", "--allow-empty", "-m", message)

    def _finding(self, title: str = "a finding the close left unruled") -> None:
        d = self.closer / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{FINDING}-finding.md").write_text(
            f"# {FINDING}: {title}\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Raised-in-batch:** none open - raised outside a delivery batch, "
            "2026-09-23T13:28:22Z\n", encoding="utf-8")

    def _close(self, *, before_commit=None) -> str:
        """Close the run in the closing checkout and commit its paperwork; the close commit."""
        lean._fixture(self.closer)
        self._finding()
        signing._git_repo(self.closer)
        rc, _out, err = lean._close(self.closer)
        self.assertEqual(0, rc, err)
        page = json.loads((self.closer / "sdlc-studio" / "reports" / f"{REPORT}.json")
                          .read_text(encoding="utf-8"))
        rows = next(s for s in page["sections"] if s["key"] == "known_issues")["rows"]
        self.assertIn(FINDING, [r["issue_id"]["value"] for r in rows],
                      "the close must list the finding, or the ruling moves nothing")
        if before_commit:
            before_commit()
        self._commit("close paperwork")
        return self._git(self.closer, "rev-parse", "HEAD").stdout.strip()

    def _rule_after_the_close(self) -> None:
        """A later commit: the operator's not-stop-ship ruling in the retro's carried table."""
        retro = self.closer / "sdlc-studio" / "retros" / "RETRO0001-lean.md"
        retro.write_text(retro.read_text(encoding="utf-8")
                         + "\n## Known issues carried\n\n| ID | Ruling | Ruled by | Date |\n"
                           f"| --- | --- | --- | --- |\n| {FINDING} | not-stop-ship | Maya | "
                           "2026-09-30 |\n", encoding="utf-8")
        self._commit("rule the finding the close left unruled")

    def _sign_in_a_clone(self, name: str) -> tuple[int, str, Path]:
        clone = self.base / name
        self._git(self.base, "clone", "-q", f"file://{self.closer}", str(clone))
        rc, out, err = signing._sign(clone, REPORT)
        return rc, out + err, clone

    def _record(self, root: Path) -> dict:
        return json.loads((root / RECORD).read_text(encoding="utf-8"))

    def test_a_ruling_committed_after_the_close_does_not_refuse_the_seal(self) -> None:
        """AC1: the tree and the page are both judged against the close commit."""
        filed = self._close()
        self._rule_after_the_close()
        rc, text, clone = self._sign_in_a_clone("ruled")
        self.assertIn(f"judged against {filed[:12]}", text)
        self.assertNotIn(STALE, text, "the page was re-derived from the working tree")
        self.assertEqual(0, rc, text)
        record = self._record(clone)
        self.assertEqual("goal-reached", record["outcome"])
        self.assertEqual(REPORT, record["signature"]["report"])
        listed = self._git(clone, "worktree", "list", "--porcelain").stdout
        self.assertEqual(1, listed.count("worktree "),
                         f"the close commit's tree was left checked out:\n{listed}")

    def test_a_page_the_close_commit_does_not_derive_is_still_refused(self) -> None:
        """AC2, the positive control: the close commit holds the finding retitled after the page
        was filed, and the ruling lands in a commit on top. Re-derived from the close commit,
        the page no longer matches, so sign refuses and seals nothing."""
        retitled = "a finding retitled after the page was filed"
        filed = self._close(before_commit=lambda: self._finding(retitled))
        self._rule_after_the_close()
        rc, text, clone = self._sign_in_a_clone("retitled")
        self.assertIn(f"judged against {filed[:12]}", text)
        self.assertEqual(2, rc, text)
        self.assertIn(STALE, text)
        self.assertIn(retitled, text, "the refusal is not the close commit's derivation")
        self.assertNotIn("not-stop-ship, ruled by Maya", text,
                         "the refusal read the ruling the later commit made")
        record = self._record(clone)
        self.assertEqual(("running", None), (record["outcome"], record.get("signature")))


if __name__ == "__main__":
    unittest.main()
