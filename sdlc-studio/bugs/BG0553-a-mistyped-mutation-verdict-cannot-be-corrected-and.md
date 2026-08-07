# BG0553: a mistyped mutation verdict cannot be corrected, and the contradiction check now turns that from a wrong number into a refusal in every mode

> **Status:** Open
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

- [ ] **AC1** The behaviour described is corrected: Registrations accumulate, and `plan_execution` holds the worst verdict per criterion, so a mutant registered `survived` by mistake cannot be corrected by...
- [ ] **AC2** The proposed fix lands, pinned by a test: Add `mutation.py retract --unit X --criterion ACn --target F --line N --mutant M --reason '<why>'`, which marks the earlier row withdrawn rather than deleting...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
