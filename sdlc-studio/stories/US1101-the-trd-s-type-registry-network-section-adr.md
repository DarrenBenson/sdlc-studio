# US1101: The TRD's type registry, network section, ADR-003, ADR-009, ADR-012 and header match what is built on 6.2

> **Status:** Ready
> **Delivers:** CR0645
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, changelog.d/US1101.md
> **Epic:** EP0293
> **Points:** 5
> **Depends on:** US1100
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the TRD's type registry, network section, ADR-003, ADR-009, ADR-012 and header to match what is built on 6.2
**So that** nothing in the TRD's design record is months behind the code (RV0028 TRD-7, TRD-8 and the ADR findings)

## Acceptance Criteria

- **AC1:** Given the type registry in code, when the TRD's registry is read, then it lists `charter` with its vocabulary and names `META_TYPES`
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdRegistryNetworkTests::test_the_type_registry_matches_the_code
- **AC2:** Given every script that calls `gh`, when the TRD's network section is read, then each caller is listed and the version-check GET is recorded as an ADR-004 exception
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdRegistryNetworkTests::test_every_gh_caller_is_listed
- **AC3:** Given ADR-003, ADR-009 and ADR-012, when they are read, then each matches what is built, ADR-012 carries a revision row, and the header's coverage line names v6.1.0 plus 6.2 on main
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdRegistryNetworkTests::test_the_adrs_and_header_match_6_2

## Notes

- From BG1065 (2026-11-01): trd.md:675 still says 'Every run in this repository now exceeds it (BG1065)'. Since BG1065, the budget is recorded beside a measured standard run (gate.py GATE_BUDGET_MEASURED, 39.8s against 45s) and a push judges only the standard lanes against it. Correct that sentence in this unit, which owns trd.md.
- Serves: Rowan Achterberg, End goal 3.
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, findings TRD-7 and TRD-8 and the ADR rows.
- AC1 must fail on: a type in the code registry or in `META_TYPES` missing from the TRD; both sets are read from the code.
- AC2 must fail on: a `gh` caller added to a script and not to the TRD; the caller set is read by scanning the scripts, with a known member asserted first (LL0043).
- AC3 must fail on: ADR-012 with no revision row, or a header naming an older baseline.
- Overlap: US1099 and US1100. Covers CR0645 AC3 and AC4.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
