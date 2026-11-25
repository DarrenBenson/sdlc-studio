# CR-0752: The run breaker reads spend as well as minutes and units: it warns at 75 and 95 per cent, lets the unit in flight finish, and a raise is a recorded decision

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py
> **Date:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T21:34:15Z

## Summary

`loop_guard budget` breaks a run on wall-clock minutes and unit count only; token capacity is checked once, at plan time, as a warning. Nothing stops a run whose spend passes its forecast while it runs: run twenty-six priced 146.4M tokens against a 105.1M forecast (1.39x, RPT0045) and run twenty-two 1.84x (RPT0041). The Claude-in-Foundry cost session recorded on 2026-11-24 (Controlling Claude Costs in Foundry) showed the shape a spend cap takes in a gateway: a warning at 75 and 95 per cent, the request in flight allowed to finish, the next refused, and every change to the cap logged with who made it and the value before and after. It also showed that gateway enforcing no cap by default when its store is down, which is a choice to state rather than inherit.

Proposed: a spend appetite (priced tokens or dollars, from `capacity.*`) joins the minutes and units `loop_guard budget` checks at each unit boundary. It warns at 75 and 95 per cent; at 100 per cent the unit in flight finishes and the next does not start; a raise mid-run names a decision id and records the value before and after. The reference says what the breaker does when the meter cannot read, since the session meter is a lower bound and delegated spend may be missing. This is the run-time guard behind the monthly budget CR0716 declares.

## Impact

The operator of an autonomous run learns that it overspent from the report after the close, not while the batch can still be cut, and a team that declares a monthly budget (CR0716) has no run-time guard behind it.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Raised |
