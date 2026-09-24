# US0585: The claim-drift lane runs in the commit gate as advisory, and its yield over one sprint is recorded before any decision to make it block

> **Status:** Done
> **Delivers:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/tests/test_precommit_claim_drift.py, tools/tests/test_precommit_lane_order.py, AGENTS.md
> **Epic:** EP0195
> **Points:** 3

## User Story

**As a** operator paying for the commit gate
**I want** the claim-drift lane advisory while its yield is measured
**So that** a new lane on a gate already over its ceiling earns its block on evidence

## Acceptance Criteria

### AC1: the lane runs in the commit gate and reports without blocking

- **Given** a staged diff carrying a claim contradiction
- **When** `git commit` is run for real in a fixture clone with the shipped hooks enabled
- **Then** the finding is printed and the commit LANDS, because a new lane on a gate already over its ceiling must earn a block on measured evidence rather than assertion
- **Verify:** manual - retired by US0879: the advisory claim-drift lane was deleted as a docs-against-docs lane that caught nothing
- **Verified:** manual (2026-09-24) - retired, superseded by US0879

### AC2: the lane is named in the gate roster

- **Given** AGENTS.md's pre-commit lane roster
- **When** the lane ships
- **Then** the roster names it, and `test_precommit_claim_drift.py` pins that naming, so the list cannot silently exempt what it forgot
- **Verify:** manual - retired by US0879: the advisory claim-drift lane was deleted as a docs-against-docs lane that caught nothing
- **Verified:** manual (2026-09-24) - retired, superseded by US0879

### AC3: its yield is recorded before any decision to block

- **Given** a run in which the lane raised findings
- **When** the sprint report is composed
- **Then** it carries the count the lane raised and how many became filed defects, so a later decision to make the lane blocking has a number to read. The DECISION itself is explicitly out of this sprint - the lane ships here, so a sprint's worth of yield cannot exist yet, and asserting otherwise would tick a criterion over a surface this diff does not touch, which is what US0584 flags
- **Verify:** manual - retired by US0879: the advisory claim-drift lane was deleted as a docs-against-docs lane that caught nothing
- **Verified:** manual (2026-09-24) - retired, superseded by US0879

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
