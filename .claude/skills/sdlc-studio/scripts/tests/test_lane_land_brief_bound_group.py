"""BG1627: lane land's bound on `critic.py brief` stops the replay it started, scratch copy and all.

The QA brief `sprint lane land` writes replays the author's recorded mutants through the mutation
runner, which runs each mutant's pytest selector in a scratch copy of the tree. Lane land bounds
the brief at `critic.BRIEF_TIMEOUT`; on that bound only critic.py was killed, so the runner and
its pytest child ran on and the scratch copy stayed. The case runs `sprint.py lane land` as its
own process, `critic.BRIEF_TIMEOUT` shrunk in it, on `test_lane_land`'s throwaway repository,
with a unit whose one recorded mutant runs a test that records its pid and sleeps, then checks
after that process exits that no runner or pytest child is left and no scratch copy remains.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import json
import os
import signal
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_land as base  # noqa: E402 - the lane fixture every landing case shares
import test_lane_land_commit_timeout_group as bound  # noqa: E402 - the process probes

A, LANE = base.A, base.LANE
#: the brief's bound in seconds: past the runner's start and its pytest child's, well short of
#: the 120 s that child sleeps
BOUND = 15
#: `sprint.py` run as a command, with the brief's bound shrunk in its own process
LAND = ("import runpy, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "import critic\n"
        f"critic.BRIEF_TIMEOUT = {BOUND}\n"
        "sys.argv = [sys.argv[2], *sys.argv[3:]]\n"
        "runpy.run_path(sys.argv[0], run_name='__main__')\n")
SLOW_TEST = """import os
import time
from pathlib import Path


def test_a():
    Path({pid!r}).write_text(str(os.getpid()), encoding="utf-8")
    time.sleep(120)
