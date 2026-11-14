"""A worker held back by a signal to its caller waits a bounded time for the caller's own
handler, then refuses, so a handler that waits on those workers cannot hang the process.

Each case runs the caller as a child process under its own timeout, so a hang fails the test
and not the suite."""
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

# From the signal to a drained pool: the worker gives the caller's handler the stop grace (one
# second) plus three, the four seconds the changelog states, then refuses. The ceiling sits
# short of twice that, a bound run afresh for each queued verifier, and leaves the rest as room
# for a busy machine; a worker that waits for good meets the driver's own timeout.
_BOUND = 4.0
_WAITS_AT_LEAST = 3.8
_EXIT_WITHIN = 7.5
_DRIVER_TIMEOUT = 20

# A caller running a one-worker verifier pool that signals itself with SIGTERM once the first
# verifier runs, then prints how long the pool took to drain and what the queued two returned.
# Under "drain" its SIGTERM handler drains the pool, waiting on the worker the relay holds
# back. Under "window" its handler raises, and a second SIGTERM lands as the relay clears its
# settled event, before the relay's `try:`, so the inner relay's raise leaves the outer one's
# count raised and the event clear; the caller catches the raise and drains the pool.
_DRIVER = """
import json, os, signal, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
window = sys.argv[2] == "window"
pool = ThreadPoolExecutor(max_workers=1)

def drain(signum, frame):
    pool.shutdown(wait=True)

def stop(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, stop if window else drain)
sys.path.insert(0, sys.argv[1])
import verify_ac

class Window(threading.Event):
    armed = True

    def clear(self):
        super().clear()
        if Window.armed:
            Window.armed = False
            os.kill(os.getpid(), signal.SIGTERM)

if window:
    verify_ac._RELAY_SETTLED = Window()
    verify_ac._RELAY_SETTLED.set()
futures = [pool.submit(verify_ac.run_verifier, cmd, 30, Path.cwd())
           for cmd in ("shell touch started; sleep 3", "shell echo one", "shell echo two")]
deadline = time.monotonic() + 15
while not Path("started").is_file() and time.monotonic() < deadline:
    time.sleep(0.02)
signalled = time.monotonic()
try:
    os.kill(os.getpid(), signal.SIGTERM)
except KeyboardInterrupt:
    pass
pool.shutdown(wait=True)
print(json.dumps({
    "elapsed": time.monotonic() - signalled,
    "queued": [type(f.exception()).__name__ if f.exception() else f.result().ok
               for f in futures[1:]],
    "relays_left": verify_ac._RELAYS_RUNNING,
    "settled": verify_ac._RELAY_SETTLED.is_set(),
    "bound": verify_ac._SIGNAL_GRACE + verify_ac._SETTLE_SLACK,
}))
"""


@unittest.skipUnless(hasattr(os, "killpg"), "the signal relay needs process groups")
class DrainingHandlerTests(unittest.TestCase):
    """A caller whose handler waits on its own workers ends within the bound, with the queued
    verifiers refused and no second signal sent."""

    def _drive(self, mode: str) -> dict:
        with tempfile.TemporaryDirectory() as d:
            caller = subprocess.Popen(
                [sys.executable, "-B", "-c", _DRIVER, str(SCRIPTS), mode],
                cwd=d, start_new_session=True, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                out, err = caller.communicate(timeout=_DRIVER_TIMEOUT)
            except subprocess.TimeoutExpired:
                os.killpg(caller.pid, signal.SIGKILL)
                caller.communicate()
                self.fail(f"the caller hung past {_DRIVER_TIMEOUT}s after one SIGTERM ({mode})")
            finally:
                if caller.poll() is None:
                    os.killpg(caller.pid, signal.SIGKILL)
                    caller.wait()
            self.assertTrue((Path(d) / "started").is_file(), "premise: nothing started")
        self.assertEqual(0, caller.returncode, err)
        return json.loads(out)

    def test_a_handler_draining_its_pool_ends_within_the_bound(self) -> None:
        """MUTANT: an unbounded wait (the worker waits on the handler that waits on it, for
        good); a bound longer or shorter than the four seconds; a bound that runs afresh for
        each queued verifier; or carrying on at the bound, so the queued verifiers run."""
        got = self._drive("drain")
        self.assertEqual(_BOUND, got["bound"], "the bound is not the four seconds stated")
        self.assertEqual(["KeyboardInterrupt", "KeyboardInterrupt"], got["queued"],
                         "a queued verifier was not refused")
        self.assertLess(got["elapsed"], _EXIT_WITHIN, "the drain outlasted the bound")
        self.assertGreaterEqual(got["elapsed"], _WAITS_AT_LEAST,
                                "the worker refused before the handler's four seconds passed")

    def test_a_handler_raising_before_the_relays_try_leaves_no_unbounded_wait(self) -> None:
        """A raise between the relay count's increment and its `try:` leaves the count raised
        and the settled event clear for good; the bound still frees the worker. MUTANT: an
        unbounded wait, so the caller's drain after catching the raise hangs."""
        got = self._drive("window")
        self.assertEqual((1, False), (got["relays_left"], got["settled"]),
                         "premise: the raise did not land between the increment and the try")
        self.assertEqual(["KeyboardInterrupt", "KeyboardInterrupt"], got["queued"],
                         "a queued verifier was not refused")
        self.assertLess(got["elapsed"], _EXIT_WITHIN, "the drain outlasted the bound")
        self.assertGreaterEqual(got["elapsed"], _WAITS_AT_LEAST,
                                "the worker refused before the handler's four seconds passed")


if __name__ == "__main__":
    unittest.main()
