# BG0556: no guard catches a --root that selects the file written but not the content read

> **Status:** Open
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

- [ ] **AC1** The behaviour described is corrected: `docgen.py references` and `docgen.py surface` shipped with a `--root` that resolved the TARGET path correctly and then called their renderer with no argument...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Point any --root-taking verb at a temporary tree containing one file the real tree does not have.
- [ ] **AC3** The proposed fix lands, pinned by a test: A conformance test per --root-taking verb: run it against a fixture root holding a distinguishable artefact, and assert the output mentions the fixture and not...

## Impact

A decorative --root is worse than a missing one. It runs, exits 0, and reports about somewhere else - so a fixture-based test of any downstream behaviour silently measures the developer's own tree, and a run from a worktree acts on the wrong checkout. The family has 71 scripts and this was found in two of them by accident.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-08 | sdlc-studio-authoring-session | Filed |
