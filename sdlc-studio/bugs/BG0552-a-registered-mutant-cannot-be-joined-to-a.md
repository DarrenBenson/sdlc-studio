# BG0552: a registered mutant cannot be joined to a measured one, so a cross-provenance contradiction in the mutation ledger is undetectable

> **Status:** Open
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

- [ ] **AC1** The behaviour described is corrected: A MEASURED ledger row names the generator's fault class (`stub-return-null`).
- [ ] **AC2** The proposed fix lands, pinned by a test: Add `--class` to `register`, validated against the generator's fault-class vocabulary, and join the contradiction check on (target, hash, line, class).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
