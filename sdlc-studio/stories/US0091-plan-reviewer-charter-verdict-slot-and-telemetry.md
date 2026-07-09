# US0091: Plan-reviewer charter, verdict slot and telemetry

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0019
> **Persona:** QA seat
> **Affects:** reference-agent-prompt-template.md, reference-sprint.md, templates/core/story.md, scripts/plan_review.py, scripts/critic.py
> **Depends on:** US0090

## User Story

**As a** QA seat asked to review a plan before it is built
**I want** a charter that has me re-check each spec-derived AC against its cited source section, a verdict slot in the story, and telemetry of the outcome
**So that** the plan-review gate has a defined attack angle and its value is measurable over time

Closes the remainder of CR0194 (charter, verdict slot, telemetry, benchmark note). Depends on US0090's gate + phase-record plumbing.

## Acceptance Criteria

### AC1: The plan-reviewer charter is defined

- **Given** the agent-prompt template
- **When** a plan-review is invoked
- **Then** a documented charter (rendered under the QA/tester seat, a separate instance from the plan's author) instructs the reviewer to re-read each cited spec section and flag any AC that contradicts or inverts it, defaulting to challenge-the-written-ACs and escalating to blind re-derivation for high-difficulty units
- **Verify:** grep "Plan-Review Charter" .claude/skills/sdlc-studio/reference-agent-prompt-template.md

### AC2: The story template carries a plan-review verdict slot

- **Given** `templates/core/story.md`
- **When** a story is authored
- **Then** it carries an optional Plan-Review slot (verdict, reviewer, date) the gate can populate
- **Verify:** grep "Plan-Review" .claude/skills/sdlc-studio/templates/core/story.md

### AC3: Plan-review outcomes are recorded to telemetry

- **Given** a plan-review verdict recorded via the phase field
- **When** the record is written
- **Then** a telemetry event capturing the plan-review outcome (id, phase, verdict, reviewer != author) is appended to `.local/telemetry.jsonl`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::TelemetryTests

### AC4: The gate is described in the reference docs

- **Given** the sprint reference
- **When** an operator reads how implementation is gated
- **Then** the plan-review gate, its deterministic trigger, and the operator-override path are described
- **Verify:** grep "plan-review" .claude/skills/sdlc-studio/reference-sprint.md

### AC5: The benchmark note records the measurable hypothesis

- **Given** the N=5 benchmark follow-up
- **When** the gate ships
- **Then** a note records that a future rerun/fixture can measure whether the gate catches the seeded R5-inversion failure mode
- **Verify:** grep "R5-inversion" .claude/skills/sdlc-studio/reference-sprint.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0194 (charter, verdict slot, telemetry) |
