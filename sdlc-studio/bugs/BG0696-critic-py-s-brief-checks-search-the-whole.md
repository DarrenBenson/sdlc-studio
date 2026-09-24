# BG0696: critic.py's brief checks search the whole brief, so a unit's own text hides a dropped surface, and a REJECT marked as matching no brief can never be retired

> **Status:** Open
> **Closes with:** US0923 closes part (2), brief provenance matching, only. Part (1), missing_practices and missing_claim_surfaces searching the whole brief, has no closing story and stays live, so this bug is not closed when that story ships (D0264, backlog sweep D0265)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0671-delivery-qa.txt (qa seat); verdicts/BG0671-delivery-engineering.txt (engineering seat); verdicts/BG0672-delivery-qa.txt (qa seat); verdicts/BG0672-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

(1) `missing_claim_surfaces` and `missing_practices` search the whole brief, not the block they check (critic.py:3414-3448), so a unit whose own text or quoted prior verdict names a surface word hides a dropped surface: with comments removed from `_CLAIM_INVENTORY_BLOCK`, critic.py brief --unit BG0671 --tier full exits 0 with a fingerprint while BG0677 is refused as it should be. The matching scope dates from 3f73ab64 and no open id covers it. The three-line check block is written twice, in the rejoinder and first-round branches, and restates brief()'s tier test (critic.py:4231-4233 and 4273-4275 against 3635). reference-review.md:452-458 and the fragment say each refusal names only what is missing, but the practices and surface refusals still append the full roll-call (critic.py:3434-3438, 3455-3458). (2) The NOTE record prints on a marked row says 're-brief the seat to clear it', but a marked REJECT is never cleared: `_brief_key` returns an empty key for it (critic.py:751) and `_unanswered_rejects` keeps every row with an empty key (critic.py:727-729), so no later approval retires it. Probed through the CLI: a marked REJECT, then a re-brief and a matched APPROVE, and `verdict_for` still returns the marked REJECT; 3f73ab64 returns the same, so only the wording is new (critic.py:4328-4333). The new tier parameter of `_seats_whose_brief_matches` is reused as the loop variable (critic.py:140 and 172), harmless today because the tier list is built before the loop.

## Steps to Reproduce

1. In a copy, delete the comments entry from `_CLAIM_INVENTORY_BLOCK.` critic.py brief --unit BG0671 --seat engineering --tier full exits 0 and prints a fingerprint; critic.py brief --unit BG0677 --seat engineering --tier full exits 2. 2. In a seat-carded fixture: critic.py record --unit US0101 --verdict REJECT --brief 0123456789ab (the row is marked), then critic.py brief --unit US0101 --seat qa and record an APPROVE with the printed fingerprint; the unit's verdict still reads REJECT.

## Proposed Fix

Search only the rendered block for practices and claim surfaces. Share one helper for the tier check in both branches. Either drop the roll-call or correct the docs. For a marked REJECT, either let a later matched APPROVE by an independent reviewer retire it, or make the NOTE name the route that does clear it. Rename the loop variable.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: (1) `missing_claim_surfaces` and `missing_practices` search the whole brief, not the block they check (critic.py:3414-3448), so a unit whose own text or quoted...
- [ ] **AC2** The proposed fix lands, pinned by a test: Search only the rendered block for practices and claim surfaces.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0923 ships - planning: SUPERSEDED - brief practice checks: brief provenance/practice checks deleted in batch 2; superseded only once US0923 ships (D0264) |
| 2026-09-24 | Claude Opus 5.5 | US0907 round-2 review: US0923 covers part (2) only; part (1), the whole-brief practice and claim-surface search, stays live |
