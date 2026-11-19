# US1198: Sprint drive step performs the whole chain after a hand-back in one command and prints the next prompt path

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, sdlc-studio/reviews/command-audit.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0326
> **Points:** 5
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

### AC4: One command handles a reviewer's REJECT and names the repair builder's prompt

- **Given** the same unit with its reviewer's REJECT verdict file written under `sdlc-studio/reviews/verdicts/<unit>/`
- **When** `sprint.py drive step --after <reviewer id>` is run
- **Then** it records the REJECT, writes the repair brief carrying the refusal and blocking findings verbatim (US1195's brief), exits 0, and its last line is the repair builder's prompt path, which exists and holds that brief. Fails on: a second command needed to brief the repair, or a prompt path printed for the next unit while this one is rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_reject_hand_back_briefs_the_repair_and_names_its_prompt

### AC5: One command handles a repair's hand-back and names the round-two reviewer's prompt

- **Given** a repair builder's worktree for a unit whose round-one verdict was a REJECT
- **When** `sprint.py drive step --after <repair id>` is run
- **Then** it lands the repair, records the self-check, writes the round-two QA brief as a rejoinder quoting the unanswered REJECT, exits 0, prices the repair's return as AC1 prices a builder's, and its last line is the round-two prompt path for the reviewer who rejected, whose resumed hand-back AC2 then accepts. Fails on: a fresh round-one brief that drops the REJECT, a prompt addressed to a different reviewer, or a second command needed to land or brief the repair
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_repair_hand_back_is_landed_and_the_round_two_prompt_named

### AC6: A REJECT at the review round cap stops and prints no prompt path

- **Given** a unit whose round-two verdict is a REJECT, with `review.max_rounds` at its default of 2
- **When** `sprint.py drive step --after <reviewer id>` is run
- **Then** it records the REJECT, briefs no third repair, exits non-zero and prints a decision record that names the round cap and the operator ruling owed, with no prompt path. Fails on: a third repair briefed and its prompt printed, so a round `critic.py record` refuses is built
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py::SprintDriveStepTests::test_a_reject_at_the_round_cap_stops_with_a_decision_record

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
