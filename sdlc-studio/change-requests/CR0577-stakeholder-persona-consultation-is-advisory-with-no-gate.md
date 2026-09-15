# CR-0577: Stakeholder persona consultation is advisory with no gate, so a story batch reaches delivery with no persona ever consulted

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/reference-consult.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** Operator question and ruling ('Both': consult now and file the gate), 2026-09-15. Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Doctrine rule 7 says consult before freezing a design and adds the live stakeholders when an artefact touches the running system, but nothing enforces it: no command refuses a batch whose stories no stakeholder persona has read. The operator asked on 2026-09-15 when personas are consulted and whether it is mandated; it is not. Their first consult of this kind, run the same day over CR0526's four stories, returned one Reject and two Concerns and seven candidate units - findings no Three-Amigos plan review had raised.

## Impact

Operators and consuming projects that rely on stakeholder personas to catch a design that does not serve its users: today the consult happens only when someone remembers, and the persona files go unread.

## Acceptance Criteria

- [ ] A stakeholder consult run through the shipped consult produces a recorded artefact naming the units it covered and each persona's verdict
- [ ] sprint plan (or refine) refuses, or reports under a stated knob, a story batch no recorded stakeholder consult covers, naming the uncovered stories
- [ ] A sanctioned skip exists and costs a written reason, which the close reports

## Recommendation

Record a consult as an artefact (the consultation template's output under reviews/) and have `sprint plan` (or `refine`) refuse, or report under a knob, a story batch with no recorded stakeholder consult covering it, with a sanctioned skip that costs a sentence. Decide the scope: every story, or stories touching the running system as rule 7 says.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
