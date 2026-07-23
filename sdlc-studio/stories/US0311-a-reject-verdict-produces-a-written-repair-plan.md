# US0311: A REJECT verdict produces a written repair plan, one entry per finding, naming the change, the approach and what it might break

> **Status:** Done
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Depends on:** BG0265, BG0256
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/repair_plan.py
> **Epic:** EP0106
> **Points:** 3

## User Story

**As an** agent repairing a rejected sprint
**I want** each finding answered by a written entry naming the change, the approach and what
it might break, before I edit anything
**So that** the approach is a thing that can be argued with, rather than a decision made
inside the edit and visible only afterwards

## Acceptance Criteria

### AC1: a REJECT verdict yields a repair plan with one entry per finding

- **Given** a recorded sprint-review verdict of REJECT carrying N findings
- **When** the repair plan is created for it
- **Then** the plan holds exactly N entries, each naming the finding it answers by id, and a
  plan with fewer entries than the verdict has findings is refused rather than accepted as
  partial - a silently unanswered finding is how a round's defects survive into the next
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairPlanTests::test_a_plan_missing_an_entry_for_any_finding_is_refused
- **Verified:** yes (2026-07-23)

### AC2: an entry that names no approach or no risk is refused before it is stored

- **Given** a repair-plan entry carrying a change but no stated approach, and a second
  carrying both but naming nothing it might break
- **When** the plan is created
- **Then** both are refused and nothing is written, because an entry without an approach is
  a restatement of the finding and an entry without a risk is an assertion that the repair
  is free - which is the belief every round from 3 to 10 of RUN-01KY3MFX held and lost
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairPlanTests::test_an_entry_without_an_approach_or_a_risk_is_refused
- **Verified:** yes (2026-07-23)

### AC3: a plan exists only for a verdict that actually rejected

- **Given** a recorded verdict of APPROVE
- **When** a repair plan is requested against it
- **Then** it is refused and names the verdict it found, so a repair plan cannot be
  manufactured to launder a change nobody rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairPlanTests::test_a_repair_plan_against_a_non_reject_verdict_is_refused
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
