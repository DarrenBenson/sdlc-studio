# EP0264: The record informs the work: goals trace to the PRD, and briefs carry the history and constraints of the files they touch

> **Status:** Draft
> **Derived Point Total:** 21
> **Parent:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0594. Delivers the work CR0594 requested.

## Story Breakdown

- [x] [US0927: A sprint plan names the PRD outcome or persona its goal serves, and flags a goal that serves none](../stories/US0927-a-sprint-plan-names-the-prd-outcome-or.md)
- [x] [US0928: The seat reviewing a Sprint Goal is shown the PRD outcomes and the personas' End goals](../stories/US0928-the-seat-reviewing-a-sprint-goal-is-shown.md)
- [ ] [US0929: The PRD describes the lean product and lists the outcomes a Sprint Goal can serve](../stories/US0929-the-prd-describes-the-lean-product-and-lists.md)
- [ ] [US0930: A reviewer's brief lists the recent Done units that changed each file the unit touches, with the defects their reviews found](../stories/US0930-a-reviewer-s-brief-lists-the-recent-done.md)
- [ ] [US0931: A build lane's brief carries the same file history, and tells the author that history outranks an artefact's account](../stories/US0931-a-build-lane-s-brief-carries-the-same.md)
- [ ] [US0932: A build lane's brief carries the TRD constraints of the components its unit touches](../stories/US0932-a-build-lane-s-brief-carries-the-trd.md)
- [ ] [US0933: The TRD and TSD stop restating lists and counts the code derives, and the tests that pinned the restatements are deleted](../stories/US0933-the-trd-and-tsd-stop-restating-lists-and.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a sprint plan whose goal names no PRD outcome or persona, then the plan flags it as serving none
- [ ] Given the PRD after the refresh, then it describes the lean loop (persona rulings, the one-page report, lesson classes) and no longer describes the retired learning loop as current
- [ ] Given a lane or critic brief for a unit, then it lists, for each file the unit touches, the most recent Done units that changed it with their review findings
- [ ] Given a TRD section on a component a unit touches, then the build brief carries its constraints; a TRD or TSD section nothing reads is cut

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
