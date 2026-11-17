# US1198: Sprint drive step performs the whole chain after a hand-back in one command and prints the next prompt path

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py
> **Epic:** EP0326
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint drive step performs the whole chain after a hand-back in one command and prints the next prompt path
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: One command handles a builder's hand-back and prints the reviewer's prompt path

- **Given** an open run and a builder's worktree `agent-<id>` holding the unit's staged change and hand-in
- **When** `sprint.py drive step --after <id>` is run
- **Then** it lands the lane, records the self-check, writes the QA brief and prices the return in that one command, exits 0, and the last line of stdout is the path of the reviewer's prompt file, which exists and holds the QA brief. Fails on: a step that stops after the landing and leaves the brief to a second call, or prints a path that does not exist
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_builders_hand_back_is_landed_briefed_and_the_review_prompt_named

### AC2: One command handles a reviewer's hand-back and names what is next

- **Given** the same unit with its reviewer's APPROVE verdict file written under `sdlc-studio/reviews/verdicts/<unit>/`
- **When** `sprint.py drive step --after <reviewer id>` is run
- **Then** it records the verdict, runs the criteria, moves the unit, returns its lane and commits the paperwork, exits 0, and its last line is the next unit's builder prompt path, or says the wave has ended when none is left. Fails on: a second command needed to accept or to commit the paperwork, or a prompt path printed for a unit already built
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_reviewers_hand_back_is_accepted_and_the_next_prompt_named

### AC3: A refusal inside the chain stops it and prints no prompt path

- **Given** a builder's hand-back whose commit hook refuses the landing, and an agent id the run has no lane for
- **When** `sprint.py drive step --after <id>` is run for each
- **Then** the first stops at the landing, exits non-zero and prints the decision record with no prompt path; the second exits 2 naming the unknown agent and changes nothing. Fails on: a prompt path printed after a refused step, so the orchestrator spawns a reviewer for a lane that never landed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_refused_step_prints_a_decision_record_and_no_prompt_path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
