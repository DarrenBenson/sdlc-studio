# BG1440: lane return --model with no total is dropped without a word, the model trim is untested, and help/sprint.md omits that a several-unit total is not split when a unit has no Points

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_return_model_edges.py, changelog.d/BG1440.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of US0999, qa-seat-US0999-r1, verdict sdlc-studio/reviews/verdicts/US0999/2ebec7ba6f15-a12df297.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T03:20:46Z

## Summary

Run twelve's US0999 review (APPROVE, non-blocking): `sprint lane return --model <m>` given with no `--tokens`/`--agent` total is dropped silently (unchanged from before US0999); no test pins the trimming of the model string the recorders apply; and the help/sprint.md sentence corrected this run says a total given for several units is split by points without saying that a unit with no Points leaves the total unrecorded (BG1397's refusal).

## Steps to Reproduce

Run `sprint lane return --units US0101 --model claude-opus-5-5` with no total: it exits 0 and says nothing about the model.

## Proposed Fix

Say in one line that a model with no total is not recorded; pin the trim with a padded model string; add the no-Points clause to the help sentence.

## Acceptance Criteria

- [ ] **AC1** Given `lane return --model` with no total, when it runs, then it prints one line saying the model was not recorded because no total was given. Fails on: silence.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_model_edges.py::LaneReturnModelEdgeTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A lone --model is dropped silently; workaround is to pass a total.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
