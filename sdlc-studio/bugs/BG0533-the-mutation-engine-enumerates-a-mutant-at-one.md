# BG0533: the mutation engine enumerates a mutant at one line and applies it at another, because only the enumerator excludes multiline-string spans when counting occurrences

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** Found by the engineering and QA seats at the RUN-01KZBBZ0 batch boundary. The desync is pre-existing: `git log -S` puts the divergence at c40e9c2c (CR0146), well before 367459cd. What was new was US0632's claim that the engine is AST-based, which is retracted on the artefact.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`enumerate_mutations` identifies a mutant by (file, class, occurrence ordinal) over a per-line regex scan, and skips occurrences inside multiline-string spans when counting. `mutated_text` re-counts that ordinal to find what to patch and does NOT apply the same exclusion. The two therefore disagree whenever a pattern occurs inside a docstring or other multiline string above the real occurrence: the mutant is REPORTED at the correct line and APPLIED at the wrong one.

The consequence is the exact hazard mutation testing exists to avoid, inverted: the tool edits code the criterion does not name, the criterion's own test passes because the code it pins was never touched, and the run records a SURVIVED that is evidence about nothing. A false survivor sends an author to fix a test that is already sound; a false kill is worse.

This supersedes BG0531, which scoped the hazard to the hand-`register` path on my incorrect claim that the automated engine was AST-based. It is not. BG0531's fix is still wanted for the registered path; this is the automated one.

## Steps to Reproduce

Demonstrated by an independent seat, 2026-08-06, RUN-01KZBBZ0. Author a file whose docstring contains `if a == b:` and whose real body contains `if 1 == 1:` below it. `enumerate_mutations` reports the `invert-guard` mutant at the real line (12). `apply_mutation` patches line 5, inside the docstring. The mutant is recorded against line 12 and the bytes changed at line 5.

## Proposed Fix

Share ONE occurrence-counting routine between `enumerate_mutations` and `mutated_text`, so the exclusion cannot apply on one side only - two readers of one file will disagree eventually, and the second is written by whoever did not know the first existed.

Then assert the invariant rather than trusting the shared helper: after applying, the index of the changed line must equal the mutation's recorded `line`, and the run must abort loudly if it does not. That check is two lines, is independent of how the anchor is computed, and would have caught this the day it was introduced. It is also what US0632's AC3 asks for, which is why that criterion is now carried unmet rather than narrowed away.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `enumerate_mutations` identifies a mutant by (file, class, occurrence ordinal) over a per-line regex scan, and skips occurrences inside multiline-string spans...
- [ ] Following the recorded steps no longer reproduces the defect: Demonstrated by an independent seat, 2026-08-06, RUN-01KZBBZ0.
- [ ] The proposed fix lands, pinned by a test: Share ONE occurrence-counting routine between `enumerate_mutations` and `mutated_text`, so the exclusion cannot apply on one side only - two readers of one...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
