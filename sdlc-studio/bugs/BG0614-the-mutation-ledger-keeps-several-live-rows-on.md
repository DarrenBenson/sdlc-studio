# BG0614: the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the join takes whichever was iterated last

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** Adversarial review of BG0606, 2026-08-25, which found three live rows on BG0606 AC1 row 0. Widened to a full-ledger audit by the authoring session, finding 14 keys.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`register_mutant` appends rather than replacing, so re-registering a criterion after re-executing its mutant leaves BOTH rows live. `plan_execution` joins on `(criterion, row)` and takes the last iterated, which is correct only by accident of ordering. Audited 2026-08-25 across the whole ledger: FOURTEEN live keys carry more than one row, and NINE of them carry rows naming DIFFERENT tests - BG0606 AC1 row 0 has three, two of which record the kill against `test_every_reviewed_plan_is_still_in_derived_shape`, a node that no longer exists anywhere in the repository. A verdict recorded against a test that cannot be run is evidence of nothing, and it is indistinguishable from a live one at the join. `mutation.py retract` writes a `withdrawn` marker and the readers honour it, so the machinery to resolve this exists and is simply not applied to same-key re-registration.

## Steps to Reproduce

1. Register a mutant for a unit's criterion. 2. Re-execute it after an edit and register again with the same unit, criterion and row. 3. Read the ledger: both rows are live, neither is marked withdrawn, and nothing reports the duplication. Audited 2026-08-25: 9 live duplicate keys across the corpus, 4 of them naming different tests.

## Proposed Fix

Make a same-key registration SUPERSEDE the row it replaces - write the `withdrawn` marker on the older row with `superseded by re-registration` as the reason, so the log still shows both and the join sees one. Add an audit that reports any live key holding more than one row, because nothing does today and this was found by hand during a review rather than by a check.

## Acceptance Criteria

- [ ] **AC1** Given a mutant re-registered against the same unit, criterion and row, when the ledger is read, then the earlier row is marked WITHDRAWN and the join sees exactly one - the log still shows both
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_same_key_registration_supersedes_the_row_it_replaces
- [ ] **AC2** Given a ledger holding a live duplicate key, when the audit runs, then it REPORTS the key and the rows - nothing does today, and the nine live duplicates were found by hand during a review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_reports_a_live_duplicate_key
- [ ] **AC3** Given a ledger with no duplicate keys, when the audit runs, then it is silent - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_clean_ledger_audits_silently

## Impact

`plan_execution` decides whether a unit's planned mutants were executed, and `transition -> Fixed` refuses on its answer. When two live rows disagree, the gate's verdict is a fact about iteration order. Worse, a stale row can carry a verdict for a test that has since been renamed or deleted, so a unit can pass the terminal gate on evidence that cannot be re-run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
