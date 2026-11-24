"""BG1713: lanes started together add their worktrees one at a time.

Two `git worktree add` runs against one repository at once can refuse one of them with a commondir
error (a CI run of `sprint lane run` over two units saw it). `lanes._lane_worktree` now makes its
add holding a lock file in the git common dir. Each case runs it against a throwaway repository;
the race is made deterministic by holding every add open for a moment and counting how many are
open together, not by hoping git collides.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import threading
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

UNITS = [f"US010{n}" for n in range(6)]
#: how long each add is held open, in seconds
HELD = 0.15
#: a process that takes the lock, says so, and holds it for `{hold}` seconds
HOLDER = """import fcntl, sys, time
fh = open(sys.argv[1], "a")
fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
print("held", flush=True)
time.sleep({hold})
"""


class LaneWorktreeConcurrentTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve() / "repo"
        self.root.mkdir()
        (self.root / "a.txt").write_text("a\n", encoding="utf-8")
        gitutil.git(["init", "-q", "-b", "main"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], self.root)
        self.lock = self.root / ".git" / lanes.WORKTREE_LOCK
        self.open_adds = self.most_open = 0
        self.adds: list[str] = []
        self._count = threading.Lock()
        self.real = lanes._run_git

    def _held_open(self, cwd, *args):
        """`lanes._run_git`, a `worktree add` held open for `HELD` seconds and counted."""
        if args[:2] != ("worktree", "add"):
            return self.real(cwd, *args)
        with self._count:
            self.open_adds += 1
            self.most_open = max(self.most_open, self.open_adds)
            self.adds.append(" ".join(args))
        try:
            time.sleep(HELD)
            return self.real(cwd, *args)
        finally:
            with self._count:
                self.open_adds -= 1

    def test_parallel_adds_all_succeed(self) -> None:
        got: dict[str, Path | Exception] = {}

        def add(unit: str) -> None:
            try:
                got[unit] = lanes._lane_worktree(self.root, unit)
            except Exception as exc:  # noqa: BLE001 - the case reads what each call did
                got[unit] = exc

        with unittest.mock.patch.object(lanes, "_run_git", self._held_open):
            threads = [threading.Thread(target=add, args=(unit,)) for unit in UNITS]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(60)
        self.assertEqual(sorted(UNITS), sorted(got))
        for unit, made in got.items():
            self.assertIsInstance(made, Path, f"{unit}: {made!r}")
            self.assertTrue(made.is_dir(), unit)
            self.assertEqual(f"lane-{unit.lower()}", made.name)
        self.assertEqual(len(UNITS), len(self.adds), "premise: every unit ran its add")
        self.assertEqual(1, self.most_open, "adds ran together")

    def test_two_calls_for_one_unit_add_it_once(self) -> None:
        """The add re-checks the path once it holds the lock: the second of two lanes for one
        unit reuses the worktree the first added instead of adding it again and failing."""
        got: list[Path | Exception] = []

        def add() -> None:
            try:
                got.append(lanes._lane_worktree(self.root, "US0101"))
            except Exception as exc:  # noqa: BLE001
                got.append(exc)

        with unittest.mock.patch.object(lanes, "_run_git", self._held_open):
            threads = [threading.Thread(target=add) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(60)
        self.assertEqual(1, len(self.adds), self.adds)
        self.assertEqual(2, len(got))
        self.assertTrue(all(isinstance(g, Path) for g in got), got)
        self.assertEqual(got[0], got[1])

    def test_the_add_waits_for_the_common_dir_lock_and_releases_it(self) -> None:
        holder = subprocess.Popen(
            [sys.executable, "-c", HOLDER.format(hold=1.0), str(self.lock)],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.kill)
        self.assertEqual("held", holder.stdout.readline().strip(), "premise: the lock is held")
        held_at = time.monotonic()
        path = lanes._lane_worktree(self.root, "US0101")
        waited = time.monotonic() - held_at
        self.assertGreaterEqual(waited, 0.5, "the add did not wait for the lock")
        self.assertTrue(path.is_dir())
        self._assert_free()
        # released after a refused add as well: the unit's branch is checked out elsewhere
        gitutil.git(["branch", "lane-us0102"], self.root)
        other = Path(self._tmp.name) / "elsewhere"
        gitutil.git(["worktree", "add", "-q", str(other), "lane-us0102"], self.root)
        with self.assertRaises(lanes.LandError) as caught:
            lanes._lane_worktree(self.root, "US0102")
        self.assertIn("could not be created", str(caught.exception))
        self._assert_free()

    def _assert_free(self) -> None:
        """The lock can be taken at once: nothing still holds it."""
        import fcntl  # noqa: PLC0415 - POSIX only, as the lock is
        with open(self.lock, "a") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def test_a_lock_held_past_the_wait_refuses_the_add(self) -> None:
        holder = subprocess.Popen(
            [sys.executable, "-c", HOLDER.format(hold=3.0), str(self.lock)],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.kill)
        self.assertEqual("held", holder.stdout.readline().strip())
        with unittest.mock.patch.object(lanes, "WORKTREE_LOCK_WAIT", 0.3):
            with self.assertRaises(lanes.LandError) as caught:
                lanes._lane_worktree(self.root, "US0101")
        self.assertIn("was still held after", str(caught.exception))
        self.assertFalse((self.root / lanes.RUN_WORKTREES / "lane-us0101").exists())

    def test_a_linked_worktree_root_locks_in_the_main_checkouts_common_dir(self) -> None:
        """From a linked worktree the git dir is `.git/worktrees/<name>` and the root's `.git`
        is a file; the lock is still the one file in the common dir, so lanes started from the
        main checkout and from a linked one exclude each other. Mutants: `--git-dir` for
        `--git-common-dir`; the root's own `.git`."""
        linked = Path(self._tmp.name) / "linked"
        gitutil.git(["worktree", "add", "-q", "-b", "linked-root", str(linked)], self.root)
        made = lanes._lane_worktree(linked.resolve(), "US0101")
        self.assertTrue(made.is_dir())
        self.assertTrue(self.lock.is_file(), "the lock is not in the main checkout's common dir")
        stray = [p for p in (self.root / ".git" / "worktrees").rglob(lanes.WORKTREE_LOCK)]
        self.assertEqual([], stray, "a lock was made in the linked worktree's own git dir")
        self.assertTrue((linked / ".git").is_file())
        # a lane started from the linked root waits on the lock another process holds there
        holder = subprocess.Popen(
            [sys.executable, "-c", HOLDER.format(hold=1.0), str(self.lock)],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.kill)
        self.assertEqual("held", holder.stdout.readline().strip())
        began = time.monotonic()
        lanes._lane_worktree(linked.resolve(), "US0102")
        self.assertGreaterEqual(time.monotonic() - began, 0.5)

    def test_a_lock_file_that_cannot_be_opened_refuses_the_add(self) -> None:
        self.lock.mkdir()
        with self.assertRaises(lanes.LandError) as caught:
            lanes._lane_worktree(self.root, "US0101")
        self.assertIn(f"the lane worktree lock {self.lock} cannot be opened", str(caught.exception))
        self.assertFalse((self.root / lanes.RUN_WORKTREES / "lane-us0101").exists())

    def test_where_flock_is_unavailable_the_add_goes_ahead_unlocked(self) -> None:
        """Windows has no `fcntl`: the lock is a no-op there and the worktree is still added."""
        with unittest.mock.patch.dict(sys.modules, {"fcntl": None}):
            made = lanes._lane_worktree(self.root, "US0101")
        self.assertTrue(made.is_dir())
        self.assertFalse(self.lock.exists(), "a lock file was made with no flock to take")

    def test_an_existing_worktree_is_reused_without_the_lock(self) -> None:
        made = lanes._lane_worktree(self.root, "US0101")
        with unittest.mock.patch.object(lanes, "_worktree_lock") as locked, \
                unittest.mock.patch.object(lanes, "_run_git") as ran:
            again = lanes._lane_worktree(self.root, "US0101")
        self.assertEqual(made, again)
        locked.assert_not_called()
        ran.assert_not_called()

    def test_a_root_that_is_no_repository_takes_no_lock_and_says_why(self) -> None:
        bare = Path(self._tmp.name) / "plain"
        bare.mkdir()
        with self.assertRaises(lanes.LandError) as caught:
            lanes._lane_worktree(bare, "US0101")
        self.assertIn("could not be created", str(caught.exception))
        self.assertEqual([], [p.name for p in bare.iterdir() if p.name == lanes.WORKTREE_LOCK])


if __name__ == "__main__":
    unittest.main()
