# CR-0736: Sprint plan names the files a story will change that no test reaches, and the brownfield runbook gains a pin-behaviour stage

> **Status:** In Progress
> **Decomposed-into:** EP0373
> **Parent:** RFC0067
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/help/brownfield-runbook.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, tools/tests/test_plan_unpinned_code.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py
> **Evidence:** spawned by RFC0067, ruled 2026-11-17
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:40:03Z

## Summary

The brownfield runbook validates a generated spec against tests, but no stage pins what existing code does before a story changes it, and `sprint plan` accepts a story whose Affects no test imports or exercises. RFC0067 ruled a warning that a project can arm: plan names the unpinned source files per unit, `plan.unpinned_code` (warn, refuse) decides whether the batch is taken, and the runbook gains a stage that writes characterisation tests ahead of the first change.

## Impact

Any team adopting the skill on existing code with thin tests, where a builder's own new tests pass and the behaviour that was never pinned changes unseen.

## Acceptance Criteria

- [ ] `sprint plan` names, per unit, each source file in its Affects that no test file imports directly or through one hop in the repo map
- [ ] With `plan.unpinned_code: refuse` the batch is refused naming those files; with warn, the default, it is planned and the warning is printed
- [ ] A file the unit itself creates is never reported as unpinned
- [ ] The brownfield runbook has a numbered stage, before the first code change, that pins existing behaviour with tests and states how to tell it is done

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
