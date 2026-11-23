"""BG1413: a Ctrl-C during the kill grace of a timed-out lane still SIGKILLs what is left of it.

At a lane's timeout `sprint lane run` sends its process group SIGTERM, waits up to
`lanes.KILL_GRACE` for the group to empty, then sends SIGKILL. A KeyboardInterrupt raised in
that wait skipped the SIGKILL, so a child that ignores SIGTERM ran on after the command exited.
One case drives `sprint.py lane run` as its own process on `test_lane_run`'s throwaway
repository and confined fake CLIs and presses Ctrl-C (SIGINT) inside the grace; the other calls
`_kill_group` itself with the grace's wait interrupted.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_run as base  # noqa: E402 - the lane run fixture: repository and fake CLIs

lanes = base.lanes
SPRINT = base.SCRIPTS / "sprint.py"
#: a child that ignores SIGTERM, as a hung tool would, and says so once it does: its pid is
#: written under a temporary name and renamed into place, so child.pid is never seen empty
DEAF = ("import os, signal, sys, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "with open(sys.argv[1] + '.tmp', 'w') as fh:\n"
        "    fh.write(str(os.getpid()))\n"
        "os.replace(sys.argv[1] + '.tmp', sys.argv[1])\n"
        "time.sleep(60)\n")
#: the fake CLI: it records its pid, starts the deaf child, and on SIGTERM marks it and exits
FAKE = r'''#!{python}
import json, os, signal, subprocess, sys, time
log = os.environ["FAKE_LOG"]
with open(os.path.join(log, "codex.json"), "w") as fh:
    json.dump({{"pid": os.getpid()}}, fh)
def term(*_):
    open(os.path.join(log, "term"), "w").close()
    os._exit(0)
signal.signal(signal.SIGTERM, term)
child = subprocess.Popen([sys.executable, "-c", {deaf!r}, os.path.join(log, "child.pid")])
child.wait()
'''


def _wait_for(check, seconds: float, what: str) -> None:
    deadline = time.monotonic() + seconds
    while not check():
        if time.monotonic() > deadline:
            raise AssertionError(f"timed out waiting for {what}")
        time.sleep(0.01)


def _read_pid(path: Path) -> int | None:
    """The pid `path` holds, or None while it is missing or holds no integer yet."""
    try:
        return int(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@unittest.skipUnless(hasattr(os, "killpg") and Path("/proc/self/stat").exists(),
                     "process groups and /proc are needed to see the child")
class KillGraceInterruptTests(base._LaneCase):

    def setUp(self) -> None:
        super().setUp()
        (self.bin / "codex").write_text(FAKE.format(python=sys.executable, deaf=DEAF),
                                        encoding="utf-8")

    def _child(self, seconds: float = 30) -> int:
        """The deaf child's pid, waited for under `seconds` until child.pid holds one: read
        sooner, the file can be missing, or empty if its writer creates it before writing."""
        path = self.log / "child.pid"
        _wait_for(lambda: _read_pid(path) is not None, seconds, "a pid in child.pid")
        pid = _read_pid(path)
        self.addCleanup(base._sigkill, pid)  # a case that fails leaves no child behind
        return pid

    def test_a_ctrl_c_in_the_grace_still_sigkills_a_child_ignoring_sigterm(self) -> None:
        """MUTANT: the SIGKILL sent only after the grace's wait, outside a `finally` (the
        KeyboardInterrupt from the wait skips it and the deaf child runs on)."""
        wt = self._worktree()
        lane = subprocess.Popen(
            [sys.executable, "-B", str(SPRINT), "lane", "run", "--harness", "codex", "--units",
             base.UNIT, "--worktree", str(wt), "--timeout", "3", "--root", str(self.root)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.addCleanup(lambda: lane.poll() is None and lane.kill())
        _wait_for(lambda: (self.log / "term").exists(), 60, "the lane's timeout SIGTERM")
        child = self._child()
        cli = json.loads((self.log / "codex.json").read_text(encoding="utf-8"))["pid"]
        # the CLI is reaped inside the grace, so the group lives on only in the deaf child,
        # out of reach of the handler that kills it while the CLI runs
        _wait_for(lambda: not Path(f"/proc/{cli}").exists(), lanes.KILL_GRACE, "the CLI's reap")
        self.assertTrue(base._running(child), "the deaf child died before the Ctrl-C")
        lane.send_signal(signal.SIGINT)
        out, _ = lane.communicate(timeout=60)
        self.assertIn("KeyboardInterrupt", out, "the Ctrl-C was not what ended the lane run")
        self.assertFalse(base._outlives(child), "the child ignoring SIGTERM outlived the lane run")

    def test_an_interrupted_grace_sigkills_the_group_and_propagates(self) -> None:
        """MUTANT: as above, `_kill_group` called directly with its wait interrupted; also the
        interruption swallowed (no KeyboardInterrupt reaches the caller)."""
        leader = subprocess.Popen(
            [sys.executable, "-c",
             "import subprocess, sys, time\n"
             f"subprocess.Popen([sys.executable, '-c', {DEAF!r}, sys.argv[1]])\n"
             "time.sleep(60)\n", str(self.log / "child.pid")], start_new_session=True)
        self.addCleanup(lambda: leader.poll() is None and leader.kill())
        _wait_for(lambda: (self.log / "child.pid").exists(), 30, "the deaf child")
        child = self._child()
        with unittest.mock.patch.object(lanes.time, "sleep", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                lanes._kill_group(leader, grace=30)
        self.assertFalse(base._outlives(child), "the child ignoring SIGTERM outlived the kill")
        self.assertIsNotNone(leader.returncode, "the group's leader was not reaped")

    def _throwaway(self) -> subprocess.Popen:
        """A process whose pid a pid file can hold: killed and reaped at cleanup."""
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        self.addCleanup(proc.wait)
        self.addCleanup(proc.kill)
        return proc

    def test_child_waits_for_a_child_pid_its_writer_has_not_filled(self) -> None:
        """MUTANT: `_child` reads child.pid the moment it is called. A writer caught between
        creating the file and writing to it leaves it empty (ValueError); one not yet started
        leaves it missing (OSError). Here the pid lands 0.3 s after the read begins."""
        path = self.log / "child.pid"
        for created in (True, False):
            with self.subTest(created=created):
                path.unlink(missing_ok=True)
                if created:
                    path.write_text("", encoding="utf-8")
                proc = self._throwaway()
                timer = threading.Timer(0.3, path.write_text, (str(proc.pid),),
                                        {"encoding": "utf-8"})
                timer.start()
                self.addCleanup(timer.cancel)
                self.assertEqual(proc.pid, self._child())

    def test_child_gives_up_at_its_bound(self) -> None:
        """MUTANT: `_child` ignores the bound it is handed, or reads without waiting (ValueError,
        not the timeout): a child.pid that never fills fails the case by name, inside the bound."""
        (self.log / "child.pid").write_text("", encoding="utf-8")
        started = time.monotonic()
        with self.assertRaisesRegex(AssertionError, "timed out waiting for a pid in child.pid"):
            self._child(0.2)
        self.assertLess(time.monotonic() - started, 10, "the wait ignored its bound")

    def test_the_deaf_child_moves_its_pid_into_place(self) -> None:
        """MUTANT: the deaf child writes child.pid in place, `open(path, 'w')` creating it empty
        before the write. A child.pid already there read-only cannot be opened for writing,
        though a rename over it lands, and no temporary name is left behind."""
        if os.geteuid() == 0:
            self.skipTest("root writes a read-only file in place")
        work = self.log / "atomic"
        work.mkdir()
        path = work / "child.pid"
        path.write_text("old", encoding="utf-8")
        path.chmod(0o444)
        deaf = subprocess.Popen([sys.executable, "-c", DEAF, str(path)],
                                stderr=subprocess.DEVNULL)
        self.addCleanup(deaf.wait)
        self.addCleanup(deaf.kill)
        _wait_for(lambda: _read_pid(path) is not None or deaf.poll() is not None, 30,
                  "the deaf child's pid or its exit")
        self.assertEqual(deaf.pid, _read_pid(path))
        self.assertEqual(["child.pid"], [p.name for p in work.iterdir()])


if __name__ == "__main__":
    unittest.main()
