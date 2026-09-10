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
shift 2>/dev/null || true

# Optional SELECTION: the test module paths the pre-commit gate resolved from the changed
# surface. Absent means run everything, because a missing list is an unanswered question and
# never an answer of "nothing to run" - the same contract `changed_paths` keeps.
#
# Passed as dotted module names with the tests directory on PYTHONPATH rather than as file
# paths: `unittest` refuses a path ("Empty module name"), and running from inside the tests
# directory instead would change the cwd every fixture resolves its relative paths against.
#
# The noise ratchet below holds a SELECTED run to the sum of the selected modules' budgets
# and a full run to the recorded total, so selecting less never loosens it (BG0644).
#
# The budget is read and its shrink-only rule checked BEFORE the suite: a raised entry refuses
# the commit before a test runs, and a budget file that is named but missing or unreadable
# refuses loudly - there is no fall-back to an absolute number.
budget="${TEST_NOISE_BUDGET_FILE:-$(dirname "$0")/test-noise-baseline.json}"
python3 "$(dirname "$0")/test_noise.py" --budget-check "$budget" || exit 1

if [ "$#" -gt 0 ]; then
  mods=""
  for f in "$@"; do
    base="${f##*/}"
    mods="$mods ${base%.py}"
  done
  out="$(PYTHONPATH="$skill/tests${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest $mods 2>&1)"
  rc=$?
else
  out="$(python3 -m unittest discover -s "$skill/tests" 2>&1)"
  rc=$?
fi

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
# The budget file (tools/test-noise-baseline.json) is a RATCHET over declared debt, not an
# amnesty: one entry per test module, measured alone, plus `_total` for the discovery run. A
# SELECTED run is held to the SUM of its modules' entries and a full run to `_total`, so the
# guarantee the selected path gives is: a commit whose selection leaks more than its modules'
# recorded debt is refused - the absolute-count check this replaced could not say that, because
# a subset almost always printed fewer lines than the whole suite whatever it added. What the
# sum cannot see is one module's overrun masked by a sibling's slack within the same selection;
# that bound is stated rather than hidden. Lower an entry as leaks are captured - `budget-check`
# refuses a raised one against the committed file.
#
# `_total` is the discovery run's measured figure and the entries need not sum to it: modules
# measured alone print their import-time leaks once each (at most a couple of lines here), and
# one entry, test_config, is held at its state-independent figure because the test gathers status
# over the REAL tree and prints whatever this clone's ledger prints - twelve lines while a run is
# open, none on CI. That was BG0647; since it re-pointed the test at a fixture the entry is the module's own line,
# and the figure here is kept state-independent on the same rule for any future entry. The history below is the scalar ratchet's,
# kept because each line records a leak captured.
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
# 129 -> 120 (US0485/BG0425): main was already at 130 - one over its own ratchet - and had been
# since before this commit, so the lane was red on main and the noise gate was enforcing nothing.
# It landed because a reused suite-verdict record let a retry skip the suites entirely (BG0423).
# Measured at HEAD and again with the change to prove the extra line was pre-existing rather than
# newly added. Ten `main(["build", ...])` calls in test_digest.py were leaking a `digest: wrote N`
# line each with nothing capturing stdout; capturing them took 130 -> 120, and the ratchet is
# lowered to match rather than raised to accommodate.
# 121 -> 119 (BG0541 wave): the lane was RED on main again - measured at 121 on the
# untouched tree and at 121 with this sprint's change, so the extra line was pre-existing
# and the gate had been enforcing nothing since it arrived. `test_stats_runs_without_error`
# was letting `repo_map.py stats` print its whole summary to the console while asserting
# only the exit code; capturing it retires two lines and gives the test something to say.
# Lowered to match rather than raised to accommodate, as the entries above.
# 119 -> 106 (BG0631/BG0636 wave): two shipped warnings started firing from inside library
# calls that most fixtures make in passing - the unverifiable-criteria report in
# `file_finding.file_finding()` and the unreadable-closure report in `critic.repair_state()`.
# They leaked 37 lines across 24 uncaptured call sites in ten modules, took a full run to 145,
# and turned CI red on main. Every one of the commits that added them passed this gate, because
# the hook runs a SELECTED subset and the check is an absolute `count <= baseline` - filed as
# BG0644, and the reason a leak now reaches main before anyone sees it. The sites are captured
# through the new `tests/quiet.py`, which yields the buffer rather than dropping it so a test
# that wants to assert on the diagnostic still can. Measured at 106 with the captures in place.
# Lowered to match rather than raised to accommodate, as every entry above. 106 is now the
# `_total` entry of the budget file; the scalar is no longer passed.
# 107 -> 106 (BG0637/BG0608/BG0654/BG0658 round two): the lane was RED on main again. Measured
# at 107 in a detached worktree at HEAD and at 107 with this round's change, so the extra line
# was pre-existing and the gate had been enforcing nothing since it arrived. `test_cli_record`
# in test_critic.py was letting `critic.py record` print the line naming what it wrote with
# nothing capturing stdout; capturing it and ASSERTING on it takes the run back to 106 and
# gives the test the half a return code cannot carry. test_critic's entry is lowered 3 -> 1 to
# match what it now leaks alone, rather than left over-declared. Lowering it to 1 then put the
# SELECTED run one line over its own sum - the bound this file already states, a module's
# overrun masked by a sibling's slack - so test_critic's last leak was captured as well: an
# escalation fixture whose deliberately-narrow Affects made the filer note it, 0 now. That
# STILL left the selected run one over, so every module was measured alone against its entry -
# 129 of them - and exactly one was over: test_mutation, leaking the `WITHDREW` line from the
# refusal remedy it runs as printed, with an entry of 0. Captured and asserted on. Whatever the
# masking, a per-module sweep is what settles it; the sum alone cannot. `_total` follows the
# three captures down, 106 -> 104.
if [ -n "${mods:-}" ]; then
  # shellcheck disable=SC2086
  printf '%s\n' "$out" | python3 "$(dirname "$0")/test_noise.py" --budget "$budget" --select $mods
else
  printf '%s\n' "$out" | python3 "$(dirname "$0")/test_noise.py" --budget "$budget"
fi
