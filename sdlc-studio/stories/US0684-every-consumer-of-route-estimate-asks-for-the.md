# US0684: Every consumer of route.estimate asks for the basis it can support, and a caller asking for a basis that does not resolve is refused rather than degraded

> **Status:** Draft
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

- [ ] **AC1** Given `route.estimate` called with the DECLARED basis, when it returns, then the band is computed from the unit's `Affects` and stated size, and the dict names the basis as declared - which is the only question a planner or a pre-code gate can ask
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_the_declared_basis_scores_from_affects_and_size
- [ ] **AC2** Given `route.estimate` called with the DIFF basis and a base ref against which the unit's hunks resolve, when it returns, then the band is computed from those hunks and the dict names the basis as diff
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_the_diff_basis_scores_from_the_hunks
- [ ] **AC3** Given `route.estimate` called with the DIFF basis where no diff resolves, when it returns, then it REFUSES rather than falling back to the declared basis - a silent degradation to a whole-file score is indistinguishable from the defect this epic removes, so the caller decides rather than the estimator
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_an_unresolvable_diff_basis_refuses_rather_than_degrading
- [ ] **AC4** Given `sprint.py` banding a batch, `plan_review._difficulty_band` deciding the pre-code gate and `handoff.py` seeding suitability, when each calls the estimator, then each asks for the declared basis and NONE of the three is refused for want of a diff that cannot exist yet
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::DifficultyBandTests::test_the_pre_code_callers_ask_for_the_declared_basis
- [ ] **AC5** Given `critic.py` choosing a review tier for a DELIVERED unit, when it calls the estimator, then it asks for the diff basis, and when that does not resolve it falls back to the existing unknown-band tier rather than to a whole-file score
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefTierTests::test_the_tier_asks_for_the_diff_basis
- [ ] **AC6** Given a caller that names no basis at all, when the estimator is called, then it REFUSES rather than choosing one - a default here would silently reinstate the conflation the two names exist to prevent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::EstimateBasisTests::test_an_unnamed_basis_is_refused

## Summary

Diff-scoping the estimator without changing its callers replaces a constant `full` band with a constant unresolvable one, because three of the four consumers run BEFORE the unit is implemented. This unit makes the basis explicit and makes each caller ask for the one it can support: `sprint.py` at plan time, `plan_review._difficulty_band` at the pre-code gate and `handoff.py`'s suitability seed take the DECLARED basis; `critic.py`'s tier selection, which runs against a delivered diff, takes the DIFF basis.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Created via `new` (deterministic) |
