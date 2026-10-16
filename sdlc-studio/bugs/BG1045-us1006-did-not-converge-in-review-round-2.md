# BG1045: US1006 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_push_first_estimate.py, changelog.d/BG1045.md
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T11:00:55Z

## Summary

US1006 was rejected at round 2, the review cap, by qa seat (US1006 r1), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the repair of round-1's FIXED\_FIGURE finding is OVER-CLAIMED (tools/tests/test\_push\_first\_estimate.py:40-43): its comment and the commit message say it refuses any time unit "or a number carrying one", and the spelled-out and hour forms are now killed (five minutes, roughly fifteen minutes, about an hour, and the AGENTS.md rewordings), but a number glued to a unit word matches neither alternative - the first needs a word boundary before the unit, which a digit denies, and the second takes only a lone s, m or h - so "expect ~5min", "expect 300sec", "expect 10minutes" and "expect 2hrs" appended to the first-run line pass the AC1 test, and an AGENTS.md pre-push row reading "about 5min" or "about 1hr" passes the AC4 test (all six survive the module, and each was re-run alone with the mutant shown on disk), while the round-1 regex caught "~5min", "300sec" and "10minutes", so the repair lost reach the test had - widening the second alternative's unit to `(?:s/m/h/secs?/seconds?/mins?/minutes?/hrs?/hours?)` closes it; [pre-existing] BG1043 the cost line reads pytest-xdist by distribution metadata (tools/gate\_timing.py:219) while the full-suite lane decides by importlib.util.find\_spec("xdist") (gate.py:894) - round-1 finding 6's reading half, now filed and open, and its core-count half CLOSED: the line says "across this machine's cores (pytest-xdist, -n auto)" (tools/gate\_timing.py:239), TRUE against gate.py:2414 - round-1 rulings otherwise, each mutant re-executed against a passing control (8 passed) with the tree byte-identical after: the AC3 finding CLOSED (mean-for-median and a figure beside the floor both killed, and reverting the skewed series or the floor-line check lets each survive, so the new assertions carry the kill), the fallback finding CLOSED (deleting it or giving it a figure killed by test\_the\_hook\_falls\_back\_to\_a\_line\_without\_a\_figure), the history-guard finding CLOSED (killed by test\_first\_run\_is\_silent\_beside\_a\_recorded\_history), the module-count finding CLOSED (glob("*.py") killed through the fixture's conftest.py and \_helpers.py, and a TEST\_SUITE\_DIRS drift killed by test\_the\_counted\_directories\_are\_the\_gates), the docstring finding CLOSED (--help lists all four subcommands) - claim inventory: the SUITE\_DIRS comment "a test pins the two", the test docstring's MUTANTS list (every named mutant killed) and the unchanged changelog TRUE by execution, and the commit message's "Full push gate green on devserver1" UNVERIFIABLE, counted on trust

## Steps to Reproduce

1. Read the round 2 REJECT of US1006 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1006 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the repair of round-1's FIXED\_FIGURE finding is OVER-CLAIMED (tools/tests/test\_push\_first\_estimate.py:40-43): its comment and the commit message say it refuses any time unit "or a number carrying one", and the spelled-out and hour forms are now killed (five minutes, roughly fifteen minutes, about an hour, and the AGENTS.md rewordings), but a number glued to a unit word matches neither alternative - the first needs a word boundary before the unit, which a digit denies, and the second takes only a lone s, m or h - so "expect ~5min", "expect 300sec", "expect 10minutes" and "expect 2hrs" appended to the first-run line pass the AC1 test, and an AGENTS.md pre-push row reading "about 5min" or "about 1hr" passes the AC4 test (all six survive the module, and each was re-run alone with the mutant shown on disk), while the round-1 regex caught "~5min", "300sec" and "10minutes", so the repair lost reach the test had - widening the second alternative's unit to `(?:s/m/h/secs?/seconds?/mins?/minutes?/hrs?/hours?)` closes it
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_every_way_of_stating_a_duration_is_read_as_one
  - **Verified:** yes (2026-10-14)
- [ ] **AC2** US1006 AC1 still passes: Given a fixture clone with no recorded boundary run and no recorded full commit-suite run, when a branch push and then a tag push run the hook, then each cost line says no run is recorded on this clone and states no fixed number of minutes.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_no_fixed_duration_is_announced_without_a_recorded_run
  - **Verified:** yes (2026-10-14)
- [ ] **AC3** US1006 AC2 still passes: Given the same clone, when the push runs once with pytest-xdist hidden from python3 and once with it present, then the cost line says the suite runs serially in the first case and in parallel across the machine's cores in the second, naming the number of test modules each time.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_the_cost_line_reads_parallel_or_serial_from_the_interpreter
  - **Verified:** yes (2026-10-14)
- [ ] **AC4** US1006 AC3 still passes: Given a clone with no boundary-push series but a recorded `total` (full commit-suite) series, when a branch push runs the hook, then the cost line cites that series' median as a floor for this machine and still states no fixed figure.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_a_recorded_full_commit_suite_run_is_cited_as_a_floor
  - **Verified:** yes (2026-10-14)
- [ ] **AC5** US1006 AC4 still passes: Given AGENTS.md, when the pre-push row of its refusal table is read, then it states no fixed duration and names `gate_timing.py estimate --suite boundary-push`, and running that command from the repository root exits 0.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_agents_md_names_the_command_not_a_figure
  - **Verified:** yes (2026-10-14)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
| 2026-10-14 | Claude Opus 5.5 (author) | Groomed: the round-2 [pre-existing] item is BG1043's, open, and a review does not block on it, so its criterion is dropped; Affects narrowed to where the fix lands; joins the open run (operator ruling, as BG0950's carry) |
