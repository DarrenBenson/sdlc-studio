"""BG1190: a verifier that outlives its ceiling is killed with everything it spawned.

`subprocess.run(shell=True, timeout=...)` kills only the shell, so a shell verifier's children
ran on after its timeout verdict and loaded every verifier after it. Each fixture here is a
shell that records its process group and backgrounds a subshell whose own child sleeps, so a
leak shows as a live process in that group once `verify_ac.run_verifier` has returned.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_verify_timeout_reaps.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
from __future__ import annotations

import contextlib
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import verify_ac  # noqa: E402

_PROC = Path("/proc")
_SLEEP = 6     # how long the fixture's grandchild sleeps; outlives every ceiling below
_CEILING = 2   # the verifier's timeout, in seconds


def _spawning(d: Path) -> str:
    """A shell command that writes its process group to `d/pgid`, backgrounds a subshell whose
    child sleeps `_SLEEP` seconds, writes that subshell's pid to `d/child`, then waits on it."""
    q = shlex.quote(str(d))
    return (f"cut -d' ' -f5 /proc/$$/stat > {q}/pgid; "
            f"(sleep {_SLEEP}; echo late) & echo $! > {q}/child; wait")


def _stat(pid: int) -> list[str] | None:
    """The fields of `/proc/<pid>/stat` after the command name, or None once the pid is gone."""
    try:
        text = (_PROC / str(pid) / "stat").read_text()
    except OSError:
        return None
    return text.rsplit(")", 1)[1].split()


def _running(pid: int) -> bool:
    """True while `pid` exists and is neither a zombie nor dead."""
    fields = _stat(pid)
    return fields is not None and fields[0] not in ("Z", "X")


def _live_members(pgid: int) -> list[int]:
    """Every pid in process group `pgid` that is still running."""
    live = []
    for entry in _PROC.iterdir():
        if entry.name.isdigit():
            fields = _stat(int(entry.name))
            if fields and int(fields[2]) == pgid and fields[0] not in ("Z", "X"):
                live.append(int(entry.name))
    return live


