# CR-0369: a sprint that needs an operator decision should ask a structured question, not stop in dense prose

> **Status:** Complete
> **Decomposed-into:** EP0092
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/SKILL.md
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator-reported, and reproduced repeatedly in this session. When a run reaches something only the operator can decide, it stops and explains itself in prose. The operator then has to read a dense block to work out what is actually being asked, what the options are, and which one the agent recommends. The operator's habitual workaround is to type 'ask me the questions', which makes the agent re-present the same decision as a short multiple-choice - evidence that the decision was always expressible that way and the prose was the wrong surface for it. Two separable faults. First, the run stops earlier than it needs to: a decision that only blocks ONE unit halts the whole batch, when the other units could have continued and the question been asked once at the point it genuinely blocks. Second, when the question is finally asked it arrives as narrative rather than as a decision with named options, so the operator does the work of extracting the choice from the explanation.

## Impact

Every interactive run. The operator pays attention-cost per stop, reading prose to find a question, and often has to prompt for the structured form explicitly. Runs also stall further than necessary, because a single undecidable unit stops units that were never blocked. Both effects push toward the operator disengaging from the decision or answering it under-informed, which is the opposite of what a human-in-the-lead process is for.

## Acceptance Criteria

- [ ] Given a batch where one unit needs an operator decision and others do not, when the run reaches it, then the blocked unit is set aside and the remaining units continue, so the run stops only when it can make no further progress
- [ ] Given the run must ask the operator something, when it asks, then the question is presented in a structured form - the question itself, named options, and the consequence of each - rather than as prose the operator must parse a decision out of
- [ ] Given the agent has a view on the right answer, when the question is presented, then its recommendation is marked as such with the reason, so the operator can accept the default quickly or override it deliberately
- [ ] Given several decisions accumulated while the run continued, when the run finally stops, then they are asked together rather than one stop per decision
- [ ] Given a non-interactive run, when a decision is needed, then behaviour is unchanged - the question is recorded and the unit is blocked, never silently defaulted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
