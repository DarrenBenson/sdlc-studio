"""BG0780: the allocation lock names a non-busy flock error, and its callers report its timeout.

US0948 made `allocation_lock` fail closed with `AllocationLockTimeout`. Four edges were left:
every `OSError` from flock was retried as if another writer held the lock (ENOLCK on NFS then
waited out the timeout and blamed a writer that did not exist); a provisional verdict whose
withdrawal timed out dropped the transition's refusal; two best-effort writers swallowed the
timeout into a debug log; and `sprint.py` let it escape as a traceback.

The lock is held by a real second process, because flock is cross-process. Its timeout is cut
to a fraction of a second in-process so the tests do not wait out the shipped ten seconds.
Every workspace is a temporary directory that removes itself.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import contextlib
import errno
import io
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import file_finding  # noqa: E402
import sprint  # noqa: E402
import transition  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

try:
    import fcntl
    HAS_FLOCK = True
except ImportError:  # pragma: no cover - the non-POSIX branch is a documented no-op
    HAS_FLOCK = False

#: A process that takes the lock, says so on stdout, then holds it until killed.
HOLDER = textwrap.dedent("""
    import sys, time
    sys.path.insert(0, sys.argv[1])
    from lib import sdlc_md
    with sdlc_md.allocation_lock(sys.argv[2]):
        print("held", flush=True)
        time.sleep(60)
