# CR-0471: A sprint is named by its goal, not only by its run id, so the goal is visible wherever the sprint is listed

> **Status:** In Progress
> **Decomposed-into:** EP0187
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (operator-raised, RUN-01KYKVZM close); agent; skill v5.0.0

## Summary

A run carries a Sprint Goal and is identified only by its ULID. The goal reaches the run state and the plan and never reaches the name, so nothing that lists sprints can show what they were for without opening each one.

## Impact

Anyone reading a list of sprints, and every artefact that references one. A run is identified as RUN-01KYKVZM and nothing else: the id is a ULID, so a list of them carries no information at all about what any sprint was for. Every other artefact type in this project is named type-id-slug and is therefore readable in a directory listing, a git log or an index; a sprint is the one thing whose whole purpose is a goal and whose name does not mention it. The effect compounds with the queue RFC0057 introduces - a planned queue of sprints a second person is meant to read and run is unusable when every entry is an opaque id.

## Acceptance Criteria

- [ ] A sprint that surfaces as a file is named sprint-<run id>-<goal slug>, slugged from the Sprint Goal by the shared slug helper, proven by a test written red before the fix
- [ ] The bare run id remains the canonical identifier and resolves the sprint regardless of the slug, so rewording a goal does not orphan references, proven by a test that resolves a sprint whose recorded goal no longer matches its filename
- [ ] A run with no goal recorded falls back to the id alone rather than inventing a slug, proven by a test written red before the fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (operator-raised, RUN-01KYKVZM close) | Raised |
