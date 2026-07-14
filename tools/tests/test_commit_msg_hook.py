"""Repo-only test for the tracked .githooks/commit-msg gate.

The hook's DECISION logic is unit-tested in the shipped engagement_floor suite
(CommitMsgCheckTests). This test exercises the bash gate end-to-end, the way git invokes
it (a message file path as $1): a multi-id subject with no `Refs:` trailer is REFUSED
(non-zero, the commit does not land), the same subject with the trailers passes, and the
things it deliberately still lets through keep passing - a solo id, a merge, a revert, a
fixup/squash, and every honest-degrade case (no script / unreadable message).
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "commit-msg"


def _run(message: str, *, path: str | None = None, cwd: str | None = None,
         env_extra: dict[str, str] | None = None):
    with tempfile.TemporaryDirectory() as d:
        msg = Path(d) / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = dict(os.environ)
        env.update(env_extra or {})
        target = path if path is not None else str(msg)
        return subprocess.run(["bash", str(HOOK), target], capture_output=True,
                              text=True, env=env, cwd=cwd)


class CommitMsgGateTests(unittest.TestCase):
    """The load-bearing pair: refuse the bare multi-id subject, pass the trailered one."""

    def test_multi_id_without_refs_is_refused(self):
        r = _run("feat(CR0257, CR0258): batch fix")
        self.assertNotEqual(r.returncode, 0,
                            "a multi-id subject with no Refs: trailer must REFUSE the commit")
        out = r.stdout + r.stderr
        # The refusal has to be cheap to satisfy: the exact trailer lines, ready to paste.
        self.assertIn("Refs: CR0257", out)
        self.assertIn("Refs: CR0258", out)
        self.assertIn("--no-verify", out)  # the one escape, named

    def test_multi_id_with_refs_trailers_passes(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\nRefs: CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).strip(), "")

    def test_multi_id_with_comma_list_trailer_passes(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257, CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_partially_covered_multi_id_is_refused_naming_the_gap(self):
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\n")
        self.assertNotEqual(r.returncode, 0)
        out = r.stdout + r.stderr
        self.assertIn("Refs: CR0258", out)


class DeliberatelyAllowedTests(unittest.TestCase):
    """What the gate lets through on purpose. Each of these must keep passing."""

    def test_solo_id_without_a_trailer_passes(self):
        # One id: attribution is unambiguous, the floor's git leg already handles it.
        r = _run("fix(BG0134): the hook now refuses")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_no_id_passes(self):
        r = _run("docs: tidy the README")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_merge_subject_passes(self):
        # git wrote this message; the author cannot restructure it.
        r = _run("Merge pull request #7 from x (CR0257, CR0258)")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_revert_subject_passes(self):
        r = _run('Revert "feat(CR0257, CR0258): batch fix"\n\nThis reverts commit deadbeef.\n')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fixup_and_squash_subjects_pass(self):
        for prefix in ("fixup! ", "squash! ", "amend! "):
            with self.subTest(prefix=prefix):
                r = _run(prefix + "feat(CR0257, CR0258): batch fix")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_commented_scaffolding_is_ignored(self):
        # git's scaffolding (# lines, and in verbose mode the diff) is not the subject.
        msg = ("# Please enter the commit message...\n"
               "# On branch main\n"
               "fix(BG0134): solo\n")
        r = _run(msg)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class HonestDegradeTests(unittest.TestCase):
    def test_missing_message_file_does_not_block(self):
        r = _run("", path="/nonexistent/COMMIT_EDITMSG")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_no_argument_does_not_block(self):
        r = subprocess.run(["bash", str(HOOK)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_outside_a_repo_carrying_the_script_degrades_to_pass(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            r = _run("feat(CR0257, CR0258): batch fix", cwd=elsewhere)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class InProgressOperationTests(unittest.TestCase):
    """A replayed/machine-written message (merge, revert, cherry-pick, rebase) is exempt:
    the author did not type it, and the work it records was gated on its original commit.
    Exercised in a throwaway git repo that symlinks this repo's skill scripts, so the
    real repo's .git is never touched."""

    def _sandbox(self, d: str) -> Path:
        root = Path(d)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        os.symlink(REPO / ".claude", root / ".claude")
        return root

    def test_multi_id_is_refused_in_the_sandbox_without_a_marker(self):
        # The negative control: proves the sandbox itself is not what lets the next
        # test's commit through - the marker is.
        with tempfile.TemporaryDirectory() as d:
            root = self._sandbox(d)
            r = _run("feat(CR0257, CR0258): batch fix", cwd=str(root))
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_in_progress_markers_exempt_the_commit(self):
        for marker in ("MERGE_HEAD", "REVERT_HEAD", "CHERRY_PICK_HEAD", "rebase-merge"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as d:
                root = self._sandbox(d)
                target = root / ".git" / marker
                if marker == "rebase-merge":
                    target.mkdir()
                else:
                    target.write_text("deadbeef\n", encoding="utf-8")
                r = _run("feat(CR0257, CR0258): batch fix", cwd=str(root))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class NoSecondBypassTests(unittest.TestCase):
    def test_the_old_strict_env_var_is_not_a_bypass(self):
        # SDLC_ENGAGEMENT_STRICT used to be the opt-in to block. Blocking is now the
        # behaviour; no env var may turn the gate back off (--no-verify is the one escape).
        for value in ("0", "", "1"):
            with self.subTest(value=value):
                r = _run("feat(CR0257, CR0258): batch fix",
                         env_extra={"SDLC_ENGAGEMENT_STRICT": value})
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
