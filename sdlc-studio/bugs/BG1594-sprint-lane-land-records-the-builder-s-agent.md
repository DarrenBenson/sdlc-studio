# BG1594: sprint lane land records the builder's agent id as the self-check author instead of the building seat, so lane accept writes a verdict row the retro cannot score as a seat's

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** lane accept US1317, 2026-11-18: 'critic.py record: WARNING: author agent-adf464901f9fa8e86 lacks the <holder> (<role>) form'.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:19:48Z

## Summary

For US1316 and US1317 in run seventeen, `sprint lane land` recorded the self-check, and `sprint lane accept` then recorded the APPROVE with author 'agent-adf464901f9fa8e86' and warned that it lacks the `<holder> (<role>)` form. The lane brief names the building seat (Dani Okafor (engineering)) and says the review brief's record command names it as the author, but the land does not carry it through.

## Steps to Reproduce

Land a unit with `sprint lane land`, then `sprint lane accept --unit <id> --verdict <file> --reviewer 'Sam Eriksson (qa)'`: the record warns that the author agent-<id> lacks the `<holder> (<role>)` form.

## Proposed Fix

Record the lane brief's building seat as the self-check author at land, and have lane accept read it, so the verdict row names the seat.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: For US1316 and US1317 in run seventeen, `sprint lane land` recorded the self-check, and `sprint lane accept` then recorded the APPROVE with author...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Land a unit with `sprint lane land`, then `sprint lane accept --unit <id> --verdict <file> --reviewer 'Sam Eriksson (qa)'`: the record warns that the author...
- [ ] **AC3** The proposed fix lands, pinned by a test: Record the lane brief's building seat as the self-check author at land, and have lane accept read it, so the verdict row names the seat.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
