# US1141: The sprint hands off to a resume brief and resumes from it in a fresh session at the same next action

> **Status:** Done
> **Delivers:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, changelog.d/US1141.md, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0302
> **Points:** 3
> **Depends on:** US1140
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The sprint hands off to a resume brief and resumes from it in a fresh session at the same next action
**So that** CR0670 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given an open fixture run, then `sprint.py handoff [--agent <unit>=<agent-id> ...] [--issue "<text>" ...]` writes the brief to `sdlc-studio/.local/resume-brief.md` and prints its path, its estimated tokens against the 8,000 budget and the next action; with no open run, a brief over budget or an `--agent` value without `=`, it exits 2 naming why and writes nothing. It writes nothing under `sdlc-studio/handoffs/` and sets no `handoff` key in the run state. Fails on: a brief written with no open run or over budget, a malformed `--agent` accepted, or an HO file or `handoff` key written (the surface US0978 retired).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HandoffCliTests::test_handoff_writes_the_bounded_brief_and_refuses_without_a_run_or_over_budget
  - **Verified:** yes (2026-11-09)
- **AC2:** Given a fixture run handed off with `sprint.py handoff`, then `sprint.py resume`, run as a separate process holding only the tree, prints the brief and the same next action the handoff recorded; given a tree that moved after the handoff (a lane landed), it prints the next action the tree now yields and names the brief's as stale; with no brief on disk, or a brief naming a run other than the open one, it exits 2. Fails on: a next action that differs from the handoff's on an unchanged tree, a stale action printed as current, or a resume over another run's brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::ResumeCliTests::test_resume_in_a_fresh_process_reaches_the_handoffs_next_action_and_names_drift
  - **Verified:** yes (2026-11-09)
- **AC3:** Given a plannable fixture batch, then `sprint plan --write` ends its output by naming its next step as `sprint.py handoff`, then wave 1 started in a fresh session with `sprint.py resume`; a plan without `--write` prints no such line. Fails on: the line missing after `--write`, or printed by a preview that opened no run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::PlanNextStepTests::test_plan_write_names_a_fresh_session_as_its_next_step
  - **Verified:** yes (2026-11-09)
- **AC4:** Given the shipped docs, then help/sprint.md shows `sprint.py handoff` and `sprint.py resume` as fenced invocations the sprint parser accepts, and the generated command surface (`docgen.py surface`) lists both verbs. Fails on: either verb missing from either page, or a documented flag the parser does not own.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::HelpTests::test_help_and_the_command_surface_list_handoff_and_resume
  - **Verified:** yes (2026-11-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
| 2026-11-09 | Claude Opus 5.5 (run nine) | Affects names the unit's changelog fragment, which grooming left out |
| 2026-11-09 | Claude Opus 5.5 (run nine) | Affects gains sprint_report.py: the new top-level verbs need entries in NON_CEREMONY_VERBS, which the close-checklist coverage test requires |
