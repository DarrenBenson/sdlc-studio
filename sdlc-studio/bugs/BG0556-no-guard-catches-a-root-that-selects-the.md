# BG0556: no guard catches a --root that selects the file written but not the content read

> **Status:** Fixed
> **Verification depth:** functional (executed: all 128 invocable --root verbs measured against the real tree and an empty fixture; the guard was falsified by making resolve_root ignore a named root family-wide, which it caught by name; mutation: 2 declared mutants, both KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py
> **Created:** 2026-08-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio-authoring-session; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`docgen.py references` and `docgen.py surface` shipped with a `--root` that resolved the TARGET path correctly and then called their renderer with no argument, defaulting the content to the real installed skill tree. Every conformance test passed: the flag existed, bound dest `root`, defaulted to `.`, and was accepted before and after the verb. `test_cli_grammar.py` checks a --root's GRAMMAR exhaustively and its EFFECT not at all. The defect survived a green 6348-test suite and was found by the first test that ran the command against a fixture root and looked at what came out.

## Steps to Reproduce

Point any --root-taking verb at a temporary tree containing one file the real tree does not have. Run the command. If the output describes the real tree rather than the fixture, the flag is decorative. As shipped, docgen references --root TMP wrote TMP's file with the real tree's 56 references.

## Proposed Fix

A conformance test per --root-taking verb: run it against a fixture root holding a distinguishable artefact, and assert the output mentions the fixture and not the real tree. Grammar conformance already sweeps every parser in the family, so the enumeration to hang it on exists; what is missing is any assertion that the value is READ.

## Acceptance Criteria

- [x] **AC1** Given a `--root` pointed at an empty fixture, when a proven-discriminating verb runs from inside this repository, then its answer names nothing from this repository - the flag is READ, not merely parsed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k no_verb_answers_about_the_real_tree
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given the same verbs pointed at the REAL tree, when they run, then each names a real artefact - so a clean AC1 means the flag was obeyed, not that the verb prints nothing either way.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k every_listed_verb_can_actually_fail
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given the inventory of swept verbs, when it is compared against the verbs the sweep can invoke, then it is a strict subset of them - so the coverage gap cannot be closed by pasting the rest in, which would read as complete and assert less.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py -k inventory_is_a_measured_subset
  - **Verified:** yes (2026-08-14)

## Impact

A decorative --root is worse than a missing one. It runs, exits 0, and reports about somewhere else - so a fixture-based test of any downstream behaviour silently measures the developer's own tree, and a run from a worktree acts on the wrong checkout. The family has 71 scripts and this was found in two of them by accident.

## Resolution

All 128 `--root`-taking verbs the sweep can invoke without extra required arguments were run twice - against the real tree and against an empty fixture - and their outputs compared. **23 of the 128 answer differently. The other 105 print nothing that names a tree at all**, so no fixture sweep can speak for them, and the shipped inventory says so rather than counting them as covered. A guard reporting "128 verbs checked" when only 23 could ever fail is the vacuous-verifier shape this repository keeps paying for.

Two of the 23 are excluded on purpose: `repo_map build` and `project_upgrade` WRITE, so the control half would modify the tree it is measuring.

The guard was then falsified before being trusted: making `resolve_root` ignore a named root - one line, family-wide - is caught, naming the offending verb and calling the flag decorative. And the control half is itself pinned, so an entry that quietly stops discriminating fails rather than passing forever.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in lib/sdlc_md.py `resolve_root`, ignore a named root so every --root in the family is decorative | Given a `--root` pointed at an empty fixture, when a proven-discriminating verb runs from inside this repository, then its answer names nothing from this repository - the flag is READ, not merely parsed. |
| AC2 | in tests/test_cli_grammar.py, replace `_REAL_TREE_MARKER` with a pattern that never matches | Given the same verbs pointed at the REAL tree, when they run, then each names a real artefact - so a clean AC1 means the flag was obeyed, not that the verb prints nothing either way. |
| AC3 | in tests/test_cli_grammar.py, widen `ROOT_EFFECT_VERBS` to every invocable --root verb, so 105 rows that cannot fail read as coverage | Given the inventory of swept verbs, when it is read, then it is the MEASURED discriminating set rather than every verb the sweep can invoke, so the guard never claims coverage it does not have. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-08 | sdlc-studio-authoring-session | Filed |
