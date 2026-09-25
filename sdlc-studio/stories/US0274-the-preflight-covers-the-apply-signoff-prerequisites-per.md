# US0274: the preflight covers the apply-signoff prerequisites per unit, not just the gate lanes

> **Status:** Done
> **Delivers:** CR0359
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0089
> **Points:** 3

## User Story

**As an** operator closing a sprint
**I want** the preflight to cover the apply-signoff prerequisites per unit, not just the gate lanes
**So that** a unit missing a verdict or evidence is named before the close chain starts

## Acceptance Criteria

### AC1: the apply-signoff prerequisites are covered, not just the gate lanes

- **Given** a run whose batch units lack a recorded critic verdict, adversarial evidence, or an
  independent reviewer-of-record sign-off
- **When** the pre-flight runs
- **Then** each missing prerequisite is named per unit, alongside the gate lanes - these surface
  only after the whole chain has passed today, which is what made a close take four runs
- **Verify:** manual - retired by US0917: the per-unit sign-off preview is deleted; review coverage is the `review-coverage` pre-flight row, and the seal stops on a unit with no independent APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0917

### AC2: a unit covered by a sprint-level review is not reported as missing

- **Given** a batch unit with no per-unit verdict but covered by an independent sprint-level
  full-diff review
- **When** the pre-flight runs
- **Then** it is NOT reported as missing its critique, because sprint coverage satisfies that gate
  and a pre-flight that over-reports is as untrustworthy as one that under-reports
- **Verify:** manual - retired by US0917: the per-unit sign-off preview is deleted; review coverage is the `review-coverage` pre-flight row
- **Verified:** manual (2026-09-25) - retired, superseded by US0917

### AC3: the check asks the real authority, never its own copy of the rule

- **Given** the sign-off rules enforced by `critic`
- **When** the pre-flight evaluates them
- **Then** it calls `critic`'s own predicates rather than reimplementing independence, so the
  pre-flight and the gate cannot drift apart and disagree about the same unit
- **Verify:** manual - retired by US0917: the per-unit sign-off preview is deleted; the seal's review bar is `conformance.critiqued_unmet`
- **Verified:** manual (2026-09-25) - retired, superseded by US0917

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | US0917 | AC1-AC3 retired in the D0259 pattern: the per-unit sign-off preview is deleted |
