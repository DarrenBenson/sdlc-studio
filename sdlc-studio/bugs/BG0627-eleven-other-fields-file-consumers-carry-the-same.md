# BG0627: eleven other fields-file consumers carry the same `or ""` guard, so a falsey value is reported as a missing field across five more modules

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 8
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/ledger.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py
> **Evidence:** Enumerated 2026-08-27 by an independent plan review of BG0622, which was asked to list the set rather than assert one: 12 non-test call sites across 10 modules, of which 5 modules carry the identical `str(x.get(k) or "").strip()` guard - ledger.py:86, decisions.py:468, handoff.py:825, validate.py:1086, and roughly 16 field validators in file_finding.py between lines 1442 and 1932. `verdict_polarity` behaviour confirmed by execution: "True" reads yes, "False" reads no, while "", "None" and "0" all read unclear.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0622 repairs `_seat_from_dict` in `sprint.py`, where `str(d.get(f) or "").strip()` makes a JSON `false` indistinguishable from a missing field. The same shape sits on eleven other fields-file consumers across five modules, so the same class of value is mis-reported there too: `str(0 or "")` is empty, and so is `str(False or "")`.

This is deliberately NOT one blanket repair. The right rule differs by field TYPE, and applying one rule to both is how a fix becomes a defect:

- a TYPED field - a yes/no verdict, a count - must be tested for PRESENCE and then coerced, so both `false` and `0` reach the record;
- a PROSE field - `rationale`, `note`, `title`, `reason` - must be tested for presence AND for being non-empty after coercion, because accepting `"rationale": false` would store the string `False` as a rationale, which is worse than refusing it.

The enumeration above is a lower bound, not a boundary - LL0043. So the deliverable is not only the edits: it is a mechanical check that no NEW `or ""` reaches a fields-file consumer, without which the list silently exempts whatever the next author adds.

## Steps to Reproduce

1. In any of the five modules, pass a fields-file whose typed field carries a JSON `false` or a `0`. 2. The loader reports it as a missing field, naming a key the document plainly contains. 3. Change the value to `true` and it is accepted. Measured on `sprint.py` as BG0622; the same guard shape was then enumerated at ledger.py:86, decisions.py:468, handoff.py:825, validate.py:1086 and across `file_finding.py`'s field validators.

## Proposed Fix

Split the guard by field type rather than sweeping one rule across all of them. Give the shared loader two helpers - one that tests presence and coerces (typed fields), one that tests presence and non-emptiness (prose fields) - and route each existing guard to whichever its field is. Then add the boundary: a check that refuses a new `\.get\([^)]*\) or ""` on a fields-file consumer, so the module list stops being a lower bound. Without that check this unit fixes five modules and exempts the sixth nobody has written yet.

## Acceptance Criteria

> **Re-framed 2026-09-08 after plan review.** The original criteria asked for a JSON `false`
> to be ACCEPTED into a typed field. There is no typed field: every fields-file call site in
> the five named modules passes prose keys only, and `load_fields_file` refuses any key
> outside its allowlist. The defect that does reproduce is the other one - a non-string in a
> prose field is not refused by name, it CRASHES.

- [ ] **AC1** Given a fields file whose PROSE field carries a non-string - `false`, `0`, `5`, a list - when the document is read, then it is REFUSED naming that field. A required prose key is already refused today; a non-required one reaches a string method and raises `AttributeError` with a traceback, which is neither a refusal nor a name
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_a_non_string_prose_field_is_refused_naming_it
  - **Verified:** no
- [ ] **AC2** Given a fields file whose prose fields are all strings AND whose TYPED fields carry non-strings - a `points` integer, an `acs` list, a `verify` list, a `line` number - when the document is read, then it is ACCEPTED and every one of those values reaches the record unchanged. The typed half is what stops the fix being a blanket refusal: three modules outside this unit's surface pass a numeric `line` through the same loader, and a rule refusing every non-string breaks them while satisfying AC1
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_a_well_formed_fields_file_is_still_accepted
  - **Verified:** no
- [ ] **AC3** Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_the_five_shipped_commands_refuse_by_name_and_never_traceback
  - **Verified:** no
