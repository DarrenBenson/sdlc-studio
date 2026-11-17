# EP0352: CI and the push gate give one verdict on the skill suite because both run it the same way

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0712
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0712. Delivers the work CR0712 requested.

## Story Breakdown

- [ ] [US1263: CI runs the skill suite through the push gate's own pytest plan, under coverage, so a test green at push is green in CI](../stories/US1263-ci-runs-the-skill-suite-through-the-push.md)
- [ ] [US1264: The green-run noise gate has one implementation that CI and the push both read, and the second copy is retired](../stories/US1264-the-green-run-noise-gate-has-one-implementation.md)

## Acceptance Criteria (Epic Level)

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-010 describes cannot recur there: RUN-01M3VF2J on US0977; RUN-01M7GEHM on BG1489.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-010 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
