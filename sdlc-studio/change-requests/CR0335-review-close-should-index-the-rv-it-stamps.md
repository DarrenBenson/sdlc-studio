# CR-0335: review close should index the RV it stamps and name the commit remedy when the anchor is uncommitted

> **Status:** Complete
> **Decomposed-into:** EP0072
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Two seams in the review close at RUN-01KXPJG9: (1) `review_prep` close stamps state and derives LATEST from the RV record but leaves the RV without an index row - the close chain's reconcile caught it as drift and the ceremony stopped a full round for a mechanical fix reconcile apply then performed anyway; ensure the row at close (reuse the index helper). (2) gate's review-current lane reads git COMMIT time, so a freshly derived but uncommitted LATEST.md still reads stale and the remedy says 'run review' - the honest remedy in that state is 'commit the close paperwork'; detect the dirty-anchor case and name it.

## Impact

Both seams stop the close chain with a misleading or unnecessary round-trip; the wrong remedy ('run review' when the review exists uncommitted) sends an agent to redo finished work.

## Acceptance Criteria

- [ ] `review_prep` close ensures the RV's index row exists (reconcile finds no missing-row afterwards)
- [ ] review-current distinguishes an uncommitted-but-current anchor and names the commit remedy

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
