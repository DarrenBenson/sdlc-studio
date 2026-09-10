# BG0612: Three limbs that survived the closure of BG0599 and BG0602: an edit-verb gap, an unpinned checklist roster and an import-time blind spot

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Both parent filings were re-verified against source by an independent goal review on 2026-08-25 before any code was written, and closed with the source lines that settle them recorded on each artefact. This unit carries only the limbs that survived that verification.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0599 and BG0602 were closed on 2026-08-25 because their stated causes do not reproduce at HEAD - derive already reports every fault in one invocation, and the close checklist is an explicit tuple rather than a name-prefix scan. Three narrower defects inside those filings do stand, and are carried here rather than lost with the artefacts that named them.

## Steps to Reproduce

Edit verbs: `verify_ac.py`'s `_EDIT_VERBS` holds 61 verbs and omits `restore` and `keep`, so a mutant phrased as 'restore the base constant' is refused for carrying no edit verb while a synonym passes - observed repeatedly while authoring test plans on RUN-01M0JD1W. Roster: `sprint_report.py`'s `CHECKLIST` tuple is asserted by no test that pins its names or its length, so a check removed from it is a silent shrink. Import blind spot: `_resolve_item` resolves a checklist entry through `globals().get(...)` at call time, so an entry naming a function nobody wrote is discovered when the close runs rather than when the module loads.

## Proposed Fix

Add the two missing verbs and a test that fails on their absence. Pin the CHECKLIST roster by exact names and count. Resolve every registered check at import and refuse there, so a registered-but-undefined entry cannot reach a close.

## Acceptance Criteria

- [ ] **AC1** Given a mutant cell whose edit verb is `restore` or `keep` - neither is in the 61-entry vocabulary today - when `testplan derive` runs, then the cell is accepted; and given a cell with no edit verb at all, it is still refused. The vocabulary is widened, not disabled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EditVerbVocabularyTests::test_restore_and_keep_are_accepted_and_a_verbless_cell_is_still_refused
  - **Verified:** no
- [ ] **AC2** Given the close checklist roster, when its test runs, then it asserts the roster's exact entry names and its exact count, so deleting an entry fails the test rather than silently shrinking the close report
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRosterTests::test_the_roster_asserts_its_exact_names_and_count
  - **Verified:** no
- [ ] **AC3** Given a roster entry naming a resolver that is absent, and one naming an attribute that exists but is not callable, when `sprint_report` is imported, then each is refused at import. `_resolve_item` catches broadly and degrades a missing resolver to UNANSWERED at close time, which is the moment a missing check is least recoverable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRosterTests::test_an_undefined_or_uncallable_resolver_refuses_at_import
  - **Verified:** no
- [ ] **AC4** Given a roster whose every entry resolves to a callable, when the module is imported, then it loads normally - the paired control, so the import check is shown to discriminate rather than to refuse everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistRosterTests::test_a_fully_defined_roster_imports_normally
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, delete the two entries `restore` and `keep` from `_EDIT_VERBS` | Given a mutant cell whose edit verb is `restore` or `keep` - neither is in the 61-entry vocabulary today - when `testplan derive` runs, then the cell is accepted; and given a cell with no edit verb at all, it is still refused. The vocabulary is widened, not disabled |
| AC1 | in `.claude/skills/sdlc-studio/scripts/verify_ac.py`, delete the edit-verb limb from `testplan_row_faults`, so a cell naming no edit is accepted | The refusal itself is exercised, not the vocabulary constant |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint_report.py, drop the `known-issues` entry from the CHECKLIST literal | Given the close checklist roster, when its test runs, then it asserts the roster's exact entry names and its exact count, so deleting an entry fails the test rather than silently shrinking the close report |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint_report.py, delete the module-level loop that walks CHECKLIST and resolves each name | Given a roster entry naming a resolver that is absent, and one naming an attribute that exists but is not callable, when `sprint_report` is imported, then each is refused at import. `_resolve_item` catches broadly and degrades a missing resolver to UNANSWERED at close time, which is the moment a missing check is least recoverable |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint_report.py, narrow the import-time validation to a `hasattr` test, so an attribute that is not callable passes it | Given a roster entry naming a resolver that is absent, and one naming an attribute that exists but is not callable, when `sprint_report` is imported, then each is refused at import. `_resolve_item` catches broadly and degrades a missing resolver to UNANSWERED at close time, which is the moment a missing check is least recoverable |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint_report.py, raise unconditionally from the import-time validation | Given a roster whose every entry resolves to a callable, when the module is imported, then it loads normally - the paired control, so the import check is shown to discriminate rather than to refuse everything |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
| 2026-09-10 | Claude Opus 5 | Delivered. Five mutants, five killed. The vocabulary gains four restorative verbs, measured 61 entries before and 65 after. The roster is named rather than counted - 22 entries, listed in order - and the import-time resolver check sits at the END of the module rather than beside the roster, because the resolvers are defined below it and the check placed there refuses the module's own first entry. AC3's verifier imports a COPY of the shipped module with one roster entry rewritten, rather than re-running the check's logic in the test: a helper that rebuilds the thing under test passes with the thing deleted, which this repository has now shipped twice |
| 2026-09-10 | Claude Opus 5 | Delivery review, three seats per commit group: 33 verdicts, 18 REJECTs, every finding answered on the record. The class the round found is one shape - a criterion whose words go further than its fixture. Repaired here: AC1's edit-verb check now drives the shipped reader instead of re-typing the predicate; the probe's untrusted branch counts a runner-error exit, so a grep selector that is a typo stops classifying as the healthy class; the probe's delivered-detection reads the Refs trailers of delivery commits as well as subjects, after a census showed every one of its 25 findings was a unit the same commit had delivered; the two ruling verbs and the anchored-row rule are executed through the shipped command rather than in process; the boundary scan sees this repository's own subprocess idiom; the terminal test-plan gate states one absence once; and plan_execution judges a mutation row by its own site, which is where the anchors were never reaching. Two findings were refuted by execution and recorded as OVER-CLAIMED rather than repaired |
