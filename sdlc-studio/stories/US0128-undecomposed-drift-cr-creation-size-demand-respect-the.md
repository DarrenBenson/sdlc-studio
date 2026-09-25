# US0128: undecomposed drift + CR-creation Size demand respect the gate

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0034
> **Points:** 3

## User Story

**As an** operator on a project that has not opted into the two-backlog workflow
**I want** `reconcile` not to flag my childless CRs, and CR creation to keep the legacy points flow
**So that** upgrading the skill does not fill my drift report or refuse my CR creation until I opt in.

## Acceptance Criteria

### AC1: undecomposed drift surfaces only when enforced

- **Given** an accepted (Approved) childless CR, in an enforced project and an unenforced one
- **When** `reconcile detect` runs
- **Then** the enforced project reports it as `undecomposed`; the unenforced project does not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::EnforcementGateTests::test_undecomposed_drift_only_surfaces_when_enforced
- **Verified:** yes (2026-07-15)

### AC2: CR creation keeps the legacy points flow when not enforced

- **Given** `artifact new --type cr --points 5` in an enforced project and an unenforced one
- **When** the CR is created
- **Then** the unenforced project writes `Points` and grooms (legacy flow); the enforced project holds the strict Size demand and refuses it
- **Verify:** manual - retired by US0900: an unsized CR is no longer refused at filing; sprint plan still refuses it
- **Verified:** manual (2026-09-24) - retired, superseded by US0900

### AC3: an unenforced project writes a CR's legacy points

- **Given** `artifact new --type cr --points 5` in an enforced project and an unenforced one
- **When** the CR is created
- **Then** the unenforced project writes `Points` (legacy flow); the enforced project writes no `Points` onto the request and warns that `--points` was ignored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::EnforcementGateTests::test_unenforced_cr_creation_keeps_the_legacy_points_flow
- **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | US0900 | AC2 split: its refusal half is retired - an unsized CR is now written; refine sizes the epic it writes, never the CR. Sprint plan still demands a size when the CR itself is planned directly. The legacy-points half, still true, is AC3 with the kept test |
