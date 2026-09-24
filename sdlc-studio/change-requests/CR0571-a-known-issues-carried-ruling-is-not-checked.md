# CR-0571: A Known issues carried ruling is not checked against who may rule, so the stop-ship hold the doctrine gives the operator is self-releasable

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md). Rated High for the Primary persona by the consult.
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`retro.carried_issues` accepts any non-empty Ruled by cell, and US0626's predicate answers a unit on any ruling. The doctrine rule US0625 ships says the ruling is made by the operator or a recorded delegate in a separate trust boundary, never the session that did the work; nothing enforces it. About 124 of 1,081 valid rulings in this repository name the operator; all 46 in RETRO0116 name the authoring agent, including the one deferring CR0526 itself.

## Impact

Every operator relying on D0193's hold: a close can be released by the agent that did the work writing its own ruling row.

## Acceptance Criteria

- [ ] A Known issues carried row whose Ruled by names the authoring session's principal is read as a proposal, not a ruling, by every reader of the carried table
- [ ] A row ruled by the operator or a recorded delegate outside the authoring trust boundary still answers its unit
- [ ] How an unattended close proceeds when every ruling is a proposal is settled by an operator decision recorded before build

## Recommendation

Treat a row whose ruler is inside the authoring session's trust boundary as a proposal (unruled), reusing `critic signoff`'s principal predicate. This conflicts with US0626 AC3 as approved and with D0194's unattended-close reading, so it needs an operator ruling on how an unattended close proceeds before it is built. Include the team case (who is the operator on a team of three).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - [+constraint] principal check on carried rulings: D0257 signer decides |
