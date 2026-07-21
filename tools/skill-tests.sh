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

# The hook environment is part of the test environment. `git commit -a` runs the pre-commit
# hook with GIT_INDEX_FILE set to an ABSOLUTE path (the outer repo's .git/index.lock); a
# staged `git add` + `git commit` sets it to the RELATIVE `.git/index`. Every test that
# builds a throwaway repo in a temp dir and shells out to git then inherits it: under the
# relative form it resolves inside the fixture and nothing is wrong, under the absolute one
# every fixture git call reads and writes the OUTER repo's index. That asymmetry is why this
# read as flaky tests - the same commit passed when staged and failed with -a.
#
# Scrubbed below: every variable that can point git at a different repository, index, object
# store or path prefix. That is the "The Git Repository" set in `git help git` ENVIRONMENT
# VARIABLES, plus GIT_PREFIX, which git sets for hooks only. Measured against git 2.53, a
# hook invoked by `git commit -a` is handed GIT_INDEX_FILE and GIT_PREFIX from this list;
# the rest are scrubbed because a developer's shell or a CI runner can export them, not
# because git itself does. GIT_INDEX_FILE, GIT_DIR and GIT_WORK_TREE were each confirmed to
# break the suite on their own; GIT_PREFIX was confirmed harmless and is scrubbed anyway.
#
# Deliberately NOT scrubbed: GIT_AUTHOR_*/GIT_COMMITTER_* (confirmed harmless here - the
# fixtures set their own identity via tests/gitutil.py), GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM
# (tests set these to /dev/null themselves for hermeticity; clearing them would weaken that),
# and GIT_EDITOR/GIT_EXEC_PATH (not repo state). Widen the list, do not delete it, if a
# future git hands hooks another repo-locating variable.
#
# tools/tests/test_skill_tests_env.py pins this list from BOTH sides - every name here is
# cleared for the child, and the fixture-owned variables above are NOT. It cannot know about
# a variable a future git invents; adding one to that list is a human step.
#
# This scrub protects the child of THIS script and nothing else, which is why it is no longer
# the only defence. A protection built for one suite does not cover the suite beside it: the
# hook's tool-tests lane, a CI runner, and a developer's shell all reach the same fixtures by
# other routes. The shipped fixture helper - .claude/skills/sdlc-studio/scripts/tests/gitutil.py -
# therefore drops the same variables at the point a fixture git call is actually made, and
# ships that defence to consuming projects, where this script does not exist. The same list is
# now written out in four places; test_skill_tests_env.py holds them equal AND sweeps the repo
# for an unregistered fifth, so a new copy cannot arrive with nothing pinning it.
unset -v GIT_DIR GIT_COMMON_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_INDEX_VERSION \
  GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE \
  GIT_CEILING_DIRECTORIES GIT_DISCOVERY_ACROSS_FILESYSTEM GIT_PREFIX

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
# plan each with nothing capturing stdout. Wrapping them suppressed 105 lines in total: the 6
# the briefing had just added, and 99 that predated this change. 233 + 6 - 105 = 134.
#
# This number was first recorded as 68. That was not a measurement of the suite, it was a
# measurement of a blind detector: the exclusion list swallowed any indented line and any
# capitalised one, and the leak patterns demanded an alarm word. A baseline is only ever as
# true as the detector that produced it - re-measure after touching either.
# 132 -> 129 (RUN-01KY321Q): the root-anchoring and vacuity work captured three
# more leaks in test_loop_guard and test_lessons, whose resolved-path lines made the
# existing prints longer and easier to spot. Lowered to match, per the ratchet rule.
# 134 -> 132 (US0277/US0278): the selection-reporting lines made two uncaptured
# `main(...)` calls in test_mutation.py noisier; capturing their stdout/stderr also
# retired the SURVIVED/REFUSED lines they had been leaking since before the ratchet.
TEST_NOISE_BASELINE="${TEST_NOISE_BASELINE:-129}"

printf '%s\n' "$out" | python3 "$(dirname "$0")/test_noise.py" --baseline "$TEST_NOISE_BASELINE"
