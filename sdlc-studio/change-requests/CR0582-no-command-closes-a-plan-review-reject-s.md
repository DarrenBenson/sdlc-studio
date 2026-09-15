# CR-0582: No command closes a plan-review REJECT's findings from the independent re-review that approved the repaired plan

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-scripts-review.md
> **Evidence:** findings/todo.txt, RUN-01M2JA6J 2026-09-15: FILE AT CLOSE glue CRs, 'plan-repair closures from approving re-review'; the session's hand-written plan_repair_closures.py and plan_repair_closures2.py.
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

After an independent plan-review round APPROVES a repaired plan, critic.py repair --phase plan-review still needs one closure per finding raised by every unanswered plan-review REJECT on the unit, written by hand. RUN-01M2JA6J wrote a throwaway script for it twice: it read the unanswered plan-review REJECTs through the private `critic._unanswered_rejects`, collected their findings, and wrote a --closed-file pointing each at the repair in the unit's Revision History and at the approving round's brief fingerprint.

## Impact

Authors closing plan review, more often now that rounds are capped: every approved re-review costs a hand-built closure file that reaches into private helpers, the hand-rolled shape the toolchain rule exists to remove.

## Acceptance Criteria

- [ ] On a unit whose plan-review REJECTs are followed by an independent APPROVE, the new mode records a closure for every outstanding finding naming the approving verdict, and the unit's plan-review repair reads complete
- [ ] On a unit whose only later APPROVE is the author's own, the mode is refused, naming the independence rule, and writes nothing
- [ ] On a unit with no APPROVE after its REJECTs, the mode is refused and writes nothing

## Recommendation

Add a critic.py repair --phase plan-review mode that, for a unit whose latest plan-review verdict is an independent APPROVE carrying a brief fingerprint, writes a fixed closure for every finding of each unanswered REJECT citing that APPROVE's reviewer, date and fingerprint, and refuses when the APPROVE is not independent or is not later than the REJECTs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
