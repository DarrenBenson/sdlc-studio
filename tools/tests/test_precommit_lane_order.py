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

MESSAGE FIRST (US0372). The expensive lanes since moved OUT of `pre-commit` altogether,
behind the commit-message check in `commit-msg`: git runs `pre-commit` before the message
exists, so no ordering inside one hook could ever put the message rules first. The order
is therefore pinned across the PAIR, and `MessageCheckOrderTests` holds it.

These tests read the shipped hooks, so a change to either has to come here first. What
they cannot show is that a lane ran at all - `tools/tests/test_message_first_gate.py`
executes the pair over a real `git commit` for that.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

GITHOOKS = Path(__file__).resolve().parents[2] / ".githooks"
HOOK = GITHOOKS / "pre-commit"
MSG_HOOK = GITHOOKS / "commit-msg"


def _text(hook: Path = HOOK) -> str:
    return hook.read_text(encoding="utf-8")


def _line_matching(pattern: str, hook: Path) -> int:
    """1-indexed line of the first line matching `pattern` in `hook`."""
    for i, line in enumerate(_text(hook).splitlines(), 1):
        if re.search(pattern, line):
            return i
    raise AssertionError(f"no line matching {pattern!r} in {hook.name}")


def _lane_line(key: str, hook: Path = HOOK) -> int:
    """1-indexed line of the `run "<key>"` invocation."""
    return _line_matching(rf'^\s*run\s+"{re.escape(key)}"', hook)


def _lane_keys(hook: Path = HOOK) -> list[str]:
    return re.findall(r'^\s*run\s+"([^"]+)"', _text(hook), re.M)


#: Every lane each hook is expected to declare. This is the anti-loss guard: a reorder
#: that drops a lane would otherwise pass every ordering assertion below while silently
#: reducing coverage.
#: `gate` is deliberately absent: it is an inline if/else block, not a `run "..."` lane.
EXPECTED_LANES = {
    "style", "links", "skill-spec", "versions", "budgets", "neutrality", "action-pins",
    "floor-pending", "markdown", "markdown-payload",
}

#: The lanes that cost real wall-clock, and that therefore may not run until every cheap
#: refusal - including the commit-message rules - has had its chance.
EXPENSIVE_LANES = {"skill-tests", "tool-tests"}


class LaneOrderTests(unittest.TestCase):
    def test_markdown_lanes_run_before_the_unit_suites(self) -> None:
        # Across the pair: the cheap lanes live in `pre-commit`, which git runs first in
        # its entirety, so every one of them precedes the suites in `commit-msg`.
        for cheap in ("markdown", "markdown-payload"):
            self.assertIn(cheap, _lane_keys(HOOK),
                          f'the "{cheap}" lane must stay in pre-commit, ahead of the suites - a '
                          "markdown error must not cost a full unit-suite run first")
        for suite in EXPENSIVE_LANES:
            self.assertIn(suite, _lane_keys(MSG_HOOK))

    def test_the_cheap_static_guards_all_precede_the_suites(self) -> None:
        for cheap in ("style", "links", "budgets", "neutrality", "versions", "floor-pending"):
            self.assertIn(cheap, _lane_keys(HOOK))
        self.assertEqual(EXPENSIVE_LANES & set(_lane_keys(HOOK)), set(),
                         "an expensive lane is back in pre-commit, which runs before the "
                         "commit message exists")

    def test_no_lane_is_lost_in_the_reorder(self) -> None:
        # A dropped lane is a silent coverage cut.
        self.assertEqual(set(_lane_keys(HOOK)), EXPECTED_LANES)
        self.assertEqual(set(_lane_keys(MSG_HOOK)), EXPENSIVE_LANES)

    def test_every_lane_key_is_unique(self) -> None:
        keys = _lane_keys(HOOK) + _lane_keys(MSG_HOOK)
        self.assertEqual(len(keys), len(set(keys)), f"a lane is invoked twice: {keys}")


class MessageCheckOrderTests(unittest.TestCase):
    """AC3: the order is pinned so it cannot silently revert.

    The saving is real only if the message verdict is reached before the first expensive
    lane AND the refusal leaves before them. Both are read from the shipped hooks here;
    `test_message_first_gate.py` proves the same two properties by execution.
    """

    def test_the_message_check_precedes_the_expensive_lanes(self) -> None:
        check = _line_matching(r"python3 .*check-commit-msg", MSG_HOOK)
        for lane in sorted(EXPENSIVE_LANES):
            self.assertLess(check, _lane_line(lane, MSG_HOOK),
                            f'the commit-message check must be invoked before "{lane}"')
        # The refusal has to LEAVE before them; reaching the verdict and then running the
        # suites anyway would report the defect early and still charge for it.
        refusal_exit = _line_matching(r"^\s*exit 1\b", MSG_HOOK)
        self.assertLess(check, refusal_exit)
        for lane in sorted(EXPENSIVE_LANES):
            self.assertLess(refusal_exit, _lane_line(lane, MSG_HOOK))
        # ...and they are gone from the hook git runs before the message exists.
        self.assertEqual(EXPENSIVE_LANES & set(_lane_keys(HOOK)), set())

    def test_the_timing_and_budget_recording_moved_with_the_suites(self) -> None:
        """The measurement has to wrap the lanes wherever they now run: an estimate before
        them, a per-suite record, the scope judgement and the per-commit total after."""
        msg = _text(MSG_HOOK)
        for fragment in ("gate_timing.py estimate", "record --suite skill-tests",
                         "record --suite tool-tests", "gate_timing.py scope",
                         "record --suite total", "gate_timing.py budget"):
            self.assertIn(fragment, msg, f"{fragment!r} did not move with the suites")
        self.assertLess(_line_matching(r"gate_timing\.py estimate", MSG_HOOK),
                        _lane_line("skill-tests", MSG_HOOK),
                        "the cost must be announced before it is paid")

    def test_the_message_hook_never_blocks_a_commit_on_its_own_timing(self) -> None:
        # Same rule the pre-commit lanes are held to: an advisory measurement that can fail
        # a commit is worse than no measurement.
        for line in _text(MSG_HOOK).splitlines():
            if "gate_timing.py" in line:
                self.assertIn("2>/dev/null", line, f"unguarded timing call: {line.strip()}")

    def test_pre_commit_hands_the_selection_over_rather_than_deciding_twice(self) -> None:
        """The selection rule stays in ONE place. `pre-commit` sees the staged index and
        decides; `commit-msg` obeys the record. A second copy of the grep in the message
        hook would be a rule that could drift against the one the skip message describes."""
        self.assertIn("test_relevant=", _text(HOOK))
        self.assertNotIn("test_relevant=", _text(MSG_HOOK))


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
