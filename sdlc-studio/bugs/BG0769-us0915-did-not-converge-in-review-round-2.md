# BG0769: US0915 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, changelog.d/US0915.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, sdlc-studio/bugs/BG0510-the-plan-review-ledger-has-no-kind-column.md, sdlc-studio/bugs/BG0596-testplan-run-from-plan-keys-by-criterion-so.md, sdlc-studio/bugs/BG0631-a-repair-row-names-neither-the-rejection-nor.md, sdlc-studio/bugs/BG0645-critic-py-brief-rejoinder-ignores-phase-plan-review.md, sdlc-studio/bugs/BG0666-an-unauthored-test-plan-row-is-exempt-from.md, sdlc-studio/stories/US0631-the-test-plan-is-reviewed-by-an-independent.md, sdlc-studio/stories/US0634-the-cost-is-measured-over-one-run-and.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T10:39:48Z

## Summary

US0915 was rejected at round 2, the review cap, by qa-rev-US0915, so it was carried as a known issue rather than reviewed again. The findings still open: [new] the repair's over-claim guard in test\_no\_stamp\_names\_a\_deleted\_test flags any yes-stamped criterion naming --phase plan-review including US0915 AC1 which asserts the refusal, so main goes red once US0915 is stamped Done, fix about 2 lines [LC-002]; [new] non-blocking: the guard matches only the literal flag so prose naming a plan-review rejoinder passes; [new] non-blocking: BG0666 AC3, BG0671 AC4 and BG0672 AC1 Test Plan rows still name mutants of deleted plan-review code; [pre-existing] non-blocking: reference-review.md and reference-scripts-review.md still describe plan review (US0924)

## Steps to Reproduce

1. Read the round 2 REJECT of US0915 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0915 again in a later run.

## Acceptance Criteria

- [ ] **AC1** Given US0915's carried work applied onto main and its own criteria stamped `Verified: yes` (as Done writes them), then `test_lean_no_plan_phase.py` passes: the over-claim guard does not flag US0915 AC1, which asserts the refusal. Fails on: the round-2 guard, which lists `US0915 AC1` twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py
- [ ] **AC2** Given a yes-stamped criterion that claims `--phase plan-review` still runs (BG0672 AC1's removed clause restored), then the guard still flags it. Fails on: an exemption wide enough to pass every criterion that names the flag
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py::PlanPhaseGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Engineering seat | Groomed: two executable criteria for landing US0915's carried work with the guard's false positive fixed; added to RUN-01M3BK9Y's batch as BG0767 was for US0909 |
