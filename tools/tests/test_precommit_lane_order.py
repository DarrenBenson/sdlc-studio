"""The pre-commit gate's lane ORDER and its short-circuit (US0268).

Two separate properties, and the second is the one that actually saves the time.

ORDER. The cheap guards must be invoked before the expensive unit suites. Measured
before the change: the suites ran at hook lines 117-136 and the markdown lanes at
142-164, so a one-line markdown error was reported only after ~132 seconds of tests.

SHORT-CIRCUIT. Ordering alone changes nothing, because `run()` records a failure and
returns 0 - the hook runs every lane and checks `fail` at the very end. Without a guard
on the expensive block, moving markdown earlier just reports it earlier and still pays
for the suites. The suites must therefore be skipped when a cheaper lane has already
failed, and that skip must be NAMED: this hook's standing rule is that a guard which
quietly does not run is indistinguishable from one that ran and passed.

These tests read the shipped hook, so a change to it has to come here first.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".githooks" / "pre-commit"


def _text() -> str:
    return HOOK.read_text(encoding="utf-8")


def _lane_line(key: str) -> int:
    """1-indexed line of the `run "<key>"` invocation."""
    for i, line in enumerate(_text().splitlines(), 1):
        if re.match(rf'^\s*run\s+"{re.escape(key)}"', line):
            return i
    raise AssertionError(f'no `run "{key}"` lane in the hook')


def _lane_keys() -> list[str]:
    return re.findall(r'^\s*run\s+"([^"]+)"', _text(), re.M)


#: Every lane the hook is expected to run. This is the anti-loss guard: a reorder that
#: drops a lane would otherwise pass every ordering assertion below while silently
#: reducing coverage.
#: `gate` is deliberately absent: it is an inline if/else block, not a `run "..."` lane.
EXPECTED_LANES = {
    "style", "links", "skill-spec", "versions", "budgets", "neutrality", "action-pins",
    "floor-pending", "skill-tests", "tool-tests", "markdown", "markdown-payload",
}


class LaneOrderTests(unittest.TestCase):
    def test_markdown_lanes_run_before_the_unit_suites(self) -> None:
        suites = _lane_line("skill-tests")
        for cheap in ("markdown", "markdown-payload"):
            self.assertLess(_lane_line(cheap), suites,
                            f'the "{cheap}" lane must be invoked before "skill-tests" - a '
                            "markdown error must not cost a full unit-suite run first")

    def test_the_cheap_static_guards_all_precede_the_suites(self) -> None:
        suites = _lane_line("skill-tests")
        for cheap in ("style", "links", "budgets", "neutrality", "versions", "floor-pending"):
            self.assertLess(_lane_line(cheap), suites)

    def test_no_lane_is_lost_in_the_reorder(self) -> None:
        # This story changes ORDER only. A dropped lane is a silent coverage cut.
        self.assertEqual(set(_lane_keys()), EXPECTED_LANES)

    def test_every_lane_key_is_unique(self) -> None:
        keys = _lane_keys()
        self.assertEqual(len(keys), len(set(keys)), f"a lane is invoked twice: {keys}")


class ShortCircuitTests(unittest.TestCase):
    """Ordering without a short-circuit saves nothing - `run` never exits."""

    def test_run_does_not_exit_so_a_guard_is_required(self) -> None:
        # Pins the premise. If `run` were ever changed to exit on failure, the guard
        # below would be redundant and this test says so rather than letting the two
        # mechanisms drift into contradicting each other.
        body = re.search(r"^run\(\)\s*\{(.*?)^\}", _text(), re.M | re.S)
        self.assertIsNotNone(body, "the hook must define run()")
        self.assertNotRegex(body.group(1), r"\bexit\b",
                            "run() does not exit; the expensive block needs its own guard")

    def test_the_unit_suites_are_guarded_by_the_accumulated_failure(self) -> None:
        # The suites must not run once a cheaper lane has already failed.
        text = _text()
        guard = re.search(r'if \[ "\$fail" -eq 0 \].*?git diff --cached --name-only', text, re.S)
        self.assertIsNotNone(
            guard,
            'the unit-suite block must be guarded by `[ "$fail" -eq 0 ]`, or a failing cheap '
            "lane still pays for the full suite - `run` records the failure and returns 0")

    def test_the_short_circuit_skip_is_named(self) -> None:
        # A silent skip is indistinguishable from a lane that ran and passed.
        self.assertRegex(
            _text(), r"SKIP.*unit suites.*cheaper lane",
            "the short-circuit skip must SAY it skipped and why, like the docs-only skip does")


if __name__ == "__main__":
    unittest.main()
