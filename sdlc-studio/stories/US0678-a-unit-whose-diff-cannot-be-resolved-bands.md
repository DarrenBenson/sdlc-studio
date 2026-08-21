# US0678: A unit whose diff cannot be resolved bands FULL and names the basis the estimate used

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A unit whose diff cannot be resolved bands FULL and names the basis the estimate used
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose diff cannot be resolved - no base ref, no git history, or an unreadable tree - when it is scored, then it bands FULL and the returned dict names the basis it used, preserving the existing rule that unknown risk fails towards the deeper review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_an_unresolvable_diff_bands_full_and_names_its_basis
- [ ] **AC2** Given any estimate, when it returns, then the dict states whether the score came from the DIFF or from the whole file, so a reader can tell a measured band from a degraded one - the two are different facts and a caller that cannot distinguish them will trust both equally
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_the_estimate_names_diff_or_whole_file_as_its_basis

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
