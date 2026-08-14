# BG0579: the per-commit gate has outgrown the tool timeouts that run it, so a commit is KILLED rather than refused - and a kill reads as a hang, which invites --no-verify

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/run-suite.sh, tools/gate_timing.py, tools/tests/test_gate_timing.py
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

- [ ] **AC1** The behaviour described is corrected: The selected gate now costs 590-617s against a declared 380s budget, and the hook itself reports OVER on every commit.
- [ ] **AC2** The proposed fix lands, pinned by a test: The selection is not the defect - it is correct, and a change to a hub module genuinely reaches most of the suite.

## Impact

Every commit touching shared surface. The gate is this repository's primary control and its own doctrine says a guard whose cost is paid on every commit gets switched off - this is that sentence coming true, measured. The immediate harm is not a wrong verdict but a MISSING one: a killed run records nothing, so nothing downstream can tell a commit that was never gated from one that passed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-14 | sdlc-studio | Filed |
