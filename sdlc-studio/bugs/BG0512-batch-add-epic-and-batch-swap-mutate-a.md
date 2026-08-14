# BG0512: batch add-epic and batch swap mutate a live batch without the ungroomed census, so a unit the plan gate would refuse can enter a run

> **Status:** Fixed
> **Verification depth:** functional (executed: add-epic over an ungroomed fixture refuses and adds nothing; mutation: 2 declared mutants, both KILLED after the first verifier was found VACUOUS - it pointed at tests whose fixtures were groomed, so disabling the census changed nothing; restore byte-exact)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint.py plan` refuses a batch holding an ungroomed unit, and since BG0511 that census covers bugs as well as stories. The in-flight batch verbs do not consult it: `_cmd_batch_add_epic` and `_cmd_batch_swap` add units to an open run's batch without asking whether they are groomed, so a unit the planner would have refused at the door can be admitted through the side. Found by the independent batch review of RUN-01KZ56M6, which confirmed no unit in that batch was wrongly admitted - the gap is real but was not exercised. It predates BG0511 rather than being opened by it: before that census covered bugs, bugs were unchecked at both entrances, so this is the residue the contract split leaves rather than a hole it made.

## Steps to Reproduce

1. Open a run with a groomed batch.
2. Create a bug with Affects and Points but no acceptance criteria.
3. Add its epic (or swap it in) with `sprint.py batch add-epic` or `batch swap`.
4. The unit joins the batch. `sprint.py plan` would have refused it, and `transition --status Fixed` will refuse it later.

## Acceptance Criteria

- [x] **AC1** Given an ungroomed unit, when `batch add-epic` runs, then it refuses on the same census `sprint plan` refuses on and adds NOTHING - a unit the plan gate rejected must not enter through an in-flight verb.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py -k an_ungroomed_unit_is_refused_and_nothing_is_added
- [x] **AC2** Given the refusal, when it prints, then it names `batch add-epic` rather than `sprint plan` - a message naming the wrong command sends the reader to the wrong place.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py -k the_refusal_names_its_own_verb

## Proposed Fix

Route both verbs through the same `breakdown` census `plan --write` uses, and refuse on the same terms. The census already exists and already covers every type; what is missing is the call. A recorded override belongs here too, since an in-flight add is sometimes deliberate - but it must be recorded rather than silent.

## Impact

A run can acquire work that cannot reach a terminal status, and the first honest signal is a refusal at delivery - which is exactly the failure BG0511 removed from the front door. The two entrances to a batch disagree about what may enter it.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py `_cmd_batch_add_epic`, delete the breakdown census call so an ungroomed unit is added | Given an ungroomed unit, when `batch add-epic` runs, then it refuses on the same census `sprint plan` refuses on and adds NOTHING - a unit the plan gate rejected must not enter through an in-flight verb. |
| AC2 | in sprint.py `_cmd_batch_add_epic`, restore `_refuse_ungroomed` so the refusal names sprint plan | Given the refusal, when it prints, then it names `batch add-epic` rather than `sprint plan` - a message naming the wrong command sends the reader to the wrong place. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
