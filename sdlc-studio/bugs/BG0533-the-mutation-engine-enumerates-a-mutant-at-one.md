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

### AC1: the line CHANGED is the line the mutation was enumerated at

- **Given** a target whose pattern occurs inside a multiline string above the real occurrence - `if a == b:` in a docstring above a body `if 1 == 1:`
- **When** `mutation.py run` applies the enumerated mutant
- **Then** the index of the changed line equals the mutation's recorded `line`, asserted after the write rather than trusted from the anchor computation
- **Mutant:** drop the equality - the mutant is reported at line 12 and applied at line 5, which is today's behaviour and was reproduced by two independent seats
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AppliedWhereEnumeratedTests::test_the_changed_line_is_the_enumerated_line
- **Verified:** no

### AC2: a disagreement ABORTS the run rather than recording a verdict

- **Given** an enumerated line and an applied line that differ
- **When** the run notices
- **Then** it aborts loudly naming both, because a verdict attributed to a line the tool did not edit is worse than no verdict - a false KILL is a green mutation score for code that was never mutated
- **Mutant:** warn and continue - the run completes and publishes a score, and the instrument the whole evidence story leans on reports success it did not achieve
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AppliedWhereEnumeratedTests::test_a_line_disagreement_aborts_loudly
- **Verified:** no

### AC3: one routine counts occurrences for both readers

- **Given** `enumerate_mutations`, which skips multiline-string spans when counting, and `mutated_text`, which re-counts without that exclusion
- **When** the source is searched for the ordinal
- **Then** exactly ONE routine does the counting and both call it - two readers of one file disagree eventually, and the second is written by whoever did not know the first existed
- **Mutant:** keep two counting sites and fix only the exclusion - they agree today and drift again at the next edit, which is how this survived since c40e9c2c
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AppliedWhereEnumeratedTests::test_one_routine_counts_for_both_readers
- **Verified:** no

### AC4: the positive control - an ordinary mutant still applies and still kills

- **Given** a target with no multiline-string decoy
- **When** a mutant is applied
- **Then** it lands, its test fails, and the verdict is KILLED - a guard that refuses every application passes AC1 and AC2 for exactly the wrong reason
- **Mutant:** abort on every application - the criteria above stay green while mutation testing stops working entirely
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::AppliedWhereEnumeratedTests::test_an_ordinary_mutant_still_applies_and_kills
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
