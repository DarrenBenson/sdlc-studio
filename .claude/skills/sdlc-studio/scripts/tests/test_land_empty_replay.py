"""BG1409: replaying a staged change onto main lands no empty commit for a builder commit main holds.

`sprint lane land` replays the staged change onto the root's branch before the commit. That
replay rebased the builder's own commits too, with flags meant for the staged change alone, so a
builder commit main already carried was kept as an empty commit and landed. Every case drives
`sprint.py lane land` through its entry point, on `test_lane_land`'s throwaway repository, stub
hook and builder worktree.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_land as base  # noqa: E402 - the lane fixture every landing case shares

A = base.A


def _empty_commits(root: Path) -> list[str]:
    """The subject of each commit on main whose tree is its parent's: an empty commit."""
    out = []
    for sha in base._git(root, "rev-list", "--no-merges", "main").split():
        if len(base._git(root, "rev-list", "--parents", "-n", "1", sha).split()) < 2:
            continue  # the fixture's root commit has no parent to compare with
        if gitutil.git(["diff", "--quiet", f"{sha}^", sha], root, check=False).returncode == 0:
            out.append(base._git(root, "log", "-1", "--format=%s", sha))
    return out


class LandEmptyReplayTests(base._LaneFixture):

    def _builder_commit_main_holds(self) -> None:
        """A builder commit in the worktree whose change main then takes in a commit of its own,
        as a fix cherry-picked to main while the lane ran."""
        base._write(self.wt, "src/b.py", "B = 2\n")
        gitutil.git(["add", "--", "src/b.py"], self.wt)
        gitutil.git(["commit", "-q", "-m", "fix: b is two, in the lane"], self.wt)
        self._move_main("src/b.py", "B = 2\n")

    def test_the_probe_names_an_empty_commit_on_main(self) -> None:
        """Positive control for `_empty_commits`, so neither case passes on a probe that finds
        nothing: an empty commit made on main is named, and a commit with a change is not."""
        self.assertEqual([], _empty_commits(self.root))
        gitutil.git(["commit", "-q", "--allow-empty", "-m", "chore: nothing"], self.root)
        self._move_main("src/b.py", "B = 3\n")
        self.assertEqual(["chore: nothing"], _empty_commits(self.root))

    def test_a_builder_commit_main_holds_lands_no_empty_commit(self) -> None:
        """MUTANT: the replay rebases with `--empty=keep --reapply-cherry-picks` again (the
        builder commit is kept, emptied, and lands)."""
        self._builder_commit_main_holds()
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual([], _empty_commits(self.root), "an empty commit landed on main")
        # positive control: the staged change landed as the lane's one commit, on main's head
        self.assertEqual(f"feat({A}): a is two", base._git(self.root, "log", "-1", "--format=%s"))
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))
        self.assertEqual("B = 2\n", (self.root / "src/b.py").read_text(encoding="utf-8"))
        self.assertIn("replayed the staged change onto main", out)
        self.assertFalse(self.wt.exists(), "the worktree was not removed")

    def test_a_staged_change_main_holds_beside_such_a_commit_leaves_nothing_to_commit(self):
        """MUTANT: the replayed change is reset off whatever commit the rebase ends on (the
        builder's own commit is taken back out and its change staged again). Both the builder
        commit and the staged change are on main, so nothing lands and no hook runs."""
        self._builder_commit_main_holds()
        head = self._move_main("src/a.py", "A = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        before = self._hook_runs_in_the_worktree()  # the builder's own commit ran the hook
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn("the staged change is already on main", out)
        self.assertEqual(before, self._hook_runs_in_the_worktree(),
                         "an empty change was committed")
        self.assertEqual(head, base._git(self.root, "rev-parse", "HEAD"))
        self.assertEqual([], _empty_commits(self.root), "an empty commit landed on main")

    def test_a_builder_commit_main_holds_in_a_different_commit_is_dropped(self) -> None:
        """MUTANT: the replay rebases with `--empty=keep` (main took the builder's change in a
        commit carrying another change too, so git's cherry-pick detection does not drop it: the
        builder commit is emptied by the rebase, kept, and lands)."""
        base._write(self.wt, "src/b.py", "B = 2\n")
        gitutil.git(["add", "--", "src/b.py"], self.wt)
        gitutil.git(["commit", "-q", "-m", "fix: b is two, in the lane"], self.wt)
        base._write(self.root, "src/b.py", "B = 2\n")
        base._write(self.root, "src/c.py", "C = 1\n")
        gitutil.git(["add", "--", "src/b.py", "src/c.py"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: main takes b with c"], self.root)
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual([], _empty_commits(self.root), "an empty commit landed on main")
        subjects = base._git(self.root, "log", "--format=%s", "main").splitlines()
        self.assertNotIn("fix: b is two, in the lane", subjects)
        self.assertEqual(f"feat({A}): a is two", subjects[0])

    def test_a_prepare_commit_msg_hook_leaves_the_replay_off_main(self) -> None:
        """The rebase of the replay runs a `prepare-commit-msg` hook on the scratch commit too,
        so the scratch commit is not told by its message: the lane's own commit lands, through
        the pre-commit hook, and no replay commit reaches main."""
        hook = self.root.parent / "hooks" / "prepare-commit-msg"
        hook.write_text("#!/bin/sh\nprintf '\\nPrepared-By: a hook\\n' >> \"$1\"\n",
                        encoding="utf-8")
        hook.chmod(0o755)
        moved = self._move_main("src/b.py", "B = 2\n")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land(A)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual(1, self._hook_runs_in_the_worktree(), "the lane's commit ran no hook")
        self.assertEqual(f"feat({A}): a is two", base._git(self.root, "log", "-1", "--format=%s"))
        self.assertEqual(moved, base._git(self.root, "rev-parse", "HEAD^"))
        self.assertNotIn("the staged change is already on main", out)
        self.assertNotIn("lane land: the staged change, replayed",
                         base._git(self.root, "log", "--format=%B", "main"))
        self.assertEqual("A = 2\n", (self.root / "src/a.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
