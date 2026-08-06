# BG0534: testplan derive's edit-verb check is an enumeration, so it refuses honest mutants written with a verb nobody listed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01KZCAJX grooming, 2026-08-06. Five refusals on five honest mutants across four units, each resolved by a synonym swap that changed no meaning. `verify_ac.py` `_EDIT_VERBS`; the guard is `testplan_row_faults`.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_EDIT_VERBS` in `verify_ac.py` is a 29-item literal list, and `testplan_row_faults` refuses any mutant field that contains none of them. Authoring the first five real test plans in this repo hit it FIVE times on legitimate mutants: `move the affects check below the batch write`, `print the bare message without quoting the gate`, `keep two separate counting sites`, `duplicate the counting loop`, and `downgrade the abort to a warning`. Every one names a file and describes a concrete edit; none contains a listed verb. Each had to be reworded into a synonym the list happens to hold - `reorder`, `drop`, `revert`, `replace` - which changed the prose and not the meaning.

US0629 AC2 anticipated exactly this failure and guarded only half of it. Its own wording: "A legitimate mutant that happens to share the criterion's vocabulary must still be accepted, or `derive` becomes a guard that refuses honest work while its refusal test passes for exactly that reason." The near-miss ACCEPT control exists for the OVERLAP limb. The VERB limb has no such control, so nothing in the suite can tell a narrow list from a correct one.

This is LL0043 in the refusing direction: an enumeration of a rule is a lower bound, and this one refuses whatever it forgot.

## Steps to Reproduce

1. Author a test plan whose mutant reads `in sprint.py, move the affects check below the batch write`. 2. `verify_ac.py testplan derive --unit <id>` refuses: `carries no edit verb - name what is changed, not what stops working`. 3. Change the single word `move` to `reorder` and it is accepted. Nothing else about the row changed. Reproduced on BG0533 AC2 and AC3, BG0521 AC2, BG0516 AC2 and BG0530 AC5 while grooming RUN-01KZCAJX.

## Proposed Fix

Add the near-miss ACCEPT control the overlap limb already has: a fixture of legitimate mutants written with verbs NOT on the list, asserted accepted. That test is what makes the list's width a measured property instead of an author's guess, and it will fail today.

Then widen the check rather than the list. A mutant naming a path from `Affects` and describing an edit is better recognised by shape than by vocabulary - for instance, any imperative verb in the leading clause. If the list stays, it must be derived from something (the repo's own recorded mutants across every unit's Mutation-checked field would do) rather than hand-enumerated, or it will refuse the next verb nobody thought of.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `_EDIT_VERBS` in `verify_ac.py` is a 29-item literal list, and `testplan_row_faults` refuses any mutant field that contains none of them.
- [ ] The proposed fix lands, pinned by a test: Add the near-miss ACCEPT control the overlap limb already has: a fixture of legitimate mutants written with verbs NOT on the list, asserted accepted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
