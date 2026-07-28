# CR-0457: init never creates sdlc-studio/issues/, so the issue type is unusable on a new project

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

`init run` creates the artefact tree but omits issues/ and its _index.md, so the Discovery-side intake type cannot be used at all until someone notices and hand-makes the directory - which the doctrine forbids elsewhere.

## Impact

`init run` creates the artefact tree but omits issues/ and its _index.md, so the Discovery-side intake type cannot be used at all until someone notices and hand-makes the directory - which the doctrine forbids elsewhere.

## Acceptance Criteria

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Raised |
