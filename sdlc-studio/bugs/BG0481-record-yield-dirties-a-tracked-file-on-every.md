# BG0481: record_yield dirties a tracked file on every commit, and the yield it accumulates is not the real one

> **Status:** Fixed
> **Verification depth:** functional (yield moved to sdlc-studio/.local/, which .gitignore covers; legacy counts carried over; test asserts the new path)
> **Severity:** High
> **Points:** 3
> **Affects:** tools/check_spec_claims.py, .githooks/pre-commit, tools/tests/test_precommit_claim_drift.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** independent-critic (qa seat); human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`record_yield` writes sdlc-studio/retros/evidence/claim-drift-yield.json, which is TRACKED at HEAD and which the hook never stages. So every commit leaves the working tree dirty with a modified tracked file the author did not touch. `git check-ignore` exits 1, confirming it is not ignored.

The repo already carries the precedent this should have followed: `TIMINGS_REL` = "sdlc-studio/.local/gate-timings.json" puts hook-written state under .local/, where it is untracked by design.

Beyond hygiene it undercuts US0585's AC3. The committed value reads runs 6 / findings 1, while a replay shows commit 3c195846 alone would have produced 31. The number a later blocking decision reads is therefore not the accumulated yield of the lane, and the advisory period exists precisely so that number can be trusted.

## Steps to Reproduce

1. Start from a clean tree.
2. Stage any diff and run the shipped pre-commit hook block verbatim.
3. git status -> `M sdlc-studio/retros/evidence/claim-drift-yield.json` (modified, unstaged), unstaged, tracked.
4. git check-ignore sdlc-studio/retros/evidence/claim-drift-yield.json -> exit 1 (not ignored).

## Proposed Fix

Move the accumulator under sdlc-studio/.local/ as gate-timings.json already is, so hook-written state is untracked. Then re-accumulate from a replay over the corpus rather than carrying forward the six runs recorded so far, because the current file understates the yield by roughly an order of magnitude and is the input to the decision on whether the lane may block.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `record_yield` writes sdlc-studio/retros/evidence/claim-drift-yield.json, which is TRACKED at HEAD and which the hook never stages.
- [ ] The proposed fix lands, pinned by a test: Move the accumulator under sdlc-studio/.local/ as gate-timings.json already is, so hook-written state is untracked.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | independent-critic (qa seat) | Filed |
