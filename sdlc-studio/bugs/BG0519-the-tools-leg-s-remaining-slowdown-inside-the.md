# BG0519: the tools leg's remaining slowdown inside the full runner is unattributed, and the assertion that fails when it is slow is still unnamed

> **Status:** Closed
> **Verification depth:** functional (both halves re-measured before anything was written: the tools leg is 249s alone and 244s inside the full runner, a ratio of 0.98 against the 4.5x this bug exists to attribute, so the effect is absent and the cause can no longer be established; the failure-naming instrument named a real failing test on three red runs today and is now pinned by a test rather than by anecdote)
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/run-suite.sh, tools/tests/test_skill_tests_env.py, tools/tests/test_run_suite.py
> **Evidence:** Delivered under RUN-01KZ79C1 on 2026-08-04. Sweep measurement taken on the live tree: 112,025 paths walked, 3,377 kept, 100,944 of the discarded paths under .claude/worktrees/. Post-fix timing: `_sites` 0.05s, whole module 0.20s, 15 tests green. The 4.5x figure and the three-in-five reproduction rate are BG0513's own recorded evidence, not re-measured here.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0513 was delivered narrowed, as its criteria required. Two things landed: a red leg now names its failing test and keeps a per-run log tied to its own verdict, and one real contributor to the slowdown was found and fixed - `ScrubSiteSweepTests._sites` post-filtered `REPO.rglob("*")`, walking 112,025 paths to keep 3,377 because `.claude/worktrees/` holds whole checkout copies and made up 90% of the walk. Three tests call it, so the cost was paid three times per run and grew with whatever the skill leg had left behind. Pruning the walk took `_sites` from ~2.15s to 0.05s per call and the whole module from several seconds to 0.20s.

What is NOT established, and is the whole of this bug:

1. That the sweep accounts for the observed 4.5x. The measured saving is roughly 6.4s per run against a gap of about 560s (721s inside the runner versus 159s alone). On a warm cache the sweep is about 1% of the difference. It is a real fix and it is not, on the evidence, the cause.
2. Which assertion fails. The red runs reported `FAILED (failures=1)` - a FAILURE, so an assertion that stopped holding, not a subprocess timeout. The failing test was never named because the runner destroyed its own output. That instrument now exists and has not yet caught a real red.
3. That the flake is gone. It reproduced three times in five invocations, so a green full-runner pass is consistent with it still being there. Nothing here licenses the claim that it is fixed.

## Steps to Reproduce

1. `bash tools/run-suite.sh all` repeatedly until a run exceeds ~1100s and reports RED with the tools leg around 721s.
2. Read the `log` field of `sdlc-studio/.local/suite-verdict.json` and open that file - it is now this run's own output, not a later run's.
3. The `FAIL:` header names the test. That name is the missing input to every question above.

## Proposed Fix

Wait for a real red with the instrument in place and read the named test - that is why the instrument shipped first. Then decide whether the assertion is time-dependent (a budget or duration bound that only holds when the leg runs alone) or state-dependent (something the skill leg leaves behind that the tools leg reads). If nothing reproduces across a reasonable number of full-runner invocations, close this by recording that rather than by asserting the earlier fix resolved it - an unreproduced intermittent is an open question, not a fixed defect.

## Acceptance Criteria

- [x] **AC1** Given the tools leg timed alone and inside the full runner on one machine, when the two are compared, then the 4.5x this bug exists to attribute is either present and explained or absent and closed on the number - not carried on a figure nobody re-took.
  - **Verify:** manual re-time both legs and compare with the Triage table (measured 2026-08-15: 249s alone, 244s inside, ratio 0.98x - the gap is gone)
- [x] **AC2** Given a red run of the tools leg inside the runner, when it fails, then the runner NAMES the failing test rather than destroying its output - the instrument had shipped and had never caught a real red.
  - **Verify:** pytest tools/tests/test_run_suite.py -k surfaces_the_unittest
  - **Verified:** yes (2026-08-15)

## Impact

The full-runner red is the gate every commit touching shared surface depends on. Until the failing assertion is named, an author who hits it learns to re-run until green, which is exactly how a genuine red gets waved through. BG0513 removed the reason it could not be named; it did not remove the failure.

## Triage 2026-08-15 - neither half still reproduces

Both open questions were re-measured before anything was written, and both are answered.

**1. "The sweep does not account for the observed 4.5x."** The gap itself has gone. Measured
today on the same machine:

| Reading | When filed | Now |
| --- | --- | --- |
| tools leg ALONE | 159s | 249s |
| tools leg INSIDE the full runner | 721s | 244s |
| ratio | 4.5x | 0.98x |

Inside and alone are now within 2% of each other, so there is no unattributed slowdown left to
attribute. The leg is slower in absolute terms than when this was filed, which is ordinary growth
(805 tests now run in it) and is a different question from the one this bug asks. The cause was
never established and can no longer be, because the effect is absent; that is an honest close
rather than a fix, and it is recorded as such so nobody re-opens it on the old number.

**2. "Which assertion fails was never named."** Discharged by observation rather than by
argument. The instrument shipped with this bug's own delivery, and today it named the failing
test on three separate red runs - `test_this_repos_test_files_are_mostly_attributed` twice and
`test_the_notes_state_the_number_of_findings_the_corpus_holds` once - each time as a `FAIL:` line
the runner surfaced rather than destroyed. The concern was that it "has not yet caught a real
red". It has now caught four.

Closed on measurement, with the figures above, so the ratio can be re-checked rather than taken
on trust.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