@unittest.skipUnless((_PROC / "self" / "stat").is_file(), "reads process state from /proc")
class TimeoutReapsTheGroupTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.d = Path(tmp.name)
        self.addCleanup(self._sweep)

    def _sweep(self) -> None:
        """Kill whatever a red run left behind, never this test process's own group."""
        child, pgid = self._recorded(required=False)
        if pgid and pgid != os.getpgrp():
            with contextlib.suppress(OSError):
                os.killpg(pgid, signal.SIGKILL)
        if child:
            with contextlib.suppress(OSError):
                os.kill(child, signal.SIGKILL)

    def _recorded(self, required: bool = True) -> tuple[int | None, int | None]:
        """The (child pid, process group) the fixture shell wrote before it was killed."""
        try:
            child = int((self.d / "child").read_text().strip())
            pgid = int((self.d / "pgid").read_text().strip())
        except (OSError, ValueError):
            if required:
                self.fail("the fixture shell never recorded its child and group within the ceiling")
            return None, None
        return child, pgid

    def assertReaped(self) -> None:
        child, pgid = self._recorded()
        self.assertFalse(_running(child), f"the backgrounded child {child} outlived the verdict")
        self.assertEqual(_live_members(pgid), [], f"process group {pgid} still has live members")

    def test_a_timed_out_shell_verifier_leaves_no_live_process_in_its_group(self) -> None:
        """Mutant: `_run_in_group` back to `subprocess.run(cmd, shell=True, timeout=...)`, or a
        `proc.kill()` in place of `os.killpg`, or `start_new_session` dropped (the group is then
        this test's own, and live). Each leaves the sleeping subshell running and fails here."""
        res = verify_ac.run_verifier(f"shell {_spawning(self.d)}", timeout=_CEILING, cwd=self.d)
        self.assertEqual((res.ok, res.kind, res.exit_code, res.stderr), (False, "shell", 124, "timeout"))
        self.assertReaped()

    def test_a_timed_out_eval_verifier_leaves_no_live_process_in_its_group(self) -> None:
        """Mutant: `_run_eval` back to its own `subprocess.run(command, shell=True, timeout=...)`.
        The eval verb shells out too, so its children leak the same way and fail here."""
        res = verify_ac.run_verifier(f"eval {_spawning(self.d)} --threshold 0.5",
                                     timeout=_CEILING, cwd=self.d)
        self.assertEqual((res.ok, res.kind, res.exit_code, res.stderr), (False, "eval", 124, "timeout"))
        self.assertReaped()

    def test_an_interrupted_wait_still_kills_the_group(self) -> None:
        """A Ctrl-C no longer reaches a verifier in its own session, so the interrupt must kill
        its group. Mutant: `_run_in_group` catching `subprocess.TimeoutExpired` alone; the
        KeyboardInterrupt then leaves the shell and its subshell running and fails here."""
        real_popen = subprocess.Popen

        class _Interrupted(real_popen):  # type: ignore[misc, valid-type]
            def communicate(self, *args, **kwargs):
                with contextlib.suppress(subprocess.TimeoutExpired):
                    super().communicate(timeout=_CEILING)
                raise KeyboardInterrupt

        with unittest.mock.patch.object(verify_ac.subprocess, "Popen", _Interrupted), \
                self.assertRaises(KeyboardInterrupt):
            verify_ac.run_verifier(f"shell {_spawning(self.d)}", timeout=60, cwd=self.d)
        self.assertReaped()

    def test_the_kill_waits_until_the_group_is_gone(self) -> None:
        """A killed member can outlast `proc.wait()` until init reaps it, so the kill probes the
        group until it is gone. Mutant: the probe loop removed (no probe), or returning after the
        first probe answers (one probe); either fails the count of three."""
        real_killpg, probes = os.killpg, []

        def fake_killpg(pgid: int, sig: int) -> None:
            if sig != 0:
                return real_killpg(pgid, sig)
            probes.append(pgid)
            if len(probes) < 3:
                return None
            raise ProcessLookupError(pgid)

        with unittest.mock.patch.object(verify_ac.os, "killpg", fake_killpg):
            res = verify_ac.run_verifier(f"shell {_spawning(self.d)}", timeout=_CEILING, cwd=self.d)
        self.assertEqual(res.exit_code, 124)
        _, pgid = self._recorded()
        self.assertEqual(probes, [pgid] * 3)
        self.assertReaped()

    def test_without_killpg_the_timeout_still_reads_red(self) -> None:
        """Where `os.killpg` does not exist the verifier alone is killed. Mutant: the
        `hasattr(os, "killpg")` branch removed; the AttributeError then escapes as a crash
        instead of a timeout verdict."""
        with unittest.mock.patch.dict(verify_ac.os.__dict__):
            del verify_ac.os.__dict__["killpg"]
            started = time.monotonic()
            res = verify_ac.run_verifier(f"shell exec sleep {_SLEEP}", timeout=1, cwd=self.d)
        self.assertEqual((res.ok, res.exit_code, res.stderr), (False, 124, "timeout"))
        self.assertLess(time.monotonic() - started, _SLEEP)

    def test_a_verifier_inside_its_ceiling_returns_its_own_output(self) -> None:
        """The control: the in-time path through the same helper. Mutant: `_run_in_group`
        returning empty streams, or a fixed return code; either fails the exact result here."""
        res = verify_ac.run_verifier("shell echo out; echo err >&2; exit 3", timeout=_CEILING, cwd=self.d)
        self.assertEqual((res.ok, res.kind, res.exit_code, res.stdout, res.stderr),
                         (False, "shell", 3, "out\n", "err\n"))
        green = verify_ac.run_verifier("shell echo fine", timeout=_CEILING, cwd=self.d)
        self.assertEqual((green.ok, green.exit_code, green.stdout), (True, 0, "fine\n"))


if __name__ == "__main__":
    unittest.main()
