# BG0553: a mistyped mutation verdict cannot be corrected, and the contradiction check now turns that from a wrong number into a refusal in every mode

> **Status:** Fixed
> **Verification depth:** functional (executed through the shipped CLI in a throwaway fixture: the filed reproduction reproduced, all three refusals confirmed with the positive control beside them, and the transition seen to stop blocking after the retraction; mutation: 7 declared mutants, all KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZEF9M delivery review round 3 of US0661, 2026-08-07, qa seat, reproduced through the shipped CLI. The proposed supersede was implemented, reddened test_a_survivor_refuses_the_transition_and_names_the_criterion, and was reverted.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Registrations accumulate, and `plan_execution` holds the worst verdict per criterion, so a mutant registered `survived` by mistake cannot be corrected by registering it `killed` - the survivor stands. That rule is deliberate and right: a genuine correction and an author registering their way out of a survivor are byte-identical to the tool, and `test_a_survivor_refuses_the_transition_and_names_the_criterion` pins it.

US0661's self-contradiction check makes the cost sharper. Two rows for one mutant with opposite verdicts now REFUSE the terminal transition in every mode, `off` included, with no escape but `--force`. So an author who mistypes a verdict and tries to fix it is worse off than one who leaves it wrong: the wrong number was a wrong number, and the correction is a hard block.

A review round proposed superseding the earlier row. That was tried and reverted, because it opens exactly the escape the worst-verdict rule closes. The answer is not to make correction cheap; it is to make it VISIBLE - a retraction that is recorded as a retraction, so the ledger shows both that the first verdict was withdrawn and who withdrew it.

## Steps to Reproduce

1. `mutation.py register --unit X --criterion AC1 --target f.py --line 2 --mutant m --test t --verdict survived`. 2. Realise the verdict was mistyped and register the same mutant `killed`. 3. `plan_execution` still reports the survivor - correct, and deliberate. 4. `transition.py set --status Fixed` under any mode, `off` included, is now REFUSED for a self-contradicting ledger.

## Proposed Fix

Add `mutation.py retract --unit X --criterion ACn --target F --line N --mutant M --reason '<why>'`, which marks the earlier row withdrawn rather than deleting it, and have both `plan_execution` and the contradiction check skip withdrawn rows. The reason is the point: an unexplained retraction is the escape hatch, and a recorded one is an audit trail.

## Acceptance Criteria

- [x] **AC1** Given a mutant registered `survived` by mistake and the correct `killed` beside it, when the mistake is retracted, then the plan reads the surviving evidence and the criterion is satisfied.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k withdrawn_verdict_stops_holding
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given a retraction, when the ledger is read, then the row is still there marked withdrawn - carrying the reason and the verdict it withdrew - and the summary counts the retraction rather than losing it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k withdrawal_is_recorded_and_not_deleted
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given two rows for one mutant with opposite verdicts, when one verdict is retracted, then only that row is withdrawn - the verdict is part of the join, so a correction cannot take the correct row with the mistake.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k verdict_is_part_of_the_join
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given a reason too thin to audit, when a retraction is attempted, then it is refused - an unexplained retraction is the escape hatch the worst-verdict rule exists to close.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k reason_too_thin_to_audit
  - **Verified:** yes (2026-08-14)
- [x] **AC5** Given join fields that match no live row, when a retraction is attempted, then it refuses rather than reporting a success that did nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k matches_nothing_refuses
  - **Verified:** yes (2026-08-14)
- [x] **AC6** Given a MEASURED row, when a retraction is attempted, then it is refused - withdrawing an observation is not correcting it, and the refusal says to measure again.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k measured_verdict_cannot_be_retracted
  - **Verified:** yes (2026-08-14)
- [x] **AC7** Given a ledger corrected by retraction, when the shipped transition verb runs, then it no longer reports the ledger as contradicting itself and no longer holds the transition.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k withdrawn_row_stops_contradicting
  - **Verified:** yes (2026-08-14)

## Resolution

`mutation.py retract` withdraws a registered verdict and leaves the withdrawal on the record: the row stays, carrying who withdrew it, when, and why, and the summary gains a `retracted` tally. Correction works; it is never quiet.

Running the verb found a defect reading it had not. The join was originally the four fields the bug names - unit, criterion, line, prose - and every refusal was correct while the success case did the wrong thing: it matched BOTH rows for one mutant and withdrew them together, so an author correcting a mistyped `survived` silently lost the `killed` beside it and ended with no evidence rather than the right evidence. The verdict is now part of the join.

A measured row cannot be retracted at all. Withdrawing a measurement is editing an observation; the way to correct one is to measure again.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in mutation.py `plan_execution`, stop skipping withdrawn rows so a retraction has no effect | Given a mutant registered `survived` by mistake and the correct `killed` beside it, when the mistake is retracted, then the plan reads the surviving evidence and the criterion is satisfied. |
| AC2 | in mutation.py `retract_mutant`, delete the row instead of marking it withdrawn | Given a retraction, when the ledger is read, then the row is still there marked withdrawn - carrying the reason and the verdict it withdrew - and the summary counts the retraction rather than losing it. |
| AC3 | in mutation.py `retract_mutant`, drop the verdict from the join so both rows are withdrawn | Given two rows for one mutant with opposite verdicts, when one verdict is retracted, then only that row is withdrawn - the verdict is part of the join, so a correction cannot take the correct row with the mistake. |
| AC4 | in mutation.py, set `_RETRACT_REASON_MIN` to 0 so an unexplained retraction is accepted | Given a reason too thin to audit, when a retraction is attempted, then it is refused - an unexplained retraction is the escape hatch the worst-verdict rule exists to close. |
| AC5 | in mutation.py `retract_mutant`, return a zero-count success instead of refusing | Given join fields that match no live row, when a retraction is attempted, then it refuses rather than reporting a success that did nothing. |
| AC6 | in mutation.py `retract_mutant`, drop the provenance filter so a measured row can be withdrawn | Given a MEASURED row, when a retraction is attempted, then it is refused - withdrawing an observation is not correcting it, and the refusal says to measure again. |
| AC7 | in transition.py `_ledger_contradiction`, stop skipping withdrawn rows | Given a ledger corrected by retraction, when the shipped transition verb runs, then it no longer reports the ledger as contradicting itself and no longer holds the transition. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
