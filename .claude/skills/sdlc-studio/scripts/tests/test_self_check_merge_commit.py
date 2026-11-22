"""BG1120: an author's edit made while resolving a merge stales the self-check record.

The own-change view sets aside another unit's later commits to a declared file by walking `git
log --name-only` over it, and a merge commit lists no file there. An edit the author made while
resolving a merge conflict was never seen, so the record's digest still matched the content with
the other units' commits set aside, and the brief gate under `block` admitted a diff the
self-check never covered. The walk now reads a merge's combined diff (`git log -c`), which names
a file the merge left differing from every parent, its own content: a conflict resolution. A
merge that takes a file whole from one parent names nothing, so a clean merge of another unit's
branch still does not stale the record.

Each case drives `critic.py` through its entry point in a throwaway project, the fixture shared
with `test_self_check_survives_a_later_unit`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import sys
import tempfile
import unittest
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
        """AC1. Mutant: the walk without `-c`, so the merge lists no file, both units' commits
        are set aside and the record reads current. The guard: the content as it stands moved,
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

    def test_a_merge_taking_a_file_whole_from_one_side_does_not_stale_the_record(self) -> None:
        """The positive controls. Mutants: every merge naming a declared file read as the
        author's (`-m`, which names a file the merge brought in from its other parent); the
        combined diff read for a merge that took the file whole from one side."""
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
