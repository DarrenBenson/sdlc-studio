# BG0595: one commit-msg hook test runs against the real repository, so it consumes the developer's gate handoff and starts a full suite inside a unit test

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/tests/test_commit_msg_hook.py, .githooks/commit-msg, tools/tests/test_precommit_lane_order.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

`tools/tests/test_commit_msg_hook.py:131` invokes the hook with no argument, no `cwd` and no
`env`:

`r = subprocess.run(["bash", str(HOOK)], capture_output=True, text=True)`

so it runs against the REAL repository the test process is sitting in. With no message file
`check_message` is 0, so the hook skips the message rules entirely and falls through to the
handoff block at line 179, reads `$GIT_DIR/sdlc-gate-suites` from the developer's own git
directory, deletes it, and runs the full lane set - inside a unit test. Every other test in the
file builds a throwaway repo under `tempfile` and scrubs `GIT_DIR`, `GIT_WORK_TREE` and
`GIT_INDEX_FILE`; this one does neither.

The production half is narrower than the test half and is still real: an invocation carrying NO
readable message file has no commit to gate, so entering the suite-running block is work nobody
asked for, whoever made the call.

WHAT THIS BUG DOES NOT CHANGE, because it is deliberate and recorded. The hook leaves the handoff
in place when it REFUSES a message, and `.githooks/commit-msg` says why at that exit: "Left where
it is: the retry runs pre-commit again, which rewrites the record from the index as it stands
then." An earlier cut of this bug proposed deleting the record on every exit path. That would have
broken a documented design for a defect it does not cause.

CORRECTION, twice, recorded rather than quietly dropped. Filed 2026-08-18 claiming the trigger was
a DIRTY WORKING TREE - `25 passed in 1.84s` with 14 uncommitted paths says otherwise. Re-filed
2026-08-19 claiming the trigger was a record surviving a REFUSED message - true, but that is the
recorded design, and it is not what makes a test run the suite. The trigger is one test that never
leaves the real repository. Both wrong readings were reached by reasoning from the code rather than
running it; the right one came from planting a record and timing the suite.

## Steps to Reproduce

Measured 2026-08-19 at 05ccd081.

1. Clean: `python3 -m pytest tools/tests/test_commit_msg_hook.py -q` reports `25 passed, 10
   subtests passed in 1.84s`, exit 0. A dirty working tree changes nothing - 14 uncommitted paths
   were present for that run.
2. Plant the record the hook consumes: `printf 'precommit_seconds=1
' > .git/sdlc-gate-suites`.
3. Re-run the same file. It does not complete within 120s, and `.git/sdlc-gate-suites` is GONE -
   the unit test consumed the real repository's record and entered the lane block behind it.
4. The path: `test_no_argument_does_not_block` (line 131) passes neither `cwd` nor `env`, so
   `git rev-parse --git-path` resolves inside the developer's repository. `check_message` is 0
   because no message file was given, so both `exit 1` message refusals are skipped and control
   reaches line 179.

Positive control for the fix: with the record planted, the run must still finish in seconds.

## Proposed Fix

Run the hook against a throwaway git repository rather than the one under development, as the sibling hook tests do, or set the environment the lane reads so `repo-writes` is scoped to a fixture. The bar is that the test's result must not change when a developer has unrelated uncommitted work. Check the other tests in this file for the same coupling before assuming it is the only one - a non-hermetic test that fails only during delivery is one people learn to ignore, which is worse than not having it.

## Acceptance Criteria

