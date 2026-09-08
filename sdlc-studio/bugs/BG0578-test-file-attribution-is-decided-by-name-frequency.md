# BG0578: test-file attribution is decided by name frequency, so mentioning one more module silently changes a file's owner

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** tools/test_census.py, tools/tests/test_test_census.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Evidence:** RUN-01KZQ03V, 2026-08-14, while delivering BG0556 - the full suite went red on an attribution change caused by adding an inventory of script names to a test module.
> **Created:** 2026-08-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-14T01:30:38Z

## Summary

`test_census.attribute` places a test file by counting how often it names each sibling module and taking the most-mentioned. That makes the owner a property of the prose rather than of the subject. `test_cli_grammar.py` was attributed to `transition.py` on a count; BG0556 added an inventory naming 21 scripts, `sprint.py` among them, the count tied, and the file became unattributed - tripping a ratchet that is documented as never being raised. Nothing about what the file tests changed.

## Steps to Reproduce

1. `python3 -c "import sys; sys.path.insert(0,'tools'); import test_census as tc, pathlib; print(tc.attribute(pathlib.Path('.').resolve(), '.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py'))"` 2. Add one more mention of any sibling module to that file. 3. Re-run: the owner changes, or the file becomes unattributed on a tie. Observed 2026-08-14: transition.py -> unattributed, on a diff that added no coverage of transition.py at all.

## Proposed Fix

Attribution should prefer a DECLARED owner over a counted one: a unit's `Affects` already names the file, and a module-level marker in the test would state its subject outright. Counting stays as the fallback for files that declare nothing. A tie should also report the candidates rather than dropping the file, so the ratchet moves on a real coverage change and not on prose.

## Acceptance Criteria

- [ ] **AC1** Given a test file carrying a module-level subject marker, when `test_census.attribute` places it, then it returns the declared subject whatever the mention counts say, and BEFORE the by-name route as well. Measured over the two test trees, 95 of 204 files are placed by that route and only 73 by counting, so a marker consulted after it would be ignored on most of the corpus
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_a_module_level_subject_marker_decides_the_owner
  - **Verified:** no
- [ ] **AC2** Given a test file with no marker whose declaring unit names exactly ONE script in `Affects`, when attribute places it, then it returns that script; and given one whose declaring units name several between them, the declaration does not decide, counting continues, and the result says which route answered. Most files here are declared by several units naming many scripts, so a rule that only handles the single-script case decides almost nothing
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_a_single_script_declaration_decides_and_a_multi_script_one_defers
  - **Verified:** no
- [ ] **AC3** Given a test file with neither a marker nor a deciding declaration, and one sibling module named more often than any other, when attribute places it, then it returns that module - counting survives as the fallback, not as the rule
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_counting_is_the_fallback_and_says_so
  - **Verified:** no
- [ ] **AC4** Given a test file whose two most-mentioned siblings TIE and which carries a marker or a single-script declaration, when attribute places it, then it is ATTRIBUTED by that route rather than reported unattributed. A tie already names its tied candidates today, so asserting the wording alone passes on unmodified code; what is false at HEAD is that the file gets an owner
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_a_tie_with_a_declared_owner_is_attributed_not_unattributed
  - **Verified:** no
- [ ] **AC5** Given `.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py` as it stands - unattributed today on a tie between two sibling modules - when one more mention of any sibling is added to a copy of it and attribution is re-run, then the owner is unchanged. The copy is made into a temp tree carrying the SIBLING MODULE DIRECTORY with it: a copy beside the original is an untracked file the repo-writes lane refuses, and a copy alone answers that no source module sits beside it
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_one_more_mention_cannot_move_the_grammar_module
  - **Verified:** no
- [ ] **AC6** Given the attribution map taken over the real corpus through the shipped entry point, when a prose-only mention is added to a copied test file and the map is retaken, then NO file's owner changes. The ratchet counts unattributed files, so an owner flip from one module to another leaves its number untouched - the count cannot observe the defect in this bug's own title, and the map can. The entry point requires a junit report, so the criterion is satisfied with one generated over the copied tree rather than with the corpus's own
  - **Verify:** pytest tools/tests/test_test_census.py::AttributionTests::test_the_owner_map_is_stable_under_a_prose_only_edit
  - **Verified:** no

## Impact

The ratchet is the guard on test attribution and it fires on edits that change no coverage, which trains raising the baseline - the one action its own comment forbids. A file that legitimately has no owner (a cross-cutting family sweep) is indistinguishable from one that lost its owner to a wording change.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/test_census.py, delete the marker lookup from `attribute` | Given a test file carrying a module-level subject marker, when `test_census.attribute` places it, then it returns the declared subject whatever the mention counts say, and BEFORE the by-name route as well. Measured over the two test trees, 95 of 204 files are placed by that route and only 73 by counting, so a marker consulted after it would be ignored on most of the corpus |
| AC2 | in tools/test_census.py, widen the declaration route to take the first script of a multi-script declaration | Given a test file with no marker whose declaring unit names exactly ONE script in `Affects`, when attribute places it, then it returns that script; and given one whose declaring units name several between them, the declaration does not decide, counting continues, and the result says which route answered. Most files here are declared by several units naming many scripts, so a rule that only handles the single-script case decides almost nothing |
| AC3 | in tools/test_census.py, delete the counting fallback so a file with no declared subject is dropped | Given a test file with neither a marker nor a deciding declaration, and one sibling module named more often than any other, when attribute places it, then it returns that module - counting survives as the fallback, not as the rule |
| AC4 | in tools/test_census.py, return the unattributed result whenever the counts tie, before the declared routes are consulted | Given a test file whose two most-mentioned siblings TIE and which carries a marker or a single-script declaration, when attribute places it, then it is ATTRIBUTED by that route rather than reported unattributed. A tie already names its tied candidates today, so asserting the wording alone passes on unmodified code; what is false at HEAD is that the file gets an owner |
| AC5 | in tools/test_census.py, remove the marker branch so mention frequency decides `test_cli_grammar.py` again | Given `.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py` as it stands - unattributed today on a tie between two sibling modules - when one more mention of any sibling is added to a copy of it and attribution is re-run, then the owner is unchanged. The copy is made into a temp tree carrying the SIBLING MODULE DIRECTORY with it: a copy beside the original is an untracked file the repo-writes lane refuses, and a copy alone answers that no source module sits beside it |
| AC6 | in tools/test_census.py, drop the per-file owner from the entry point's payload, emitting only the tally | Given the attribution map taken over the real corpus through the shipped entry point, when a prose-only mention is added to a copied test file and the map is retaken, then NO file's owner changes. The ratchet counts unattributed files, so an owner flip from one module to another leaves its number untouched - the count cannot observe the defect in this bug's own title, and the map can. The entry point requires a junit report, so the criterion is satisfied with one generated over the copied tree rather than with the corpus's own |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-14 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
