"""US0948: a writer that cannot take the allocation lock writes nothing instead of losing rows.

`sdlc_md.allocation_lock` used to give up waiting after its timeout and yield WITHOUT the lock,
so a slow holder let every waiter through unserialised (39 of 65 concurrent verdict rows lost
with the lock held 12 seconds). It now raises `AllocationLockTimeout`, naming the lock file and
the wait, and the writer's block never runs. flock is released by the kernel when its holder
dies, so failing closed cannot wedge the next writer on a killed one.

Every test runs real processes against a throwaway workspace: the lock is cross-process, so an
in-process stand-in would test nothing.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

try:
    import fcntl  # noqa: F401 - only probing that the POSIX lock exists
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

#: One writer of the concurrent wave: says it is ready, waits for the start file, then appends
#: its row with a
#: read-modify-write held under the lock, retrying whenever the lock times out. Prints how
#: many times it timed out, so the test can prove the wave really outwaited the timeout.
WRITER = textwrap.dedent("""
    import sys, time
    from pathlib import Path
    sys.path.insert(0, sys.argv[1])
    from lib import sdlc_md
    root, row, go = Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    ledger = root / "ledger.txt"
    (root / ("ready-" + row)).write_text("", encoding="utf-8")
    while not go.exists():
        time.sleep(0.005)
    timeouts = 0
    while True:
        try:
            with sdlc_md.allocation_lock(root, timeout=0.1):
                text = ledger.read_text(encoding="utf-8")
                time.sleep(0.05)
                ledger.write_text(text + row + "\\n", encoding="utf-8")
            break
        except sdlc_md.AllocationLockTimeout:
            timeouts += 1
    print(timeouts)
""")


def _hold(scripts: Path, root: Path) -> subprocess.Popen:
    """Start a holder and return once it has the lock."""
    proc = subprocess.Popen([sys.executable, "-c", HOLDER, str(scripts), str(root)],
                            stdout=subprocess.PIPE, text=True)
    line = proc.stdout.readline().strip()
    if line != "held":
        proc.kill()
        proc.wait()
        raise AssertionError(f"the holder never took the lock (said {line!r})")
    return proc


def _stop(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.kill()
    proc.wait()
    if proc.stdout:
        proc.stdout.close()


@unittest.skipUnless(HAS_FLOCK, "flock is POSIX-only; elsewhere the lock is a documented no-op")
class LockFailsClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="us0948-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_a_timed_out_writer_writes_nothing(self) -> None:
        target = self.root / "ledger.txt"
        target.write_text("row 1\n", encoding="utf-8")
        holder = _hold(SCRIPTS, self.root)
        self.addCleanup(_stop, holder)

        ran = []
        started = time.monotonic()
        with self.assertRaises(sdlc_md.AllocationLockTimeout) as caught:
            with sdlc_md.allocation_lock(self.root, timeout=0.3):
                ran.append(True)
                target.write_text("row 1\nrow 2\n", encoding="utf-8")
        waited = time.monotonic() - started

        self.assertEqual(ran, [], "the writer's block ran without the lock")
        self.assertEqual(target.read_text(encoding="utf-8"), "row 1\n")
        message = str(caught.exception)
        lock_file = str(self.root / "sdlc-studio" / ".local" / "allocation.lock")
        self.assertIn(lock_file, message, "the error must name the lock file")
        self.assertIn("0.3s", message, "the error must name how long the writer waited")
        self.assertGreaterEqual(waited, 0.3, "it gave up before the timeout")
        # A named, catchable failure the CLIs already report: they catch OSError.
        self.assertIsInstance(caught.exception, OSError)

    def test_concurrent_writers_lose_no_row(self) -> None:
        (self.root / "ledger.txt").write_text("", encoding="utf-8")
        go = self.root / "go"
        rows = [f"row {n:02d}" for n in range(20)]
        procs = [subprocess.Popen([sys.executable, "-c", WRITER, str(SCRIPTS), str(self.root),
                                   row, str(go)], stdout=subprocess.PIPE, text=True)
                 for row in rows]
        for proc in procs:
            self.addCleanup(_stop, proc)
        deadline = time.monotonic() + 60
        while len(list(self.root.glob("ready-*"))) < len(rows):  # every writer at the line
            self.assertLess(time.monotonic(), deadline, "the writers never all started")
            time.sleep(0.01)
        go.write_text("", encoding="utf-8")
        timeouts = 0
        for proc in procs:
            out, _ = proc.communicate(timeout=120)
            self.assertEqual(proc.returncode, 0, out)
            timeouts += int(out.strip())

        written = (self.root / "ledger.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(sorted(written), rows, "a concurrent writer's row was lost")
        # 20 holders of 0.05s against a 0.1s timeout must have outwaited it; without that the
        # test would pass on a lock that still proceeds unserialised once the timeout expires.
        self.assertGreater(timeouts, 0, "no writer ever timed out, so the fail path went unrun")

    def test_a_killed_holder_does_not_wedge_the_next_writer(self) -> None:
        holder = _hold(SCRIPTS, self.root)
        self.addCleanup(_stop, holder)
        os.kill(holder.pid, signal.SIGKILL)
        holder.wait()

        started = time.monotonic()
        with sdlc_md.allocation_lock(self.root, timeout=5):
            (self.root / "ledger.txt").write_text("after the kill\n", encoding="utf-8")
        self.assertLess(time.monotonic() - started, 1.0,
                        "a killed holder's lock was not released at once")
        self.assertEqual((self.root / "ledger.txt").read_text(encoding="utf-8"),
                         "after the kill\n")


if __name__ == "__main__":
    unittest.main()
