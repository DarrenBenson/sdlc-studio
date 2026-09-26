# BG0776: sprint sign --principal - seals the run with an empty principal

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py, changelog.d/BG0776.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:11:16Z

## Summary

sprint.py sign refuses an empty --principal, but the guard strips the raw string before sprint's id normaliser reads '-' as empty, so '--principal -' passes the guard and seals the run under an empty principal. An alias such as 'Sam (qa-seat)' is also not matched to recorded reviewer qa-seat. Pre-existing (identical at base); found by US0919's round-2 QA review.

## Steps to Reproduce

1. In a closed run fixture, python3 sprint.py sign --report RPT0001 --principal -. 2. It exits 0 and the run is sealed; the signature names no principal.

## Proposed Fix

Normalise the principal before the empty check, and refuse a value that normalises to empty; pin it with a test.

## Acceptance Criteria

- [ ] **AC1** Given a closed run, when `sprint.py sign --report <id> --principal` is given a value that normalises to empty (`-`, `  `, `_`), then it exits non-zero naming the principal, and the run is not sealed and no signature is written. Fails on: checking the raw string for emptiness before the id normaliser runs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py::SignPrincipalTests::test_a_principal_that_normalises_to_empty_is_refused
  - **Verified:** yes (2026-09-26)
- [ ] **AC2** Given the same run, when `sign` is given a real principal (`Darren Benson`), then it seals as before and the signature names that principal. Fails on: a guard that refuses every principal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sign_principal.py::SignPrincipalTests::test_a_real_principal_still_seals
  - **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-26 | sdlc | Groomed for v6.0.0-rc.1 (operator ruling: fixed before the rc tag) |
