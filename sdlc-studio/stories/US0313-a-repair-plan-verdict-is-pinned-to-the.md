# US0313: A repair-plan verdict is PINNED to the findings it answers, so a later finding invalidates it

> **Status:** Done
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py
> **Epic:** EP0106
> **Points:** 3

## User Story

**As a** reviewer of record
**I want** a plan verdict to name the exact findings it answered
**So that** a verdict cannot be stretched over findings nobody reviewed it against, which is
how `wsjf-inputs.json` once read as current judgement for weeks

## Acceptance Criteria

### AC1: a verdict carries a fingerprint of the finding set it answered

- **Given** a plan review recorded against a set of findings
- **When** the verdict is stored
- **Then** it carries a fingerprint derived from those findings, following the precedent
  `ac_fingerprint` already sets for pinning a story plan to its acceptance criteria
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

### AC2: a later finding invalidates the verdict

- **Given** a stored verdict, and a subsequent review round adding one finding
- **When** the gate is asked whether the plan is reviewed
- **Then** it answers no and names the finding the verdict does not cover, rather than
  reporting the plan as approved because a verdict exists
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

### AC3: an unchanged finding set leaves the verdict standing

- **Given** a stored verdict and a finding set re-read in a different order, with whitespace
  differing
- **When** the gate re-checks it
- **Then** the verdict still holds, so the pin discriminates a changed question from a
  re-serialised one and does not force a re-review on every read
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
