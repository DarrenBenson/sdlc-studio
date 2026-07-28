# CR-0456: validate.py cannot be pointed at one artefact, so checking a single story reads 1,548 files

> **Status:** Complete
> **Decomposed-into:** EP0180
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

There is no per-artefact scope, so a lane that wants to check the story it just edited validates the entire workspace. It also warns affects-unresolvable on every Draft story declaring a file it will create, which is the normal case for new work.

## Impact

There is no per-artefact scope, so a lane that wants to check the story it just edited validates the entire workspace. It also warns affects-unresolvable on every Draft story declaring a file it will create, which is the normal case for new work.

## Acceptance Criteria

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Raised |
