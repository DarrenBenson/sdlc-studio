# BG0663: the release cut turns main red: `changelog.py check` cannot name an artefact once the fragments are composed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Evidence:** CI run 34539944618, job 103080105925, step `Run script unit tests`, 2026-09-10 22:59:42Z to 23:25:52Z: `Ran 7010 tests in 1567.597s / FAILED (failures=1, skipped=15)`, the failure `changelog.py check: pointed at the real tree it named no artefact of it`. Reproduced locally in 40.59s on the same commit; `changelog.py check --root .` prints `no stray fragments`.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`test_cli_grammar.RootIsReadNotJustParsed.test_every_listed_verb_can_actually_fail_the_guard` runs every verb in `ROOT_EFFECT_VERBS` against the REAL tree and requires each to name a real artefact id - that is what earns a row its place in the fixture guard beside it. `changelog.py check` names PENDING changelog fragments, and a release cut composes every one of them, so immediately after `release_cut.py changelog-cut` the verb prints `no stray fragments` and names nothing. The row then asserts nothing and the control fails.

The failure is on a CORRECT tree. An empty `changelog.d/` right after a cut is the healthy state, and this is a boundary-only test, so the moment it runs is exactly the moment the corpus cannot satisfy it. Measured on CI run 34539944618 at commit 1a9f948d - the v5.1.0 cut - `Ran 7010 tests, FAILED (failures=1)`, and reproduced here in 40s.

## Steps to Reproduce

1. On a tree with pending fragments, run the control: it passes, because `changelog.py check` names them.
2. Run `release_cut.py changelog-cut --version <v>`; `changelog.d/` is emptied.
3. Re-run `SDLC_STUDIO_BOUNDARY_SUITE=1 pytest test_cli_grammar.py::RootIsReadNotJustParsed::test_every_listed_verb_can_actually_fail_the_guard`.
4. It FAILS on `changelog.py check`: `pointed at the real tree it named no artefact of it`.

## Proposed Fix

Drop `changelog.py check` from `ROOT_EFFECT_VERBS`. Membership is earned by MEASUREMENT against the real tree, and this verb's output depends on a population that is legitimately empty at the one boundary where the control runs - so it cannot hold a permanent row. The test's own message already offers this remedy. Record the reason in the inventory so nobody re-adds it, and name the coverage the guard loses.

## Acceptance Criteria

- [ ] **AC1** Given a tree whose `changelog.d/` is EMPTY - the state every release cut leaves - when the root-effect control runs over the whole inventory, then it PASSES. The control is about whether each listed verb reads the tree, and a verb whose output is empty on a correct tree cannot answer that question
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RootIsReadNotJustParsed::test_every_listed_verb_can_actually_fail_the_guard
- [ ] **AC2** Given the inventory, when it is read, then `changelog.py check` is absent from it and the reason is recorded beside the list. Without the recorded reason the next author re-adds it: it looks like an obvious omission, and it passes on any tree that happens to carry a pending fragment
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RootIsReadNotJustParsed::test_the_inventory_records_why_a_verb_was_withdrawn
- [ ] **AC3** Given the inventory after the removal, when the subset check runs, then it still holds - the list is non-empty and strictly smaller than the invocable surface. A repair that empties the guard satisfies the row above perfectly
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RootIsReadNotJustParsed::test_the_inventory_is_a_measured_subset_and_never_the_whole_surface

## Impact

Every release cut turns main red on the next push, and the red is indistinguishable from a real regression until somebody reads the log. It also blocks the tag: `release_cut.py tag-check` refuses a commit whose CI run is not a success, so the cut cannot become a release.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
| 2026-09-11 | Claude Opus 5 | Delivered. `changelog.py check` is withdrawn from the root-effect inventory and the reason travels with the list in `WITHDRAWN_ROOT_EFFECT_VERBS`, because a verb REMOVED from a measured inventory is indistinguishable from one nobody considered - and it passes on any tree that happens to carry a pending fragment, which is most of them. Three mutants, three killed, and two were re-aimed after surviving: `{} or {...}` is a no-op because an empty dict is falsy, and dropping ONE of nine inventory entries satisfies AC3 correctly, since AC3 is about a repair that EMPTIES the guard. A mutant that changes nothing is not weak evidence, it is none |
