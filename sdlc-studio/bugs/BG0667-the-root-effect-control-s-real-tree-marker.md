# BG0667: the root-effect control's real-tree marker is bound to an id range this project has already outgrown, so its evidence window closes as ids advance

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Evidence:** Introduced by commit 0987a620 (BG0555/BG0556) and untouched since. Measured by an independent test-plan reviewer on 2026-09-11 in an isolated copy: BG0663's AC1 mutant survives with `changelog.d/US0674.md` present (`1 passed, 10 subtests passed in 41.07s`) and dies with the directory emptied.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`test_cli_grammar._REAL_TREE_MARKER` is `\\b(?:BG05\\d\\d|US06\\d\\d|RUN-01K\\w+)`. It is what proves a verb READ the real tree rather than printing something either way, and it recognises only three id shapes fixed at the time it was written. This project now mints BG06xx and US08xx, and run ids have moved past `RUN-01K`.

The control therefore weakens silently as the corpus advances: a verb whose output names only recent ids reads as naming nothing. An independent seat measured the consequence on BG0663 - with one realistic pending fragment present (`changelog.d/US0674.md`, a live story id), the marker matched and a mutant that should have died SURVIVED; with only BG06xx fragments present, outside the marker, the same mutant died. The verdict oscillates with which ids happen to be in the tree.

A guard whose evidence window is an id range is a guard with an expiry date nobody wrote down.

## Steps to Reproduce

1. Read `_REAL_TREE_MARKER`: it matches `BG05xx`, `US06xx` and `RUN-01K...` only.
2. `ls sdlc-studio/bugs | tail -1` - this project mints BG06xx, outside it.
3. Put a `US06xx`-named pending fragment in `changelog.d/` and reinstate `changelog.py check` in the inventory: the control PASSES, because the marker matched.
4. Empty `changelog.d/` and repeat: it fails. Same code, opposite verdict, decided by which ids are in the tree.

## Proposed Fix

Derive the marker from the corpus rather than freezing a range: build it from the id prefixes the tree actually holds, or match the shape `(BG|US|CR|RFC)\\d{4}` and require the id to RESOLVE to a file. Resolving is the stronger form - it is what 'named a real artefact of this tree' actually means, and it cannot go stale.

## Acceptance Criteria

- [ ] **AC1** Given an artefact id this project mints TODAY - a BG06xx or US08xx - when the real-tree marker is asked whether it names a real artefact, then it says yes. The marker recognises three frozen ranges and this corpus has left all three, so the control it serves is already weaker than it reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_an_id_this_project_mints_today_is_recognised
- [ ] **AC2** Given an id-SHAPED string that resolves to no artefact in the tree, when the marker is asked, then it says NO. The paired control: widening the pattern until everything matches passes the row above and destroys the thing the marker is for, which is telling a real-tree answer from any answer
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_an_id_shaped_string_that_resolves_to_nothing_is_refused
- [ ] **AC3** Given the root-effect control, when it runs with pending changelog fragments present AND with none, then it reaches the same verdict. That equivalence is what the current marker cannot give, and it is the property the whole guard rests on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py::RealTreeMarkerTests::test_the_control_reaches_the_same_verdict_in_either_fragment_state

## Impact

The control exists so that a clean run of the fixture guard means the `--root` flag was obeyed, rather than that the verb prints nothing either way. As ids advance it quietly stops being able to tell those apart, and it takes the fixture guard's meaning with it - while continuing to pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
