# CR-0495: file-and-close fans one systemic blocker into one change request per unit, so a single owed sign-off filled the discovery backlog with 23 identical artefacts

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM close, dogfooding friction); agent; skill v5.0.0

## Summary

The bounded exit files every remaining blocker as a real artefact, which is right in principle - nothing waived, everything owned. But it files them per UNIT rather than per CAUSE, so a blocker whose cause is one missing approval becomes one artefact per unit in the batch.

## Impact

Anyone using the bounded exit, and everyone downstream of the discovery backlog. Observed closing RUN-01KYKVZM: the close filed CR0472 through CR0494 - one per story US0508 to US0530 - each stating the same fact, that no APPROVE verdict covers the unit. There is exactly ONE fact behind all 23: the sprint was reviewed three times, every round returned REJECT, and the operator sign-off is owed. The backlog now carries 23 artefacts that will all resolve or become void together on a single action, and a backlog whose count is inflated by an order of magnitude by one event is a backlog nobody can read. The count is also the input to triage and to the discovery-versus-delivery reporting, so the distortion is not merely cosmetic.

## Acceptance Criteria

- [ ] Blockers sharing a cause and a remedy are filed as one artefact listing the units it covers, proven by a test written red before the fix over a batch whose units are all blocked by one missing approval
- [ ] The close reports the number of blockers filed and the number of distinct causes, so a fan-out is visible when it happens, proven by a test written red before the fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM close, dogfooding friction) | Raised |
