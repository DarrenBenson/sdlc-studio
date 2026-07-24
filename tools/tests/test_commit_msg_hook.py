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
         env_extra: dict[str, str] | None = None, mid_operation: str | None = None):
    """Run the commit-msg hook against `message` in a HERMETIC fixture repo.

    The hook resolves its repo root and git dir from wherever it runs; run in the OUTER repo it
    reads the outer repo's state, and while THAT repo is mid-merge (which happens whenever the
    pre-commit suite runs during a merge commit) its in-progress-operation guard exits the hook
    early and every refusal test passes vacuously, or - worse - fails because the refusal never
    ran (BG0281). So each call builds its own throwaway git repo and runs the hook there.

    The checker (`engagement_floor.py` and its `lib/`) is made present via a symlinked `scripts`
    dir at the path the hook resolves, so the refusal actually executes - the isolation does not
    make the test vacuous (AC2). `mid_operation` writes the named in-progress marker into the
    FIXTURE's git dir, so the mid-merge behaviour is exercised deliberately rather than inherited.
    """
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        clean = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                 "GIT_CONFIG_SYSTEM": os.devnull}
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            clean.pop(name, None)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=clean)
        scripts = repo / ".claude" / "skills" / "sdlc-studio"
        scripts.mkdir(parents=True)
        (scripts / "scripts").symlink_to(
            REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        if mid_operation:
            (repo / ".git" / mid_operation).write_text("x\n", encoding="utf-8")
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        env = dict(clean)
        env.update(env_extra or {})
        target = path if path is not None else str(msg)
        return subprocess.run(["bash", str(HOOK), target], capture_output=True,
                              text=True, env=env, cwd=cwd if cwd is not None else str(repo))


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


class MidMergeIsolationTests(unittest.TestCase):
    """BG0281: a conflicted merge could not be committed through the gate, because these very
    tests failed while the outer repo was mid-merge - they inherited its MERGE_HEAD and saw the
    hook's correct early exit. The fixture is now hermetic, so the outer state cannot leak in."""

    def test_the_refusal_still_fires_while_the_OUTER_repo_is_mid_merge(self):
        # The regression proof: even if the outer repo carries MERGE_HEAD right now, a bare
        # multi-id subject is still refused, because the hook reads the fixture's state.
        r = _run("feat(CR0257, CR0258): batch fix")
        self.assertNotEqual(r.returncode, 0,
                            "the hook read the outer repo's merge state instead of the fixture's")
        self.assertIn("Refs: CR0258", r.stdout + r.stderr)

    def test_the_fixture_is_not_vacuous_the_checker_actually_ran(self):
        # AC2: a passing trailered commit must be the CHECKER passing, not the checker being
        # absent. The refusal test above already proves the checker fires; this proves the
        # symlinked checker resolves (a bad symlink would make the hook exit 0 on a bare subject).
        r = _run("feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\nRefs: CR0258\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_a_marker_in_the_fixture_itself_exits_early_as_designed(self):
        # AC3, the intended behaviour isolated: with the fixture ITSELF mid-merge, the hook
        # exits 0 on a multi-id subject - so a real merge commit is never blocked by the gate.
        r = _run("feat(CR0257, CR0258): merge two branches", mid_operation="MERGE_HEAD")
        self.assertEqual(r.returncode, 0,
                         "the hook must not block a commit while a merge is genuinely in progress")


if __name__ == "__main__":
    unittest.main()
