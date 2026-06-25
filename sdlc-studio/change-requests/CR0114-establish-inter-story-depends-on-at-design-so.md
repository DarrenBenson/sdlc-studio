# CR-0114: Establish inter-story Depends on at design so sprint-plan waves are real, not flat

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

sprint plan emits dependency waves (CR0107), but they are only as good as the declared Depends on metadata - and greenfield-authored stories declare none. A field agent planning EP0005 got all 7 stories in ONE flat parallel wave (no deps in the graph), then hand-derived the real W1-W4 sequence from the story prose - the exact work CR0107 was meant to remove. The gap: nothing establishes inter-story dependencies, so the waves feature degrades to a flat list. The --goal design rung (which grooms Draft->Ready) should declare Depends on between stories; absent that, the planner should at least flag it.

## Acceptance Criteria

- [x] the --goal design rung establishes inter-story `Depends on:` (model-instructed grooming) so a designed backlog carries the dependency graph the planner needs; documented in reference-sprint.md
- [x] when sprint plan selects a batch of >1 story with NO declared dependencies and order is priority/wsjf, it prints a hint that all units are parallel because no `Depends on:` is declared (so a flat single wave is not mistaken for 'no dependencies exist')
- [x] with deps declared, the existing wave computation (CR0107) produces the real levels; unit test covers the no-deps hint; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
