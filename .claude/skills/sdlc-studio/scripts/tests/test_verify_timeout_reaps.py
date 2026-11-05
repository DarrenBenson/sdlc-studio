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

import pytest
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


def _recorded_in(d: Path) -> tuple[int, int] | None:
    """The (child pid, process group) a `_spawning(d)` shell wrote, or None until both read."""
    try:
        return int((d / "child").read_text().strip()), int((d / "pgid").read_text().strip())
    except (OSError, ValueError):
        return None


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

    @pytest.mark.serial_only
    @pytest.mark.boundary_only
    def test_the_group_is_killed_outright_and_the_verdict_follows_at_once(self) -> None:
        """A verifier that ignores SIGTERM still dies at its ceiling, and the verdict does not
        wait out the 2 s grace. Mutants: SIGTERM sent in place of SIGKILL (the shell and its
        sleep ignore it, so the verdict waits for the sleep), or the reap `proc.wait()` removed
        (the zombie leader keeps the group probe answering until the grace runs out); either
        fails the bound."""
        started = time.monotonic()
        res = verify_ac.run_verifier("shell trap '' TERM; sleep 4; echo late", timeout=1, cwd=self.d)
        elapsed = time.monotonic() - started
        self.assertEqual((res.ok, res.exit_code, res.stderr), (False, 124, "timeout"))
        self.assertLess(elapsed, 2.5)

    @pytest.mark.serial_only
    @pytest.mark.boundary_only
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
        returning empty streams, or a fixed return code; either fails the exact result here.
        Mutant: `_LIVE_GROUPS.discard` removed; the finished verifier's pid then stays where a
        signal handler would kill whatever group reuses it, and fails the empty registry."""
        res = verify_ac.run_verifier("shell echo out; echo err >&2; exit 3", timeout=_CEILING, cwd=self.d)
        self.assertEqual((res.ok, res.kind, res.exit_code, res.stdout, res.stderr),
                         (False, "shell", 3, "out\n", "err\n"))
        green = verify_ac.run_verifier("shell echo fine", timeout=_CEILING, cwd=self.d)
        self.assertEqual((green.ok, green.exit_code, green.stdout), (True, 0, "fine\n"))
        self.assertEqual(verify_ac._LIVE_GROUPS, set())


# A caller of `run_verifier`: one command runs on the main thread, several run on a thread pool
# that an interrupt cancels and re-raises from, as `gate.py`'s verify pool does.
_DRIVER = """
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import verify_ac
ceiling, commands = int(sys.argv[2]), sys.argv[3:]
if len(commands) == 1:
    verify_ac.run_verifier(commands[0], timeout=ceiling, cwd=Path.cwd())
else:
    pool = ThreadPoolExecutor(max_workers=len(commands))
    try:
        for command in commands:
            pool.submit(verify_ac.run_verifier, command, ceiling, Path.cwd())
        pool.shutdown(wait=True)
    except BaseException:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
