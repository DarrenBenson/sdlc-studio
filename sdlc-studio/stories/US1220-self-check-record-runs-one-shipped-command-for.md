# US1220: Self-check record runs one shipped command for each criterion and stores its exit and an output digest

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0682
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py
> **Epic:** EP0333
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Self-check record runs one shipped command for each criterion and stores its exit and an output digest
**So that** CR0682 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Record runs each criterion's command once and stores its exit and an output digest

- **Given** a unit with two acceptance criteria and a CLAIMS.json holding one claim for each, whose commands call a shipped CLI and append to a counter file
- **When** `critic.py self-check record --unit <id> --claims CLAIMS.json --mutants MUTANTS.json` is run
- **Then** each command has run exactly once, and the recorded self-check holds each criterion's exit status and a digest of its output. Fails on: a command recorded and never run, a command run twice, or a claim ruled TRUE by hand while its command exits non-zero
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::CriterionCommandTests::test_record_runs_each_command_once_and_stores_exit_and_digest

### AC2: A criterion whose observable is missing from the output is ruled FALSE

- **Given** a fixture of the dropped-warning case: a criterion whose quoted observable is a warning line, and a command that exits 0 without printing it
- **When** `critic.py self-check record` is run with the claim ruled TRUE by the author
- **Then** the claim is ruled FALSE and the record is refused naming the criterion and the observable that was not seen, with nothing written; the same claim with a command that prints the warning is recorded. Fails on: an exit of 0 accepted as proof of an observable the output does not show
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::CriterionCommandTests::test_a_missing_observable_is_ruled_false_whatever_the_author_ruled

### AC3: A criterion with no claim, or with only a test selector, is refused

- **Given** a unit with two acceptance criteria
- **When** `critic.py self-check record` is given a CLAIMS.json with a claim for one criterion only, and then one whose second claim's command is a pytest selector and nothing else
- **Then** the first is refused naming the criterion with no claim, and the second is refused naming the claim that calls no shipped CLI; nothing is written either time. Fails on: a self-check recorded with a criterion unproven, or a test selector accepted in place of the shipped entry point
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::CriterionCommandTests::test_an_unclaimed_criterion_or_a_selector_only_command_is_refused

### AC4: The author's steps list each criterion with its quoted observable

- **Given** a unit with two acceptance criteria, and reference-agent-prompt-template.md
- **When** `critic.py brief` prints the author self-check steps for the unit, and the template's self-check section is read
- **Then** the steps list each criterion by number with its observable quoted from the unit's file, and the template says CLAIMS.json carries one claim for each criterion with a command through a shipped CLI. Fails on: steps that name only the commit message and the fragments
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::CriterionCommandTests::test_the_steps_list_each_criterion_with_its_quoted_observable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
