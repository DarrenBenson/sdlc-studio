# BG0585: the derived-only grooming detector is defeated by the AC-number prefix it ships with

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`is_derived_criterion` strips the leading bullet, the checkbox and the `**` emphasis, then matches the remainder against patterns anchored at `^The behaviour described is corrected:` and its four siblings. It does NOT strip the `ACn` number, so a criterion written as `- [ ] **AC1** The behaviour described is corrected: ...` leaves the body `AC1 The behaviour described is corrected: ...` and matches nothing. `conformance.unit_is_ungroomed` therefore reports `(False, '')` - GROOMED - for the numbered form, and `(True, 'derived-only')` for the otherwise identical unnumbered one. The `derived-only` shape is the one conformance.py's own docstring calls 'the shape that reads like content and is not' and the one that 'passed every check in the repo'; it is undetectable in a form the tooling itself produces and that the repo's own backlog carries.

## Steps to Reproduce

Measured 2026-08-16 at 7697ee36 by calling the shipped predicate on two texts differing only in the `**ACn**` prefix. `conformance.unit_is_ungroomed('bug', '## Acceptance Criteria\n\n- [ ] **AC1** The behaviour described is corrected: the thing is fixed.\n- [ ] **AC2** The proposed fix lands, pinned by a test: the fix lands.\n')` returns `(False, '')`. The same text with the AC-number prefixes removed returns `(True, 'derived-only')`. Both forms occur in this repository: the numbered form is what BG0582 itself carried when filed, and `sprint plan`'s own refusal message quotes it verbatim as the scaffold it rejects - `- [ ] **AC1** The behaviour described is corrected: <restates the summary>`.

## Proposed Fix

Strip a leading `ACn` token in `is_derived_criterion` before matching, in the same pass that already strips the bullet, the checkbox and the emphasis - the module's `AC_HEADING_RE` equivalent already knows the shape, so read it from there rather than adding a second spelling. Pin BOTH forms in one test: the existing coverage passes on the unnumbered form alone, which is why this survived. Check the same prefix assumption in the other consumers of `criteria_are_all_derived` before assuming this is the only one.

## Acceptance Criteria

- [ ] **AC1** Given a criterion written as `- [ ] **AC1** The behaviour described is corrected: X`, when `is_derived_criterion` reads it, then it returns True
- [ ] **AC2** Given the same criterion with no `ACn` prefix, when it reads it, then it still returns True - the existing form must not regress
- [ ] **AC3** Given an authored criterion carrying an `ACn` prefix and real content, when it reads it, then it returns False - the positive control, so stripping the number does not make every numbered criterion derived

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
