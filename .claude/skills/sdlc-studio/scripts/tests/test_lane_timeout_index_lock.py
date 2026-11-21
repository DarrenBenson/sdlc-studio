"""BG1624: a timed-out lane run leaves no `index.lock` from a `git add` it killed.

`sprint lane run` ends a timed-out lane's process group with SIGTERM, so a `git add` in it
removes the `index.lock` it holds, then SIGKILL after `lanes.KILL_GRACE`. On a loaded host a
`git add` can still be running when the grace ends, and the SIGKILL left its lock, which the
commit `lane land` needs refuses. A lane run that had to send SIGKILL now removes a lock that
appeared in the lane's worktree while it ran, and leaves one that was there before it started.

Every case drives `sprint.py lane run` through `sprint.main` on `test_lane_run`'s throwaway
repository and confined fake CLIs, with a fake `codex` of this module's own.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import os
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_run as base  # noqa: E402 - the lane run fixture: repository and fake CLIs

lanes = base.lanes
#: How many timed-out runs the loop case makes, each in a fresh worktree: a SIGKILL that lands
#: while a `git add` holds its lock is likely on any one run and all but certain over these.
RUNS = 4
#: the fake CLI, in the mode `LOCK_FAKE` names:
#:   loop - stage a file that grows by 256 KiB a round until stopped, so most of the time a
#:          `git add` is hashing it with `index.lock` held;
#:   lock - start a child that ignores SIGTERM and takes the worktree's `index.lock`, as a
#:          `git add` the grace cannot stop would;
#:   deaf - the same child, taking no lock;
#:   leave - take the worktree's `index.lock` itself, as a git of its own that crashed would
#:           leave it, then wait to be stopped, ending on the SIGTERM, so no SIGKILL is sent;
#:   exit - start the lock-taking child of `lock`, then exit 0 without waiting on it, so the
#:          lane ends on its own and its group, still holding the child, is sent SIGKILL;
#:   exit-deaf - the same, with the child of `deaf`, which takes no lock;
#:   drop - take the worktree's `index.lock` itself and exit 0 at once, so the lane ends on
#:          its own with nothing left in its group, and no SIGKILL is sent.
FAKE = r'''#!{python}
import os, signal, subprocess, sys, time
mode = os.environ["LOCK_FAKE"]
if mode in ("leave", "drop"):
    lock = subprocess.run(["git", "rev-parse", "--git-path", "index.lock"], capture_output=True,
                          text=True, check=True).stdout.strip()
    open(lock, "x").close()
    if mode == "drop":
        sys.exit(0)
    time.sleep(60)
if mode == "loop":
    grow = os.path.join("src", "grow.txt")
    while True:
        with open(grow, "a") as fh:
            fh.write("x" * 262144)
        subprocess.run(["git", "add", "--", grow], check=False)
lock = subprocess.run(["git", "rev-parse", "--git-path", "index.lock"], capture_output=True,
                      text=True, check=True).stdout.strip()
ready = os.path.join(os.environ["FAKE_LOG"], "ready")
child = subprocess.Popen([sys.executable, "-c",
    "import signal, sys, time\n"
    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
    "if sys.argv[1] in ('lock', 'exit'):\n"
    "    open(sys.argv[2], 'x').close()\n"
    "open(sys.argv[3], 'w').close()\n"
    "time.sleep(60)\n", mode, lock, ready],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
while not os.path.exists(ready):
    time.sleep(0.01)
if mode in ("exit", "exit-deaf"):
    sys.exit(0)
child.wait()
'''


class TimedOutGitAddLeavesNoLockTests(base._LaneCase):

    def setUp(self) -> None:
        super().setUp()
        (self.bin / "codex").write_text(FAKE.format(python=sys.executable), encoding="utf-8")

    def _lock(self, wt: Path) -> Path:
        return Path(base._git(wt, "rev-parse", "--absolute-git-dir")) / "index.lock"

    def _timed_out(self, wt: Path, mode: str, timeout: str = "1") -> str:
        with unittest.mock.patch.dict(os.environ, {"LOCK_FAKE": mode}):
            rc, out = self._run("codex", "--worktree", str(wt), "--timeout", timeout)
        self.assertEqual(1, rc, out)
        self.assertEqual(lanes.TIMED_OUT, self._record()["unmetered"], out)
        return out

    def test_repeated_timed_out_git_add_loops_leave_no_index_lock(self) -> None:
        """MUTANT: SIGKILL first, with no SIGTERM (a `git add` killed holding its lock leaves
        it; nothing escalated, so nothing removes it). Positive control: each loop staged."""
        for n in range(RUNS):
            with self.subTest(run=n):
                wt = self._worktree(f"wt-lock-{n}")
                self._timed_out(wt, "loop")
                self.assertIn("src/grow.txt", self._record()["staged"])
                self.assertFalse(self._lock(wt).exists(), "a killed git add left index.lock")
                done = gitutil.git(["commit", "-q", "-m", "chore: the lane's work"], wt,
                                   check=False)
                self.assertEqual(0, done.returncode, done.stderr)

    def test_a_lock_held_past_the_grace_is_removed_and_named(self) -> None:
        """MUTANT: no lock removed after the SIGKILL (the lock the killed child held stays)."""
        wt = self._worktree()
        out = self._timed_out(wt, "lock", timeout="2")
        self.assertTrue((self.log / "ready").exists(), "the lock-holding child never started")
        self.assertFalse(self._lock(wt).exists(), "the killed child's index.lock was left")
        self.assertIn(f"removed {self._lock(wt)}", out)
        self.assertEqual(0, gitutil.git(["add", "--", "src/a.py"], wt, check=False).returncode)

    def test_a_lane_that_exits_on_its_own_has_its_killed_child_s_lock_removed(self) -> None:
        """MUTANT: the lock cleared only on a timeout (a bare `_kill_group(proc)` once the CLI
        has exited on its own). The CLI exits 0 well inside its bound, leaving a child that
        ignores SIGTERM holding the worktree's `index.lock`, so the group is sent SIGKILL
        after the CLI's own exit, not at a timeout."""
        wt = self._worktree()
        with unittest.mock.patch.dict(os.environ, {"LOCK_FAKE": "exit"}):
            rc, out = self._run("codex", "--worktree", str(wt), "--timeout", "60")
        self.assertTrue((self.log / "ready").exists(), "the lock-holding child never started")
        self.assertNotEqual(lanes.TIMED_OUT, self._record().get("unmetered"), out)
        self.assertFalse(self._lock(wt).exists(), "the killed child's index.lock was left")
        self.assertIn(f"removed {self._lock(wt)}", out)
        self.assertEqual(0, gitutil.git(["add", "--", "src/a.py"], wt, check=False).returncode)

    def test_a_lock_there_before_the_run_is_left_in_place(self) -> None:
        """MUTANT: any lock found after the SIGKILL removed (one the lane never took goes)."""
        wt = self._worktree()
        lock = self._lock(wt)
        lock.write_text("", encoding="utf-8")
        before = lock.stat()
        out = self._timed_out(wt, "deaf", timeout="2")
        self.assertTrue((self.log / "ready").exists(), "the deaf child never started")
        self.assertTrue(lock.exists(), "a lock taken before the lane ran was removed")
        self.assertEqual((before.st_ino, before.st_mtime_ns),
                         (lock.stat().st_ino, lock.stat().st_mtime_ns))
        self.assertNotIn("removed", out)

    def _exits_on_its_own(self, wt: Path, mode: str) -> str:
        with unittest.mock.patch.dict(os.environ, {"LOCK_FAKE": mode}):
            rc, out = self._run("codex", "--worktree", str(wt), "--timeout", "60")
        self.assertNotEqual(lanes.TIMED_OUT, self._record().get("unmetered"), out)
        return out

    def test_a_lock_there_before_a_lane_that_exits_on_its_own_is_left_in_place(self) -> None:
        """MUTANT: the exit path's clearing told no lock was there before the run (`before`
        dropped to None there, so a lock the lane never took goes). The CLI exits leaving a
        child that ignores SIGTERM and takes no lock, so its group is sent SIGKILL."""
        wt = self._worktree()
        lock = self._lock(wt)
        lock.write_text("", encoding="utf-8")
        before = lock.stat()
        out = self._exits_on_its_own(wt, "exit-deaf")
        self.assertTrue((self.log / "ready").exists(), "the deaf child never started")
        self.assertTrue(lock.exists(), "a lock taken before the lane ran was removed")
        self.assertEqual((before.st_ino, before.st_mtime_ns),
                         (lock.stat().st_ino, lock.stat().st_mtime_ns))
        self.assertNotIn("removed", out)

    def test_a_lock_left_by_a_lane_that_exits_with_its_group_empty_is_left(self) -> None:
        """MUTANT: the exit path clearing the lock whether or not SIGKILL was sent. The CLI
        takes the lock and exits with nothing left in its group, so no SIGKILL is sent and the
        lock it left is not one a SIGKILL left."""
        wt = self._worktree()
        out = self._exits_on_its_own(wt, "drop")
        self.assertTrue(self._lock(wt).exists(), "a lock no SIGKILL left was removed")
        self.assertNotIn("removed", out)

    def test_a_lock_left_by_a_lane_that_ends_on_sigterm_is_left_in_place(self) -> None:
        """MUTANT: the lock removed whether or not SIGKILL was sent (`_kill_group` reporting a
        SIGKILL always): a lane whose group empties on the SIGTERM is sent none, so a lock it
        leaves is not one a SIGKILL left."""
        wt = self._worktree()
        out = self._timed_out(wt, "leave")
        self.assertTrue(self._lock(wt).exists(), "a lock no SIGKILL left was removed")
        self.assertNotIn("removed", out)


if __name__ == "__main__":
    unittest.main()
