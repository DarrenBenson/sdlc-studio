# US0343: A repair answering a finding in the same class as a previous round must state whether the design is retained or changed, and a plan describing only a better instance is refused past the threshold

> **Status:** Draft
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0410
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py
> **Epic:** EP0106
> **Points:** 3

## User Story

**As an** agent repairing a sprint that has already been rejected twice
**I want** the plan refused when it proposes another instance of an approach that keeps failing
**So that** the loop asks whether the design is the defect, instead of asking only what is
wrong with this attempt

## Acceptance Criteria

### AC1: a repair in the same class as a previous round must declare retain-or-change

- **Given** a repair plan answering a finding the loop has already answered once
- **When** the plan is recorded
- **Then** it carries an explicit statement that the design is RETAINED or CHANGED with the
  reason, and a plan carrying neither is refused rather than stored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::DesignDecisionTests::test_a_repeat_class_plan_without_a_retain_or_change_statement_is_refused

### AC2: past the threshold a plan describing only a better instance is refused

- **Given** a class that has failed as many consecutive rounds as the configured threshold
- **When** a plan proposes another instance of the same approach, declaring the design RETAINED
- **Then** it is refused and names the rounds the class has already failed, so the refusal
  carries the evidence rather than a bare count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::DesignDecisionTests::test_past_the_threshold_a_retained_design_is_refused_and_names_the_failed_rounds

### AC3: RETAIN is a first-class answer below the threshold, and its reason is kept

- **Given** a repeat-class plan below the threshold that declares the design RETAINED with a reason
- **When** it is recorded
- **Then** it is accepted and the reason is stored with it, so a deliberate decision to keep an
  approach is distinguishable from nobody having asked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::DesignDecisionTests::test_a_reasoned_retain_below_the_threshold_is_accepted_and_its_reason_stored

### AC4: the threshold is configurable and its default states the evidence it rests on

- **Given** a project that declares no threshold
- **When** the default is resolved
- **Then** the value is accompanied by the evidence it was chosen from rather than presented as
  a bare number, and a project-declared value overrides it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::DesignDecisionTests::test_the_default_threshold_carries_its_basis_and_a_project_value_overrides_it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
