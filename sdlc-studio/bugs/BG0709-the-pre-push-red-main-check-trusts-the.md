# BG0709: the pre-push red-main check trusts the forge's ordering, so a stale first row demands acknowledgement of a two-month-old red

> **Status:** Open
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

- [ ] **AC1** The behaviour described is corrected: The hook reads the latest push-triggered Lint run with `gh run list --workflow Lint --branch main --event push --status completed --limit 1` and trusts element...
- [ ] **AC2** The proposed fix lands, pinned by a test: Judge recency rather than position: request several rows with createdAt, take the newest by that field, and refuse to read a row older than the local HEAD's...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Filed |
