# BG0610: A --fields-file scalar where a list is expected is iterated CHARACTER BY CHARACTER, so one Verify line becomes one letter per criterion

> **Status:** Fixed
> **Severity:** High
> **Premise narrowed 2026-08-25:** the `acs` character-by-character limb was already closed under 4f276b31. What stands is the untyped path: `artifact.py:154` still reads `for i, v in enumerate((f.get("verify") or []), 1)`, so a scalar supplied for a list-valued field is still iterated per character. Build the type check; do not re-fix `acs`. Found by an independent goal review before any code was written.
> **Verification depth:** functional [[derived: criteria 4; plan rows 4; executed 4; killed 4; survived 0; not-run 0; entry point 0 of 4 criteria through the shipped CLI, 4 in-process | fp 81eb122393d9 ]] (four criteria over the shared fields-file loader, each with its own mutant executed and killed: the check removed, widened to refuse lists too, widened to every field, and moved out of the shared loader into one caller. The last is the one that matters - `artifact.py` and `file_finding.py` read one contract through one function, so a check wired into a single caller ships the repair half-applied. NOT covered: the `acs` character-slicing limb this bug was filed for, which a prior commit had already closed - that was found by a pre-code review and the criteria were narrowed to the limb still live.)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** artifact.py:154, `for i, v in enumerate((f.get("verify") or []), 1)`. Reproduced by inspection of the artefact it produced: sdlc-studio/stories/US0684 as first written carried six Verify lines of one character each. The criteria themselves rendered in a non-canonical bullet form at the same time, so the file needed rewriting by hand.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The fields-file path validates that every KEY is one the writer reads and refuses an unknown one, but it does not validate TYPES. A list-valued field supplied as a scalar string reaches `enumerate(f.get("verify") or [])` and Python iterates its characters, so a single Verify expression is distributed one LETTER per acceptance criterion. The artefact is written, indexed and reported as created. Nothing refuses, and the damage is only visible by reading the rendered file.

## Steps to Reproduce

Write a fields-file with a list of three `acs` and a scalar string `verify`. Run `artifact.py new --type story --fields-file <it>`. Observed on 2026-08-24 creating US0684: six criteria were written with Verify lines reading p, y, t, e, s and t - the letters of the word pytest, one per criterion. The command reported `created US0684 ... (indexed=True, epic_linked=True)` and exited 0. The same shape reaches any list-valued field on this path.

## Proposed Fix

Validate the TYPE of every field beside its name, with the same refusal the unknown-key check already uses. A scalar supplied where a list is expected should be refused naming the field - or coerced to a one-element list, which is what a writer means - but never iterated. Refusing is the better fit here: the filer already argues that a key nobody reads is a field that silently went missing, and a character-sliced value is the same failure one level down. `file_finding.py` shares the fields-file contract and should be held to the same rule.

## Acceptance Criteria

- [ ] **AC1** Given a fields-file supplying a scalar where a LIST-valued field is expected, when it is read, then it is REFUSED naming the field and the type it got - a string is ITERATED rather than stored, so one value becomes one character per item
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ScalarForListTests::test_a_scalar_where_a_list_is_expected_is_refused
- [ ] **AC2** Given the same field supplied as a proper list, when it is read, then it is accepted unchanged - the paired control, because a guard that refused the documented path would be worse than the defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ScalarForListTests::test_a_proper_list_is_accepted
- [ ] **AC3** Given a scalar supplied for a SCALAR field, when it is read, then it is still accepted - the rule is about list-valued fields, and demanding lists everywhere would refuse `title` and every other single-value field in the contract
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ScalarForListTests::test_a_scalar_for_a_scalar_field_is_still_accepted
- [ ] **AC4** Given the same shape supplied through either reader, when it is read, then both refuse it - `artifact.py` and `file_finding.py` share one loader, and a check wired into one caller leaves the other carrying the defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ScalarForListTests::test_both_readers_share_the_rule

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `file_finding.py`, return early from `_refuse_scalar_for_list` without checking | Given a fields-file supplying a scalar where a LIST-valued field is expected, when it is read, then it is REFUSED naming the field and the type it got - a string is ITERATED rather than stored, so one value becomes one character per item |
| AC2 | in `file_finding.py`, extend `_refuse_scalar_for_list` to refuse a list as well as a scalar | Given the same field supplied as a proper list, when it is read, then it is accepted unchanged - the paired control, because a guard that refused the documented path would be worse than the defect |
| AC3 | in `file_finding.py`, add every field name to `LIST_VALUED_FIELDS` | Given a scalar supplied for a SCALAR field, when it is read, then it is still accepted - the rule is about list-valued fields, and demanding lists everywhere would refuse `title` and every other single-value field in the contract |
| AC4 | in `file_finding.py`, move the check out of `load_fields_file` into one caller | Given the same shape supplied through either reader, when it is read, then both refuse it - `artifact.py` and `file_finding.py` share one loader, and a check wired into one caller leaves the other carrying the defect |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
