# BG0392: open_run destroys the plan-side content review, so a prediction miss can never be reported

> **Status:** Open
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

- [ ] A plan-side content review survives the plan being written.
- [ ] Recording one with no run open is refused rather than written where it will be lost.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
