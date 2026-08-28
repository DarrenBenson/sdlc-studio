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

`register_mutant` appends rather than replacing, so re-registering a criterion after re-executing its mutant leaves BOTH rows live. `plan_execution` joins on `(criterion, row)` and takes the last iterated, which is correct only by accident of ordering. Audited 2026-08-25 across the whole ledger: FOURTEEN live keys carry more than one row, and SIX of them carry rows naming DIFFERENT tests - BG0606 AC1 row 0 has three, two of which record the kill against `test_every_reviewed_plan_is_still_in_derived_shape`, a node that no longer exists anywhere in the repository. A verdict recorded against a test that cannot be run is evidence of nothing, and it is indistinguishable from a live one at the join. `mutation.py retract` writes a `withdrawn` marker and the readers honour it, so the machinery to resolve this exists and is simply not applied to same-key re-registration.

## Steps to Reproduce

1. Register a mutant for a unit's criterion. 2. Re-execute it after an edit and register again with the same unit, criterion and row. 3. Read the ledger: both rows are live, neither is marked withdrawn, and nothing reports the duplication. Audited 2026-08-25 and re-counted 2026-08-27: 14 live duplicate keys across the corpus, 6 of them naming different tests.

## Proposed Fix

Make a same-key registration SUPERSEDE the row it replaces - write the `withdrawn` marker on the older row with `superseded by re-registration` as the reason, so the log still shows both and the join sees one. Add an audit that reports any live key holding more than one row, because nothing does today and this was found by hand during a review rather than by a check.

## Why this AUDITS rather than supersedes

An earlier draft of this bug made a re-registration WITHDRAW the earlier row. That is a change
the code under repair records as asked for and refused, and it says why in place:
`register_mutant` notes that a later registration is "NOT superseded ... though a review round
asked for it", because `plan_execution` holds the opposite rule deliberately - the WORST
verdict per criterion wins, so a later kill cannot cancel an earlier survivor - "and that rule
exists because a genuine correction and an author registering their way out of a survivor are
byte-identical here". `retract_mutant`'s docstring records the same design being implemented
and then reverted.

The draft would have reopened it precisely. `plan_execution` SKIPS a withdrawn row, which is
affordable only because `retract` costs a reason of a minimum length and stays on the record; a
supersede writes the same marker with no reason and no author, so the skip becomes free. And
the draft required the supersede to fire when the test name differed - so registering
`survived`, then re-registering `killed` under a marginally different test, would withdraw the
survivor and skip it. Nine criteria, none of which pinned that.

So this unit AUDITS. Nothing today reports a duplicate key, which is the whole of the harm that
survives worst-verdict-wins: the ledger holds rows a reader cannot tell apart and no command
says so. Correcting one stays with `retract`, which costs a reason and leaves the correction on
the record where a reviewer can judge it. That is the trade the code already made, and this
bug is not the place to reverse it.

## Acceptance Criteria

- [ ] **AC1** Given a ledger holding two live rows on one `(unit, criterion, row)` key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. The disagreeing pair is the case a reader most needs told about, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_reports_a_key_whose_rows_disagree
- [ ] **AC2** Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_clean_ledger_produces_no_audit_output
- [ ] **AC3** Given the shipped command, when the audit is run as a SUBPROCESS over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today - its subcommands are run, register, retract, retractions, yield, window and prefilter - so this criterion is what makes the audit reachable at all rather than a library function nothing calls
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_verb_reports_a_duplicate_through_the_cli
- [ ] **AC4** Given THIS repository's own ledger, when the audit runs, then it names the fourteen live duplicate keys. The corpus is where this defect lives, and the count is asserted as a property of what the fixture-free ledger holds rather than as a number frozen into the test, because the ledger moves with every run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_live_ledger_duplicates_are_all_reported

## Impact

`plan_execution` decides whether a unit's planned mutants were executed, and `transition -> Fixed` refuses on its answer. When two live rows disagree, the gate's verdict is a fact about iteration order. Worse, a stale row can carry a verdict for a test that has since been renamed or deleted, so a unit can pass the terminal gate on evidence that cannot be re-run.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, narrow the duplicate test with an extra equality on the verdict column, so a key is counted only when its rows agree - the shape a killed/survived pair walks straight through | Given a ledger holding two live rows on one `(unit, criterion, row)` key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. The disagreeing pair is the case a reader most needs told about, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice |
| AC2 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, report every key the audit walks rather than only the duplicated ones, so a clean ledger produces output | Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything |
| AC3 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, keep the audit correct but omit its subcommand from the parser, so the library agrees and the shipped command cannot reach it | Given the shipped command, when the audit is run as a SUBPROCESS over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today - its subcommands are run, register, retract, retractions, yield, window and prefilter - so this criterion is what makes the audit reachable at all rather than a library function nothing calls |
| AC4 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, count a row as live only when it carries no `withdrawn` marker AND its entry is the newest for that target, so the fourteen collapse to the two that span entries - a corpus-only mutant, since no fixture here holds rows across two content hashes | Given THIS repository's own ledger, when the audit runs, then it names the fourteen live duplicate keys. The corpus is where this defect lives, and the count is asserted as a property of what the fixture-free ledger holds rather than as a number frozen into the test, because the ledger moves with every run |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
