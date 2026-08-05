# BG0526: loop_guard budget has no programmatic caller: the appetite breaker is fully fed and pulled only if the driving agent remembers

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Established while surveying cycle-time machinery on 2026-08-05: run-state.json carries the appetite stamped at sprint.py:8263, and no non-documentation caller of the budget verb exists.
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`loop_guard.py budget` exits with `BUDGET_EXIT` when the appetite is spent. Its inputs are all present and stamped at plan time: `run-state.json` carries `appetite: {units, minutes, standing_units, standing_minutes, over_appetite}`. `record` and `status` are used indirectly - `handoff.py` imports `verdict`, `elapsed_minutes` and `units_consumed`.

`budget` has no caller. Searching every `.py`, `.sh` and `.md` under the skill, the only references are DOCUMENTATION telling an agent to run it: `reference-sprint.md:649` ("between units the loop runs `loop_guard.py budget --root .`") and `reference-config.md:264`. No code path in `sprint.py` or anywhere else invokes it.

So the circuit breaker that is supposed to stop a run exceeding its appetite is fully wired to its data and fires only if the agent driving the loop remembers to pull it. That is LL0027 in the registry - a gate belongs in the command people actually run, not in the step they are told to run - and this repo's stated failure mode is rules that were read and then not followed.

## Steps to Reproduce

1. `grep -rn 'loop_guard' --include='*.py' --include='*.sh' .claude/skills/sdlc-studio/` - the only `budget` hits are in reference docs.
2. Open a run with a small `--appetite-units`, deliver past it, and observe nothing refuses on the appetite unless `loop_guard.py budget` is invoked by hand.

## Proposed Fix

Call it from the per-unit loop the same way the close chain calls its steps - between units, on the shipped path, so exceeding the appetite refuses rather than depending on recall. Keep the existing exit code contract so an agent driving it by hand still behaves identically. The appetite is a RECORD of a decision made at plan time; a breaker nobody pulls turns that decision into a suggestion.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `loop_guard.py budget` exits with `BUDGET_EXIT` when the appetite is spent.
- [ ] The proposed fix lands, pinned by a test: Call it from the per-unit loop the same way the close chain calls its steps - between units, on the shipped path, so exceeding the appetite refuses rather than...

## Impact

A run can silently exceed the appetite the operator approved, which is exactly what the appetite exists to prevent. RUN-01KZ79C1 ran well past its original 480min/15units and the resize was recorded only because the agent chose to record it. Nothing would have refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
