"""BG1120: an author's edit made while resolving a merge stales the self-check record.

The own-change view sets aside another unit's later commits to a declared file by walking `git
log --name-only` over it, and a merge commit lists no file there. An edit the author made while
resolving a merge conflict was never seen, so the record's digest still matched the content with
the other units' commits set aside, and the brief gate under `block` admitted a diff the
self-check never covered. A merge now touches each declared file it left differing both from
git's own automatic merge of its parents (its remerge diff, `git log --remerge-diff`) and from
every parent: its own content, such as a conflict resolution. A merge git made by itself names
nothing, nor does a file it took whole from one parent, so a clean merge of another unit's
branch, or of two units' edits to one file, still does not stale the record.

Each case drives `critic.py` through its entry point in a throwaway project, the fixture shared
with `test_self_check_survives_a_later_unit`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_self_check_survives_a_later_unit as later  # noqa: E402 - the shared fixture

A, SHARED = later.A, later.SHARED


def _branch(root: Path) -> str:
    return gitutil.git(["rev-parse", "--abbrev-ref", "HEAD"], root, text=True).stdout.strip()


def _merge(root: Path, branch: str, resolved: str | None = None) -> None:
    """Merge `branch`, writing `resolved` to the shared file first when the merge conflicts,
    and commit it under git's own subject, which names no unit."""
    done = gitutil.git(["merge", "-q", "--no-edit", branch], root, check=False)
    if done.returncode != 0:
        assert resolved is not None, done.stderr
        later._write(root, SHARED, resolved)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "--no-verify", "--no-edit"], root)
    subject = gitutil.git(["log", "-1", "--format=%s"], root, text=True).stdout.strip()
    assert subject.startswith("Merge branch"), subject


