# BG0709: the pre-push red-main check trusts the forge's ordering, so a stale first row demands acknowledgement of a two-month-old red

> **Status:** Fixed
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), DELIVERED
> **Verification depth:** functional (US0881 AC4's test drives the real .githooks/pre-push against a stub forge that answers a stale red first and green on the re-read, and the push is not refused; fixed in commit 8daaa2fe)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_hook.py
> **Evidence:** RUN-01M2JA6J, 2026-09-16: the refusal text, the three repeats of the query, and gh run view 30118629592 showing workflow 224575266, event push, branch main, conclusion failure, created 2026-07-24T18:52:43Z.
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The hook reads the latest push-triggered Lint run with `gh run list --workflow Lint --branch main --event push --status completed --limit 1` and trusts element zero to be the newest (.githooks/pre-push:50). It carries no recency check. On 2026-09-16 at 10:41 UTC that call returned run 30118629592, a FAILURE from 2026-07-24, while the actual latest was 35072343530 (success, 2026-09-16T08:10:29Z, same workflow id 224575266); three repeats of the identical query seconds later all returned the correct row, so the API's ordering is eventually consistent rather than guaranteed. Two harms, and the second is the serious one. The push is refused over a run nobody needs to read. And the printed remedy - `SDLC_PUSH_ACK_RED=30118629592 git push` - writes that id into sdlc-studio/.local/push-ack.json as the acknowledged red, so a clone can record having read a red that is not the current one, and the next genuinely red main is the one nobody is made to read. D0181's whole point is that a red main is read before the next push.

## Steps to Reproduce

1. Push while the forge returns a stale first row (observed 2026-09-16T10:41Z; the run output is in this bug's evidence). 2. The hook refuses, naming run 30118629592 from 2026-07-24. 3. Re-run the same gh query: it returns 35072343530, success. 4. Push again: the hook passes, with nothing acknowledged and nothing wrong with main.

## Proposed Fix

Judge recency rather than position: request several rows with createdAt, take the newest by that field, and refuse to read a row older than the local HEAD's own push as the state of main. A row whose createdAt is older than the newest row in the same answer is a stale page, and a stale page must read as UNREAD - which the hook already handles safely - never as a red to acknowledge. The acknowledgement path should also refuse an id that is not the newest row, so a stale id can never be banked.

## Acceptance Criteria

- [x] **AC1** The behaviour described is corrected: The hook reads the latest push-triggered Lint run with `gh run list --workflow Lint --branch main --event push --status completed --limit 1` and trusts element...
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read
  - **Verified:** yes (2026-09-24)
- [x] **AC2** The proposed fix lands, pinned by a test: Judge recency rather than position: request several rows with createdAt, take the newest by that field, and refuse to read a row older than the local HEAD's...
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read
  - **Verified:** yes (2026-09-24)

Both are met by US0881 AC4 (commit 8daaa2fe), which took a different shape from the proposed fix: a
red answer is re-read once before the hook refuses, and the second answer is judged, so a stale
first row no longer refuses a push. Its test above is the verification of this fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): DELIVERED - fixed at HEAD by US0881 AC4 (commit 8daaa2fe: a red answer is re-read, the second judged); planning ruled it SUPERSEDED, but the fix shipped, so it moves to Fixed |
