# US0064: Cross-script invariant test tier over the cascade seams

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0185

## User Story

**As a** skill maintainer
**I want** an invariant test tier over the cross-script cascade seams
**So that** defects like the RV0006 ones are caught by the suite next time, not by a review

## Acceptance Criteria

### AC1: Cascade invariants asserted

- **Given** one fixture repo
- **When** the invariant module runs
- **Then** it asserts one telemetry record per close, `new`-then-reconcile zero drift across every
  shipped index template, and CLI-vs-library allocation parity
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_invariants.py

### AC2: Written to the contract, proven to catch the bug

- **Given** the pre-fix code where a bug existed (BG0053/BG0060/BG0066)
- **When** the invariant runs against it
- **Then** it fails (proving it would have caught the regression)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_invariants.py -k regression

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
