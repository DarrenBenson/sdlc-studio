#!/usr/bin/env bash
# Run the shipped skill-script suite ONCE and hold it to two standards:
#
#   1. every test passes; and
#   2. a PASSING run is SILENT.
#
# The second is not fussiness. Tests that feed a tool a deliberately-bad fixture were letting
# the tool's diagnostics escape to the console, so a fully green run printed `ERROR` lines and
# the tail of 2000 passing tests read like a failure. That trains everyone - human and agent -
# to skim past `ERROR`, which is the exact reflex that lets a real one through. A signal you
# cannot distinguish from noise is not a signal.
#
# Both checks read ONE run of the suite. An earlier version of this guard ran the suite a
# second time to grep it, which doubled the pre-commit hook's runtime and timed it out: a
# guard whose cost is paid on every commit has to be cheap, or it gets disabled and then it
# guards nothing.
set -uo pipefail

skill="${1:-.claude/skills/sdlc-studio/scripts}"
out="$(python3 -m unittest discover -s "$skill/tests" 2>&1)"
rc=$?

printf '%s\n' "$out"

if [ "$rc" -ne 0 ]; then
  exit "$rc"
fi

# Diagnostics a tool wrote to the console during a GREEN run: the expected complaint from a
# bad-fixture test that was never captured. Capture it in the test and assert on it instead.
#
# Detection lives in tools/test_noise.py so it is unit-testable. The inline grep this
# replaced matched ONE shape - `ERROR`/`WARN` then an absolute path - and caught 0 of the
# leaks this suite actually produces, which are lowercase `error:`, `warning:`, `usage:`
# and tool-prefixed messages.
#
# TEST_NOISE_BASELINE is a RATCHET over declared debt, not an amnesty. The suite leaks 134
# lines today; demanding zero before the gate may run is why it ran nowhere. Frozen here,
# the gate fails the moment a change adds one. Lower it as leaks are captured - never
# raise it to make a red gate green.
#
# 233 -> 134 (US0266). Adding the gate briefing to the plan pushed the count over, and the
# rule above forbids raising the number to accommodate it - so the leaks were captured
# instead. Seven `main(["plan", ...])` call sites in test_sprint.py printed a whole rendered
# plan each with nothing capturing stdout; wrapping them removed the 6 new lines and 93 that
# predated this change.
#
# This number was first recorded as 68. That was not a measurement of the suite, it was a
# measurement of a blind detector: the exclusion list swallowed any indented line and any
# capitalised one, and the leak patterns demanded an alarm word. A baseline is only ever as
# true as the detector that produced it - re-measure after touching either.
TEST_NOISE_BASELINE="${TEST_NOISE_BASELINE:-134}"

printf '%s\n' "$out" | python3 "$(dirname "$0")/test_noise.py" --baseline "$TEST_NOISE_BASELINE"