class MergeCommitTests(unittest.TestCase):

    def setUp(self) -> None:
        self._dirs = [tempfile.TemporaryDirectory() for _ in range(2)]
        self.root, self.scratch = (Path(d.name) for d in self._dirs)
        later._project(self.root)
        self.main = _branch(self.root)
        later._record(self.root, self.scratch)

    def tearDown(self) -> None:
        for d in self._dirs:
            d.cleanup()

    def _brief(self):
        return later._brief(self.root)

    def _two_sides(self) -> None:
        """Another unit's commit to the shared file on a side branch and a third unit's on the
        main line, each changing the same line, so merging the side conflicts."""
        root = self.root
        gitutil.git(["checkout", "-q", "-b", "side"], root)
        later._commit(root, "feat(US0102): side", SHARED, "def s():\n    return 2\n")
        gitutil.git(["checkout", "-q", self.main], root)
        later._commit(root, "feat(US0103): main", SHARED, "def s():\n    return 3\n")

    def test_an_edit_in_a_merge_resolution_stales_the_record(self) -> None:
        """AC1. Mutant: the walk without the merge's remerge diff, so the merge lists no file,
        both units' commits are set aside and the record reads current. The guard: the content as it stands moved,
        so only the own-change view could have admitted it."""
        self.assertEqual(0, self._brief().returncode, "premise: a fresh record is admitted")
        self._two_sides()
        _merge(self.root, "side", "def s():\n    return 2 + 3 + 4\n")
        self.assertNotEqual(later.critic.read_self_checks(self.root)[-1]["digest"],
                            later.critic.affects_digest(self.root, A))
        r = self._brief()
        self.assertEqual(2, r.returncode,
                         f"an edit in a merge resolution was admitted:\n{r.stderr}")
        self.assertEqual("", r.stdout)
        self.assertIn(later.STALE, r.stderr)

    def test_an_edit_in_a_merge_resolution_stales_the_record_below_the_repository_top(self):
        """AC1 for a project whose root is a directory of its repository: the remerge diff is
        read from the root, as the Affects are. Mutant: the merge's files read from the
        repository's top (`proj/src/shared.py`), which matches no declared file, so the
        resolution is set aside and the record reads current."""
        top = Path(self._dirs[0].name) / "top"
        root = top / "proj"
        later._project(root, repo=False)
        gitutil.git(["init", "-q"], top)
        later._commit(top, f"feat({A}): the shared module")
        self.root = root
        later._record(root, self.scratch)
        self.assertEqual(0, self._brief().returncode, "premise: a fresh record is admitted")
        self._two_sides()
        _merge(root, "side", "def s():\n    return 2 + 3 + 4\n")
        r = self._brief()
        self.assertEqual(2, r.returncode, f"a resolution below the top was admitted:\n{r.stderr}")
        self.assertIn(later.STALE, r.stderr)

    def test_a_merge_git_cannot_read_by_its_remerge_diff_lists_no_file(self) -> None:
        """A git too old to give a remerge diff (before 2.36) refuses the flag; a merge then
        lists no file, as it did before, and the walk still sets aside another unit's commits.
        Mutants: the refusal, or git unable to run, answered with nothing in place of an empty
        map, so the walk fails; git unable to run left unguarded; a file git cannot show at a
        merge's commit left to propagate rather than answered as no judgement."""
        root = self.root
        critic = later.critic
        self._two_sides()
        _merge(root, "side", "def s():\n    return 2 + 3 + 4\n")
        self.assertIn("is stale", critic.self_check_gap(root, A) or "",
                      "premise: a git that reads the merge finds the resolution")
        base = critic.read_self_checks(root)[-1]["commit"]
        real = critic._git
        for refused in (subprocess.CompletedProcess([], 129, b"", b"unknown option\n"), None):
            def old(at, *args, refused=refused):
                return refused if "--remerge-diff" in args else real(at, *args)

            with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                    unittest.mock.patch.object(critic, "_git", old):
                self.assertIsNone(critic.self_check_gap(root, A), refused)
                self.assertEqual({}, critic._merge_resolutions(root, base, [later.SHARED]))

        def unreadable(*_args):
            raise critic._GitUnreadable("git could not show it")

        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                unittest.mock.patch.object(critic, "_rev_blob", unreadable):
            self.assertIsNone(critic._own_change_digest(root, A, base))

    def test_a_merge_taking_one_file_whole_and_merging_another_lists_only_its_own(self):
        """A merge that git merged one declared file in by itself and whose conflict in another
        was resolved by taking one side's file whole holds no content of its own in either.
        Mutant: every file the remerge diff names read as the merge's own, so the file taken
        whole from one parent stales the record."""
        root = self.root
        test = "tests/test_shared.py"
        lines = [f"V{n} = {n}\n" for n in range(1, 13)]
        later._commit(root, f"feat({A}): twelve lines", test, "".join(lines))
        later._record(root, self.scratch)
        gitutil.git(["checkout", "-q", "-b", "side"], root)
        later._write(root, test, "".join(["V2 = 2.5\n" if n == 1 else x
                                          for n, x in enumerate(lines)]))
        later._commit(root, "feat(US0102): side", later.SHARED, "def s():\n    return 2\n")
        gitutil.git(["checkout", "-q", self.main], root)
        later._write(root, test, "".join(["V11 = 11.5\n" if n == 10 else x
                                          for n, x in enumerate(lines)]))
        later._commit(root, "feat(US0103): main", later.SHARED, "def s():\n    return 3\n")
        _merge(root, "side", "def s():\n    return 2\n")
        merged = (root / test).read_text(encoding="utf-8")
        self.assertTrue("V2 = 2.5" in merged and "V11 = 11.5" in merged,
                        "premise: git merged the test file from both sides")
        listed = gitutil.git(["log", "-1", "--remerge-diff", "--name-only", "--format=", "HEAD"],
                             root, text=True).stdout.split()
        self.assertEqual([later.SHARED], listed, "premise: the remerge diff names the resolved file")
        base = later.critic.read_self_checks(root)[-1]["commit"]
        head = gitutil.git(["rev-parse", "HEAD"], root, text=True).stdout.strip()
        self.assertEqual({head: []},
                         later.critic._merge_resolutions(root, base, [later.SHARED, test]))
        r = self._brief()
        self.assertEqual(0, r.returncode, f"a file taken whole from one side staled the record:"
                                          f"\n{r.stderr}")
        self.assertNotIn(later.STALE, r.stderr)

    def test_a_clean_merge_of_two_units_edits_to_one_file_does_not_stale_the_record(self):
        """A merge git made by itself, combining another unit's edit on a side branch with a
        third unit's edit to another line of the same file on the main line, holds no content
        of its own, though the file it leaves differs from both parents. Mutant: the walk
        reading the combined diff (`-c`), which names the file, so the merge reads as the
        author's and the record is refused as stale where the base admitted it."""
        root = self.root
        lines = [f"V{n} = {n}\n" for n in range(1, 13)]
        later._commit(root, f"feat({A}): twelve lines", SHARED, "".join(lines))
        later._record(root, self.scratch)
        self.assertEqual(0, self._brief().returncode, "premise: the new record is admitted")
        gitutil.git(["checkout", "-q", "-b", "side"], root)
        later._commit(root, "feat(US0102): line two", SHARED,
                      "".join(["V2 = 'two'\n" if n == 1 else x for n, x in enumerate(lines)]))
        gitutil.git(["checkout", "-q", self.main], root)
        later._commit(root, "feat(US0103): line eleven", SHARED,
                      "".join(["V11 = 'eleven'\n" if n == 10 else x for n, x in enumerate(lines)]))
        _merge(root, "side")
        merged = (root / SHARED).read_text(encoding="utf-8")
        self.assertIn("V2 = 'two'", merged, "premise: the merge combined both sides")
        self.assertIn("V11 = 'eleven'", merged, "premise: the merge combined both sides")
        r = self._brief()
        self.assertEqual(0, r.returncode, f"a clean merge of two sides staled the record:\n"
                                          f"{r.stderr}")
        self.assertNotIn(later.STALE, r.stderr)

    def test_a_merge_taking_a_file_whole_from_one_side_does_not_stale_the_record(self) -> None:
        """The positive controls. Mutants: every merge naming a declared file read as the
        author's (`-m`, which names a file the merge brought in from its other parent); the
        remerge diff read for a merge that took the file whole from one side."""
        root = self.root
        # another unit's branch merged cleanly over a main line that did not touch the file
        gitutil.git(["checkout", "-q", "-b", "side"], root)
        later._commit(root, "feat(US0102): side", SHARED, "def s():\n    return 2\n")
        gitutil.git(["checkout", "-q", self.main], root)
        later._commit(root, "chore(US0103): elsewhere", "src/other.py", "def o():\n    return 9\n")
        _merge(root, "side")
        r = self._brief()
        self.assertEqual(0, r.returncode, f"a clean merge staled the record:\n{r.stderr}")
        self.assertNotIn(later.STALE, r.stderr)
        # a conflicted merge resolved by taking one side's file whole
        gitutil.git(["checkout", "-q", "-b", "side2"], root)
        later._commit(root, "feat(US0104): side two", SHARED, "def s():\n    return 4\n")
        gitutil.git(["checkout", "-q", self.main], root)
        later._commit(root, "feat(US0105): main two", SHARED, "def s():\n    return 5\n")
        _merge(root, "side2", "def s():\n    return 4\n")
        r = self._brief()
        self.assertEqual(0, r.returncode, f"a merge taking one side staled the record:\n{r.stderr}")
        self.assertNotIn(later.STALE, r.stderr)


if __name__ == "__main__":
    unittest.main()