""")

REAL_LOCK = sdlc_md.allocation_lock


def _short_lock(repo_root, timeout: float = 10.0):
    """The real lock with its wait cut to 0.3s, so a held lock times out quickly."""
    return REAL_LOCK(repo_root, timeout=min(timeout, 0.3))


class _Holder:
    """A second process holding the root's allocation lock from `start()` until `stop()`."""

    def __init__(self, root: Path) -> None:
        self.root, self.proc = root, None

    def start(self) -> None:
        self.proc = subprocess.Popen([sys.executable, "-c", HOLDER, str(SCRIPTS),
                                      str(self.root)], stdout=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline().strip()
        if line != "held":
            self.stop()
            raise AssertionError(f"the holder never took the lock (said {line!r})")

    def stop(self) -> None:
        if self.proc is None:
            return
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait()
        self.proc.stdout.close()
        self.proc = None


def _lock_file(root: Path) -> str:
    return str(root / "sdlc-studio" / ".local" / "allocation.lock")


def _run(fn, *args) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn(*args)
    return rc, out.getvalue(), err.getvalue()


@unittest.skipUnless(HAS_FLOCK, "flock is POSIX-only; elsewhere the lock is a documented no-op")
class LockErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="bg0780-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.holder = _Holder(self.root)
        self.addCleanup(self.holder.stop)
        patch = mock.patch.object(sdlc_md, "allocation_lock", _short_lock)
        patch.start()
        self.addCleanup(patch.stop)

    def test_a_non_busy_flock_error_is_named_at_once(self) -> None:
        """AC1. MUTANT: retry every `OSError` as if the lock were busy, so ENOLCK waits out
        the timeout and is reported as another writer holding the lock. The control: a busy
        lock (`BlockingIOError`) is still waited on and reported as the timeout."""
        def no_locks(fd, op):
            if op & fcntl.LOCK_NB:
                raise OSError(errno.ENOLCK, "No locks available")

        ran = []
        started = time.monotonic()
        with mock.patch.object(fcntl, "flock", no_locks), \
                self.assertRaises(OSError) as caught:
            with REAL_LOCK(self.root, timeout=2.0):
                ran.append(True)
        waited = time.monotonic() - started
        self.assertEqual(ran, [], "the writer's block ran without the lock")
        self.assertNotIsInstance(caught.exception, sdlc_md.AllocationLockTimeout)
        self.assertEqual(caught.exception.errno, errno.ENOLCK)
        message = str(caught.exception)
        self.assertIn("ENOLCK", message, "the error must name the errno")
        self.assertIn(_lock_file(self.root), message, "the error must name the lock file")
        self.assertNotIn("another writer", message)
        self.assertLess(waited, 1.0, "a lock that can never be had was waited on")

        def busy(fd, op):
            if op & fcntl.LOCK_NB:
                raise BlockingIOError(errno.EWOULDBLOCK, "busy")

        with mock.patch.object(fcntl, "flock", busy), \
                self.assertRaises(sdlc_md.AllocationLockTimeout):
            with REAL_LOCK(self.root, timeout=0.2):
                ran.append(True)
        self.assertEqual(ran, [])

    def test_a_stranded_provisional_row_is_named_with_the_refusal(self) -> None:
        """AC2. MUTANT: let the timeout raised by the withdrawal escape, which drops the
        transition's refusal and says nothing was written while the APPROVE row stands."""
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        # one unticked criterion and no `Verify:`: nothing speaks for the fix, so Fixed refuses
        (bugs / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n"
            "- [ ] the unit behaves\n", encoding="utf-8")
        (bugs / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n", encoding="utf-8")
        refusals: list[str] = []
        real = transition.transition

        def refused_then_held(*args, **kwargs):
            try:
                return real(*args, **kwargs)
            except ValueError as exc:
                refusals.append(str(exc))
                raise
            finally:
                self.holder.start()   # another writer takes the lock before the withdrawal

        with mock.patch.object(transition, "transition", side_effect=refused_then_held):
            rc, out, err = _run(transition.main, [
                "set", "--id", "BG0001", "--status", "Fixed", "--verdict", "APPROVE",
                "--reviewer", "rev", "--author", "dev", "--root", str(self.root)])
        self.assertEqual(len(refusals), 1, "premise: the gated transition refused")
        self.assertNotEqual(rc, 0)
        both = out + err
        self.assertIn(refusals[0], both, "the transition's refusal was dropped")
        ledger = critic.verdicts_path(self.root)
        self.assertEqual([(r["unit"], r["verdict"]) for r in critic.read_verdicts(self.root)],
                         [("BG0001", "APPROVE")], "premise: the provisional row stands")
        stranded = [ln for ln in err.splitlines() if str(ledger) in ln]
        self.assertTrue(stranded, f"the stranded row's ledger is not named: {err!r}")
        self.assertIn("BG0001", stranded[0])
        self.assertIn("APPROVE", stranded[0])
        self.assertIn(_lock_file(self.root), stranded[0], "the lock is not named")

    def test_a_swallowed_timeout_warns_on_stderr(self) -> None:
        """AC3. MUTANT: swallow the timeout into a debug log in either best-effort writer, so
        the CLI prints success while the attribution or the token stamp was never written."""
        with self.subTest(writer="file_finding attribution"):
            run_state.open_run(self.root, goal="a goal", batch=["US0001"])
            run_state.start_batch(self.root, ["US0001"])
            real_note = run_state.note_finding

            def held_note(*args, **kwargs):
                self.holder.start()
                return real_note(*args, **kwargs)

            with mock.patch.object(run_state, "note_finding", side_effect=held_note):
                rc, _out, err = _run(file_finding.main, [
                    "file", "--type", "bug", "--title", "a defect", "--severity", "High",
                    "--summary", "s", "--steps", "x", "--fix", "y", "--affects", "src/x.py",
                    "--points", "3", "--root", str(self.root)])
            self.holder.stop()
            self.assertEqual(rc, 0, err)
            filed = [p for p in (self.root / "sdlc-studio" / "bugs").glob("BG*.md")]
            self.assertEqual(len(filed), 1, "the primary write, the filed bug, must stand")
            self.assertEqual(run_state.open_batch(self.root)["findings_raised"], [],
                             "premise: the attribution was not written")
            warned = [ln for ln in err.splitlines() if ln.startswith("warning:")]
            self.assertTrue(warned and _lock_file(self.root) in warned[0],
                            f"no stderr warning naming the lock: {err!r}")

        with self.subTest(writer="sprint token stamp"):
            before = run_state.read(self.root).get(run_state.TOKEN_STAMPS) or []

            def held_stamp(root, kind, transcripts_dir=None):
                self.holder.start()
                return {"tokens": 1000, "source": "fixture", "at": "2026-09-25T00:00:00Z",
                        "kind": kind, "model": None}

            def released_build(*args, **kwargs):
                self.holder.stop()
                return {"fingerprint": "fp0780"}

            with mock.patch.object(run_state, "_stamp", side_effect=held_stamp), \
                    mock.patch("sprint_report.build_report", side_effect=released_build), \
                    mock.patch("sprint_report.file_report", return_value="RPT0001"):
                result, _out, err = _run(sprint._file_the_report, self.root, "RETRO0001")
            self.assertEqual(result, ("RPT0001", "fp0780"))
            state = run_state.read(self.root)
            self.assertEqual(state.get("report"), "RPT0001", "the primary write must stand")
            self.assertEqual(state.get(run_state.TOKEN_STAMPS) or [], before,
                             "premise: the stamp was not written")
            warned = [ln for ln in err.splitlines() if ln.startswith("warning:")]
            self.assertTrue(warned and _lock_file(self.root) in warned[0],
                            f"no stderr warning naming the lock: {err!r}")

    def test_a_sprint_writer_reports_the_timeout_in_one_line(self) -> None:
        """AC4. MUTANT: let `AllocationLockTimeout` escape `sprint.main`, which the CLI prints
        as a traceback."""
        self.holder.start()
        try:
            rc, out, err = _run(sprint.main, ["appetite", "resize", "--units", "5",
                                              "--reason", "more work", "--root",
                                              str(self.root)])
        except sdlc_md.AllocationLockTimeout as exc:
            self.fail(f"the timeout escaped as a traceback: {exc}")
        self.assertNotEqual(rc, 0)
        self.assertNotIn("Traceback", out + err)
        errors = [ln for ln in err.splitlines() if ln.startswith("error:")]
        self.assertEqual(len(errors), 1, err)
        self.assertEqual(err.strip(), errors[0], "the timeout must be one line")
        self.assertIn(_lock_file(self.root), errors[0])


if __name__ == "__main__":
    unittest.main()
