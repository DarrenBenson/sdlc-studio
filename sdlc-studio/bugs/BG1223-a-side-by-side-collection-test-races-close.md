# BG1223: A side-by-side collection test races close against the pool's pickup and reds main on GitHub CI

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1223.md
> **Evidence:** GitHub Actions run 41911840410 on 6c3209cb, job ci, test_verify_ac.py line 3536.
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T07:08:42Z

## Summary

2026-11-05, the Lint run on 6c3209cb (run 41911840410). `StampsCollectSideBySideTests.test_with_no_server_each_file_gets_a_collection_of_its_own` submits a.py and b.py and calls close at once through the `_side_by_side` helper. `_SideBySideCollection.close` shuts the pool down with `cancel_futures`=True, which by design drops a collection not yet begun, so when the worker has not picked up b.py before close, b.py is never collected and the assertion reads ['a.py'] against ['a.py', 'b.py']. It passed locally and on the gate host and failed on the CI runner. The test is wrong, not close.

## Steps to Reproduce

1. Run the test under load, or with a delay in `_SideBySideCollection._collect` before it starts.
2. It fails with Lists differ: ['a.py'] != ['a.py', 'b.py'].

## Proposed Fix

In the `_side_by_side` helper, wait for every queued collection (the futures in `_COLLECT_PENDING`) before calling close, so the test judges collection and not thread start-up. Leave close's documented cancel behaviour as it is.

## Acceptance Criteria

- [ ] **AC1** The test passes when every collection is delayed by 0.5 s before it begins, and still fails when close collects nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampsCollectSideBySideTests

## Impact

Main's GitHub CI is red, so every push must acknowledge a red run, and the test fails at random on a slow host.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
