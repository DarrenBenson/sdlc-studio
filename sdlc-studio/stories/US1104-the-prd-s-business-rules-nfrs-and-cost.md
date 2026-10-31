# US1104: The PRD's business rules, NFRs and cost model match the code, its derived counts are bands, and the engagement floor reads Partial until BG0959 is Fixed

> **Status:** Ready
> **Delivers:** CR0647
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/US1104.md
> **Epic:** EP0293
> **Points:** 3
> **Depends on:** US1103
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the PRD's business rules, NFRs and cost model to match the code, its derived counts to be bands, and the engagement floor to read Partial until BG0959 is Fixed
**So that** the PRD states only requirements the product holds (CR0647)

## Acceptance Criteria

- **AC1:** Given the code, when the PRD's business rules, NFRs and cost model are read, then they match it: the delivery units that execute Verify lines, the groomed definition, the network paths, the read-only set and the measured tokens-per-point rate
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_rules_nfrs_and_cost_model_match_the_code
- **AC2:** Given a derived count in the PRD, when it is read, then it is stated as a band per the PRD's own rule, and per-ship history sits in the changelog table, not in feature blocks
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_derived_counts_are_bands
- **AC3:** Given BG0959's status, when the PRD's engagement-floor row is read, then it reads Partial while BG0959 is open, and the verified detail criteria are ticked
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_the_engagement_floor_tracks_bg0959

## Notes

- Serves: Rowan Achterberg, End goal 3.
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, the PRD leg.
- AC1 must fail on: the PRD naming a type outside `sdlc_md.EXECUTES_VERIFIERS` as executing, or omitting one inside it; each fact is read from code.
- AC2 must fail on: a pinned derived count (a bare integer where the rule asks for a band).
- AC3 must fail on: the floor reading Complete while BG0959 is open; BG0959's status is read from its file.
- Overlap: US1103. US1102 maps these NFRs, so deliver this before US1102. Covers CR0647 AC3-AC5.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
