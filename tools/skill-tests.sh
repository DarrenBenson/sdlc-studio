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
if leaked="$(printf '%s\n' "$out" | grep -E '^(ERROR|WARN)[[:space:]]+/')"; then
  printf '\n'
  printf 'test-noise: a PASSING run printed %s diagnostic line(s):\n' "$(printf '%s\n' "$leaked" | wc -l | tr -d ' ')"
  printf '%s\n' "$leaked" | head -5
  printf '\nfix: wrap the call in contextlib.redirect_stdout/redirect_stderr and assert on the\n'
  printf '     captured text. A green suite must say nothing, or a real error hides in the noise.\n'
  exit 1
fi

exit 0
