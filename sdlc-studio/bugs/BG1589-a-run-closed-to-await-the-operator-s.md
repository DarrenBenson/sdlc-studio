# BG1589: A run closed to await the operator's signature is stamped 'closed running' on reviews/LATEST.md, because the anchor prints the raw outcome the record keeps until sign seals it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_seals_once.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Close of RUN-01M7NTY5, 2026-11-18; sdlc-studio/reviews/LATEST.md close-status block.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T10:26:05Z

## Summary

Since D0503 (US1290) a closed run keeps outcome 'running' and no `ended_at` until `sprint sign` seals it. `anchor_status_block` in sprint.py prints that outcome verbatim, so the close of RUN-01M7NTY5 stamped '> **RUN-01M7NTY5 closed running.**' on the page every fresh session reads first. The owed-signature sentence beside it is right; the outcome word contradicts it and hides the goal verdict (partial) the close recorded.

## Steps to Reproduce

Close a run under the deferred-signature default (D0503) and read the close-status block of sdlc-studio/reviews/LATEST.md: it reads 'closed running'.

## Proposed Fix

Stamp an awaiting run as 'closed, awaiting signature' with the recorded goal verdict, and pin it with a test beside the signed case.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Since D0503 (US1290) a closed run keeps outcome 'running' and no `ended_at` until `sprint sign` seals it.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Close a run under the deferred-signature default (D0503) and read the close-status block of sdlc-studio/reviews/LATEST.md: it reads 'closed running'.
- [ ] **AC3** The proposed fix lands, pinned by a test: Stamp an awaiting run as 'closed, awaiting signature' with the recorded goal verdict, and pin it with a test beside the signed case.

## Impact

The anchor tells the next session a closed run is still running, in the one file it is ordered to read first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
