# US0684: Every consumer of route.estimate asks for the basis it can support, and a caller asking for a basis that does not resolve is refused rather than degraded

> **Status:** Draft
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Delivers:** CR0549
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Epic:** EP0217
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** maintainer of a consuming project
**I want** every caller of the estimator to ask for the basis it can support
**So that** narrowing the band does not silently break the three callers that run before a diff exists

## Acceptance Criteria

- [ ] **AC1** Given `route.estimate` asked for the DECLARED basis, when it returns, then the score comes from `Points` and `Affects` breadth and the dict names the basis - the question a planner and a pre-code gate can actually ask
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_the_declared_basis_scores_from_points_and_affects
- [ ] **AC2** Given `route.estimate` asked for the DIFF basis with a base ref against which the unit's hunks resolve, when it returns, then `code` is hunk-scoped, `risk` declares itself file-level, and the dict names the basis
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_the_diff_basis_names_itself_and_scopes_code
- [ ] **AC3** Given the DIFF basis where no diff resolves, when it is asked for, then it REFUSES - and the refusal REACHES the caller rather than being swallowed. `plan_review._difficulty_band`, `sprint.py:1103` and `handoff._estimate` each catch a bare `Exception` today, so a refusal degrades silently at every existing site unless each is changed to distinguish a refusal from an unreadable unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::DifficultyBandTests::test_a_basis_refusal_reaches_the_caller_rather_than_being_swallowed
- [ ] **AC4** Given `plan_review._difficulty_band`, when it is called, then it takes the basis as a PARAMETER and passes it through - it is the single function both the pre-code gate and `critic.tier_for` reach the estimator by, so a basis that cannot travel through it cannot reach either
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::DifficultyBandTests::test_the_difficulty_band_takes_and_passes_a_basis
- [ ] **AC5** Given the three pre-code consumers - `sprint.py:1094`, `plan_review.py:106` and `:110`, `handoff.py:308` - when each calls the estimator, then each asks for the declared basis and none is refused for want of a diff that cannot exist yet
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlannerBandTests::test_the_planner_asks_for_the_declared_basis
- [ ] **AC6** Given `critic.tier_for` choosing a tier for a DELIVERED unit, when it calls through `_difficulty_band`, then it asks for the diff basis, and on a refusal it falls back to the existing unknown-band tier rather than to a whole-file score
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_tier_asks_for_the_diff_basis
- [ ] **AC7** Given the callers no earlier list named - `project_upgrade.py:706`, `route.pick` at `route.py:229` and the shipped `estimate` CLI - when the basis parameter lands, then each is MIGRATED and keeps working. `project_upgrade.rebaseline_apply` is exercised by the v4-upgrade lane of `tools/rehearse-release.sh`, which binds at the release boundary, so breaking it fails a boundary gate rather than a unit test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RebaselineBandTests::test_the_backfill_asks_for_the_declared_basis
- [ ] **AC8** Given every existing call in the suite that names no basis, when the change lands, then each is migrated rather than left to a default - a default reinstates the conflation the two names exist to prevent, and eight existing tests plus the CLI call it that way today
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_no_caller_in_the_tree_asks_for_an_unnamed_basis

## Summary

Diff-scoping the estimator without changing its callers replaces a constant `full` band with a constant unresolvable one, because three of the four consumers run BEFORE the unit is implemented. This unit makes the basis explicit and makes each caller ask for the one it can support: `sprint.py` at plan time, `plan_review._difficulty_band` at the pre-code gate and `handoff.py`'s suitability seed take the DECLARED basis; `critic.py`'s tier selection, which runs against a delivered diff, takes the DIFF basis.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
