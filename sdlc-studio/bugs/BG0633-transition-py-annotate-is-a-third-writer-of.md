# BG0633: transition.py annotate is a THIRD writer of Severity and carries no vocabulary, so the class BG0624 closed at two entry points is still open at the third

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-08-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0624 put a severity vocabulary on both writers it knew about - `file_finding.py file` and `artifact.py new` - and its own claim inventory said "nothing else writes it". A delivery review falsified that by execution: `transition.py annotate --id <bug> --field Severity --value major` exits 0 and writes `> **Severity:** major`, because `severity` is absent from `_ANNOTATE_DENYLIST`. The finding then leaves `barred_open()` and joins the disclosure page, which is the exact harm BG0624 was filed for, arriving through the entry point nobody checked.

## Steps to Reproduce

1. Create a bug fixture with `> **Severity:** Medium`.
2. Run `transition.py annotate --id <id> --field Severity --value major`.
3. Observe exit 0 and `> **Severity:** major` in the file.
4. Run `known_issues.py --bar`: the finding is now named as residue rather than classified.

## Proposed Fix

Route `annotate`'s Severity writes through the same `normalise_severity` the other two writers use, or add `severity` to `_ANNOTATE_DENYLIST` so the field can only be set by a writer that carries the vocabulary. The first is preferable: annotate exists to correct a field, and refusing to correct a severity would be a worse tool. Whichever is chosen, the third writer must be pinned by a test - stopping the class beats catching the instance, and this is the third instance of the same class in one unit.

## Acceptance Criteria

- [ ] **AC1** Given a bug fixture whose Severity is Medium, when `transition.py annotate --id <the fixture> --field Severity --value major` is run as a SUBPROCESS - the runnable form, since without `--id` argparse exits 2 and the file is unchanged for a reason that has nothing to do with the vocabulary - then it is REFUSED naming the accepted set and the file is unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateSeverityTests::test_an_off_vocabulary_severity_is_refused_through_the_shipped_command
  - **Verified:** no
- [ ] **AC2** Given the same fixture, when a RECOGNISED severity is annotated in either case - `high` or `High` - then both are accepted and the file reads the canonical spelling `High`. The positive control: a guard refusing every severity satisfies AC1 on its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateSeverityTests::test_a_differently_cased_severity_is_normalised
  - **Verified:** no
- [ ] **AC3** Given the same fixture, when the FIELD NAME is spelled in another case - `--field severity --value banana` - then the guard fires just as it does for `Severity`, and the file gains no second severity line beside the canonical one. `annotate` lowercases the field for its denylist check alone and passes the raw spelling to the writer, so today this exits 0 and inserts a duplicate; a guard keyed on the literal `Severity` passes AC1 and AC2 with the defect live
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::AnnotateSeverityTests::test_the_guard_is_keyed_on_the_normalised_field_name
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, delete the vocabulary call from `cmd_annotate` so any value reaches `_upsert_field` | Given a bug fixture whose Severity is Medium, when `transition.py annotate --id <the fixture> --field Severity --value major` is run as a SUBPROCESS - the runnable form, since without `--id` argparse exits 2 and the file is unchanged for a reason that has nothing to do with the vocabulary - then it is REFUSED naming the accepted set and the file is unchanged |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, replace the normalisation call with an exact-match `value in SEVERITY_VOCAB` test, so `high` is refused rather than written as `High` | Given the same fixture, when a RECOGNISED severity is annotated in either case - `high` or `High` - then both are accepted and the file reads the canonical spelling `High`. The positive control: a guard refusing every severity satisfies AC1 on its own |
| AC3 | in .claude/skills/sdlc-studio/scripts/transition.py, key the vocabulary guard on the raw `field` argument rather than the lowercased `key`, so only the exact spelling `Severity` is guarded | Given the same fixture, when the FIELD NAME is spelled in another case - `--field severity --value banana` - then the guard fires just as it does for `Severity`, and the file gains no second severity line beside the canonical one. `annotate` lowercases the field for its denylist check alone and passes the raw spelling to the writer, so today this exits 0 and inserts a duplicate; a guard keyed on the literal `Severity` passes AC1 and AC2 with the defect live |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-28 | sdlc-studio | Filed |
