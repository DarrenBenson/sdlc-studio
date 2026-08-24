# CR-0555: The expensive half of the test-plan gate fires before a diff exists, so move it to where one does instead of banding a signal that cannot discriminate

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-config.md
> **Evidence:** RUN-01M0JD1W, 2026-08-24: five plan-review rounds on three units, and the gate refused BG0606 - a bug whose fix had already shipped and been independently approved. CR0549's three failed remedies are recorded in that CR's corrections; D0150 rules out the class the third one belonged to.
> **Date:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_test_plan_gate` demands two different things at entry to implementation: that a `## Test Plan` EXISTS, and that an independent seat has APPROVED it. The first is cheap and is the falsifiability rule this project is built on. The second is the expensive one - it cost five plan-review rounds on three units in RUN-01M0JD1W - and it is the reason 20 of 21 open bugs cannot reach Fixed. CR0549 tried to make it proportional by banding risk, and failed three specifications for one structural reason: the gate fires BEFORE the unit is implemented, so the only signals available are the author's own declarations, and D0150 now forbids those from gating review depth. The gate does not need to be banded. It needs to fire later. `critic.tier_for` already reads a post-code band successfully, because by then a diff exists.

## Impact

Every project using the skill. Today a two-line bug fix and a rewrite pay the identical pre-code ceremony, and the ceremony is paid before anyone can see what the change is. BG0606 is the concrete case: its fix shipped and was independently approved, and it is still Open because closing it needs a plan review for work already reviewed. Nothing changes for the authoring rule - a criterion must still name a production change its test dies on, at every band - so this narrows WHEN the independent approval is demanded, not WHETHER a plan is required.

## Acceptance Criteria

- [ ] Given a unit entering implementation, when the gate runs, then a `## Test Plan` is still REQUIRED and its absence still refuses - the authoring-time rule is untouched at every band
- [ ] Given that same unit entering implementation, when the gate runs, then an independent plan-review approval is NOT demanded there, and the refusal message says when it will be
- [ ] Given a unit reaching a terminal status, when the gate runs, then the independent plan-review approval IS demanded, and a unit without one is refused exactly as it is refused at entry today
- [ ] Given the terminal gate reading a band, when it asks the estimator, then it asks on the DIFF basis, because a diff exists at that point - and no author-declared field is consulted, per D0150
- [ ] Given a project that has not adopted this, when it transitions a unit, then behaviour is unchanged - the move is behind the same dated cutoff the existing gate uses, so an existing backlog is not retro-refused
- [ ] Given the close, when it reports, then it names units whose plan approval was demanded at terminal and those exempted by the cutoff, so the move is visible rather than silent

## Recommendation

Option 1. The plan must still EXIST at entry, which preserves the authoring-time rule and costs nothing; only the independent approval moves. At the terminal transition a diff resolves, so the band is measured from the change - which is what D0150 requires and what `critic.tier_for` already does. The two-role delivery review and the plan review then both bind at the same point and can be briefed together, which is also the cheaper shape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Raised |
