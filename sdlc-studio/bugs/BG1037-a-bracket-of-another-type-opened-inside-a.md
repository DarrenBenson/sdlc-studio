# BG1037: A bracket of another type opened inside a pair is not literal, so a ';' the pair encloses is still split, and BG1032's note over-claims inside code spans

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_bracket_types.py, changelog.d/BG1032.md, changelog.d/BG1037.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T11:33:40Z

## Summary

From BG1032's round-2 QA review on 2026-10-13 (APPROVE, nothing blocking). (1) `_split_within_finding` matches a closer only against the top of its stack, so in `[new] the gate skips (see a.py:1 [draft; also c.py:2) badly` the stray `[` blocks the `)` from closing its `(`, and the `;` the parentheses enclose is split, refusing `also c.py:2) badly` as unclassified. It fails closed and costs a re-emit (the base ref refused it too), but the contract and the docstring say an unmatched opener is literal. Neither the type matching nor the code-span skip in the bracket pass is pinned. Popping to the nearest opener of the matching type accepts both this shape and `(see a] b.py:1; also c.py:2)`. (2) changelog.d/BG1032.md says a reviewer's own backslash is kept; that holds only outside code spans, because the history reader undoes the ledger's escapes inside spans too (the trade-off accepted for legacy rows).

## Steps to Reproduce

Record `VERDICT: REJECT / ISSUES: [new] the gate skips (see a.py:1 [draft; also c.py:2) badly / BLOCKING: none` with `critic.py record --from-verdict`: refused naming `also c.py:2) badly`.

## Proposed Fix

Pop to the nearest opener of the matching type, treating any opener above it as literal; pin both shapes and the code-span skip; say 'outside code spans' in the BG1032 note.

## Acceptance Criteria

- [ ] **AC1** Given a finding whose parentheses enclose a ';' and also a stray opener of another type, when it is recorded, then it is one finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_bracket_types.py::BracketTypeTests::test_a_stray_opener_of_another_type_is_literal
- [ ] **AC2** Given brackets inside a code span within a finding, when the finding is split, then they neither open nor close a pair
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_bracket_types.py::BracketTypeTests::test_brackets_inside_a_code_span_are_not_counted

## Impact

A reviewer's well-formed evidence with a stray bracket is refused and has to be re-emitted; a release note says slightly more than the code does.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
