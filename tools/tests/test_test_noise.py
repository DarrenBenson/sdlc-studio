"""Unit tests for tools/test_noise.py - the green-run noise detector (RED first).

The class these lock: a PASSING suite must say nothing. A diagnostic that escapes an
expected-failure fixture trains everyone to skim past `error`, which is the reflex that
lets a real one through. The shipped detector matched exactly one shape - `ERROR` or
`WARN` followed by an absolute path - and caught 0 of the 283 lines this repo's own suite
was leaking, because the real leaks are lowercase `error:`, `warning:`, `usage:` and
tool-prefixed messages.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "test_noise.py"


def _load():
    spec = importlib.util.spec_from_file_location("test_noise", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["test_noise"] = mod
    spec.loader.exec_module(mod)
    return mod


tn = _load()

# Real lines this repo's suite printed during a fully green run.
OBSERVED_LEAKS = [
    "error: reviewer == author - independence is the floor; a self-review never clears",
    "command_audit: 1 broken tool(s) (--strict)",
    "warning: could not load .config.yaml (config loading needs PyYAML); using defaults",
    "sprint-review refused: reviewer 'bob' == author - a sprint-level self-review",
    "usage: python3 -m unittest record [-h] --unit UNIT",
    "issue #42 not found via gh for CR-0002; skipping",
    "gh issue create failed: denied",
    "failed to create issue for CR-0001",
    "ERROR   /tmp/x/sdlc-studio/bugs/BG0001-x.md: [evidence-present] bug has no evidence",
    "WARN    /tmp/x/sdlc-studio/bugs/BG0002-y.md: [pseudo-verify] line 36",
]

# Lines a unittest run legitimately prints. Flagging any of these would make the gate
# fire on every green run, which is how a guard gets switched off.
RUNNER_OUTPUT = [
    "....................",
    "..s..x..",
    "----------------------------------------------------------------------",
    "======================================================================",
    "Ran 3048 tests in 116.245s",
    "OK",
    "OK (skipped=1)",
    "FAILED (failures=2)",
    "",
    "FAIL: test_thing (tests.test_x.ThingTests.test_thing)",
    "ERROR: test_other (tests.test_x.OtherTests.test_other)",
    "Traceback (most recent call last):",
    '  File "/x/tests/test_x.py", line 12, in test_thing',
    "    self.assertEqual(1, 2)",
    "AssertionError: 1 != 2",
    "During handling of the above exception, another exception occurred:",
]


class NoiseShapeDetectorTests(unittest.TestCase):
    """AC2: the detector catches the leak shapes this suite actually produces."""

    def test_every_observed_leak_is_detected(self) -> None:
        missed = [l for l in OBSERVED_LEAKS if not tn.leaked_lines(l)]
        self.assertEqual(missed, [], f"{len(missed)} real leak shape(s) undetected")

    def test_no_runner_output_is_flagged(self) -> None:
        false = [l for l in RUNNER_OUTPUT if tn.leaked_lines(l)]
        self.assertEqual(false, [], f"{len(false)} legitimate runner line(s) flagged")

    def test_the_original_single_shape_still_matches(self) -> None:
        """The shape the shipped guard caught must not be lost while broadening."""
        self.assertTrue(tn.leaked_lines("ERROR   /tmp/x/a.md: [rule] message"))
        self.assertTrue(tn.leaked_lines("WARN    /tmp/x/a.md: [rule] message"))

    def test_a_multiline_block_returns_each_leak_once(self) -> None:
        text = "\n".join(["....", "error: boom", "OK", "warning: hmm", "Ran 3 tests in 0.1s"])
        self.assertEqual(tn.leaked_lines(text), ["error: boom", "warning: hmm"])

    def test_a_clean_run_returns_nothing(self) -> None:
        self.assertEqual(tn.leaked_lines("\n".join(RUNNER_OUTPUT)), [])

    def test_an_assertion_message_mentioning_error_is_not_a_leak(self) -> None:
        """A failure's own text is the runner reporting, not a tool leaking."""
        self.assertEqual(tn.leaked_lines("AssertionError: error: expected this"), [])

    def test_detection_is_anchored_not_substring(self) -> None:
        """A sentence merely containing the word must not fire, or the gate cries wolf."""
        self.assertEqual(tn.leaked_lines("the parser reports an error: this is prose"), [])


class NoiseBaselineTests(unittest.TestCase):
    """The ratchet. This repo leaks 283 lines today; requiring zero before the gate can
    run at all would mean the gate never runs, which is the state it is in now. The
    baseline grandfathers the current count and fails on an INCREASE, so the debt is
    visible and cannot grow."""

    def test_a_count_at_the_baseline_passes(self) -> None:
        self.assertTrue(tn.within_baseline(283, 283))

    def test_a_count_below_the_baseline_passes(self) -> None:
        self.assertTrue(tn.within_baseline(200, 283))

    def test_a_count_above_the_baseline_fails(self) -> None:
        self.assertFalse(tn.within_baseline(284, 283))

    def test_no_baseline_means_zero_tolerated(self) -> None:
        """A project adopting the gate clean must not inherit a silent allowance."""
        self.assertFalse(tn.within_baseline(1, None))
        self.assertTrue(tn.within_baseline(0, None))


if __name__ == "__main__":
    unittest.main()
