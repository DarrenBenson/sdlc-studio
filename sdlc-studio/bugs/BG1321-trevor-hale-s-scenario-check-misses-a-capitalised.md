# BG1321: Trevor Hale's Scenario check misses a capitalised offer and a negation outside its word list, so changelog.d/US1147.md claims more than the AC7 test holds

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_persona_coherence.py, changelog.d/US1147.md
> **Evidence:** BG1318-verdict-r1 (RUN-01M7061X), findings 1 and 3
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:32:16Z

## Summary

From BG1318's QA review (qa-seat-BG1318-r1, non-blocking findings 1 and 3, 2026-11-09; both present before BG1318). (1) The outside check at tools/tests/`test_persona_coherence.py`:988 is case-sensitive, so a Scenario reading 'Sync to an enterprise tracker is offered.' passes, and changelog.d/US1147.md:15-17 says any offer is caught. (3) NEGATION (:212) is still a word list, so 'used to decline', 'seldom declines' and 'Nobody declines' pass. The verdict carries a scratch-tried fix for each.

## Steps to Reproduce

1. In a scratch copy, append 'Sync to an enterprise tracker is offered.' to Trevor Hale's Scenario and run the AC7 test: it passes.
2. Replace 'declines' with 'seldom declines' in the declining sentence and run it again: it passes.

## Proposed Fix

Match the wants case-insensitively in the outside check, and require the declining verb to stand with no qualifier rather than listing negations; reword the US1147 fragment to the claim the test then holds. Pin both with the verdict's mutants.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From BG1318's QA review (qa-seat-BG1318-r1, non-blocking findings 1 and 3, 2026-11-09; both present before BG1318).
- [ ] **AC2** The proposed fix lands, pinned by a test: Match the wants case-insensitively in the outside check, and require the declining verb to stand with no qualifier rather than listing negations; reword the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
