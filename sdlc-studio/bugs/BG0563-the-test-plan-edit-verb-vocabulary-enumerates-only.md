# BG0563: the test-plan edit-verb vocabulary enumerates only subtractive verbs, so a mutant that ADDS something cannot be stated and gets reworded until it parses

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Hit four times while authoring test plans in RUN-01KZM49Y, 2026-08-10. `_EDIT_VERBS` at verify_ac.py:2183 holds 28 verbs, every one of which removes, replaces or weakens: delete, remove, drop, stub, skip, comment out, widen, narrow, disable, bypass, truncate, collapse and so on. None adds. `testplan derive` therefore refused `add an early return guard to check_affects_resolvable`, `introduce a plan_review.first_run key`, `insert a call to the applicability predicate` and `add a plan_review.first_run key`, each with `carries no edit verb - name what is changed, not what stops working`. Each was accepted only after being reworded around the missing vocabulary, which changed the sentence and not the mutant.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The check is right that a mutant must name a production edit. Its vocabulary decides which edits can be named, and it enumerates only the subtractive ones.

That matters because an ADDITIVE mutant is the sharpest one available for a whole class of criterion. This run recorded two instances where the criterion is an absence and the mutant must therefore be an addition. US0663 AC3 requires that no configuration key can hold a concession open, so its mutant is `add such a key`. BG0559 AC2 requires that a bare skill tree stays measurable, so its mutant is `add an applicability check inside the measurement`. In both cases the strongest mutant is the one the vocabulary cannot express.

The failure mode is the quiet one. Nobody is stopped: the author rewords until the check passes, and the reworded sentence is usually a weaker description of the same edit or a description of a different one. The gate's own message pushes in that direction - `name what is changed, not what stops working` - which is exactly what the refused sentences were already doing.

This is LL0043 in the guard written to enforce criteria about guards. An enumeration of a rule is a lower bound, not a boundary, and the list silently exempts whatever it forgot - here, every mutant whose verb is `add`.

## Steps to Reproduce

1. Write a criterion whose Then clause asserts an ABSENCE - that no such key, lane or branch exists. 2. Write the only mutant that can falsify it: one that adds the thing. 3. `verify_ac.py testplan derive --unit <id> --dry-run`. 4. It refuses with `carries no edit verb`. 5. Reword to a subtractive phrasing and it passes, describing an edit that is no longer the one the criterion needs.

## Proposed Fix

Extend the vocabulary with the additive verbs - add, insert, introduce, append, register, wire, re-add - and pin the pairing rather than the list: a criterion whose Then clause is an absence must accept an additive mutant, asserted through `verify_ac.py testplan derive` on a fixture of that shape. Extending the enumeration alone repeats the defect at the next verb nobody thought of, so the test that matters is the one that fails when an absence-shaped criterion cannot state its own falsifier. Consider also whether the check should be `names a file from Affects AND a verb` rather than a closed verb list at all - the file requirement already does most of the work of distinguishing an edit from a prediction.

## Acceptance Criteria

- [ ] **AC1** A mutant whose verb is additive is accepted by `verify_ac.py testplan derive`, proven on the absence-shaped criterion that is currently refused
- [ ] **AC2** A mutant that names no production edit at all is still refused, proving the check was extended rather than removed (positive control)
- [ ] **AC3** A criterion whose Then clause asserts an absence and whose mutant cannot be stated in the vocabulary is reported as such, so the next missing verb surfaces as a finding rather than as a reworded sentence
- [ ] **AC4** The pairing is pinned by a test that fails when the vocabulary is narrowed back, rather than by an assertion over the list's contents - a test that enumerates the list agrees with it by construction

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
