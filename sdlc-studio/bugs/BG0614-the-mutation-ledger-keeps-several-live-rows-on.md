# BG0614: the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the join takes whichever was iterated last

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional [[derived: criteria 6; plan rows 6; executed 6; killed 6; survived 0; not-run 0; entry point 5 of 6 criteria through the shipped CLI, 1 in-process | fp dfdd1745417a ]] (AC3 drives the shipped verb by subprocess with exact exit codes both ways; AC1, AC2, AC4 to AC6 drive `main` in-process over a committed fixture ledger with materialised targets, so `entry_staleness` hashes real bytes; the corpus figure is recorded in the revision row from the shipped verb, never as a suite test)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-surface.md
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

- [ ] **AC1** Given a ledger holding two live rows on one `(unit, criterion, row)` key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. A row is LIVE when it is not withdrawn, whether or not its entry is stale; a row in a stale entry is reported tagged `stale entry` (three of today's keys sit in one), and each row is printed with its target and hash so a same-row pair on different hashes can be told from a same-hash pair. The audit keys on `(unit, criterion, row)`; US0818's replace keys on `(unit, criterion, row, target, hash)`, so a same-row registration against a different target PATH appends there and is named here (a different hash of the same target cannot: `register_mutant` drops the unit's own rows on the old hash before it appends). A withdrawn row is NOT live: the AC4 fixture holds a withdrawn duplicate that the expected key list excludes, so a walk counting retracted rows names it and dies. The disagreeing pair is the case a reader most needs told about, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_reports_a_key_whose_rows_disagree
  - **Verified:** yes (2026-09-08)
- [ ] **AC2** Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_a_clean_ledger_produces_no_audit_output
  - **Verified:** yes (2026-09-08)
- [ ] **AC3** Given the shipped command, when the audit is run as a SUBPROCESS over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today - its subcommands are run, register, retract, retractions, yield, window and prefilter - so this criterion is what makes the audit reachable at all rather than a library function nothing calls The audit exits 1 with a duplicate and 0 on a clean ledger, both asserted as exact codes through the CLI (argparse's 2 for a mis-typed verb satisfies neither), with the key in stdout on the duplicate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_audit_verb_reports_a_duplicate_through_the_cli
  - **Verified:** yes (2026-09-08)
- [ ] **AC4** Given a COMMITTED ledger fixture under `scripts/tests/fixtures/` whose entries name target files that exist INSIDE the fixture (so `entry_staleness` can hash them), carrying the shapes this repository's ledger holds today - measured 2026-09-07 on `sdlc-studio/.local/mutation-runs.json` by a walk over `entries[].mutants` excluding withdrawn rows, keyed on `(unit, criterion, row)`: 19 live duplicate keys, 0 disagreeing on verdict, 5 naming different tests, every one on a single `(target, hash)` entry, 3 in entries `entry_staleness` reports stale (the fixture's `stale_target.py` is written with bytes that differ from its entry's hash, so the tag branch is entered) - two rows one test, three rows two tests, four rows one test, three keys in a stale entry, AND one criterion carrying two DISTINCT rows (row 0 and row 1, each once, no duplicate) so a key that drops the row collapses them - when the audit runs, then it names every duplicated key, and does not name the two-distinct-rows criterion; the stale tag and the different-tests count are AC5 and AC6. The live corpus figure is re-measured at delivery through `mutation.py audit` and recorded in the revision row with the command; the suite never reads `.local/`, which is gitignored and absent on CI.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_live_ledger_duplicates_are_all_reported
  - **Verified:** yes (2026-09-08)
- [ ] **AC5** Given the AC4 fixture, when the audit runs, then each row whose entry `entry_staleness` reports stale is printed with the exact tag `stale entry`, and rows in current entries carry no tag - asserted as exact expected lines.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_rows_in_a_stale_entry_are_tagged_and_current_rows_are_not
  - **Verified:** yes (2026-09-08)
- [ ] **AC6** Given the AC4 fixture, when the audit runs, then its summary counts exactly the duplicated keys whose rows name DIFFERENT tests (five shapes in the fixture, matching the corpus measurement), never every duplicated key - asserted as an exact expected line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::DuplicateKeyTests::test_the_summary_counts_only_keys_whose_rows_name_different_tests
  - **Verified:** yes (2026-09-08)

## Impact

`plan_execution` decides whether a unit's planned mutants were executed, and `transition -> Fixed` refuses on its answer. When two live rows disagree, the gate's verdict is a fact about iteration order. Worse, a stale row can carry a verdict for a test that has since been renamed or deleted, so a unit can pass the terminal gate on evidence that cannot be re-run.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, narrow the duplicate test with an extra equality on the verdict column, so a key is counted only when its rows agree - the shape a killed/survived pair walks straight through; second, drop the `withdrawn` skip so the fixture's retracted duplicate is named | Given a ledger holding two live rows on one `(unit, criterion, row)` key that DISAGREE on their verdict - one killed, one survived - when the audit runs, then it reports the key and both rows. A row is LIVE when it is not withdrawn, whether or not its entry is stale; a row in a stale entry is reported tagged `stale entry` (three of today's keys sit in one), and each row is printed with its target and hash so a same-row pair on different hashes can be told from a same-hash pair. The audit keys on `(unit, criterion, row)`; US0818's replace keys on `(unit, criterion, row, target, hash)`, so a same-row registration against a different target PATH appends there and is named here (a different hash of the same target cannot: `register_mutant` drops the unit's own rows on the old hash before it appends). A withdrawn row is NOT live: the AC4 fixture holds a withdrawn duplicate that the expected key list excludes, so a walk counting retracted rows names it and dies. The disagreeing pair is the case a reader most needs told about, and a detector that only fires when the rows agree would pass a fixture nobody looks at twice |
| AC2 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, report every key the audit walks rather than only the duplicated ones, so a clean ledger produces output | Given a ledger with no duplicate keys, when the audit runs, then it is SILENT - the paired control, so reporting cannot be satisfied by reporting everything |
| AC3 | in `.claude/skills/sdlc-studio/scripts/mutation.py`, keep the audit correct but omit its subcommand from the parser, so the library agrees and the shipped command cannot reach it | Given the shipped command, when the audit is run as a SUBPROCESS over a ledger holding a duplicate, then it names the key and exits non-zero. `mutation.py` has no audit verb today - its subcommands are run, register, retract, retractions, yield, window and prefilter - so this criterion is what makes the audit reachable at all rather than a library function nothing calls The audit exits 1 with a duplicate and 0 on a clean ledger, both asserted as exact codes through the CLI (argparse's 2 for a mis-typed verb satisfies neither), with the key in stdout on the duplicate. |
| AC4 | in mutation.py, key the audit on `(unit, criterion)` and drop the row, so the fixture's two-distinct-rows criterion is named as a duplicate and the count changes; the earlier row's mutant (`newest entry per target`) was INERT on this ledger, where every duplicate sits in one entry | Given a COMMITTED ledger fixture under `scripts/tests/fixtures/` whose entries name target files that exist INSIDE the fixture (so `entry_staleness` can hash them), carrying the shapes this repository's ledger holds today - measured 2026-09-07 on `sdlc-studio/.local/mutation-runs.json` by a walk over `entries[].mutants` excluding withdrawn rows, keyed on `(unit, criterion, row)`: 19 live duplicate keys, 0 disagreeing on verdict, 5 naming different tests, every one on a single `(target, hash)` entry, 3 in entries `entry_staleness` reports stale (the fixture's `stale_target.py` is written with bytes that differ from its entry's hash, so the tag branch is entered) - two rows one test, three rows two tests, four rows one test, three keys in a stale entry, AND one criterion carrying two DISTINCT rows (row 0 and row 1, each once, no duplicate) so a key that drops the row collapses them - when the audit runs, then it names every duplicated key, and does not name the two-distinct-rows criterion; the stale tag and the different-tests count are AC5 and AC6. The live corpus figure is re-measured at delivery through `mutation.py audit` and recorded in the revision row with the command; the suite never reads `.local/`, which is gitignored and absent on CI. |
| AC5 | in .claude/skills/sdlc-studio/scripts/mutation.py, delete the `entry_staleness` call in the audit's row printer and emit an empty suffix | Given the AC4 fixture, when the audit runs, then each row whose entry `entry_staleness` reports stale is printed with the exact tag `stale entry`, and rows in current entries carry no tag - asserted as exact expected lines. |
| AC6 | in .claude/skills/sdlc-studio/scripts/mutation.py, hard-code the summary's second figure to `len(dups)` | Given the AC4 fixture, when the audit runs, then its summary counts exactly the duplicated keys whose rows name DIFFERENT tests (five shapes in the fixture, matching the corpus measurement), never every duplicated key - asserted as an exact expected line. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 1: AC1 defines live against stale entries and prints target and hash; AC4 re-measured (19 keys, not fourteen, by the walk named in the criterion), reads a committed fixture instead of the gitignored ledger, and its plan row names a mutant the fixture reaches |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 2: AC4's fixture gains materialised targets and a two-distinct-rows criterion so the (unit, criterion) mutant moves on it (qa); the Test Plan title re-synced |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 3 (all seats yes): Test Plan titles re-synced to the criteria |
| 2026-09-07 | Claude Fable 5.1 | Plan review round 1: qa REJECT answered - AC1 defines withdrawn as not live with a fixture row and a mutant, AC3 pins exact exit codes with a clean-ledger control through the CLI, AC4's three claims split into AC4, AC5 and AC6 with a row each and the drifted fixture file named; US0818's different-hash control restated as a different target path (engineering) |
| 2026-09-08 | Claude Fable 5.1 | Delivery: built in a worktree while the corpus lane ran, ported by patch. AC4's obligation, the live figure by the shipped verb `python3 .claude/skills/sdlc-studio/scripts/mutation.py audit --root .`: 21 duplicated keys, 5 naming different tests, 0 disagreeing at first run - three of the 21 were this run's own (BG0653 AC3, AC4, AC5, registered twice on unchanged bytes by a re-run of its runner, US0818's case), withdrawn with the reason and re-measured once, after which the verb reads 18 duplicated keys, 5 naming different tests, 0 disagreeing. Seven mutants, seven killed (two rows on AC1). D0183's figure by `coverage run` with `patch = subprocess` joined to `git diff -U0`: 38 added statements, 37 executed by the unit's own tests, 1 uncovered - the `continue` past a non-dict entry, which no ledger this repository writes contains; ruled by note |
| 2026-09-08 | Claude Fable 5.1 | Delivery: the commit hook's suites refused the first commit on `test_command_audit`'s verb census - a shipped verb named in no hand-written doc (263 verbs, 262 documented) - so `reference-scripts.md` names `audit` (joins Affects); BG0653's `stamps --staged`, reported by its engineering seat as uncatalogued, is named in the same sentence |
| 2026-09-08 | Claude Fable 5.1 | Delivery: the verb census reads the GENERATED catalogue, so `docgen.py surface` was re-run and its page joins Affects (.claude/skills/sdlc-studio/reference-scripts-surface.md) |
| 2026-09-08 | Claude Fable 5.1 | Delivery review round 1 (engineering, product, qa REJECT): the two catalogue bullets in `reference-scripts.md` restored to coherent prose with the `stamps --staged` and `audit` sentences at each bullet's end (the `verify_ac.py` bullet, truncated since before the base ref, now completes); `audit` reads the ledger through `ledger_entries`, so an unparseable ledger is refused with the path named and exit 1 rather than read as clean; each row prints the mutant description `retract` joins on and the summary's remedy separates rows that differ (withdraw the wrong one on the printed join fields) from rows identical on them (`retract` withdraws them together, re-register once); the docstring states what `register` writes (0) and what None marks (a pre-row-column row); the fixture README says the three stale-entry keys pair a None row with a 0 row (a walk on the literal value counts 16, the audit 19); the fragment carries one dated measurement (21 then 18 by the shipped verb, 2026-09-08). Five new mutants from the diff, each killed by a new `AuditRemedyTests` case: swallow the unreadable refusal, hard-code the different-tests figure to 5, hard-code the disagreeing figure to 0, tag only `stale` and not `missing`, drop the printed description - twelve rows on this unit, twelve killed. D0183 re-measured after the last edit: 39 added statements, 39 executed, 0 uncovered (the non-dict `continue` is gone with the loader). The first coverage read named line 2659 uncovered and outside the audit: a BG0651 mutant left in the working tree by a re-measure runner killed mid-run - restored, and every row on `mutation.py` (BG0614, BG0596, BG0597, BG0651) re-measured on the restored bytes; the live verb reads 18 duplicated keys, 5 naming different tests, 0 disagreeing |
