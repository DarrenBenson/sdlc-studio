# CR-0422: sprint close --apply-signoff derives parent epics terminal but not the decomposed CRs above them, so an operator hand-transitions every delivered CR to Complete

> **Status:** Complete
> **Decomposed-into:** EP0164
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** S

## Summary

`sprint close --apply-signoff` fans the operator's sign-off into per-unit sign-offs and Done, then `_derive_parent_epics` walks the batch's stories up to their EPICS and marks each epic terminal when all its children are Done. It stops there: the CR (or RFC) that the epic decomposes from is NOT derived, so a change request whose entire delivery is complete still reads `In Progress` until someone transitions it by hand. The derivation should continue one level up - a CR/RFC whose every decomposed epic (and any directly-delivered story) is terminal is itself Complete, by the same rule that already makes an epic terminal from its stories.

This is distinct from CR0333 (which BUILT `apply-signoff` and the epic cascade): that shipped the fan-out and the epic derivation; this closes the gap it left one level higher, at the CR/RFC tier.

## Impact

Every operator closing a sprint that delivered a CR or RFC. Observed twice now: the v5 close left 28 In-Progress CRs to hand-transition, and this session's CR0421 close left one (CR0421 itself). A change request that is fully delivered but reads `In Progress` misleads the discovery-backlog view (`status` counts it as open work), and hand-transitioning it re-introduces exactly the manual step the two-backlog derivation exists to remove - and the risk of forgetting one, so a delivered CR lingers as apparent open work.

## Acceptance Criteria

- [ ] AC1: after `apply-signoff` marks an epic terminal, a CR/RFC all of whose decomposed epics (and any directly-linked delivered stories) are terminal is itself transitioned to its terminal status (Complete for a CR, the RFC's terminal for an RFC)
- [ ] AC2: a CR/RFC with at least one non-terminal child is left unchanged - the derivation is all-children-terminal, the same rule the epic derivation already uses
- [ ] AC3: the close output names each CR/RFC it derived terminal, as it already names the epics, so the cascade is visible and auditable
- [ ] AC4: the derivation is idempotent and safe on a mixed batch (bug-only or story-only batches with no parent CR derive nothing, no error)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
