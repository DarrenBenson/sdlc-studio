# US0915: A review verdict has one phase: delivery

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer reading a sprint's review record
**I want** every recorded verdict to be a delivery verdict, with the plan-review phase, its Kind column, brief and footer gone
**So that** review rounds count one kind of review, so the report's rework figure means what it says

## Acceptance Criteria

- **AC1:** Given `critic.py record --phase plan-review` or `critic.py brief --phase plan-review`, when invoked, then each exits 2 with a message that plan review is retired and writes nothing, and neither `record --help` nor `brief --help` offers `--phase` or `--kind`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_the_plan_review_phase_is_retired
- **AC2:** Given a delivery verdict recorded with `critic.py record` and no phase flag, then `critic.py show` reads it back, and the two-round cap still counts it: a third round on the same unit is carried, not recorded as round 3
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_delivery_verdicts_still_record_and_count
- **AC3:** Given a `plan-review-verdicts.md` holding REJECT rows beside the delivery ledger, when the retro and the sprint report count review rounds, then only delivery verdicts are counted and the plan-review file's bytes are unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_rounds_count_delivery_verdicts_only
- **AC4:** Given every criterion whose stamped Verify selector names a test this story deletes (PlanCriticTests, PlanCriticIntensityTests, PlanReviewBriefTests and the plan-phase record tests in `test_critic.py`; at least those on BG0596, BG0645, BG0666, US0423, US0425), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
