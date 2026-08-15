# BG0580: ten units reached a terminal status and were signed off with test plans whose mutants were never executed, and five of those plans are still scaffold placeholders

> **Status:** Fixed
> **Verification depth:** functional (all 35 outstanding mutants across the ten units executed and killed, and the five scaffold plans authored from the mutants their own criteria already stated in prose; three mutants re-chosen after surviving and one verdict retracted on the record after being registered before it was confirmed; the gate question - whether transition->Fixed binds at the transition or was bypassed ten times - is NOT established and is carried)
> **Severity:** High
> **Points:** 8
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** RUN-01KZQ03V close, 2026-08-15. `sprint close --dry-run` at f79e0d38 raised ten done-gate stops; the placeholder count was taken with grep over the five artefacts.
> **Created:** 2026-08-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-14T01:30:38Z

## Summary

`sprint close` refuses on ten units of the open run's batch - BG0488, BG0497, BG0522, BG0523, BG0528, BG0536, BG0542, BG0543, BG0557, BG0569 - each carrying planned mutants that were never executed. Five of them (BG0488, BG0497, BG0522, BG0523, BG0528) still hold `{{name the production change this test must fail on}}` in their Test Plan rows, 26 placeholder rows in total, so the plan was never authored at all. Each of these units is Fixed, and each was signed off. The paperwork reads complete and is not: a plan whose rows are optional measures nothing, and a placeholder row measures less than nothing because it looks like a plan. This is BG0577's class - a claim nothing exercises - pointed at the evidence ledger rather than at the backlog.

## Acceptance Criteria

- [x] **AC1** Given each of the ten units this bug names, when `mutation.py run --story <id> --from-plan` is asked, then every planned mutant is executed and killed - a plan whose rows are optional measures nothing.
  - **Verify:** shell test $(for u in BG0488 BG0497 BG0522 BG0523 BG0528 BG0536 BG0542 BG0543 BG0557 BG0569; do python3 .claude/skills/sdlc-studio/scripts/mutation.py run --root . --story $u --from-plan 2>&1 | grep -c "never executed" || true; done | paste -sd+ | bc) -eq 0
  - **Verified:** yes (2026-08-15)
- [x] **AC2** Given the same ten units, when `sprint close --dry-run` runs, then none of them raises a done-gate stop.
  - **Verify:** shell test $(for u in BG0488 BG0497 BG0522 BG0523 BG0528 BG0536 BG0542 BG0543 BG0557 BG0569; do python3 .claude/skills/sdlc-studio/scripts/transition.py requirements --id $u --status Fixed 2>&1 | grep -c "unaccounted for" || true; done | paste -sd+ | bc) -eq 0
  - **Verified:** yes (2026-08-15)

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/sprint.py close --dry-run` - ten `STOP done-gate` lines, one per unit. 2. `python3 .claude/skills/sdlc-studio/scripts/mutation.py run --story BG0488 --from-plan` - AC1, AC3, AC4 and AC5 report `was PLANNED and never executed`. 3. `grep -c '{{name the production' sdlc-studio/bugs/BG0488-*.md` returns 6. Measured 2026-08-15 at f79e0d38.

## Proposed Fix

Two halves, and the second is the one that matters. FIRST, author the 26 placeholder rows and execute every planned mutant across the ten units, or record a deliberate deferral per unit rather than one blanket ruling. SECOND, and the actual repair: `transition -> Fixed` already refuses a unit whose planned mutants are unaccounted for - that gate fired here, at the CLOSE, long after the units went terminal. Establish why ten units passed it individually and are refused collectively, because one of the two readings is wrong and the difference decides whether this is ten instances of author error or one gate that does not bind when it is supposed to.

## Impact

The close cannot complete, which is how this surfaced. The larger cost is that ten units carry recorded sign-off against evidence nobody produced - and a sign-off is the artefact this repository treats as the strongest claim it makes. Every figure derived from those ten - the run's delivered count, its velocity row, the mutation-coverage lane - is computed over plans that were never executed.

## Resolution

All 35 outstanding mutants across the ten units were executed and killed, and the five scaffold
plans were authored from the mutants their own criteria already stated in prose - several
criteria named the production change explicitly ("the mutant is deleting the check's call from
`close_preflight`") while the plan table beside them still held a placeholder.

Three mutants had to be re-chosen after surviving, and one verdict was registered before it was
confirmed and then RETRACTED on the record. That last one is the same error three times over in
this run, and it has one cause: registering outside the branch that checks the result. The
helper used for the remaining thirty registers only inside the killed branch.

**The second half of this bug is NOT closed by that work and is the part worth keeping.**
`transition -> Fixed` refuses a unit whose planned mutants are unaccounted for, and it fired here
at the CLOSE rather than at any of the ten transitions. Ten units passed it individually and were
refused collectively, so either the gate does not bind at the transition or it was bypassed ten
times. Which of those is true is not established, and it decides whether this was ten author
errors or one inert gate. Carried as its own question.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | leave any one of the ten units' planned mutants unexecuted - from-plan names it again | Given each of the ten units this bug names, when `mutation.py run --story <id> --from-plan` is asked, then every planned mutant is executed and killed - a plan whose rows are optional measures nothing. |
| AC2 | leave any one unit's planned mutants unaccounted - the Fixed gate refuses it again | Given the same ten units, when `sprint close --dry-run` runs, then none of them raises a done-gate stop. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-15 | sdlc-studio | Filed |
