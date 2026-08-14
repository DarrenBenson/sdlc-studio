# BG0552: a registered mutant cannot be joined to a measured one, so a cross-provenance contradiction in the mutation ledger is undetectable

> **Status:** Fixed
> **Verification depth:** functional (executed through the shipped CLI: a real measured run and a hand registration of the opposite verdict, seen undetectable without --class, refused with it naming both instruments and the class, and an agreeing claim seen to pass; mutation: 6 declared mutants, all KILLED - the AC4 control mutant SURVIVED first because it never reached the path it named, and was replaced with one that does; restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KZEF9M delivery review round 2 of US0661, 2026-08-07, qa seat. Established by execution: a registered prose mutant and a measured fault class at the same line and hash, with opposite verdicts, exit 0.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A MEASURED ledger row names the generator's fault class (`stub-return-null`). A REGISTERED row names the edit in the author's own prose (`inverted the a == b guard`). Nothing relates the two, so the check that catches a mutant recorded killed by one instrument and survived by the other has only the line to join on - and joining on the line alone reads two genuinely different mutants at one line as the instrument lying.

US0661's AC4 was written for the cross-provenance case and is narrowed to same-provenance, because that is the part the ledger can decide. The cross-provenance half is the more valuable one: it is exactly where a hand-typed claim would be caught disagreeing with a measurement, which is the asymmetry the whole repair-evidence rule turns on.

The fix is a field, not a heuristic: `register` should record the FAULT CLASS the mutant belongs to, beside the prose, drawn from the generator's own vocabulary. Then the join is exact and the check works across provenances without guessing.

## Steps to Reproduce

1. `mutation.py run --unit X` over a file, recording a measured row at line N with class `stub-return-null`. 2. `mutation.py register --unit X --target <same file> --line N --mutant 'returned None instead of the value' --verdict survived`. 3. The two describe the same mutant with opposite verdicts and nothing detects it. 4. Change the prose to anything else and nothing changes, because the comparison was never possible.

## Proposed Fix

Add `--class` to `register`, validated against the generator's fault-class vocabulary, and join the contradiction check on (target, hash, line, class). Keep the prose: it is what a reviewer reads. Until then the check is same-provenance, which is honest about what it can see.

## Acceptance Criteria

- [x] **AC1** Given a measured run, when its rows are written, then each carries the generator's fault class in a field of its own rather than only in the prose slot a registered row fills with words.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k measured_row_records_its_fault_class
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given a measured `killed` and a hand-registered `survived` for one fault class at one line under one content hash, when a terminal transition is attempted, then it is refused and the refusal names both instruments and the class.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k hand_typed_claim_contradicting
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given a hand-registered claim that AGREES with the measurement, when the same transition is attempted, then nothing is reported - a check that fires on agreement is not a check.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k agreeing_claim_is_not_a_contradiction
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given a registered row carrying no class, when it disagrees with a measured row at the same line, then no cross-provenance contradiction is claimed - the join is exact or it is silent, never the line alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k without_a_class_the_rows_cannot_be_compared
  - **Verified:** yes (2026-08-14)
- [x] **AC5** Given a class the generator never emits, when it is registered, then it is refused - free text joins no measured row, so it records a promise it cannot keep.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k class_the_generator_never_emits
  - **Verified:** yes (2026-08-14)
- [x] **AC6** Given two DIFFERENT hand-applied mutants of one class at one line, when the ledger is checked, then no cross-provenance contradiction is claimed - the class is coarser than the prose, and this branch ignores the configured mode, so a false positive is not survivable.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k two_registered_rows_of_one_class
  - **Verified:** yes (2026-08-14)

## Resolution

`register --class` records the fault class beside the prose, validated against the generator's own vocabulary, and the contradiction check gains a second join keyed on it. The two joins do different work: within one provenance the key stays the mutant's prose, because two different mutants at one line are two honest statements; across provenances the key is the class, which is the only value the two instruments share.

The cross join is deliberately narrow. It fires only between DIFFERENT provenances, because the class is coarser than the prose and two hand-applied mutants of one class at one line would look identical to it. This branch ignores the configured mode by design - it refuses under `off` - so a false positive there is not survivable.

`--class` is optional. A hand-applied mutant does not always belong to a class the generator can produce, and requiring one would make authors pick the nearest label, which is a join that lies. Without it the rows simply cannot be compared, and that is pinned as a decision rather than left as a gap.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in mutation.py, write None into a measured row's `class` field so it can join nothing | Given a measured run, when its rows are written, then each carries the generator's fault class in a field of its own rather than only in the prose slot a registered row fills with words. |
| AC2 | in transition.py `_ledger_contradiction`, skip the cross-provenance branch entirely | Given a measured `killed` and a hand-registered `survived` for one fault class at one line under one content hash, when a terminal transition is attempted, then it is refused and the refusal names both instruments and the class. |
| AC3 | in transition.py, drop the verdict comparison so the cross join fires on agreement | Given a hand-registered claim that AGREES with the measurement, when the same transition is attempted, then nothing is reported - a check that fires on agreement is not a check. |
| AC4 | in transition.py, drop the class from the cross key, joining on the line alone | Given a registered row carrying no class, when it disagrees with a measured row at the same line, then no cross-provenance contradiction is claimed - the join is exact or it is silent, never the line alone. |
| AC5 | in mutation.py `register_mutant`, drop the fault-class vocabulary check | Given a class the generator never emits, when it is registered, then it is refused - free text joins no measured row, so it records a promise it cannot keep. |
| AC6 | in transition.py, drop the provenance comparison so two registered rows contradict | Given two DIFFERENT hand-applied mutants of one class at one line, when the ledger is checked, then no cross-provenance contradiction is claimed - the class is coarser than the prose, and this branch ignores the configured mode, so a false positive is not survivable. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
