"""BG0781: a busy lock reported as EACCES is waited on, and the lock's warnings advise no retry.

BG0780 waited only on `BlockingIOError`, so a filesystem that reports a busy flock as EACCES
(SMB without unix extensions) failed at once as Permission denied. `flock(2)` needs only an open
descriptor, so a real permission error surfaces at `open()`, before the wait: EACCES from flock
itself can only be the busy signal. Two warnings raised after a write that DID land appended the
timeout's remedy ("nothing was written; retry"), and a retry mints a duplicate. A non-busy flock
error escaped `sprint.main` as a traceback.

Every workspace is a temporary directory that removes itself; the lock's wait is cut in-process.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import contextlib
import errno
import io
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import file_finding  # noqa: E402
import sprint  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

try:
    import fcntl
    HAS_FLOCK = True
except ImportError:  # pragma: no cover - the non-POSIX branch is a documented no-op
    HAS_FLOCK = False

REAL_LOCK = sdlc_md.allocation_lock


def _timed_out(*_args, **_kwargs):
    """Raise the timeout the real lock raises when another writer holds it past the wait."""
    def busy(fd, op):
        if op & fcntl.LOCK_NB:
            raise BlockingIOError(errno.EWOULDBLOCK, "busy")

    with tempfile.TemporaryDirectory(prefix="bg0781-held-") as held, \
            mock.patch.object(fcntl, "flock", busy):
        with REAL_LOCK(held, timeout=0):
            raise AssertionError("premise: a busy lock was taken")


def _run(fn, *args) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn(*args)
    return rc, out.getvalue(), err.getvalue()


@unittest.skipUnless(HAS_FLOCK, "flock is POSIX-only; elsewhere the lock is a documented no-op")
class LockBusyEaccesTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="bg0781-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _flaky(self, error: OSError, times: int):
        """A flock that raises `error` on the first `times` non-blocking attempts, then takes it."""
        calls = []
        real = fcntl.flock

        def flock(fd, op):
            if op & fcntl.LOCK_NB:
                calls.append(op)
                if len(calls) <= times:
                    raise error
            return real(fd, op)
        return flock, calls

    def test_a_busy_lock_reported_as_eacces_is_waited_on(self) -> None:
        """AC1. MUTANT: wait only on `BlockingIOError`, so EACCES fails at once as Permission
        denied. Controls: `BlockingIOError` is still waited on, ENOLCK still fails at once, and
        a lock file the writer cannot open is a PermissionError raised before any wait."""
        for name, error in (("EACCES", OSError(errno.EACCES, "Permission denied")),
                            ("BlockingIOError", BlockingIOError(errno.EWOULDBLOCK, "busy"))):
            with self.subTest(busy=name):
                flock, calls = self._flaky(error, 3)
                ran = []
                with mock.patch.object(fcntl, "flock", flock):
                    with REAL_LOCK(self.root, timeout=5.0):
                        ran.append(True)
                self.assertEqual(ran, [True], f"a busy lock reported as {name} was not taken")
                self.assertEqual(len(calls), 4, "the writer did not wait out the busy attempts")

        with self.subTest(control="ENOLCK fails at once"):
            flock, calls = self._flaky(OSError(errno.ENOLCK, "No locks available"), 3)
            started = time.monotonic()
            with mock.patch.object(fcntl, "flock", flock), self.assertRaises(OSError) as caught:
                with REAL_LOCK(self.root, timeout=5.0):
                    self.fail("the writer's block ran without the lock")
            self.assertEqual(caught.exception.errno, errno.ENOLCK)
            self.assertEqual(len(calls), 1, "a lock that can never be had was retried")
            self.assertLess(time.monotonic() - started, 1.0)

        if hasattr(os, "geteuid") and os.geteuid() == 0:
            return  # root opens any file, so the unwritable control cannot be set up
        with self.subTest(control="an unwritable lock file surfaces at once"):
            lock_file = self.root / "sdlc-studio" / ".local" / "allocation.lock"
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            lock_file.touch()
            lock_file.chmod(0o444)
            self.addCleanup(lock_file.chmod, 0o644)
            started = time.monotonic()
            with self.assertRaises(PermissionError):
                with REAL_LOCK(self.root, timeout=5.0):
                    self.fail("the writer's block ran without the lock")
            self.assertLess(time.monotonic() - started, 1.0, "a permission error was waited on")

    def _assert_no_retry(self, line: str) -> None:
        self.assertNotIn("retry", line.lower(), f"the message advises a retry: {line!r}")
        self.assertNotIn("nothing was written", line, f"the write DID land: {line!r}")
        self.assertIn("another writer still holds it", line, "the cause must still be named")

    def test_the_lock_warnings_do_not_advise_a_retry(self) -> None:
        """AC2. MUTANT: append the timeout's generic remedy ('so nothing was written; retry once
        it finishes') to a warning raised after the write landed, where a retry duplicates."""
        with self.subTest(writer="file_finding attribution"):
            run_state.open_run(self.root, goal="a goal", batch=["US0001"])
            run_state.start_batch(self.root, ["US0001"])
            with mock.patch.object(run_state, "note_finding", side_effect=_timed_out):
                rc, _out, err = _run(file_finding.main, [
                    "file", "--type", "bug", "--title", "a defect", "--severity", "High",
                    "--summary", "s", "--steps", "x", "--fix", "y", "--affects", "src/x.py",
                    "--points", "3", "--root", str(self.root)])
            self.assertEqual(rc, 0, err)
            self.assertEqual(len(list((self.root / "sdlc-studio" / "bugs").glob("BG*.md"))), 1,
                             "premise: the finding was filed")
            warned = [ln for ln in err.splitlines() if ln.startswith("warning:")]
            self.assertEqual(len(warned), 1, err)
            self._assert_no_retry(warned[0])

        with self.subTest(writer="critic stranded row"):
            held = mock.patch.object(critic, "_ledger_lock", side_effect=_timed_out)
            err = io.StringIO()
            try:   # the row is written under the lock; only its withdrawal times out
                with self.assertRaises(ValueError), contextlib.redirect_stderr(err), \
                        critic.provisional_verdict(self.root, "BG0001", "APPROVE", "rev", "dev",
                                                   pending=lambda: True):
                    held.start()
                    raise ValueError("the transition refused")
            finally:
                held.stop()
            ledger = critic.verdicts_path(self.root)
            self.assertEqual([(r["unit"], r["verdict"]) for r in critic.read_verdicts(self.root)],
                             [("BG0001", "APPROVE")], "premise: the provisional row stands")
            stranded = [ln for ln in err.getvalue().splitlines() if str(ledger) in ln]
            self.assertEqual(len(stranded), 1, err.getvalue())
            self._assert_no_retry(stranded[0])
            self.assertIn(f"remove that row from {ledger}", stranded[0],
                          "the message must name how to remove the stranded row")

        with self.subTest(writer="sprint report-time token stamp"):
            with mock.patch.object(run_state, "stamp_tokens", side_effect=_timed_out), \
                    mock.patch("sprint_report.build_report",
                               return_value={"fingerprint": "fp0781"}), \
                    mock.patch("sprint_report.file_report", return_value="RPT0001"):
                result, _out, err = _run(sprint._file_the_report, self.root, "RETRO0001")
            self.assertEqual(result, ("RPT0001", "fp0781"), "premise: the report was filed")
            warned = [ln for ln in err.splitlines() if ln.startswith("warning:")]
            self.assertEqual(len(warned), 1, err)
            self._assert_no_retry(warned[0])

    def test_a_non_busy_flock_error_is_one_line_from_sprint(self) -> None:
        """AC3. MUTANT: catch only `AllocationLockTimeout` in `sprint.main`, so ENOLCK escapes
        as a traceback."""
        def no_locks(fd, op):
            if op & fcntl.LOCK_NB:
                raise OSError(errno.ENOLCK, "No locks available")

        with mock.patch.object(fcntl, "flock", no_locks):
            try:
                rc, out, err = _run(sprint.main, ["appetite", "resize", "--units", "5",
                                                  "--reason", "more work", "--root",
                                                  str(self.root)])
            except OSError as exc:
                self.fail(f"the flock error escaped as a traceback: {exc}")
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", out + err)
        self.assertEqual(err.strip().splitlines(), [err.strip()], "the error must be one line")
        self.assertTrue(err.startswith("error:"), err)
        self.assertIn("ENOLCK", err, "the error must name the errno")


if __name__ == "__main__":
    unittest.main()
