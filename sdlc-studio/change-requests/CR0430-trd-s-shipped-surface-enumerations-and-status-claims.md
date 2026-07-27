# CR-0430: TRD's shipped-surface enumerations and status claims have drifted: command types 30/41, gate lanes 14/17, drift kinds 5/

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Four TRD passages understate or contradict shipped code: the canonical type list omits nine shipped types (issue, refine, triage, retro, lessons, review, repo, migrate, audit) and contradicts section 6 which says migrate is listed; the gate-tier enumeration omits three shipped default lanes (window, batch-size, changelog-fragments); ADR-003 lists 5 reconcile drift kinds against the shipped 15; and the claim that the count-mismatch finding 'does not yet meet this bar; closing it is CR0132' survived four revisions after CR0132 shipped Complete on 2026-07-04.

## Impact

Four TRD passages understate or contradict shipped code: the canonical type list omits nine shipped types (issue, refine, triage, retro, lessons, review, repo, migrate, audit) and contradicts section 6 which says migrate is listed; the gate-tier enumeration omits three shipped default lanes (window, batch-size, changelog-fragments); ADR-003 lists 5 reconcile drift kinds against the shipped 15; and the claim that the count-mismatch finding 'does not yet meet this bar; closing it is CR0132' survived four revisions after CR0132 shipped Complete on 2026-07-04.

## Acceptance Criteria

- [ ] Refresh the four passages against shipped code in one pass (full type list, 17 lanes, 15 drift kinds, drop the CR0132 caveat), and either derive these enumerations from the code or add them to a doc-freshness spot-check so they cannot silently drift again.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
