# BG0507: the suite-collapse lane sets fail=1 after the green verdict is already written, so a collapsed suite is reusable

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Verification depth:** functional
> **Affects:** .githooks/commit-msg, tools/tests/test_commit_msg_hook.py, tools/tests/test_precommit_lane_order.py
> **Evidence:** Found by the independent boundary review of BG0489 (RUN-01KZ3V4D), demonstrated by execution against the shipped hook with a stubbed collapsing gate_timing.py: the hook exits 1 AND sdlc-studio/.local/gate-suite-verdict.json holds status green. The hook is byte-identical at the run base ref 130898ae, so this predates the run.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0489 moved the verdict write below both suite lanes, which closes the fail-open reached through a failing lane. It does not close the one reached through the COLLAPSE check: the scope guard that sets `fail=1` when the suite count collapses (rc 3) runs AFTER the verdict has already been written. So a run whose suite collapsed - the shape where far fewer tests ran than the surface demands - blocks the commit and still leaves `status green` at that HEAD.

`pre-commit` skips the suites when a current green verdict covers the surface, so the byte-identical retry can land the collapsed suite. This is the same fail-open family as BG0423 and BG0489, reached through the third door.

## Steps to Reproduce

1. Stub `tools/gate_timing.py` so the scope check reports a collapse (rc 3).
2. Run `.githooks/commit-msg` on a fixture whose two lanes both pass.
3. Observe: hook rc=1 (blocked), and `sdlc-studio/.local/gate-suite-verdict.json` holds `status: green`.
4. Retry byte-identically: the verdict is reused and the suites are skipped.

## Proposed Fix

Move the verdict write below the collapse check too, or make the collapse set `fail` before the write. The general shape is that the verdict must be the LAST thing a passing hook does - anything that can still set `fail` after it has been written re-opens this. Pin it with a test that executes the hook with a collapsing stub, on the same terms BG0489's test executes it with a failing lane, rather than a source-order grep.

## Acceptance Criteria

- [x] Executing `.githooks/commit-msg` with a `gate_timing.py` stub that reports a collapse (rc 3) leaves NO green verdict at that HEAD. Today the hook exits 1 and `sdlc-studio/.local/gate-suite-verdict.json` still holds `status: green`; after the fix the record is absent or not-green, checked by reading the file the next `pre-commit` would read
- [x] The byte-identical retry re-runs the suites rather than skipping them. Demonstrated end-to-end - collapse, retry, observe the suites execute - not by asserting on source order, because source order is what the current defect already satisfies
- [x] The mutant is the ordering: restoring the write to its position above the collapse check reddens the new test. Named before the test is written, and applied to prove it
- [x] BG0489's failing-lane test passes unchanged, so the third door is closed without reopening either of the first two
- [x] The verdict write is the last act of a passing hook by construction, not by inspection: any check that can still set `fail` sits above it, and the test that pins this fails if a new check is appended below

## Impact

A commit blocked by a suite collapse leaves a green verdict behind, and the next attempt over an unchanged surface reads it and runs no tests. The collapse check exists precisely because a run with far fewer tests than the surface demands is not evidence, and its refusal is currently undone by the record written above it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
