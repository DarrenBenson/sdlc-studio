# BG0755: artifact.py batch ignores a story's role, capability and benefit, and its default template leaves a page of placeholders

> **Status:** Fixed
> **Findings-filed-to:** CR0592
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG0755.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/reference-scripts-create.md
> **Evidence:** Sprint 3 planning, 2026-09-24: US0890-US0926 were minted with placeholders and rewritten to the lean shape by hand from the authors' specs.
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py batch --type story` with items carrying `role`, `capability` and `benefit` left the User Story block's persona, capability and benefit placeholders unfilled for all 37 Sprint 3 stories, and its default `full` template added about 100 lines of placeholder sections (Context, Inherited Constraints, Scope, Technical Notes, Edge Cases, Test Scenarios, Dependencies, Estimation, Rollback Envelope, Open Questions). The single-item `new` path fills the user story. An unfilled Open Questions placeholder can hold a transition.

## Steps to Reproduce

1. Write a spec item with title, epic, role, capability, benefit, acs, verify. 2. `artifact.py batch --type story --spec <file>`. 3. The User Story block keeps its placeholders.

## Proposed Fix

Fill role/capability/benefit in the batch path exactly as `new` does, and make the lean story shape the batch default (the full template stays opt-in).

## Acceptance Criteria

- [ ] **AC1** Given a batch spec story item carrying `role`, `capability` and `benefit`, when `artifact.py batch --type story` runs, then the story's `**As a**`, `**I want**` and `**So that**` lines carry those values and the file holds no `{{role}}`, `{{capability}}` or `{{benefit}}`. Fails on: HEAD, which drops the three keys and leaves the placeholders (reproduced in a fresh `init` fixture)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py::BatchStoryFieldsTests::test_batch_fills_the_user_story_block
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given `artifact.py new --type story --fields-file` carrying the same three keys, then the story's three lines carry them. Fails on: fixing only the batch path, while `new` refuses the keys at HEAD ('unknown field(s): benefit, capability, role')
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py::BatchStoryFieldsTests::test_new_fills_the_user_story_block
  - **Verified:** yes (2026-09-25)
- [ ] **AC3** Given `artifact.py batch --type story` with no `--template`, then the written story holds no `{{` placeholder anywhere, and with `--template full` it still carries the full template's sections. Fails on: HEAD's batch default of `full`, which wrote 145 lines of placeholder sections per story
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py::BatchStoryFieldsTests::test_the_batch_default_is_the_lean_shape
  - **Verified:** yes (2026-09-25)
- [ ] **AC4** Given a batch spec item carrying a misspelt key (`rol`), then the batch is refused naming the key, as `new --fields-file` refuses one. Fails on: HEAD, which ignores it silently, the path by which all 37 Sprint 3 stories lost their three fields
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_batch_story_fields.py::BatchStoryFieldsTests::test_an_unknown_batch_key_is_refused
  - **Verified:** yes (2026-09-25)

## Notes

- Premise corrected at 013a46d0: the Summary says the single-item `new` path fills the three fields; it does not, it refuses them as unknown. Neither creator can write a filled user-story block today. Land in W0 if the orchestrator creates Sprint 5's units with `artifact.py batch`, or those units need the same hand trim Sprint 3's did. Ratchet (LC-008): AC4 makes batch refuse what `new` already refuses; its measured yield is the 37 Sprint 3 stories.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5; premise about `new` corrected; 2 -> 3 points |
