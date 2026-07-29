# BG0392: open_run destroys the plan-side content review, so a prediction miss can never be reported

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`record_content_review` needs no open run and writes onto the blank state; `open_run` treats a state with no `run_id` as spent and replaces it. The natural order - review the plan, then write it - wipes the prediction with no warning, and `prediction_miss` is permanently None.

## Steps to Reproduce

`record_content_review(root`,'plan',...); `open_run(root`, batch=[...]); `content_reviews(root)[`'plan'] -> None

## Proposed Fix

Refuse to record a plan review with no run open, as `record_lane_start` does, or carry the key through `open_run.`

## Acceptance Criteria

### AC1: a plan-side review survives the plan being written

- **Given** a review recorded against an OPEN run, then a re-plan of that run
- **When** it runs
- **Then** the plan-side answer is still there, so the close can score its judgement against the prediction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContentReviewSurvivesThePlanTests::test_a_plan_review_survives_a_re_plan_of_the_open_run
- **Verified:** yes (2026-07-29)

### AC2: recording with no run open is refused, not written where it will be lost

- **Given** no run open
- **When** it runs
- **Then** the record is REFUSED, naming why - `open_run` treats a state with no run id as spent and blanks it, so the write would vanish silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContentReviewSurvivesThePlanTests::test_recording_with_no_run_open_is_refused
- **Verified:** yes (2026-07-29)

### AC3: the prediction miss is reportable once both ends exist

- **Given** a plan-side yes and a close-side partial on one run
- **When** it runs
- **Then** the miss is reported, which it never could be while the plan end was being destroyed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContentReviewSurvivesThePlanTests::test_the_miss_is_reportable_once_both_ends_exist
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
