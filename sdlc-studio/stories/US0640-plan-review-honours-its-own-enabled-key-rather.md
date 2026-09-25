# US0640: plan_review honours its own enabled key rather than the schema-version gate

> **Status:** Done
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/scripts/config.py,.claude/skills/sdlc-studio/scripts/triage_noise.py,.claude/skills/sdlc-studio/scripts/tests/test_plan_review.py,.claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_plan_review.py
> **Epic:** EP0208
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** plan_review honours its own enabled key rather than the schema-version gate
**So that** CR0510 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the knob switches the gate on under schema v2

- **Given** a project pinned at `schema_version: 2` with `plan_review.enabled: true`
- **When** `plan_review.gate` evaluates a story whose triggers fire
- **Then** it evaluates the triggers rather than returning `dormant (schema v2)`
- **Mutant:** read the schema version alone - the gate stays dormant and the whole slice is inert
- **Verify:** manual - retired by US0909: `plan_review.enabled` and the gate it switched were deleted
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC2: the knob switches it off under schema v3

- **Given** a project at `schema_version: 3` with `plan_review.enabled: false`
- **When** the same story is gated
- **Then** the gate is a no-op and its reason names the knob, not the schema version, so a reader is sent to the thing that actually decided
- **Mutant:** honour the knob only in the permissive direction - a project that deliberately turned it off gets it anyway
- **Verify:** manual - retired by US0909: `plan_review.enabled` and the gate it switched were deleted
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC3: an unset knob changes nothing for any existing project

- **Given** the key absent
- **When** the gate is evaluated at schema v2 and again at v3
- **Then** the results equal today's schema-gated behaviour exactly, so no consuming project moves
- **Mutant:** default the knob to true - every v2 project acquires a gate nobody adopted
- **Verify:** manual - retired by US0909: `plan_review.enabled` and the gate it switched were deleted
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC4: one enablement predicate, shared, so the two adopters cannot disagree

- **Given** `triage_noise.active` and the new plan-review predicate
- **When** the source is searched for the knob-then-schema resolution
- **Then** exactly one definition exists and both call it, because two copies are two answers to one question that drift apart
- **Mutant:** give `plan_review` its own copy of the resolution - the single-definition assertion reddens
- **Verify:** manual - retired by US0909: `plan_review.enabled` and the gate it switched were deleted
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC5: the knob is consulted by the COMMAND, not only by the resolver

- **Given** a project stating `plan_review.enabled: false` under schema v2
- **When** `plan_review.py check` runs against it
- **Then** the command answers differently from the same project with the knob on - the resolver returning the right value proves nothing about whether the command reads it
- **Mutant:** make `active()` ignore the stated knob - every in-process test of the resolver still passes and the command stops honouring the decision
- **Verify:** manual - retired by US0909: `plan_review.enabled` and the gate it switched were deleted
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-06 | sdlc-studio | Second review round: US0640 Affects corrected to name config.py and triage_noise.py, where AC4 actually landed; US0643 AC4 restatement narrowed - the distinction is impossible for every state the tooling produces, not by design |
| 2026-09-25 | Claude Opus 5.5 | AC1, AC2, AC3, AC4, AC5 retired by US0909 (D0259 pattern): `plan_review.enabled` and the gate it switched were deleted |
