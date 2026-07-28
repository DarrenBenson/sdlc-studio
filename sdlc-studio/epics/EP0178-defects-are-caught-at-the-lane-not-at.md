# EP0178: Defects are caught at the lane, not at review: a unit arrives with its acceptance criteria already proven

> **Status:** Draft
> **Parent:** CR0458
> **Parent:** CR0459
> **Parent:** CR0461
> **Derived Point Total:** 36
> **Parent:** CR0463
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0463. Delivers the work CR0463 requested.

## Story Breakdown

- [ ] [US0508: A lane refuses to start on a unit that carries no acceptance criteria, naming it rather than inferring a contract](../stories/US0508-a-lane-refuses-to-start-on-a-unit.md)
- [ ] [US0509: A lane runs its unit's own acceptance criteria before returning, and a unit whose criteria do not pass comes back blocked](../stories/US0509-a-lane-runs-its-unit-s-own-acceptance.md)
- [ ] [US0510: A lane returns the proof the test strategy assigned to its unit, or states plainly that it could not and why](../stories/US0510-a-lane-returns-the-proof-the-test-strategy.md)
- [ ] [US0511: The lane obligations travel with the dispatch prompt, so they do not depend on who wrote that sprint's brief](../stories/US0511-the-lane-obligations-travel-with-the-dispatch-prompt.md)
- [ ] [US0512: A unit adding a mechanism carries an acceptance criterion naming the caller that consumes it](../stories/US0512-a-unit-adding-a-mechanism-carries-an-acceptance.md)
- [ ] [US0513: A unit whose mechanism has no caller yet says so explicitly and names the follow-up that completes it](../stories/US0513-a-unit-whose-mechanism-has-no-caller-yet.md)
- [ ] [US0514: A bug reaching a terminal status with no acceptance-criteria section is refused, as a story reaching Done already is](../stories/US0514-a-bug-reaching-a-terminal-status-with-no.md)
- [ ] [US0515: The existing AC-less units are baselined so the new rule blocks a new one without blocking on the backlog it reveals](../stories/US0515-the-existing-ac-less-units-are-baselined-so.md)
- [ ] [US0516: A filed finding carries acceptance criteria derived from its own evidence, so a lane has a contract to deliver against](../stories/US0516-a-filed-finding-carries-acceptance-criteria-derived-from.md)
- [ ] [US0517: A finding's Affects names where the fix will land rather than where the evidence was read, and includes the test file](../stories/US0517-a-finding-s-affects-names-where-the-fix.md)

## Acceptance Criteria (Epic Level)

- [ ] A lane refuses to start on a unit that carries no acceptance criteria, naming the unit, rather than inferring a contract from the summary.
- [ ] Before returning a unit, a lane runs that unit's own acceptance criteria and returns the result; a unit whose criteria do not pass comes back as blocked rather than as fixed.
- [ ] A lane returns the proof the plan's test strategy assigned to that unit, or states plainly that it could not and why, so an unmet obligation is visible at the lane rather than at the close (BG0358).
- [ ] For a unit that adds a mechanism, the lane confirms the caller named in its criteria actually reaches it (CR0461), so an inert mechanism is caught by the author rather than by a reviewer.
- [ ] The dispatch prompt carries these as obligations on the lane, so the checks travel with the work rather than depending on whoever wrote that sprint's prompt remembering them.

### From CR0461

- [ ] A unit that adds or changes a mechanism carries at least one acceptance criterion naming the CALLER that consumes it - the hook, the lane, the command - not only the function's own behaviour.
- [ ] A unit whose mechanism has no caller yet states that explicitly as consumer-only or producer-only, and names the follow-up that completes it, so the gap is recorded rather than implied.
- [ ] The Ready criteria and the story template say this in the place an author is looking when they write the criterion, not only in a lesson they would have to recall.
- [ ] The adversarial review prompt asks it directly - does this criterion describe a function nothing calls - so it is checked by the pass that has caught every instance so far.

### From CR0459

- [ ] A bug reaching a terminal status with no acceptance-criteria section is refused, as a story reaching Done already is.
- [ ] The existing instances are recorded as a baseline so the new rule blocks a new one without blocking on the backlog it reveals.
- [ ] The conformance sweep covers bugs for this stage rather than being story-scoped, so the two gates agree.

### From CR0458

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
