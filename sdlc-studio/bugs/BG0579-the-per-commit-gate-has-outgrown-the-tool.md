# BG0579: the per-commit gate has outgrown the tool timeouts that run it, so a commit is KILLED rather than refused - and a kill reads as a hang, which invites --no-verify

> **Status:** Fixed
> **Verification depth:** functional (profiled rather than guessed: 4 tests were 452s of 934s, and the largest was a boundary-only lane's test paid on every commit; measured 934s -> 569s in per-commit shape, with the deferred tests executing in full under the marker; mutation: 4 declared mutants, all KILLED - three SURVIVED on the first pass, including one where the check matched a commented-out line, and all three were re-chosen or the check strengthened; restore byte-exact)
> **Severity:** High
> **Points:** 5
> **Affects:** tools/run-suite.sh, .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/tests/boundary.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, tools/tests/test_boundary_marker.py, tools/tests/test_test_census.py
> **Evidence:** RUN-01KZQ03V, 2026-08-14. A commit carrying BG0553 and BG0552 was killed at 600s by the harness running it; re-running it detached succeeded in the same shape. Timings read from sdlc-studio/.local/gate-timings.json.
> **Created:** 2026-08-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-14T01:30:38Z

## Summary

The selected gate now costs 590-617s against a declared 380s budget, and the hook itself reports OVER on every commit. The skill suite is 483-524s of that; every other lane together is under 90s. On 2026-08-14 a commit exceeded a 600s tool ceiling and was killed mid-run: no refusal, no verdict, no record - just a dead process and a working tree that still had everything staged. The hook already anticipated this and mitigated it by ANNOUNCING the expected duration first, which does not stop a timeout from firing. A killed gate is indistinguishable from a hung one, and the documented escape from a hung gate is `git commit --no-verify` - so the failure mode actively trains the bypass, on the one guard the repository leans on hardest.

## Steps to Reproduce

1. Touch a hub module (`lib/sdlc_md.py`, `mutation.py`, `transition.py`) - selection correctly follows the import graph and reaches ~100 modules / ~5300 tests. 2. `git commit`. 3. Observe `gate-budget: OVER - 590s of a 380s budget [selected run]`. 4. Run the same commit under any 600s-ceiling wrapper: the process is killed with no output and no commit, and `git status` still shows everything staged. Measured 2026-08-14 from `sdlc-studio/.local/gate-timings.json`: skill-tests 483/485/490/495/520/524s over the last ten runs; total.selected 574-632s.

## Proposed Fix

The selection is not the defect - it is correct, and a change to a hub module genuinely reaches most of the suite. The cost is the suite's own wall-clock: ~5300 tests in ~500s on a 16-core machine, single-process. Options, in the order they should be considered: (a) run the skill suite in parallel - the machine has 16 idle cores and the suite is already process-isolated per module, so this is the only change that attacks the actual number rather than the reporting of it; (b) move the slowest lanes to the push boundary, where release-rehearsal already lives, and say so in AGENTS.md; (c) at minimum, make an exceeded budget a REFUSAL with a written verdict rather than something a timeout discovers, so a killed gate can never be mistaken for a hung one.

## Acceptance Criteria

- [x] **AC1** Given the boundary runner `tools/run-suite.sh`, when it is read, then it sets the boundary marker - the deferred tests must run somewhere, and this is the somewhere.
  - **Verify:** pytest tools/tests/test_boundary_marker.py -k boundary_runner_sets_the_marker
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given every command in CI that runs the suites, when the workflow is read, then each carries the marker - CI is the independent boundary, and a runner without it drops whatever is deferred in its tree.
  - **Verify:** pytest tools/tests/test_boundary_marker.py -k ci_sets_the_marker
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given any test deferred to the boundary, when the marker is read, then it carries a stated reason - what a reader of a per-commit run sees in place of the test, and what a reviewer judges the trade against.
  - **Verify:** pytest tools/tests/test_boundary_marker.py -k every_marked_test_carries_a_reason
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given the set of deferred tests, when it is counted, then it is non-empty and small - an unused marker is a mechanism that looks like coverage, and a growing one is a per-commit gate quietly becoming a subset nobody chose.
  - **Verify:** pytest tools/tests/test_boundary_marker.py -k marked_set_stays_small_and_named
  - **Verified:** yes (2026-08-14)

## Impact

Every commit touching shared surface. The gate is this repository's primary control and its own doctrine says a guard whose cost is paid on every commit gets switched off - this is that sentence coming true, measured. The immediate harm is not a wrong verdict but a MISSING one: a killed run records nothing, so nothing downstream can tell a commit that was never gated from one that passed.

## Resolution

Profiled rather than guessed, and the profile changed the fix. Parallelism was the obvious answer and the wrong one: four tests were **452s of a 934s run**, and the largest was `ReleaseRehearsalLaneTests` at **228s - 24% of the whole suite** - whose own docstring reads *"the rehearsal binds at the push and release boundaries and nowhere else"*.

**The lane was boundary-only and its test was not.** AGENTS.md says the rehearsal is off the per-commit path because the gate is already over its budget there; the test that exercises it was paying that cost on every commit, to measure something no commit can reach. That is this repository's recurring shape - a rule stated in one place and not applied to the thing that exercises it - and it means the repair is the existing boundary rule applied consistently, not a new mechanism.

Two tests are deferred: the rehearsal lane, and this run's own 15-verb `--root` control at 83s. Measured: the skill suite in per-commit shape falls from **934s to 569s, a 39% cut**, and nothing is removed - `run-suite.sh` and every CI command set the marker, so push, release, close and CI all execute them in full.

The blindfold is what gets guarded. `tools/tests/test_boundary_marker.py` asserts that the runner sets the marker, that every CI command does, that each deferral carries a reason, and that the marked set stays small - because a marker nobody honours is an exclusion with better manners, and this repository has twice shipped a lane believing it was enforced when it was not.

Writing that guard produced two false positives of its own, both worth recording: it first refused on a COMMENT mentioning `coverage run`, then on a YAML step NAME mentioning `skill-tests.sh`. A guard that cries wolf on prose is one whose real refusal gets waved through.

**Not fixed here:** the underlying arithmetic. ~5,300 tests still run single-process on a 16-core machine, and the remaining two heavy tests (74s and 67s) are ordinary integration tests with no boundary argument behind them. Parallelism would need `pytest-xdist`, which is a dependency change this repository's pure-stdlib policy puts to the operator.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/run-suite.sh, comment out the boundary export so every deferred test runs nowhere | Given the boundary runner `tools/run-suite.sh`, when it is read, then it sets the boundary marker - the deferred tests must run somewhere, and this is the somewhere. |
| AC2 | in .github/workflows/lint.yml, drop the marker from a CI runner | Given every command in CI that runs the suites, when the workflow is read, then each carries the marker - CI is the independent boundary, and a runner without it drops whatever is deferred in its tree. |
| AC3 | in tests/boundary.py, remove the reason floor so an unexplained deferral is accepted | Given any test deferred to the boundary, when the marker is read, then it carries a stated reason - what a reader of a per-commit run sees in place of the test, and what a reviewer judges the trade against. |
| AC4 | in tests/test_gate.py, remove every boundary marker so the mechanism guards nothing | Given the set of deferred tests, when it is counted, then it is non-empty and small - an unused marker is a mechanism that looks like coverage, and a growing one is a per-commit gate quietly becoming a subset nobody chose. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-14 | sdlc-studio | Filed |
