# CR-0463: A delivery lane returns without proving its own acceptance criteria, so basic AC failures survive to review

> **Status:** In Progress
> **Decomposed-into:** EP0178
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised: trim review by finding issues in-sprint); agent; skill v5.0.0

## Summary

A lane writes tests, runs them, and returns. Nothing requires it to prove the unit's ACCEPTANCE CRITERIA are met before it hands the unit back. The consequence is measurable: of the twenty major findings across two review rounds on RUN-01KYJZGZ, about seventeen were mechanically catchable before the lane returned, and all of them instead cost a full review round plus a repair cycle.

Four checks would have caught them. Six units reached Fixed carrying no acceptance-criteria section at all - a lane could refuse to start on a unit with nothing to deliver against. Four mechanisms shipped reaching no caller, and one shipped a consumer whose producer does not exist - an acceptance criterion naming the caller (CR0461), checked before the lane returns, catches all five. Six units were assigned mutation proof by the plan's own test strategy and none delivered any, with nothing comparing demand to evidence (BG0358).

The remaining three were genuine review work and should stay there: a verifier that tested only the cases that do not bite, a selection that claimed itself resolved while missing dependents, and a cache that fired over a change the tests catch. Each needed a counter-example constructed from the real repository, which is judgement, not a check.

## Impact

Who: every sprint, and directly the operator's time. RUN-01KYJZGZ was estimated at five hours and took seven, and the two-hour overrun was repair cycles driven by findings that arrived late. Review time is not the problem to attack - review found real defects both rounds - the problem is that basic acceptance-criteria failures reach it at all. What breaks without this: a review round is spent on things a thirty-second check would have refused, and the expensive adversarial judgement that only a reader can supply is crowded out by bookkeeping.

## Acceptance Criteria

- [ ] A lane refuses to start on a unit that carries no acceptance criteria, naming the unit, rather than inferring a contract from the summary.
- [ ] Before returning a unit, a lane runs that unit's own acceptance criteria and returns the result; a unit whose criteria do not pass comes back as blocked rather than as fixed.
- [ ] A lane returns the proof the plan's test strategy assigned to that unit, or states plainly that it could not and why, so an unmet obligation is visible at the lane rather than at the close (BG0358).
- [ ] For a unit that adds a mechanism, the lane confirms the caller named in its criteria actually reaches it (CR0461), so an inert mechanism is caught by the author rather than by a reviewer.
- [ ] The dispatch prompt carries these as obligations on the lane, so the checks travel with the work rather than depending on whoever wrote that sprint's prompt remembering them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-raised: trim review by finding issues in-sprint) | Raised |
