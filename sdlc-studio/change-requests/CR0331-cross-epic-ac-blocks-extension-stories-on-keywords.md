# CR-0331: cross-epic-ac blocks extension stories on keywords owned by a terminal epic

> **Status:** Superseded
> **Superseded-by:** BG0184 (refiled as a Bug - silent planning-gate failure)
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/ac_scope.py, .claude/skills/sdlc-studio/scripts/audit.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The tranche audit hard-blocks (NOT READY) a story whose ACs mention a distinctive keyword owned by another epic even when that epic is Done. The lint's purpose is to catch an AC depending on a capability that does not exist yet; a terminal epic's capability exists, so a CR that extends a shipped subsystem (the normal brownfield case) always trips it. Observed planning the 2026-07-16 big sprint: US0193/US0196/US0198 flagged on 'schedule' (EP0052), 'down'/'judged' (EP0046/EP0053) and 'composed' (EP0058) - all Done epics their parent CRs deliberately modify. `ac_scope`'s own docstring says advisory/operator-decides, but audit.py maps it to a blocking issue. Suppress (or downgrade to informational) a keyword whose owning epic is terminal; keep the block for non-terminal owners.

## Impact

Every brownfield sprint over extension CRs shows NOT READY units at the triage STOP; the operator either learns to wave the flag through (cry-wolf, the CR0113 failure mode again) or agents reword seeded ACs to dodge a keyword lint, corrupting operator-approved AC text.

## Acceptance Criteria

- [ ] A distinctive keyword whose owning epic is terminal (Done/Superseded) does not raise cross-epic-ac; it may surface as informational context
- [ ] A keyword owned by a non-terminal epic still blocks as today
- [ ] Unit test covers both; the US0193/US0196/US0198 shapes pass the tranche audit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Raised |
