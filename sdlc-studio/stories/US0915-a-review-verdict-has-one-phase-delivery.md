# US0915: A review verdict has one phase: delivery

> **Status:** Draft
> **Depends on:** US0909, US0911, US0913 - each reads verdicts with phase plan-review (EP0263 readiness)
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, changelog.d/US0915.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, sdlc-studio/bugs/BG0510-the-plan-review-ledger-has-no-kind-column.md, sdlc-studio/bugs/BG0596-testplan-run-from-plan-keys-by-criterion-so.md, sdlc-studio/bugs/BG0631-a-repair-row-names-neither-the-rejection-nor.md, sdlc-studio/bugs/BG0645-critic-py-brief-rejoinder-ignores-phase-plan-review.md, sdlc-studio/bugs/BG0666-an-unauthored-test-plan-row-is-exempt-from.md, sdlc-studio/stories/US0631-the-test-plan-is-reviewed-by-an-independent.md, sdlc-studio/stories/US0634-the-cost-is-measured-over-one-run-and.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer reading a sprint's review record
**I want** every recorded verdict to be a delivery verdict, with the plan-review phase, its Kind column, brief and footer gone
**So that** review rounds count one kind of review, so the report's rework figure means what it says

## Acceptance Criteria

- **AC1:** Given `critic.py record --phase plan-review` or `critic.py brief --phase plan-review`, when invoked, then each exits 2 with a message that plan review is retired and writes nothing, and none of `record`, `brief`, `supersede` or `show` offers `--phase` or `--kind` in its `--help`; a delivery verdict recorded with no phase flag is read back by `critic.py show`, and a third round on the same unit is still carried, not recorded as round 3. Fails on: hiding the flags from `record` and `brief` only, and on a deletion that breaks the delivery path or the two-round cap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_the_plan_review_phase_is_retired
- **AC2:** Given a `plan-review-verdicts.md` holding REJECT rows beside the delivery ledger, when the retro and the sprint report run, then the retro's review split names no test-plan-review arm, the sprint report's rework figure is unchanged from the same run without that file (control), and the plan-review file's bytes are unchanged. Fails on: HEAD's `retro.review_cost_split`, which still reports a plan-review arm
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_rounds_count_delivery_verdicts_only
- **AC3:** Given the criteria whose stamped Verify selector names a test this story deletes (PlanReviewBriefTests, PlanReviewBriefUnauthoredNoteTests, PlanReviewKindTests, PlanReviewOriginTests, PlanReviewBriefTeachesMultiRowTests, the plan-review test in RepairPhaseJoinTests, `test_retro.py::PlanVersusCodeReviewCostTests` and `test_sprint.py`'s `test_a_plan_review_round_does_not_inherit_delivery_batch_rounds`): BG0510 (8), BG0596 (1), BG0631 (1), BG0645 (2), BG0666 (1), US0631 (3) and US0634 (2), then each is retired in the D0259 pattern (`Verify: manual - retired by US0915: <why>`, `Verified: manual (<date>) - retired, superseded by US0915`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Engineering call, which holds the size at 5: `phase` stays as an internal parameter defaulting to `delivery`, and only the CLI surface, the plan-review brief and the Kind column go. Stripping the whole API would be 8 points.
- The old AC2 (delivery verdicts still record and count) passed at HEAD, so it is now the control half of AC1. The sprint-report half of the old AC3 already passed (the report reads only `critic-verdicts.md`), so it is the control in AC2.
- `PlanCriticTests` and `PlanCriticIntensityTests` (US0423, US0425) pin `plan_critique`, the pre-plan lens pass, not this phase. They stay.
- Lands after US0909, US0911 and US0913, which each call `verdict_for` or `read_verdicts` with `phase="plan-review"`, and before US0912 and US0914.
- The shared prose edit to `reference-scripts-review.md` moved to US0924.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 5 points held with `phase` kept internal; AC1 covers record, brief, supersede and show, and takes the old AC2 as its control; AC2 names the retro's test-plan arm and keeps the report as control; stamps set corrected (PlanCriticTests dropped) and measured (18 criteria); Affects adds test_sprint.py and the changelog fragment, and moves reference-scripts-review.md to US0924 |