"""
_CALLER_CEILING = 30  # far beyond the fixture's sleep, so only the signal can end the verifier
_PROMPT = 3           # seconds the caller and its verifiers get to be gone after the signal


@unittest.skipUnless((_PROC / "self" / "stat").is_file(), "reads process state from /proc")
class SignalToTheCallerReapsTests(unittest.TestCase):
    """A verifier leads its own session, outside its caller's process group, so a signal sent to
    that group (`remote-gate.sh` cancelling with `kill -TERM -- -<pgid>`, a Ctrl-C at the
    terminal) does not reach it. Each test runs a caller in a session of its own, signals the
    caller's group the way those do, and requires every verifier group gone promptly after."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.d = Path(tmp.name)
        self.dirs: list[Path] = []
        self.addCleanup(self._sweep)

    def _sweep(self) -> None:
        """Kill whatever a red run left behind, never this test process's own group."""
        for d in self.dirs:
            rec = _recorded_in(d)
            if rec and rec[1] != os.getpgrp():
                with contextlib.suppress(OSError):
                    os.killpg(rec[1], signal.SIGKILL)

    def _caller(self, n: int) -> subprocess.Popen:
        """Start a caller running `n` spawning verifiers, and return once each has recorded."""
        self.dirs = [self.d / str(i) for i in range(n)]
        for d in self.dirs:
            d.mkdir()
        caller = subprocess.Popen(
            [sys.executable, "-c", _DRIVER, str(SCRIPTS), str(_CALLER_CEILING),
             *(f"shell {_spawning(d)}" for d in self.dirs)],
            cwd=self.d, start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self._end, caller)
        deadline = time.monotonic() + 20
        while not all(_recorded_in(d) for d in self.dirs):
            if caller.poll() is not None or time.monotonic() > deadline:
                self.fail("the caller's verifiers never recorded their groups")
            time.sleep(0.05)
        return caller

    @staticmethod
    def _end(caller: subprocess.Popen) -> None:
        if caller.poll() is None:
            with contextlib.suppress(OSError):
                os.killpg(caller.pid, signal.SIGKILL)
            caller.wait()

    def assertCallerAndGroupsGone(self, caller: subprocess.Popen, sig: int) -> None:
        try:
            caller.wait(timeout=_PROMPT)
        except subprocess.TimeoutExpired:
            self.fail(f"the caller was still running {_PROMPT} s after its group was sent {sig!r}")
        self.assertEqual(caller.returncode, -sig, "the caller did not die by the signal it was sent")
        groups = [rec[1] for rec in map(_recorded_in, self.dirs) if rec]
        deadline = time.monotonic() + _PROMPT
        while any(_live_members(g) for g in groups) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertEqual({g: _live_members(g) for g in groups}, {g: [] for g in groups},
                         "a verifier group outlived its caller")

    def test_sigterm_to_the_callers_group_kills_its_verifier(self) -> None:
        """Mutants: the handler not installed for SIGTERM, `_LIVE_GROUPS.add` removed, or the
        handler's `os.killpg` removed (the verifier then outlives its caller); or the handler
        not re-raising the signal (the caller then exits 0, not by SIGTERM)."""
        caller = self._caller(1)
        os.killpg(caller.pid, signal.SIGTERM)
        self.assertCallerAndGroupsGone(caller, signal.SIGTERM)

    def test_sigint_to_the_callers_group_kills_its_worker_threads_verifiers(self) -> None:
        """Ctrl-C reaches the main thread only; the verifiers run on two pool threads. Mutants:
        the handler not installed for SIGINT (the caller waits for the verifiers to finish), or
        the prior handler not called (no `KeyboardInterrupt`, so the caller exits 0)."""
        caller = self._caller(2)
        os.killpg(caller.pid, signal.SIGINT)
        self.assertCallerAndGroupsGone(caller, signal.SIGINT)

    def test_an_ignored_signal_is_left_ignored(self) -> None:
        """A caller started under `nohup`, or in the background of a script, ignores SIGHUP or
        SIGINT, and importing `verify_ac` must not make that signal fatal. Mutant: the reaper
        installed over `SIG_IGN` too (the import then replaces it, and fails here); the
        SIGTERM half is the control that the reaper is installed at all."""
        probe = ("import signal, sys; signal.signal(signal.SIGHUP, signal.SIG_IGN); "
                 "sys.path.insert(0, sys.argv[1]); import verify_ac; "
                 "print(signal.getsignal(signal.SIGHUP) == signal.SIG_IGN, "
                 "signal.getsignal(signal.SIGTERM) == verify_ac._reap_on_signal)")
        out = subprocess.run([sys.executable, "-c", probe, str(SCRIPTS)], capture_output=True,
                             text=True, timeout=60, check=True).stdout
        self.assertEqual(out.split(), ["True", "True"])


if __name__ == "__main__":
    unittest.main()