"""


def _runners(root: Path) -> list[int]:
    """The pids of mutation runners started over `root`, read from `/proc`; [] without it."""
    out = []
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            argv = (proc / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if any(a.endswith(b"mutation.py") for a in argv) and str(root).encode() in argv:
            if bound._running(int(proc.name)):
                out.append(int(proc.name))
    return out


class LandBriefBoundKillsReplayTests(base._LaneFixture):

    def setUp(self) -> None:
        super().setUp()
        self.dir = self.log.parent
        self.tmp = self.dir / "tmp"
        self.tmp.mkdir()
        self.pid = self.dir / "slow.pid"

    def _hand_in_a_slow_replay(self) -> None:
        """A's lane: its change, a test that sleeps, its fragment, and a self-check whose
        runner report keeps one mutant against that test, so the brief replays it."""
        self._stage("src/a.py", "A = 2\n")
        self._stage("tests/test_a.py", SLOW_TEST.format(pid=str(self.pid)))
        self._stage(f"changelog.d/{A}.md", "a is two\n")
        base._write(self.wt, f"{LANE}/commit-msg.txt", f"feat({A}): a is two\n")
        base._write(self.wt, f"{LANE}/{A}-claims.json", json.dumps(
            [{"surface": "commit message", "claim": "a is two", "ruling": "TRUE"},
             {"surface": f"changelog.d/{A}.md", "claim": "a is two", "ruling": "TRUE"}]))
        base._write(self.wt, f"{LANE}/{A}-mutation-edits.json", json.dumps(
            {"kind": "mutation-edits", "version": 1, "unit": A, "edits": "EDITS.json",
             "counts": {"killed": 1, "survived": 0, "not_applied": 0, "error": 0},
             "mutants": [{"mutant": "a is three", "file": "src/a.py", "old": "A = 2",
                          "new": "A = 3", "test": "tests/test_a.py::test_a", "result": "killed",
                          "answer": ""}]}))

    def _stray(self) -> list[int]:
        """Each runner or slow pytest still running, killed here so a failing case leaves none."""
        left = _runners(self.root)
        if self.pid.is_file():
            slow = int(self.pid.read_text(encoding="utf-8"))
            if bound._outlives(slow):
                left.append(slow)
        for pid in left:
            with contextlib.suppress(OSError):
                os.kill(pid, signal.SIGKILL)
        return left

    def test_the_bound_stops_the_runner_and_its_pytest_and_removes_the_scratch_copy(self):
        """MUTANTS: the brief run with `subprocess.run(..., timeout=...)` again (only critic.py
        is killed); its group sent SIGKILL with no SIGTERM first (the runner cannot remove its
        scratch copy or stop its pytest, which runs in a session of its own)."""
        self._hand_in_a_slow_replay()
        r = subprocess.run(
            [sys.executable, "-B", "-c", LAND, str(base.SCRIPTS), str(base.SPRINT), "lane",
             "land", "--worktree", str(self.wt), "--units", A, "--root", str(self.root)],
            capture_output=True, text=True, timeout=300, cwd=str(self.root),
            env=self._env() | {"TMPDIR": str(self.tmp)}, check=False)
        out = r.stdout + r.stderr
        self.addCleanup(self._stray)
        self.assertEqual(1, r.returncode, out)
        self.assertIn(f"{A}: self-check recorded; QA brief NOT WRITTEN - `critic.py brief` was "
                      f"stopped at {BOUND}s", out)
        # positive control: the replay reached the mutant's test before the bound fired
        self.assertTrue(self.pid.is_file(), "the replay never ran the mutant's test\n" + out)
        self.assertEqual([], self._stray(), "a runner or its pytest outlived the land")
        self.assertEqual([], sorted(p.name for p in self.tmp.glob("mutation_edits_*")),
                         "the replay's scratch copy was left behind")
        self.assertFalse((self.root / f"sdlc-studio/.local/briefs/{A}-qa.txt").exists())

    def test_the_brief_alone_is_given_critic_s_replay_stop_grace(self) -> None:
        """MUTANT: the brief's bound given no grace of its own (`grace = None`, so KILL_GRACE:
        two seconds, in which a runner stopping a real tree's pytest need not have removed its
        scratch copy). Every other `critic.py` call keeps lane land's own bound and grace."""
        seen = []

        def bounded(cmd, timeout, grace=None, **popen):
            seen.append((cmd[2], timeout, grace))
            return subprocess.CompletedProcess(cmd, 0, "", "")

        with unittest.mock.patch.object(base.lanes, "_bounded", bounded):
            base.lanes._critic(self.root, "brief", "--unit", A, "--seat", "qa")
            base.lanes._critic(self.root, "self-check", "record", "--unit", A)
        self.assertEqual([("brief", base.critic.BRIEF_TIMEOUT, base.critic.REPLAY_STOP_GRACE),
                          ("self-check", base.lanes.CRITIC_TIMEOUT, None)], seen)
        self.assertGreater(base.critic.REPLAY_STOP_GRACE, base.lanes.KILL_GRACE)

    def test_the_bound_gives_the_group_the_grace_it_was_handed(self) -> None:
        """MUTANT: `_bounded` ends its group at the bound with KILL_GRACE, not the grace it was
        handed (`_kill_group(proc)`). The command stops cleanly one second after its SIGTERM:
        handed eight, it is given the time to; KILL_GRACE, shrunk here to 0.3 s so the case is
        quick, would end it by SIGKILL first."""
        where = Path(self._tmp.name)
        ready, stopped = where / "ready", where / "stopped"
        stop = (f"trap 'sleep 1; : > {stopped}; exit 0' TERM; : > {ready}; "
                "while :; do sleep 0.05; done")
        with unittest.mock.patch.object(base.lanes, "KILL_GRACE", 0.3):
            with self.assertRaises(subprocess.TimeoutExpired):
                base.lanes._bounded(["sh", "-c", stop], 2, 8, stdout=subprocess.DEVNULL)
        self.assertTrue(ready.exists(), "the command never set its SIGTERM trap")
        self.assertTrue(stopped.exists(), "the command was killed inside the grace it was handed")


if __name__ == "__main__":
    unittest.main()
