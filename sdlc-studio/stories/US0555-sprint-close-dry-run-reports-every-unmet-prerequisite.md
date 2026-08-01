# US0555: sprint close --dry-run reports every unmet prerequisite of the whole close chain in one read-only pass, retro content included, and writes nothing

> **Status:** Done
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0189
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** an operator about to close a sprint
**I want** one read-only pass that reports every refusal the whole close chain would raise
**So that** I fix them together instead of discovering them one serial four-hundred-second round-trip at a time

## Acceptance Criteria

### AC1: every step is evaluated, not just the first that refuses

- **Given** a run whose close would refuse at step 2 and again at step 5
- **When** `sprint close --dry-run` runs
- **Then** BOTH refusals are reported in one pass, each named with its step, rather than stopping at the first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDryRunTests::test_every_refusing_step_is_reported_not_only_the_first
- **Verified:** yes (2026-07-29)

### AC2: retro CONTENT is validated, which is what `preflight` cannot reach

- **Given** a retro that exists but whose carried-lessons section or disposition vocabulary would fail `retro validate`
- **When** the dry run reports
- **Then** the content defect appears in the same pass as the structural prerequisites, which is the class `preflight` misses because it runs before the retro exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDryRunTests::test_retro_content_defects_are_reported_in_the_same_pass
- **Verified:** yes (2026-07-29)

### AC3: the dry run writes nothing

- **Given** a workspace whose artefact tree is recorded before the dry run
- **When** the dry run completes, whether it reports refusals or none
- **Then** no tracked file, index, run-state or `.local` record has changed
- **Preserves:** the close's own write path is untouched by this story, so the sprint.py seam it shares with US0559 is owned here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDryRunTests::test_the_dry_run_writes_nothing
- **Verified:** yes (2026-07-29)

### AC4: a clean dry run says so, and the real close then does not refuse

- **Given** a run whose prerequisites are all met
- **When** the dry run reports and the real close follows over the same tree
- **Then** the dry run reports no refusal and the close completes without one, so a clean dry run is a usable prediction rather than an encouragement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDryRunTests::test_a_clean_dry_run_predicts_a_close_that_does_not_refuse
- **Verified:** yes (2026-07-29)

### AC5: a step the dry run cannot evaluate is reported as unevaluated, never as passing

- **Given** a step whose prerequisite cannot be judged read-only
- **When** the dry run reports
- **Then** that step is listed as unevaluated with the reason, and the pass is not reported as clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseDryRunTests::test_an_unevaluated_step_is_never_reported_as_passing
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-08-01 | sdlc-studio | Retitled: was 'sprint close --dry-run reports every unmet prerequisite of all seven steps in one read-only pass, retro content included, and writes nothing' |
