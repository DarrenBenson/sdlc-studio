# BG0614: the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the join takes whichever was iterated last

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
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

## Scope of the supersede

`register_mutant` is keyed on the target file's CONTENT HASH and its own docstring records
that registrations on unchanged content ACCUMULATE. So the supersede's scope is the whole
design decision, and it is settled here rather than left to the implementer: it is scoped to
the ENTRY being appended to.

Measured over the ledger, 12 of the 14 duplicate keys sit inside one entry and 2 span
entries - BG0607's AC6 and AC7, across entries with DIFFERENT content hashes and different
targets. A cross-entry supersede would withdraw a live mutant registered against a file that
has since changed, which is evidence about code that still exists. Clearing 12 of 14 and
naming the other 2 is the honest outcome; clearing 14 of 14 is the one that looks tidier and
destroys evidence.

Three collisions with the existing `retract` path, each pinned below rather than discovered
in delivery: `retract` decrements the entry summary, and a supersede writing only the marker
would leave the join and the coverage lane disagreeing - this defect one layer down; it
refuses rows already carrying a marker, so a later legitimate retraction of a superseded row
would fail saying it matched nothing; and it refuses MEASURED rows, because withdrawing one
destroys run evidence.

Two consequences of writing a `withdrawn` marker, settled here rather than discovered in
delivery. `critic._withdrawn_block` renders every withdrawn row into the seat brief under a
heading telling the reviewer to judge the retraction and that an unconvincing one is a
finding - which is false about a supersede, since nobody retracted anything, and the first
repair pass would manufacture twelve at once. And `retract_mutant` skips rows already
carrying a marker, so a later legitimate retraction of a superseded row fails saying it
matched nothing. Both are pinned below rather than named and left.

## Acceptance Criteria

- [ ] **AC1** Given a mutant re-registered against the same unit, criterion and row IN THE SAME ENTRY and naming a DIFFERENT test, when the ledger is read, then the earlier row carries a withdrawn marker and the join sees one live row. The different test is required by the criterion, not left to the fixture: 8 of the 14 real duplicates share a test name, so a same-test fixture leaves the narrowing mutant alive
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_re_registration_in_the_same_entry_withdraws_the_earlier_row
- [ ] **AC2** Given a ledger holding two live rows on one key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. The disagreeing pair is the case the join gets wrong, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_reports_a_key_whose_rows_disagree
- [ ] **AC3** Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_clean_ledger_produces_no_audit_output
- [ ] **AC4** Given a re-registration made after the target's content hash CHANGED, so the two rows sit in different entries, when the ledger is read, then BOTH stay live and the audit names them. Withdrawing across entries would retract evidence about a file that still exists, and 2 of this corpus's 14 duplicates are exactly that shape
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_cross_entry_duplicate_is_reported_not_withdrawn
- [ ] **AC5** Given a supersede, when the entry summary is read, then its counts match the live rows. `retract` already adjusts them, and a marker written without that adjustment leaves the coverage lane counting a row the join no longer sees - which is this bug's own defect, one layer down
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_entry_summary_matches_the_live_rows_after_a_supersede
- [ ] **AC6** Given a MEASURED row rather than a registered one, when a re-registration would supersede it, then it is REFUSED. `retract` already refuses these because withdrawing one destroys run evidence, and a supersede with no such guard is a quieter way to do the same thing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_measured_row_is_never_superseded
- [ ] **AC7** Given the shipped command, when the audit is run as a subprocess over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today, so this criterion is what makes the audit reachable at all rather than a library function nothing calls
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_verb_reports_a_duplicate_through_the_cli

- [ ] **AC8** Given a superseded row, when the seat brief is generated, then it is NOT rendered as a retraction. `critic._withdrawn_block` tells the reviewer to judge a retraction and that an unconvincing one is a finding; a supersede is neither, and the first repair pass would put twelve of them in front of a reviewer
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DuplicateKeyTests::test_a_superseded_row_is_not_rendered_as_a_retraction
- [ ] **AC9** Given a superseded row, when it is later retracted for a real reason, then the retraction SUCCEEDS. `retract_mutant` skips rows already carrying a marker and reports that nothing matched, so without this the supersede quietly makes a row uncorrectable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_superseded_row_can_still_be_retracted

## Impact

`plan_execution` decides whether a unit's planned mutants were executed, and `transition -> Fixed` refuses on its answer. When two live rows disagree, the gate's verdict is a fact about iteration order. Worse, a stale row can carry a verdict for a test that has since been renamed or deleted, so a unit can pass the terminal gate on evidence that cannot be re-run.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, mark the earlier row withdrawn only when its test command also matches, so a re-registration naming a different test leaves both rows live - the narrowing a careless implementer adds to avoid retracting evidence | Given a mutant re-registered against the same unit, criterion and row IN THE SAME ENTRY and naming a DIFFERENT test, when the ledger is read, then the earlier row carries a withdrawn marker and the join sees one live row. The different test is required by the criterion, not left to the fixture: 8 of the 14 real duplicates share a test name, so a same-test fixture leaves the narrowing mutant alive |
| AC2 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, narrow the duplicate test so a key counts only when its rows also AGREE on their verdict, passing over a killed/survived pair - the case the join actually gets wrong | Given a ledger holding two live rows on one key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. The disagreeing pair is the case the join gets wrong, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice |
| AC3 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, report every key the audit walks rather than only the duplicated ones, so a clean ledger produces output - the over-correction | Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything |
| AC4 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, widen the supersede across every entry rather than the one being appended to, so a row registered against a file that has since changed content hash is withdrawn along with the true duplicate | Given a re-registration made after the target's content hash CHANGED, so the two rows sit in different entries, when the ledger is read, then BOTH stay live and the audit names them. Withdrawing across entries would retract evidence about a file that still exists, and 2 of this corpus's 14 duplicates are exactly that shape |
| AC5 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, remove the summary adjustment from the supersede path, keeping only the marker write, which is the shorter diff and leaves the counts describing a row the join has stopped returning | Given a supersede, when the entry summary is read, then its counts match the live rows. `retract` already adjusts them, and a marker written without that adjustment leaves the coverage lane counting a row the join no longer sees - which is this bug's own defect, one layer down |
| AC6 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, drop the provenance guard so a MEASURED row is superseded like a registered one, destroying run evidence | Given a MEASURED row rather than a registered one, when a re-registration would supersede it, then it is REFUSED. `retract` already refuses these because withdrawing one destroys run evidence, and a supersede with no such guard is a quieter way to do the same thing |
| AC7 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, keep the audit correct but omit its subcommand from the parser, so the library agrees and the shipped command cannot reach it | Given the shipped command, when the audit is run as a subprocess over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today, so this criterion is what makes the audit reachable at all rather than a library function nothing calls |
| AC8 | in `.claude/skills/sdlc-studio/scripts/critic.py`, remove the provenance test from `_withdrawn_block`'s row selection, so it renders whatever carries a marker and a supersede reaches the reviewer wearing a retraction's heading | a superseded row is not rendered as a retraction |
| AC9 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, keep `retract_mutant`'s blanket skip of rows carrying any marker, so a superseded row can never be retracted afterwards | a superseded row can still be retracted |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
