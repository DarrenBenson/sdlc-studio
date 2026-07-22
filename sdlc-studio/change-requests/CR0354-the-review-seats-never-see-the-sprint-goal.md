# CR-0354: the review seats never see the Sprint Goal - they score WSJF and nothing reviews what the run is for

> **Status:** In Progress
> **Decomposed-into:** EP0098
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Personas contribute exactly one thing at plan time: seat-scored WSJF. Product Owner supplies value, time-criticality and risk-reduction, QA supplies risk, and those replace the derived Cost of Delay so the batch SORTS differently. That is an ordering input, not a review. No seat is asked whether the Sprint Goal is the right goal, whether this batch can achieve it, or what done means for it - and the goal is the thing the closing review judges the increment against.

The mechanism is also manual, advisory and stale-tolerant: with no wsjf-inputs.json the plan falls back to priority, and a stale file only warns. In RUN-01KXVYGR the plan reported 'no seat inputs (priority fallback)' across all 32 units and 'wsjf-inputs.json is 8.6 day(s) old' - so zero persona involvement in a plan that was then executed for a full session.

That run is the argument. Its Sprint Goal, 'the sized delivery backlog is empty', was unreachable BY CONSTRUCTION: with `two_role_after` set, every story needs a reviewer-of-record sign-off that the authoring session is refused, so the best reachable end state was always 'built, verified, at Review'. Nobody noticed until the close, and the verdict was recorded as partial. A Product Owner seat asked 'is this goal achievable by this batch, and what does done mean for it' is precisely the check that catches an unreachable goal before the work rather than after it.

## Impact

The Sprint Goal is what the closing review judges the increment against, and it is written by whoever runs plan with nothing pressure-testing it. The one human gate in the plan path is the triage STOP, and the brief presented there carries the goal unreviewed - so the operator approves a batch against a goal no seat has examined. When the goal is wrong or unachievable the cost lands at the close, after the work is done.

## Acceptance Criteria

- [ ] sprint plan consults the review seats on the Sprint Goal and batch coherence, not only for WSJF scores: is the goal achievable by this batch, what does done mean for it, and does the batch hang together as one increment
- [ ] the seat verdict is recorded on the run state at plan time, so the close judges the goal against what the seats said THEN rather than a later reconstruction
- [ ] the consult is BLOCKING at --goal plan - a plan whose goal no seat has reviewed is not written. Recommended over advisory: this run is a clean example of what advisory bought, and the check is cheap. If the operator prefers advisory, only this criterion changes
- [ ] a goal that no seat can judge achievable is reported with the reason, and the plan names the reachable end state instead of writing the aspirational one
- [ ] --skip-personas remains the recorded escape and says on the plan that the goal went unreviewed, so the close can see it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