- [ ] **AC4** Given a NEW `.get(...) or ""` guard added to a fields-file consumer, when the repository's own check runs, then it REFUSES. The enumeration in this bug is a lower bound, and the check is what turns it into a boundary
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_a_new_or_empty_guard_is_refused_by_the_repository_check
  - **Verified:** no
- [ ] **AC5** Given an `or ""` that is NOT on a fields-file path - `sprint.py` alone carries 35, and `decisions.py` uses them to read ledger records - when the same check runs, then it PASSES. Without this control a check that refuses every `or ""` in the tree satisfies AC4 and refuses the repository
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_an_unrelated_or_empty_guard_is_left_alone
  - **Verified:** no

## Impact

Every one of these loaders is on the recommended `--fields-file` path, which exists precisely so prose carrying shell metacharacters is stored verbatim. An operator who takes the recommended path and writes a boolean gets an error naming a field their file contains, and the workaround - write the string - is documented nowhere. On a verdict field the bias has a direction: the positive value records and the negative one refuses.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/file_finding.py, delete the type check from `resolve_prose_fields`, where the prose keys are known, so a bool reaches the string method | Given a fields file whose PROSE field carries a non-string - `false`, `0`, `5`, a list - when the document is read, then it is REFUSED naming that field. A required prose key is already refused today; a non-required one reaches a string method and raises `AttributeError` with a traceback, which is neither a refusal nor a name |
| AC2 | in .claude/skills/sdlc-studio/scripts/file_finding.py, hoist the new refusal out of `resolve_prose_fields` into `load_fields_file`, where it sees typed keys too | Given a fields file whose prose fields are all strings AND whose TYPED fields carry non-strings - a `points` integer, an `acs` list, a `verify` list, a `line` number - when the document is read, then it is ACCEPTED and every one of those values reaches the record unchanged. The typed half is what stops the fix being a blanket refusal: three modules outside this unit's surface pass a numeric `line` through the same loader, and a rule refusing every non-string breaks them while satisfying AC1 |
| AC3 | in .claude/skills/sdlc-studio/scripts/ledger.py, bypass the shared loader and read the JSON directly at this command's call site | Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site |
| AC3 | in .claude/skills/sdlc-studio/scripts/decisions.py, bypass the shared loader and read the JSON directly at this command's call site | Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site |
| AC3 | in .claude/skills/sdlc-studio/scripts/handoff.py, bypass the shared loader and read the JSON directly at this command's call site | Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site |
| AC3 | in .claude/skills/sdlc-studio/scripts/validate.py, bypass the shared loader and read the JSON directly at this command's call site | Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site |
| AC3 | in .claude/skills/sdlc-studio/scripts/file_finding.py, call `load_fields_file` from `cmd_file` without the prose resolution that follows it | Given each of the five named modules' shipped COMMANDS rather than their loaders, when a fields file carries a non-string in a prose field, then each exits non-zero naming the field and none prints a traceback. A library test cannot see a command that stops calling the shared loader, and each module reaches it by its own call site |
| AC4 | in .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, narrow the boundary sweep's predicate so a guard on a fields-file path is not matched | Given a NEW `.get(...) or ""` guard added to a fields-file consumer, when the repository's own check runs, then it REFUSES. The enumeration in this bug is a lower bound, and the check is what turns it into a boundary |
| AC5 | in .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, drop the fields-file scoping from the sweep's predicate | Given an `or ""` that is NOT on a fields-file path - `sprint.py` alone carries 35, and `decisions.py` uses them to read ledger records - when the same check runs, then it PASSES. Without this control a check that refuses every `or ""` in the tree satisfies AC4 and refuses the repository |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
| 2026-09-10 | sdlc-studio | Delivered. `_refuse_non_string_prose` refuses a non-string in a prose key from `resolve_prose_fields` and from `file_finding`'s own `cmd_file`, never from `load_fields_file` (which still carries typed values); `prose_value` replaces the `or ""` guard at ten call sites across the five modules; an AST sweep in `test_ledger.py` reports every remaining `.get(...) or ""` on a fields-file receiver against a registered set of 2, the residue outside this unit's `Affects`. 9 declared mutants applied and killed. |
