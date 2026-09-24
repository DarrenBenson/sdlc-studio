# US0909: A story reaches In Progress and Done without a plan review

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_json_report.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, tools/test-noise-baseline.json, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer running a sprint on the lean loop
**I want** a story to move from Ready to In Progress and Done with no plan-review verdict on record
**So that** no unit waits on a pre-code review that rejected 60% of plans over test apparatus rather than code (D0252)

## Acceptance Criteria

- **AC1:** Given a schema-v3 fixture story that cites a spec path and exceeds the old affects threshold, with no plan-review verdict and no override field, when `transition.py set` moves it to In Progress and then Done through the CLI, then neither move is refused and no output mentions plan review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_an_unreviewed_spec_story_is_not_refused
- **AC2:** Given the scripts tree, then `plan_review.py` does not exist and no shipped script imports it (including `project_upgrade.rebaseline` and `telemetry`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_nothing_imports_plan_review
- **AC3:** Given `critic.py brief` on a high-band unit and on a trivial unit, then the first is tiered `full` and the second `light`, read from `route.estimate`'s band now that `_difficulty_band` no longer lives in `plan_review.py`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_the_brief_tier_still_follows_the_route_band
- **AC4:** Given config-defaults.yaml, then it carries no `plan_review` block; the upgrade rebaseline of a v3 fixture reports no `plan-review` re-review entry and `telemetry.py show --summary --format json` has no `plan_review` key
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_no_plan_review_config_rebaseline_or_telemetry
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `plan_review.py check` or `plan_review.py record` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (`test_plan_review.py` and `test_lane_plan_review.py`; at least those on US0090, US0091, US0640, US0662, US0663), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
