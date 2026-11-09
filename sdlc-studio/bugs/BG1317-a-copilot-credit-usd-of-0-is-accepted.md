# BG1317: A Copilot `credit_usd` of 0 is accepted and prices every Copilot reading at $0, and reference-sprint.md's list of price sources omits the newer ones

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Evidence:** US1144-verdict-r1 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T16:46:47Z

## Summary

From US1144's QA review (qa-seat-US1144-r1, non-blocking, 2026-11-09). (1) lib/prices.py around line 220 accepts a Copilot `credit_usd` of 0 (or a project override setting it so), and every Copilot reading is then priced at $0 rather than refused as unpriced, so a typo reads as a free run. (2) reference-sprint.md:671 lists the price table's sources without the xAI, Cursor and GitHub Copilot pages US1143 and US1144 added.

## Steps to Reproduce

1. Set `credit_usd` to 0 in a scratch project's pricing override and price a Copilot reading: it reads $0.00.
2. Read reference-sprint.md:671: the xAI, Cursor and GitHub Copilot price sources are not named.

## Proposed Fix

Refuse a `credit_usd` that is not greater than 0 at load, naming the key, with a test beside a positive control; name the newer price sources at reference-sprint.md:671 within its line budget.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1144's QA review (qa-seat-US1144-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Refuse a `credit_usd` that is not greater than 0 at load, naming the key, with a test beside a positive control; name the newer price sources at...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
