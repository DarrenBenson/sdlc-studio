# CR-0349: sprint plan cannot record a deliberate over-appetite batch, only silently raise the ceiling

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A 32-unit batch was 4x the unit appetite and 2.2x the token forecast. The only way to proceed is --appetite-units 32 --appetite-minutes 480, which RAISES the ceiling so the plan then reports the batch as fitting. The over-commitment disappears from the record at exactly the moment it is accepted: the close reads a plan that says 32/32, not one that says 32 against a standing appetite of 8. A retro asking why a run overran finds no trace of the decision.

## Impact

The appetite is the run-level circuit breaker. Raising it to fit the batch is indistinguishable, afterwards, from the batch having fitted - so the instrument records compliance rather than the deliberate breach it actually measured.

## Acceptance Criteria

- [ ] an over-appetite batch is recorded as over-appetite on the run state, with the standing appetite and the accepted one both kept
- [ ] the close and the retro report the over-commitment rather than the raised ceiling

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
