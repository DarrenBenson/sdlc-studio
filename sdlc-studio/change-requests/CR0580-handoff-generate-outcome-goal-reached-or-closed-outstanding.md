# CR-0580: handoff generate --outcome goal-reached or closed-outstanding ends a run over an unanswered set, and close_owed credits it as a completed close

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/help/handoff.md
> **Evidence:** US0823 stakeholder consult, RUN-01M2JA6J 2026-09-15 (consult-US0823-stakeholders.md), list B item B1 (Maya Okafor, Jonah Reyes, Trevor Hale; High) and evidence E4 (handoff.py:885, close_owed.py:351); changelog.d/US0823.md discloses that generate --outcome still accepts both outcomes.
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

RULED by the operator (D0206): generate refuses goal-reached and closed-outstanding over a non-empty unanswered set, and AC3's prose is amended to match. handoff.py generate --outcome accepts every closed outcome, goal-reached and closed-outstanding included (handoff.py:885), and `close_owed.py`:351 reads both as 'the close completed'. So generate --outcome goal-reached over nine unanswered units exits 0 and is credited as a completed close: a side door round the stop-ship question that the work closing the other doors left open. Refusing only those two outcomes over a non-empty set breaks no literal assertion of the approved criteria (AC3 and AC5 use budget-spent, AC6 passes no outcome, and AC3's unconditional-raise mutant is still killed), but it contradicts AC3's 'never refuses' prose - the operator ruled the refusal and the prose amendment (D0206).

## Impact

Anyone who ends a run through handoff generate, and every reader that trusts a goal-reached close (`close_owed` and the release bar through it): a run with open stop-ship questions is recorded as closed and credited, so the close's hold can be stepped round with one command. All three consulted personas raised it independently and rated it High.

## Acceptance Criteria

- [ ] handoff.py generate --outcome goal-reached over a run whose unanswered set is non-empty exits non-zero, names each held unit and writes no handoff, beside the same command over an answered run, which succeeds
- [ ] handoff.py generate --outcome budget-spent over the same non-empty set still succeeds and records the set
- [ ] The clean close's own handoff step over an answered run still closes goal-reached

## Recommendation

On the operator's ruling, refuse goal-reached and closed-outstanding in handoff generate when the unanswered set is non-empty, naming the held units and the ways out; stopped, budget-spent and blocked still report and close. The clean close calls generate only after its own hold has passed, so the refusal costs it nothing, provided generate reads the same retro as the close (the named-retro pass-through lands first). Record the ruling beside the change, since it amends AC3's stated contract.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
