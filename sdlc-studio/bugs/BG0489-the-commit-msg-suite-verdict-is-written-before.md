# BG0489: the commit-msg suite verdict is written before the tool-tests lane runs, so a green verdict survives its failure

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/gate.py, tools/tests/test_run_suite.py
> **Severity:** High
> **Points:** 3

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

## Impact

A commit blocked by the tool-tests lane leaves behind a GREEN verdict at that HEAD. The next byte-identical attempt reads it and skips both suites, so a red tree can be committed on the strength of a verdict recorded before the failing lane ran. This is the precise fail-open BG0423 was filed to close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
