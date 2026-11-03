# BG1191: The batch's phase plugin reads serial_only before a conftest's own trylast hook, so a mark that hook applies runs on an xdist worker

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py, changelog.d/BG1191.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** US1112 round-2 verdict, scratchpad run5/US1112-verdict-r2.txt, the trylast conftest fixture.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T10:03:36Z

## Summary

2026-11-03, US1112's round-2 review (qa-seat-US1112-r1, APPROVE, non-blocking). The verify batch splits its phases with a `-p` plugin whose `trylast` collection hook reads each test's `serial_only` mark (`verify_ac.py`:1838-1869). Its comment and changelog.d/US1112.md:18 say a mark a conftest hook or a project plugin applies counts. A conftest hook that is itself `@pytest.hookimpl(trylast=True)` and marks a test `serial_only` runs after the batch's hook: the reviewer's fixture gave phases ('parallel',) and the test ran on worker gw0. The verdict still comes from a real run, so no criterion reads vacuous, but the serial isolation the mark asks for is lost. No conftest in this repository applies `serial_only.`

## Steps to Reproduce

1. A fixture project whose conftest has `@pytest.hookimpl(trylast=True)` on `pytest_collection_modifyitems`, adding `serial_only` to `test_late.`
2. Run the verify batch over a Verify line naming `test_late` with pytest-xdist installed.
3. The batch runs only the parallel phase and `test_late` runs on an xdist worker.

## Proposed Fix

Read the mark in a hookwrapper around `pytest_collection_modifyitems`, after every implementation has run, or narrow the comment and the changelog to hooks that are not themselves trylast.

## Acceptance Criteria

- [ ] **AC1** A `serial_only` mark that a conftest's own trylast `pytest_collection_modifyitems` applies puts the test in the batch's serial phase.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py

## Impact

A project that marks a test `serial_only` from a late hook gets it run beside other tests in the batch, which is the isolation the mark exists to prevent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
