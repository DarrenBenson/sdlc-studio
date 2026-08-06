# EP0207: A unit's test plan is written and reviewed before its code, because reviewing the test is cheaper than reviewing the code

> **Status:** Done
> **Derived Point Total:** 26
> **Parent:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0525. Delivers the work CR0525 requested.

## Story Breakdown

- [x] [US0629: a test plan is DERIVED from the unit's criteria by the tooling, naming per criterion the production change the test must fail on](../stories/US0629-a-test-plan-is-derived-from-the-unit.md)
- [x] [US0630: a unit reaching delivery without a reviewed test plan is REFUSED by the command that starts the work](../stories/US0630-a-unit-reaching-delivery-without-a-reviewed-test.md)
- [x] [US0631: the test plan is reviewed by an independent seat before the code, and that review is recorded like a code review](../stories/US0631-the-test-plan-is-reviewed-by-an-independent.md)
- [x] [US0632: at delivery each planned mutant is EXECUTED against the shipped test and its death recorded](../stories/US0632-at-delivery-each-planned-mutant-is-executed-against.md)
- [x] [US0633: a criterion whose mutant cannot be named is refused at grooming](../stories/US0633-a-criterion-whose-mutant-cannot-be-named-is.md)
- [x] [US0634: the cost is measured over one run and reported: passes spent on test-plan review versus on code review](../stories/US0634-the-cost-is-measured-over-one-run-and.md)

## Acceptance Criteria (Epic Level)

- [ ] A unit reaching delivery without a test plan is REFUSED by the command that starts the work, not reported at the close - the plan names, per criterion, the production change the test must fail on
- [ ] The test plan is reviewed as its own artefact by an independent seat BEFORE the code is written, and that review is recorded the way a code review is
- [ ] The plan is derived from the unit's acceptance criteria by the shipped tooling, not hand-authored, so a criterion cannot be silently missing from it
- [ ] At delivery, each planned mutant is EXECUTED against the shipped test and its death recorded - a plan that was written and never checked is the same paperwork problem one level up
- [ ] A criterion whose mutant cannot be named is refused at grooming, since nobody yet knows what would falsify it
- [ ] The cost is measured over one run and reported: passes spent on test-plan review versus passes spent on code review, so the claim that this is cheaper is a number rather than an assertion

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
