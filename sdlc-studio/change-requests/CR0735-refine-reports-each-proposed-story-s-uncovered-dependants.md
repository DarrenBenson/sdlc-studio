# CR-0735: Refine reports each proposed story's uncovered dependants and near-duplicate symbols before it decomposes

> **Status:** In Progress
> **Decomposed-into:** EP0372
> **Parent:** RFC0067
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/help/refine.md, tools/tests/test_refine_impact.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py
> **Evidence:** spawned by RFC0067, ruled 2026-11-17
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:40:02Z

## Summary

`refine apply` turns a request into stories from the breakdown it is handed and never consults the repo map, so a story can change a module without anyone learning that three other files import it, or that a second module of nearly the same shape exists and may be the one meant. RFC0067 ruled the check advisory: refine prints, per story, the files that import its Affects and are covered by no story in the breakdown, and any symbol elsewhere in the map whose name and signature closely match one in its Affects, then decomposes regardless.

## Impact

Whoever refines a request against a codebase larger than they hold in their head; the surprise today surfaces at build or review, after the points are spent.

## Acceptance Criteria

- [ ] `refine apply --dry-run` and `apply` print, for each story, the files that import a file in its Affects and appear in no story's Affects in the same breakdown
- [ ] They print any symbol outside the story's Affects whose name and parameter list closely match a symbol inside them, by a rule the help page states
- [ ] The report never changes the exit code or the stories written, and says so when the repo map is absent or stale instead of printing nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