- [ ] **AC1** Given an `sdlc-gate-suites` record planted in the repository the test process runs in, when the commit-msg hook tests run, then their verdict and their wall-clock duration are unchanged from a run with no such record - the test PLANTS the record rather than depending on what the developer's git directory happens to hold
- [ ] **AC2** Given both of those runs, when they are compared, then BOTH are green - equality reached by making the record-absent run red too is not the property this asks for, and this is the control that says so
- [ ] **AC3** Given an invocation of the hook carrying NO readable message file, when it runs, then it exits before the suite-running block: there is no commit to gate, so running the lanes is work nobody asked for. The condition is the ABSENT MESSAGE and never the identity of the caller - the hook must not learn to recognise a test, which is the second bypass `NoSecondBypassTests` exists to forbid
- [ ] **AC4** Given every test in `test_commit_msg_hook.py`, when it invokes the hook, then it passes an explicit `cwd` and an environment with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` removed - `test_no_argument_does_not_block` passes neither today, and one exemption in twenty-five is the whole defect
- [ ] **AC5** Given the full suite run twice, once with the record planted in the real git directory and once without, when the two verdicts are compared OUTSIDE the suite with each exit code read from `$?` on its own line and never through a pipe, then they are identical and any test whose result differs is NAMED

## Impact

A unit test that reaches outside its fixture is not measuring the product, and this one
reaches into the developer's own git directory: it consumes a one-shot record another
commit was going to use, and then runs the full lane set - 1.84s becomes minutes, inside a
file whose other twenty-four tests are hermetic. The record it eats was left deliberately
for a retry, so the commit that was going to consume it now pays a second full gate.

The production half matters beyond the test: any invocation carrying no message file has no
commit to gate, and running the lanes for it is work nobody asked for. The hook cannot tell
a test from a person and must not try (`NoSecondBypassTests` exists to forbid exactly that),
so the condition to check is the absent message, not the caller.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `commit-msg`, remove the early exit for an invocation carrying no message file | Given an `sdlc-gate-suites` record planted in the repository the test process runs in, when the commit-msg hook tests run, then their verdict and their wall-clock duration are unchanged from a run with no such record - the test PLANTS the record rather than depending on what the developer's git directory happens to hold |
| AC2 | in `commit-msg`, raise a failure whenever no record is present | Given both of those runs, when they are compared, then BOTH are green - equality reached by making the record-absent run red too is not the property this asks for, and this is the control that says so |
| AC3 | in `commit-msg`, move the message-absent exit below the handoff block | Given an invocation of the hook carrying NO readable message file, when it runs, then it exits before the suite-running block: there is no commit to gate, so running the lanes is work nobody asked for. The condition is the ABSENT MESSAGE and never the identity of the caller - the hook must not learn to recognise a test, which is the second bypass `NoSecondBypassTests` exists to forbid |
| AC4 | unnameable: no change to production can falsify a rule about `test_commit_msg_hook.py`'s own harness - that each invocation supplies a cwd and a scrubbed environment - and the behaviour it protects is pinned by AC1 | Given every test in `test_commit_msg_hook.py`, when it invokes the hook, then it passes an explicit `cwd` and an environment with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` removed - `test_no_argument_does_not_block` passes neither today, and one exemption in twenty-five is the whole defect |
| AC5 | in `commit-msg`, revert the handoff read to run before the message-file check | Given the full suite run twice, once with the record planted in the real git directory and once without, when the two verdicts are compared OUTSIDE the suite with each exit code read from `$?` on its own line and never through a pipe, then they are identical and any test whose result differs is NAMED |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Criteria re-pointed by adversarial goal review: evidence taken outside the instrument under repair, and the enumerated case generalised to its class |
| 2026-08-19 | sdlc-studio | Premise CORRECTED: a dirty tree does not reproduce; the trigger is a one-shot record left behind by a REFUSED commit message, and the consequence is a nested full-suite run inside a unit test |
| 2026-08-19 | sdlc-studio | Scope widened to `.githooks/commit-msg` and re-pointed 2 -> 3: the corrected premise puts the defect in the hook's exit paths, not only in the test |
| 2026-08-19 | sdlc-studio | Premise corrected a SECOND time, by execution: the trigger is one non-hermetic test (line 131, no cwd and no env), not a record surviving a refusal - which is deliberate and documented at the hook's own exit |
