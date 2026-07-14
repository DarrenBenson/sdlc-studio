# CR-0260: A breakdown step that makes a backlog plannable: Affects, size (bugs too), dependencies, shared-file clusters

> **Status:** Proposed
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/core/bug.md

## Summary

Planning keeps hitting units that cannot be sized or sequenced, and the gap is closed by hand every time. The `--goal design` rung exists and establishes `Depends on` (and, from a PRD, decomposes to epics+stories), but it does NOT groom an existing CR/bug backlog into a PLANNABLE state. Four things are missing, each hit three times in one session:

1. Units declare no `Affects`, so `complexity.py` cannot size them and they fall back to a flat 50k base - hand-groomed three times.
2. **Bugs have no size field at all**, only Severity (which is priority, not size), so a bug can never be sized even in principle.
3. Nothing detects **shared-file clusters**. The planner knows only declared `Depends on`, so it reported CR0257 and BG0132 as safely parallel when both touch `file_finding.py` - it has produced a wrong parallel wave three times.
4. A CR is never decomposed into stories, so its Done is never gated on executable ACs (only stories carry real verifiers - see BG0132).

Operator's framing: during planning, if something is missing we should add it - either in the plan, or as a distinct breakdown step that turns CRs into epics/stories and adds size, complexity and points to everything, bugs included.

## Impact

Every sprint plan. Today the planner's output is only as good as metadata nobody is required to supply, so it silently under-informs: a flat forecast, a fake-parallel wave, an unsizeable bug. The operator gets a plan that looks authoritative and is not. Closing it also removes the hand-grooming that has preceded every plan this session.

**Effort:** L

## Acceptance Criteria

- [ ] The design/breakdown step refuses to hand a batch to  while any unit lacks  or a size, naming the units - a backlog that cannot be sized is not a designed backlog.
- [ ] Bugs carry a size/effort field (this is CR0257's undone AC2), mapped to the canonical unit RFC0034 D1 settled (S/M/L -> token bands; story points stay a within-story aid).
- [ ] The planner surfaces SHARED-FILE CLUSTERS as a coordination hint, derived from the  it already parses: units touching the same file are reported as one cluster, not as independent parallel work.
- [ ] A CR is decomposed into stories where the work warrants executable ACs, so Done is gated on real verifiers rather than prose (BG0132).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
