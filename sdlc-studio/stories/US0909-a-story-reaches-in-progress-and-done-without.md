# US0909: A story reaches In Progress and Done without a plan review

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_json_report.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, tools/test-noise-baseline.json, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py, changelog.d/US0909.md, sdlc-studio/bugs/BG0510-the-plan-review-ledger-has-no-kind-column.md, sdlc-studio/bugs/BG0529-four-run-01kz9315-units-carry-no-verifier-that.md, sdlc-studio/bugs/BG0565-has-run-history-is-non-recursive-so-a.md, sdlc-studio/bugs/BG0567-the-upgrading-project-baseline-compares-against-this-tree.md, sdlc-studio/bugs/BG0637-critic-clean-escapes-underscores-inside-code-spans-corrupting.md, sdlc-studio/reviews/root-census.md, sdlc-studio/stories/US0090-deterministic-plan-review-trigger-and-gate.md, sdlc-studio/stories/US0091-plan-reviewer-charter-verdict-slot-and-telemetry.md, sdlc-studio/stories/US0094-upgrade-re-baseline-census-and-bucketed-report.md, sdlc-studio/stories/US0640-plan-review-honours-its-own-enabled-key-rather.md, sdlc-studio/stories/US0662-a-project-with-no-closed-run-reports-the.md, sdlc-studio/stories/US0663-the-softening-expires-on-run-history-alone-so.md, sdlc-studio/stories/US0684-every-consumer-of-route-estimate-asks-for-the.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer running a sprint on the lean loop
**I want** a story to move from Ready to In Progress and Done with no plan-review verdict on record
**So that** no unit waits on a pre-code review that rejected 60% of plans over test apparatus rather than code (D0252)

## Acceptance Criteria

- **AC1:** Given a schema-v3 fixture holding a committed `sdlc-studio/retros/RETRO0001-x.md` (so HEAD refuses rather than softens a first run), `plan_review.enabled` unset, and a story that cites a spec path and exceeds the old Affects threshold, with green executable criteria, an independent delivery APPROVE, no plan-review verdict and no override field, when `transition.py set` moves it to In Progress and then Done through the CLI, then neither move is refused and no output mentions plan review. Fails on: deleting only the Done-side check and leaving the In Progress entry gate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_an_unreviewed_spec_story_is_not_refused
  - **Verified:** yes (2026-09-25)
- **AC2:** Given the scripts tree, then `plan_review.py` does not exist, no shipped script imports it (including `project_upgrade.rebaseline`), and `telemetry.record_plan_review` does not exist. Fails on: deleting the module but leaving telemetry's writer, which never imported it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_nothing_imports_plan_review
  - **Verified:** yes (2026-09-25)
- **AC3:** Given `plan_review` blocked from import, when `critic.py brief` runs on a high-band unit and on a trivial unit, then the first is tiered `full` and the second `light`, `critic.tier_for` reading the band from `route.estimate` directly. Fails on: leaving `tier_for` calling `plan_review._difficulty_band`, which raises on the blocked import
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_the_brief_tier_still_follows_the_route_band
  - **Verified:** yes (2026-09-25)
- **AC4:** Given config-defaults.yaml, then it carries no `plan_review` block; the upgrade rebaseline of a v3 fixture reports no `plan-review` re-review entry; `telemetry.py show --summary --format json` has no `plan_review` key, and a telemetry log holding a historical plan-review event summarises with no `plan_review` key. Fails on: dropping the writer but leaving the summary block that still reads old events
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_no_plan_review_config_rebaseline_or_telemetry
  - **Verified:** yes (2026-09-25)
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `plan_review.py check` or `plan_review.py record` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_the_surface_names_no_retired_verb
  - **Verified:** yes (2026-09-25)
- **AC6:** Given the criteria whose stamped Verify selector names a test this story deletes (`test_plan_review.py`, `test_lane_plan_review.py`, UpgradeBaselineTests, PlanReviewGateTests, FirstRunPlanReviewSofteningTests and PlanReviewEventTests): BG0510 (2), BG0529 (1), BG0565 (1), BG0567 (5), BG0637 (1), US0090 (4), US0091 (1), US0094 (4), US0640 (5), US0662 (1), US0663 (1) and US0684 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0909: <why>`, `Verified: manual (<date>) - retired, superseded by US0909`), no `Verified: yes` selector under sdlc-studio/ names a deleted test node, and US0641's stamp survives because `BriefTierTests::test_an_unresolvable_band_tiers_full` is rewritten against `route.estimate` under the same name
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_review.py::PlanReviewGoneTests::test_no_stamp_names_a_deleted_test
  - **Verified:** yes (2026-09-25)

## Notes

- `route.py` is not edited: `tier_for` calls `route.estimate` directly.
- The shared prose edit to `reference-scripts-review.md` moved to US0924.
- Adjacent to US0911 in `transition._pre_write_gates` (1320-1395), so the two go in different waves.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC1 fixture holds a committed retro, an APPROVE and green criteria; AC2 adds `telemetry.record_plan_review`; AC3 blocks the `plan_review` import so it fails at HEAD; AC4 adds a historical telemetry event; AC6 names the measured stamps (28 criteria) and keeps US0641's; Affects adds reference-scripts-create.md, reference-upgrade.md and the changelog fragment, drops route.py and moves reference-scripts-review.md to US0924 |
