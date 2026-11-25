# BG1649: lane accept returns before lane return when its transition fails, so a unit finished by hand stays in flight and its span reads NOT MEASURED

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1649.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T04:43:48Z

## Summary

RUN-01M7TTK3, US1299: lane accept recorded the round-two APPROVE, ran `verify_ac`, then transition.py set refused Done (AC3 had no Verify line). lib/lanes.py returns 1 at that point (lines 980-984), before the 'sprint.py lane return' call that clears the unit from run-state `lanes_in_flight` and closes its span. The unit was then moved to Done by hand with transition.py, which does not touch the lane marker, so the close printed 'US1299's lane was briefed and never returned - its span is left open and reads NOT MEASURED' and 'IN FLIGHT at close: US1299 ... its work may be in this tree unattributed', though its repair had landed in 2aa31057 and its return was priced. Neither lane accept's refusal nor the close names 'sprint.py lane return --units X' as the step that finishes it.

## Steps to Reproduce

Groom a unit with one criterion lacking a Verify line, land it, and run sprint.py lane accept on an APPROVE verdict: the transition refuses. Move it with transition.py set --status Done. Run sprint.py close: the unit is reported briefed and never returned.

## Proposed Fix

When the transition refuses after an APPROVE, name the finishing command in the refusal ('after fixing it, run transition.py set ... then sprint.py lane return --units X'), or have lane accept accept a --resume that re-runs only the transition and the return; and have the close's in-flight note say which command clears a lane whose unit is already terminal.

## Acceptance Criteria

- [ ] **AC1** Given an APPROVE whose `transition.py set` refuses, when `lane accept` prints its refusal, then it names the finishing step (`transition.py set ...` then `sprint.py lane return --units <ID>`). Fails on: the `transition.py set` branch of `_accept` names no next step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_refused_transition_names_the_lane_return_that_finishes_the_unit
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given a unit finished by hand after that refusal and still in `lanes_in_flight`, when `sprint.py close` runs, then its in-flight note names `sprint.py lane return --units <ID>` as the command that clears a lane whose unit is already terminal. Fails on: the note says only that the span reads NOT MEASURED.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightCloseTests::test_a_terminal_unit_in_flight_names_the_lane_return_that_clears_it
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** Given the same unit, when `sprint.py lane return --units <ID>` is run after the hand transition, then the unit leaves `lanes_in_flight` and its span closes (positive control for the named command). Fails on: a named command that does not clear the lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_lane_return_after_a_hand_transition_clears_the_lane
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: the proposed fix offers two routes; the criteria take the first (name the finishing command, also in the close note), so a `--resume` flag is not required; points raised to 3 for two surfaces and three tests (split if the builder adds `--resume`) |
