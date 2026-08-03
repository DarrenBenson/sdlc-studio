# BG0489: the commit-msg suite verdict is written before the tool-tests lane runs, so a green verdict survives its failure

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/commit-msg, tools/tests/test_commit_msg_hook.py
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional

## Summary

BG0423 moved the fail-open rather than closing it. In `.githooks/commit-msg` the verdict write and the failure-log write both sit BEFORE `run "tool-tests"`. So when skill-tests passes and tool-tests FAILS, the hook records `suite-verdict status=green`, blocks the commit, and writes no `gate-suite-last.log`.

`gate.suite_decision` then reuses that green verdict on a byte-identical retry and SKIPS both lanes - which is exactly the mechanism BG0423 documents. AC2's Given is 'a commit blocked on a suite lane', and the tool-tests lane is one.

Reproduced with the hook's own control flow and both lanes stubbed: skill-tests ok -> RECORDED suite-verdict status=green; tool-tests FAIL -> Commit blocked; no gate-suite-last.log written.

## Steps to Reproduce

1. Stub the two lanes in a copy of .githooks/commit-msg: skill-tests exits 0, tool-tests exits 1.
2. Run the hook. Observe `RECORDED suite-verdict status=green` and `Commit blocked` together, and no gate-suite-last.log.
3. Retry byte-identically: `gate.suite_decision` reuses the green and skips both lanes.

## Proposed Fix

Move the verdict and log writes AFTER the last suite lane, so the recorded verdict describes every lane that ran. Pin it with a test that stubs tool-tests to fail and asserts no green verdict is written - BG0423's own verifiers are source-text greps over the hook and execute nothing, which is why this survived.

## Narrowed at delivery

The CODE half was already fixed. `53107b9b` (2026-08-02 23:23, "three stop-ship defects the
closing review found") moved the verdict write below the tool lane, ten hours after this bug was
filed at 13:37 the same day. Verified by execution rather than by reading the hook: with the tool
lane failing, the shipped hook writes no verdict at all.

What was NOT delivered is the half this bug's own Proposed Fix asks for, and it is the half that
matters - **every existing test of this guard is a `text.index` grep over the hook's source.**
`SuiteVerdictFailOpenTests` asserts the guard's presence and the write's position in the file; it
executes nothing. That is exactly why the defect survived one repair and then recurred in a
different position: a grep for `if [ "$fail" -eq 0 ]` was green on both broken shapes.

So this unit delivers the executing test, and the criteria below are written against that.

## Acceptance Criteria

- [x] **AC1: a failing tool lane leaves no verdict behind, proven by running the hook.**
  - **Given** a fixture repo whose skill lane passes and whose tool lane is a real red unittest
    module, discovered the way the hook discovers it
  - **When** `.githooks/commit-msg` is executed against it
  - **Then** the commit is blocked AND no `gate-suite-verdict.json` exists, so the byte-identical
    retry has nothing to reuse
  - **Verify:** python3 -m unittest discover -s tools/tests -p test_commit_msg_hook.py -k test_a_failing_tool_lane_writes_no_green_verdict
  - **Verified:** yes (2026-08-03)

- [x] **AC2: the control case records a green verdict, so the refusal is not satisfied by a hook that records nothing.**
  - **Given** the same fixture with the tool lane passing
  - **When** the hook runs
  - **Then** it exits zero, the output shows the tool lane reached, and a `green` verdict is
    written - which is also what proves the fixture is not vacuous
  - **Verify:** python3 -m unittest discover -s tools/tests -p test_commit_msg_hook.py -k test_the_control_case_records_a_green_verdict
  - **Verified:** yes (2026-08-03)

## Verification evidence

Functional. Both mutants executed against the shipped hook, `__pycache__` purged and re-run under
`python3 -B`, hook restored byte-identical afterwards (`git diff` empty):

| Mutant | Result |
| --- | --- |
| hoist the `--record-suite-verdict` block above `run "tool-tests"` - BG0489's exact shape | killed by AC1 |
| disable the `--record-suite-verdict` call | killed by AC2 |

**Honest scope of the addition.** The first mutant is also caught by the existing source-order
grep, so on today's hook the two overlap. The executing test earns its place on the mutants the
grep cannot see - any change that keeps the file's text order while altering when the write runs -
and on the fact that it asserts the artefact a later commit actually reads rather than the text
that is meant to produce it. It is not claimed to catch strictly more than the greps today.

## Impact

A commit blocked by the tool-tests lane leaves behind a GREEN verdict at that HEAD. The next byte-identical attempt reads it and skips both suites, so a red tree can be committed on the strength of a verdict recorded before the failing lane ran. This is the precise fail-open BG0423 was filed to close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
