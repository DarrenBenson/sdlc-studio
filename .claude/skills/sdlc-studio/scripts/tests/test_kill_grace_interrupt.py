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
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_run as base  # noqa: E402 - the lane run fixture: repository and fake CLIs

lanes = base.lanes
SPRINT = base.SCRIPTS / "sprint.py"
#: a child that ignores SIGTERM, as a hung tool would, and says so once it does
DEAF = ("import signal, sys, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "open(sys.argv[1], 'w').write(str(__import__('os').getpid()))\n"
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


@unittest.skipUnless(hasattr(os, "killpg") and Path("/proc/self/stat").exists(),
                     "process groups and /proc are needed to see the child")
class KillGraceInterruptTests(base._LaneCase):

    def setUp(self) -> None:
        super().setUp()
        (self.bin / "codex").write_text(FAKE.format(python=sys.executable, deaf=DEAF),
                                        encoding="utf-8")

    def _child(self) -> int:
        pid = int((self.log / "child.pid").read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()
