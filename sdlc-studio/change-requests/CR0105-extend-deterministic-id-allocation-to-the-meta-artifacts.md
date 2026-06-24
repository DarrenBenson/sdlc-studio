# CR-0105: Extend deterministic id-allocation to the meta-artifacts (review/retro/persona/lessons)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

next_id.py allocate and artifact.py new cover the 8 pipeline types (bug/cr/epic/plan/rfc/story/test-spec/workflow) and auto-allocate collision-free ids inside new/batch/file_finding, so operators never hand-pick. But review (RV####), retro (RETRO####), persona, and lessons (LL####) are absent from both - so they are still hand-numbered (RV0005 itself was hand-picked by reading the reviews dir this session), violating the never-hand-allocate-ids doctrine for exactly the artifacts the maintenance workflow creates most.

## Acceptance Criteria

- [x] next_id.py allocate --type accepts review, retro, persona, and lessons, returning the next collision-free id (respecting --remote)
- [x] The review/retro creation paths consume the allocator rather than hand-picking the number (artifact.py new extended where it has a sensible template, else documented in reference-scripts.md)
- [x] A unit test covers allocation for at least review and retro (gap detection + next-number)
- [x] CHANGELOG [Unreleased] entry in the same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
