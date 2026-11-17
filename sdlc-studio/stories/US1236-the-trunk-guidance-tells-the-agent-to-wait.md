# US1236: The trunk guidance tells the agent to wait on its CI run with one blocking watch and to read a red main first

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0697
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-code.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/scripts/tests/test_trunk_ci_wait_guidance.py
> **Epic:** EP0340
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The trunk guidance tells the agent to wait on its CI run with one blocking watch and to read a red main first
**So that** CR0697 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The trunk guidance waits on the push's CI run with one blocking command

- **Given** the `trunk` section of `reference-code.md`
- **When** its steps after `git push origin main` are read
- **Then** it tells the agent to wait on the run that push started with one blocking command under a timeout, naming `gh run watch <id> --exit-status` for GitHub, and says never to poll in a loop. Fails on: guidance that ends at the push, or that shows a loop over `gh run list`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_ci_wait_guidance.py::TrunkCiWaitGuidanceTests::test_the_trunk_section_waits_with_one_blocking_watch_under_a_timeout

### AC2: A red main is read before the next push

- **Given** the same section
- **When** its rule for a run that ends red is read
- **Then** it says a red main is read before anything is pushed again, and points at the red-run policy instead of restating it. Fails on: guidance that lets the next unit be pushed over a red main
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_ci_wait_guidance.py::TrunkCiWaitGuidanceTests::test_a_red_main_is_read_before_the_next_push

### AC3: The agent instructions template carries the rule within its budget

- **Given** the shipped `templates/agent-instructions.md`
- **When** its integration rule is read
- **Then** it states the one blocking wait and the red-main read in the words of the reference's rule, and the template stays within its character budget. Fails on: a template silent on the wait, so a consuming project's agent never reads the rule, or one pushed over its budget
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_trunk_ci_wait_guidance.py::TrunkCiWaitGuidanceTests::test_the_agent_instructions_template_carries_the_wait_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
