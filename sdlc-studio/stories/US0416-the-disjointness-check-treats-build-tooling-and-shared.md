# US0416: the disjointness check treats build tooling and shared config as coupling, not as ordinary files

> **Status:** Review
> **Delivers:** CR0415
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a unit touching build tooling is never offered as parallel-safe

- **Given** a file-disjoint batch where one unit touches build tooling
- **When** the delivery-mode offer is computed
- **Then** a unit touching build tooling is never offered as parallel-safe
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeBuildToolingCouplingTests::test_a_unit_touching_build_tooling_is_never_parallel_safe
- **Verified:** yes (2026-07-24)

### AC2: the set of build-tooling paths is declared, not inferred by name

- **Given** the build-tooling coupling rule
- **When** a path's membership is decided
- **Then** the set of build-tooling paths is declared, not inferred by name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeBuildToolingCouplingTests::test_the_build_tooling_set_is_declared_not_inferred_by_name
- **Verified:** yes (2026-07-24)

### AC3: the contract is documented where the mode is documented

- **Given** the delivery-mode section of reference-sprint.md
- **When** the build-tooling coupling is looked for there
- **Then** the contract is documented where the mode is documented
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeBuildToolingCouplingTests::test_the_contract_is_documented_where_the_mode_is
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
