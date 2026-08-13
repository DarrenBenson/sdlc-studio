# BG0550: register drops a file's earlier registered mutants without saying so, so an edit after registering silently empties a unit's evidence

> **Status:** Open
> **Verification depth:** functional (executed through the CLI on a throwaway fixture: register twice, edit the file, register again - the run now prints DROPPED 2 earlier registration(s) where it printed nothing)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** RUN-01KZEF9M, 2026-08-07. Eight BG0541 registrations silently lost; found by re-running `--from-plan`, not by any message.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`register_mutant` drops every registered entry for a target whose content hash differs from the one being written - correct, since evidence about bytes the file no longer has is not evidence. It says nothing about it. The success line reports `N registered mutant(s) on this content` and a reader takes N as the running total, when the previous content's records have just been discarded. In RUN-01KZEF9M eight mutants registered against `transition.py` were dropped by a later registration after an intervening edit, and the loss was found only because `run --from-plan` was re-run by hand and reported seven rows as never executed. The ledger also reports its own bounded truncation loudly (`dropped N oldest entries`), which is the same class of loss and the precedent for reporting this one.

## Steps to Reproduce

1. `mutation.py register --unit X --criterion AC1 --target m.py --line 2 ...`. 2. Edit `m.py`. 3. Register a second mutant on the same target. 4. The output says `1 registered mutant(s) on this content` and never mentions that AC1's record was dropped. 5. `run --story X --from-plan` now reports AC1 as never executed.

## Proposed Fix

Print the count and the criteria dropped, in the shape the truncation note already uses: `note: N registered mutant(s) on earlier content of m.py were dropped (AC1, AC2) - re-register them against the current bytes`. The behaviour is right; the silence is the defect. A workflow consequence worth stating in the same place: register AFTER the last edit to a file, or expect to re-register.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `register_mutant` drops every registered entry for a target whose content hash differs from the one being written - correct, since evidence about bytes the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Print the count and the criteria dropped, in the shape the truncation note already uses: `note: N registered mutant(s) on earlier content of m.py were dropped...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
