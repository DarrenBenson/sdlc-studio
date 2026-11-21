"""BG1610: a commit stopped at lane land's bound leaves no hook, or child of one, running.

`sprint lane land` commits through the repository's hooks under `lanes.COMMIT_TIMEOUT`. On the
bound only git was killed, so the commit-msg hook it ran, and whatever that hook started, were
reparented and ran on, loading the host while the land said they were stopped. Each case runs
`sprint.py lane land` as its own process, `lanes.COMMIT_TIMEOUT` shrunk in it, on
`test_lane_land`'s throwaway repository with a commit-msg hook stub that starts a long-lived
child and waits on it, then checks after that process exits that neither is left running.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_land as base  # noqa: E402 - the lane fixture every landing case shares

A = base.A
#: the bound the land runs under, in seconds: well past git's own start, well short of the child
BOUND = 3
#: a commit-msg hook that records its pid, starts a child that would run 300 s, and waits on it
HOOK = """#!/bin/sh
echo $$ > "{dir}/hook.pid"
sleep 300 &
echo $! > "{dir}/child.pid"
wait
"""
#: `sprint.py` run as a command, with the commit's bound shrunk in its own process
LAND = ("import runpy, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from lib import lanes\n"
        f"lanes.COMMIT_TIMEOUT = {BOUND}\n"
        "sys.argv = [sys.argv[2], *sys.argv[3:]]\n"
        "runpy.run_path(sys.argv[0], run_name='__main__')\n")


def _running(pid: int) -> bool:
    """Whether `pid` is a live process, a zombie counting as dead."""
    stat = Path(f"/proc/{pid}/stat")
    if Path("/proc/self/stat").exists():
        try:
            return stat.read_text().rsplit(")", 1)[1].split()[0] != "Z"
        except OSError:
            return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def _sigkill(pid: int) -> None:
    with contextlib.suppress(OSError):
        os.kill(pid, signal.SIGKILL)


def _outlives(pid: int, seconds: float = 2.0) -> bool:
    """Whether `pid` still runs `seconds` from now: a killed process is reaped by whoever
    inherits it a moment after the kill, so the wait is polled."""
    deadline = time.monotonic() + seconds
    while _running(pid):
        if time.monotonic() > deadline:
            return True
        time.sleep(0.02)
    return False


class LandCommitTimeoutKillsHooksTests(base._LaneFixture):

    def setUp(self) -> None:
        super().setUp()
        self.dir = self.log.parent
        hook = self.dir / "hooks" / "commit-msg"
        hook.write_text(HOOK.format(dir=self.dir), encoding="utf-8")
        hook.chmod(0o755)

    def _pid(self, name: str) -> int:
        pid = int((self.dir / name).read_text(encoding="utf-8").strip())
        self.addCleanup(_sigkill, pid)  # a case that fails leaves nothing of the hook behind
        return pid

    def _land_bounded(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", "-c", LAND, str(base.SCRIPTS), str(base.SPRINT), "lane",
             "land", "--worktree", str(self.wt), "--units", A, "--root", str(self.root)],
            capture_output=True, text=True, timeout=120, cwd=str(self.root),
            env=self._env(), check=False)

    def test_the_bound_stops_the_hook_and_its_child_and_commits_nothing(self) -> None:
        """MUTANT: the commit run with `subprocess.run(..., timeout=...)` again, or `Popen`
        with no session of its own (only git is killed; the hook and its child run on)."""
        main_before = base._git(self.root, "rev-parse", "HEAD")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land_bounded()
        out = r.stdout + r.stderr
        self.assertEqual(1, r.returncode, out)
        self.assertIn(f"the commit's hooks ran past {BOUND}s and were stopped, so nothing was "
                      f"committed and main is as it was", out)
        # positive control: the hook ran, and started its child, before the bound fired
        hook, child = self._pid("hook.pid"), self._pid("child.pid")
        self.assertFalse(_outlives(hook), "the commit-msg hook outlived the land")
        self.assertFalse(_outlives(child), "the hook's child outlived the land")
        self.assertEqual(main_before, base._git(self.root, "rev-parse", "HEAD"))
        self.assertTrue(self.wt.is_dir(), "the worktree was removed after the bound fired")
        self.assertEqual("src/a.py", base._git(self.wt, "diff", "--cached", "--name-only"))
        gitdir = Path(base._git(self.wt, "rev-parse", "--absolute-git-dir"))
        self.assertFalse((gitdir / "index.lock").exists(), "the stopped commit left index.lock")

    def test_a_ctrl_c_during_the_commit_stops_its_group_and_propagates(self) -> None:
        """MUTANT: only a timeout ends the group (`except subprocess.TimeoutExpired` in
        `_bounded`), so a Ctrl-C leaves the child running, out of reach in its own session."""
        script = f'sleep 300 & echo $! > "{self.dir}/child.pid"; wait'
        timer = threading.Thread(target=self._interrupt_once_started, daemon=True)
        timer.start()
        with self.assertRaises(KeyboardInterrupt):
            base.lanes._bounded(["sh", "-c", script], 120, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        timer.join(10)
        self.assertFalse(_outlives(self._pid("child.pid")), "the child outlived the Ctrl-C")

    def _interrupt_once_started(self) -> None:
        """Press Ctrl-C (SIGINT to this process) once the command's child has started."""
        deadline = time.monotonic() + 30
        while not (self.dir / "child.pid").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        os.kill(os.getpid(), signal.SIGINT)

    def test_a_hook_that_ends_in_time_still_commits(self) -> None:
        """Positive control for the bound: a hook that returns well inside it lands the lane."""
        (self.dir / "hooks" / "commit-msg").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self._stage("src/a.py", "A = 2\n")
        self._hand_in()
        r = self._land_bounded()
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertEqual(f"feat({A}): a is two", base._git(self.root, "log", "-1", "--format=%s"))


if __name__ == "__main__":
    unittest.main()
