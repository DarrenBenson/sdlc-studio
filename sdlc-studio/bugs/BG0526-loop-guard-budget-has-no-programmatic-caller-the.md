# BG0526: loop_guard budget has no programmatic caller: the appetite breaker is fully fed and pulled only if the driving agent remembers

> **Status:** Fixed
> **Verification depth:** functional (executed through the shipped CLI in a throwaway workspace: the breaker fires at a terminal transition when the appetite is spent, stays silent with budget remaining and with no appetite declared, and leaves the transition's exit code and record untouched; mutation: 4 declared mutants, all KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
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

- [x] **AC1** Given an open run whose appetite is spent, when a unit reaches a terminal status through the shipped `transition set`, then the breaker is pulled and the spend is reported - not left to whether the driving agent remembered.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k spent_appetite_is_reported
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given the same, when the transition runs, then it is REPORTED and not refused - the unit just finished, and what a boundary check stops is the next one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k reports_and_does_not_refuse
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given budget remaining, or no appetite declared at all, when a unit transitions, then nothing is printed - a line after every transition is one nobody reads on the day it matters.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k silent_when_there_is_nothing_to_say
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given a run state that cannot be read, when a unit transitions, then the transition still succeeds and prints no traceback - this is a report beside work already done, and it gates nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k unreadable_run_never_breaks
  - **Verified:** yes (2026-08-14)

## Impact

A run can silently exceed the appetite the operator approved, which is exactly what the appetite exists to prevent. RUN-01KZ79C1 ran well past its original 480min/15units and the resize was recorded only because the agent chose to record it. Nothing would have refused.

## Resolution

The premise was re-checked before anything was written: `budget_verdict` still had no caller outside `loop_guard.py` itself, so the finding stood.

The breaker is now pulled where a unit boundary actually happens - `transition.py set` reaching a terminal status - which is the command people run rather than the step a reference doc tells them to run.

It REPORTS rather than refuses, and that is the deliberate half. The unit whose transition triggers the check has already been delivered; blocking it would punish the wrong action and leave the record wrong as well. What a ceiling stops is the next unit starting, and the message says so, alongside the on-the-record way to move the ceiling (`sprint appetite resize`) rather than quietly overrun it.

It is also silent unless the appetite is actually spent, and silent when the run state cannot be read. Both are unusual for this repository, whose guards fail closed - and both are right here precisely because this gates nothing: a line printed after every transition is one nobody reads, and a report beside completed work must never turn a good transition into a traceback. `loop_guard budget` remains the verb that answers the question with an exit code.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in transition.py `cmd_set`, delete the `_report_appetite` call so nothing pulls the breaker | Given an open run whose appetite is spent, when a unit reaches a terminal status through the shipped `transition set`, then the breaker is pulled and the spend is reported - not left to whether the driving agent remembered. |
| AC2 | in transition.py `cmd_set`, return non-zero when the appetite is spent | Given the same, when the transition runs, then it is REPORTED and not refused - the unit just finished, and what a boundary check stops is the next one. |
| AC3 | in transition.py `_report_appetite`, drop the exhausted check and report every time | Given budget remaining, or no appetite declared at all, when a unit transitions, then nothing is printed - a line after every transition is one nobody reads on the day it matters. |
| AC4 | in transition.py `_report_appetite`, narrow the except so an unreadable run state escapes | Given a run state that cannot be read, when a unit transitions, then the transition still succeeds and prints no traceback - this is a report beside work already done, and it gates nothing. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Filed |
