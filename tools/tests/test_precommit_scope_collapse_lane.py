"""The SHELL half of the collapse contract (BG0413), which had no test at all.

The python half is well covered: `test_gate_timing.py` pins exit 3, the ack rules and the
recording rules. But the verdict only costs anything if `.githooks/commit-msg` acts on it, and
an independent round-3 review mutated the hook three ways - reading exit 2 instead of 3,
dropping the non-empty-note belt, and not setting `fail=1` - and ALL THREE survived the entire
589-test tools suite. One end of the contract was pinned and the other was free.

That is the same shape as the defect the unit exists to fix: a guard whose verdict reaches
nothing. So these tests drive the REAL tracked hook in a hermetic repo, with `gate_timing.py`
stubbed to the collapse contract, and assert on the commit that results.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

# Imported as a MODULE, not by name: `from ... import WindowGuardTests` binds that TestCase
# into this module's namespace and unittest then collects and re-runs all of its cases here.
import test_precommit_window_guard as _wg

_git = _wg._git

#: A `gate_timing.py` honouring the real contract: `scope` prints the verdict and exits 3,
#: every other subcommand is silent and exits 0. Stubbed rather than real so the test is about
#: the HOOK's reaction, not about re-deriving a collapse.
COLLAPSE_STUB = '''import sys
if len(sys.argv) > 1 and "scope" in sys.argv:
    print("gate-budget: suite scope COLLAPSED, commit BLOCKED - "
          "500 tests ran against a peak of 5000 - a 90% drop")
    sys.exit(3)
sys.exit(0)
'''

#: The shapes python itself produces. The hook must treat NONE of them as a collapse.
QUIET_EXIT_2 = 'import sys\nsys.exit(2)\n'          # argparse error / missing file
EXIT_3_NO_MESSAGE = 'import sys\nsys.exit(3)\n'      # the code, with nothing to say


class ScopeCollapseLaneTests(unittest.TestCase):
    """Borrows the hermetic fixture whose every other guard passes, WITHOUT inheriting its
    tests - subclassing a TestCase re-runs every parent case, so the 32 window-guard tests
    would execute a second time in every run of this module for no added coverage."""

    CLAIMED = _wg.WindowGuardTests.CLAIMED

    def setUp(self) -> None:
        self._fixture = _wg.WindowGuardTests("run")   # a carrier for _repo/_commit, never executed

    def _with_gate_timing(self, root: Path, body: str) -> None:
        (root / "tools" / "gate_timing.py").write_text(body, encoding="utf-8")

    def _run(self, stub: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture._repo(Path(d))
            self._with_gate_timing(root, stub)
            _git(root, "add", "-A")
            return self._fixture._commit(root, self.CLAIMED, "VALUE = 2\n")

    def test_a_collapse_verdict_BLOCKS_the_commit(self) -> None:
        """The load-bearing case. Mutating the hook to read exit 2 lets this commit land while
        still printing `commit BLOCKED` - and then `gate green.` underneath it."""
        rc, out = self._run(COLLAPSE_STUB)
        self.assertNotEqual(0, rc, "a collapsed suite committed green")
        self.assertIn("COLLAPSED", out)
        self.assertNotIn("gate green.", out,
                         "the gate reported green over a suite that had stopped running")

    def test_pythons_OWN_exit_2_does_not_block(self) -> None:
        """A missing or mis-invoked `gate_timing.py` exits 2. Reading 2 as `collapsed` refused
        every commit with a blank red line, breaking the hook's stated promise to degrade
        honestly - and it left a test red on main for six commits."""
        rc, out = self._run(QUIET_EXIT_2)
        self.assertEqual(0, rc, f"a tool error blocked a legitimate commit:\n{out}")
        self.assertIn("gate green.", out)

    def test_exit_3_with_NOTHING_to_say_does_not_block(self) -> None:
        """The second belt. A lane that blocks must be able to state why; a refusal printing an
        empty line is indistinguishable from the gate breaking."""
        rc, out = self._run(EXIT_3_NO_MESSAGE)
        self.assertEqual(0, rc, f"a silent exit 3 blocked the commit:\n{out}")

    def test_a_missing_gate_timing_script_does_not_block(self) -> None:
        """The end-to-end form of the same promise, with the file genuinely absent."""
        with tempfile.TemporaryDirectory() as d:
            root = self._fixture._repo(Path(d))
            (root / "tools" / "gate_timing.py").unlink(missing_ok=True)
            _git(root, "add", "-A")
            rc, out = self._fixture._commit(root, self.CLAIMED, "VALUE = 3\n")
        self.assertEqual(0, rc, f"an absent gate_timing.py blocked the commit:\n{out}")


if __name__ == "__main__":
    unittest.main()
