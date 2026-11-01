# US1103: The PRD's baseline reads v6.1.0 plus 6.2, no shipped feature row carries [Unreleased], and the inventory has a row for each capability shipped since July

> **Status:** Done
> **Delivers:** CR0647
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/US1103.md
> **Epic:** EP0293
> **Points:** 5
> **Depends on:** US1098, US1082
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the PRD's baseline to read v6.1.0 plus 6.2, no shipped feature row to carry [Unreleased], and the inventory to have a row for each capability shipped since July
**So that** the PRD no longer reads as frozen at v4.1, and the Product Owner sign-off can be given against it (RV0028 PRD-10)

## Acceptance Criteria

- **AC1:** Given the PRD, when it is read, then its baseline names v6.1.0 plus 6.2 on main and no feature row for a shipped capability carries [Unreleased]
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdBaselineTests::test_no_shipped_row_is_unreleased
  - **Verified:** yes (2026-11-01)
- **AC2:** Given the capabilities RV0028 PRD-10 names as shipped since July 2026, when the feature inventory is read, then each has a row
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdBaselineTests::test_every_capability_since_july_has_a_row
  - **Verified:** yes (2026-11-01)

## Notes

- Serves: Rowan Achterberg, End goal 3.
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, the PRD leg, PRD-10.
- AC1 must fail on: one [Unreleased] marker left on a shipped row, or an older baseline in the header.
- AC2 must fail on: one PRD-10 capability with no row. The capability set comes from RV0028's PRD-10 row as the test's named fixture, since no code enumerates capabilities.
- Overlap: US1104 edits prd.md and the same test module; deliver in sequence, after US1098. Covers CR0647 AC1 and AC2.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
| 2026-10-31 | Claude Opus 5.5 | Run-four plan (D0392): depends on US1082, which shares a file this unit declares |
