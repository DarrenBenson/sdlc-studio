"""BG1677: lane accept's bound on a sibling script stops what the script started.

`lanes._script`, which `sprint lane accept` runs, runs `critic.py record`, `verify_ac.py run`,
`transition.py set` and `sprint.py lane return` under a bound. `subprocess.run` killed only the
script at that bound, so a child it had started (the tests `verify_ac.py run` runs, say) ran on
after the accept said it was stopped.
Each case points `lanes.SCRIPTS` at a throwaway directory holding a stub script that starts a
long-lived child, so the bound, the group kill and the captured output are read on a script the
case wrote.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import inspect
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_land_commit_timeout_group as probes  # noqa: E402 - the process probes

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

#: the bound in seconds: past the stub's start, well short of the 60 s its child would run
BOUND = 4
#: a stub script that records its child's pid, under a temporary name renamed into place, and waits
STUB = """import subprocess, sys
from pathlib import Path

child = subprocess.Popen(["sleep", "60"])
Path(sys.argv[1]).with_suffix(".tmp").write_text(str(child.pid), encoding="utf-8")
Path(sys.argv[1]).with_suffix(".tmp").rename(sys.argv[1])
child.wait()
"""
#: a stub script that answers on both streams, names its directory and exits 3
QUICK = """import os, sys

print("said on stdout")
print(os.getcwd())
print("said on stderr", file=sys.stderr)
sys.exit(3)
"""


class LaneScriptTimeoutGroupTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name).resolve()
        (self.dir / "scripts").mkdir()
        patch = unittest.mock.patch.object(lanes, "SCRIPTS", self.dir / "scripts")
        patch.start()
        self.addCleanup(patch.stop)

    def _stub(self, name: str, body: str) -> None:
        (self.dir / "scripts" / name).write_text(body, encoding="utf-8")

    def test_a_timed_out_script_leaves_no_child_running(self) -> None:
        """MUTANT: `_script` through `subprocess.run` again, which kills only the script."""
        self._stub("slow.py", STUB)
        pid_file = self.dir / "child.pid"
        # the stub takes the pid file as its first argument, and `_script` adds `--root` after
        with self.assertRaises(lanes.LandError) as caught:
            lanes._script(self.dir, "slow.py", str(pid_file), "second", timeout=BOUND)
        self.assertIn(f"`slow.py {pid_file} second` ran past {BOUND}s and was stopped, so "
                      f"nothing after it ran", str(caught.exception))
        deadline = time.monotonic() + 10
        while (child := probes._read_pid(pid_file)) is None and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertIsNotNone(child, "premise: the stub started its child before the bound")
        self.addCleanup(probes._sigkill, child)
        self.assertFalse(probes._outlives(child), "the script's child outlived the bound")

    def test_a_script_inside_the_bound_returns_its_output(self) -> None:
        """Positive control: a script that ends in time answers as `subprocess.run` did, with
        its argv, its status and both streams as text."""
        self._stub("quick.py", QUICK)
        done = lanes._script(self.dir, "quick.py", "arg", timeout=BOUND)
        self.assertEqual(3, done.returncode)
        self.assertEqual(f"said on stdout\n{self.dir}\n", done.stdout, "run in the root")
        self.assertEqual("said on stderr\n", done.stderr)
        self.assertEqual([sys.executable, str(self.dir / "scripts" / "quick.py"), "arg",
                          "--root", str(self.dir)], done.args)

    def test_script_runs_through_the_bounded_runner(self) -> None:
        source = inspect.getsource(lanes._script)
        self.assertIn("_bounded(", source)
        self.assertNotIn("subprocess.run", source)


if __name__ == "__main__":
    unittest.main()
