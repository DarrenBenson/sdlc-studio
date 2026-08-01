# EP0195: The claim inventory runs at delivery, where a stale sentence costs seconds instead of a review round

> **Status:** Draft
> **Derived Point Total:** 13
> **Parent:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0517. Delivers the work CR0517 requested.

## Story Breakdown

- [ ] [US0583: A staged diff changing a literal while its own prose still states the old value is flagged, naming both sites, and a diff whose prose agrees produces no finding](../stories/US0583-a-staged-diff-changing-a-literal-while-its.md)
- [ ] [US0584: A criterion ticked in a diff whose named surface that diff does not touch is flagged, and one whose surface it does touch is not](../stories/US0584-a-criterion-ticked-in-a-diff-whose-named.md)
- [ ] [US0585: The claim-drift lane runs in the commit gate as advisory, and its yield over one sprint is recorded before any decision to make it block](../stories/US0585-the-claim-drift-lane-runs-in-the-commit.md)

## Acceptance Criteria (Epic Level)

- [ ] A staged diff that changes a numeric or symbolic literal while its own prose in the same diff still states the old value is flagged, naming both sites - proven against BG0413's exit 2/3 pair
- [ ] A criterion ticked `[x]` in a diff whose named surface that diff does not touch is flagged - proven against BG0460's two ticks over a byte-identical story
- [ ] A diff whose prose and code agree produces NO finding, so the lane cannot be satisfied by one that always fires
- [ ] The lane reports and does not block on first ship, and its yield over one sprint is recorded before any decision to make it blocking
- [ ] Replayed over the RUN-01KYX375 diffs, the lane names the three findings the review rounds cost three passes to find

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
