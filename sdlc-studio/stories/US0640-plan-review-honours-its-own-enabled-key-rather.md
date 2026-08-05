# US0640: plan_review honours its own enabled key rather than the schema-version gate

> **Status:** Ready
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::EnablementKeyTests::test_the_knob_switches_the_gate_on_under_schema_v2

### AC2: the knob switches it off under schema v3

- **Given** a project at `schema_version: 3` with `plan_review.enabled: false`
- **When** the same story is gated
- **Then** the gate is a no-op and its reason names the knob, not the schema version, so a reader is sent to the thing that actually decided
- **Mutant:** honour the knob only in the permissive direction - a project that deliberately turned it off gets it anyway
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::EnablementKeyTests::test_the_knob_switches_the_gate_off_under_schema_v3

### AC3: an unset knob changes nothing for any existing project

- **Given** the key absent
- **When** the gate is evaluated at schema v2 and again at v3
- **Then** the results equal today's schema-gated behaviour exactly, so no consuming project moves
- **Mutant:** default the knob to true - every v2 project acquires a gate nobody adopted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::EnablementKeyTests::test_an_unset_knob_preserves_the_schema_gated_behaviour

### AC4: one enablement predicate, shared, so the two adopters cannot disagree

- **Given** `triage_noise.active` and the new plan-review predicate
- **When** the source is searched for the knob-then-schema resolution
- **Then** exactly one definition exists and both call it, because two copies are two answers to one question that drift apart
- **Mutant:** give `plan_review` its own copy of the resolution - the single-definition assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::EnablementKeyTests::test_one_shared_enablement_predicate_serves_both_adopters

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
