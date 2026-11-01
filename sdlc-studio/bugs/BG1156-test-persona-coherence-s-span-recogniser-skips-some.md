# BG1156: test_persona_coherence's span recogniser skips some `script.py verb` shapes, and its mixed-unit probe cannot tell first-listed Primary from first-path owner

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_persona_coherence.py, changelog.d/US1081.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1081 full-tier APPROVE by qa-seat-US1081-r1 (brief 56745dcdbded).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T05:12:11Z

## Summary

qa-seat-US1081-r1's full-tier APPROVE of US1081 (2026-11-01) found two low gaps in the tests US1081 added. (1) `SCRIPT_VERB` (tools/tests/`test_persona_coherence.py`:265) matches only a span starting with the script name or a `python3` prefix, so `python .../sprint.py sigh`, `sprint.py --root . sigh` and `uv run sprint.py sigh` are never checked against the script's `--help`. Two such spans added to Maya's card survived. The docstring at :362 and changelog.d/US1081.md:72 say every `script.py verb` span is checked. (2) AC3's mint cross-check (:415) builds the mixed probe's Affects in index order, so 'first-listed Primary' and 'owner of the first Affects path' always agree, and a mutant routing by the first path's owner survives CardsStateTheRunTests. `test_artifact.py`:2529 still kills that mutant across the suite.

## Steps to Reproduce

1. Add a span `sprint.py --root . sigh` to Maya's card in a throwaway worktree; run `test_persona_coherence.py`: green.
2. Make artifact.py's mixed-unit branch return the first path's owner; run CardsStateTheRunTests: green.

## Proposed Fix

Widen `SCRIPT_VERB` to read the script and the verb after any interpreter, path or option (or narrow the two prose claims to the shapes it reads). Build the AC3 probe with the paths in reverse index order.

## Acceptance Criteria

- [ ] **AC1** A `script.py verb` span written after an interpreter, a path or an option is checked against the script's --help, so a misspelt verb in that shape fails the test.
  - **Verify:** pytest tools/tests/test_persona_coherence.py
- [ ] **AC2** AC3's mint cross-check fails on a mutant that routes a mixed unit by its first Affects path's owner.
  - **Verify:** pytest tools/tests/test_persona_coherence.py

## Impact

Two test-claim sentences claim more than the tests check, and one cross-check relies on another module to catch a routing regression.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
