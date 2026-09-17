# CR-0588: run_state readers cannot tell a field that is empty from a field the schema never had, so a typo reads as a state

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RUN-01M2JA6J close, 2026-09-16: `closed_at` read as None on a run whose outcome was goal-reached and whose ended_at was 12:51:09Z; run_state.FIELDS carries no such key.
> **Date:** 2026-09-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`run_state.FIELDS` documents the record's fields and the module's docstring says the list documents rather than gates. A reader asking for a key that is not in FIELDS gets `None`, which is exactly what a real field holds before it is written. At the RUN-01M2JA6J close the authoring session read `closed_at` - a field this schema has never had, the closed signal being `outcome` in `run_state.CLOSED` plus `ended_at` - saw None, and reported the run as unsealed four times over roughly an hour. Three further close attempts were run against a condition that was already true, one of them spending the loop guard's last round and producing a cap refusal that went to the operator as a decision. The record was correct throughout; only the reader was wrong, and nothing in the tooling could say so.

## Impact

Anyone reading run state programmatically, and every agent that reports a run's status from it. A misspelt or imagined key is indistinguishable from an unwritten one, so a false state can be reported with complete confidence and no error.

## Acceptance Criteria

- [ ] `run_state` exposes a reader that refuses a field absent from FIELDS, naming the unknown key and the nearest known one
- [ ] a helper answers whether a run is closed from the outcome vocabulary, so no caller re-derives it
- [ ] the refusal is proven on the exact mistake that produced this CR - reading `closed_at` on a closed run - beside the correct read, which must pass

## Recommendation

Give the module a strict reader - `run_state.get(state, field)` - that refuses a key absent from FIELDS, naming it and the closest match, and use it wherever a state is REPORTED rather than merely defaulted. Leave the permissive dict access for forward-compatible writers, which the docstring already explains. A helper that answers `is_closed(state)` from the outcome vocabulary would remove the most common hand-rolled version of this question.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Raised |
