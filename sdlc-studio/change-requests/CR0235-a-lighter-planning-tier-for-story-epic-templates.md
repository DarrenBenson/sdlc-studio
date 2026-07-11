# CR-0235: A lighter planning tier for story/epic templates

> **Status:** Proposed
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

The full story template's structural floor is ~171 lines (epic ~148) once every mandated heading survives, so a dense pre-implementation planning story cannot get under ~170 lines however economically it is written - today's 25 sdlc-bench stories all landed at 170-192 against a ~120 target. batch defaults to full; minimal exists but drops sections planning stories genuinely want (ACs with Verify targets, scope). Add a 'planning' tier between them: metadata, user story, ACs with Verify/target lines, scope, technical notes - no inherited-constraint tables or module views until implementation.

## Acceptance Criteria

- [ ] artifact.py --template planning produces a story skeleton under 60 lines with ACs, scope and Verify targets intact
- [ ] validate.py accepts the planning tier; transition to implementation-facing statuses may require promotion to full

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Raised |
