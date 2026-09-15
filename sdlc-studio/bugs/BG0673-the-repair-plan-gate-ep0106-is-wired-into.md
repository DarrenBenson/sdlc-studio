# BG0673: the repair-plan gate (EP0106) is wired into nothing: no command records a plan or verdict, and turning review.repair_plan_gate on refuses nothing a delivery command runs

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repair_plan.py` (EP0106, RFC0053, D0054) ships `record_repair_plan` (line 158), `review_repair_plan` (233) and `repair_gate` (298), and a `review.repair_plan_gate` setting (default off). None of the three has a caller outside `repair_plan.py` itself; its CLI offers only `brief` and `gate`, so neither a plan nor its verdict can be recorded by any command; `critic.repair_provenance` (critic.py:2957) is defined and never called. A project that turns the setting on gets no refusal from any command it actually runs - the shipped-but-unwired gate LL0027 names. CR0544 asks for a repair-approach review as if none existed; this is its prior art. Reproduced at 51f264db by grep and `repair_plan.py --help`; found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/repair_plan.py --help` - verbs are only {brief, gate}.
2. `grep -rn 'repair_gate\|record_repair_plan\|review_repair_plan' .claude/skills/sdlc-studio/scripts --include=*.py | grep -v /tests/` - every hit is inside `repair_plan.py.`
3. `grep -rn 'repair_provenance(' ... | grep -v 'def '` - no caller.

## Proposed Fix

Wire it (operator ruling, 2026-09-15 sprint planning): add record and review verbs to repair_plan.py, and call `repair_gate` from the transition that terminal-closes a repair unit when the setting is on. CR0544 asks for exactly this capability, so this builds on RFC0053's shipped half rather than replacing it.

## Acceptance Criteria

- [ ] **AC1** With `review.repair_plan_gate` on, the transition that terminal-closes a repair unit with no reviewed plan is refused, naming the gate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairGateIsReachableTests::test_the_gate_refuses_at_the_terminal_transition
- [ ] **AC2** A repair plan and its independent verdict can be recorded through a shipped command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairGateIsReachableTests::test_a_plan_and_verdict_record_through_the_cli
- [ ] **AC3** With the setting off, the terminal transition of a repair unit is unchanged - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::RepairGateIsReachableTests::test_the_gate_off_changes_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
| 2026-09-15 | sprint planning 2026-09-15 | Operator ruling at sprint planning: WIRE the gate, do not retire it. The retire alternatives are removed from the fix and the criteria. |
