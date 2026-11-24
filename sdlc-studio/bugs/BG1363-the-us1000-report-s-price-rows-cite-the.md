# BG1363: The US1000 report's price rows cite the config while their values come from the page's own price table

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, changelog.d/BG1363.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1000-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:21:13Z

## Summary

Rows cite `PRICES_SOURCE` (`sprint_report.py`:4560) but read the envelope's `price_table`, so a reader following the source can find a different number; the delegated-reach clause also over-counts what it priced. Reported non-blocking at review.

## Steps to Reproduce

Read the sentence against the behaviour the review probed.

## Proposed Fix

Reword to what the code does.

## Acceptance Criteria

- [ ] **AC1** Given the page or output named, its wording states only what the code does. Fails on: the over-claim the review quoted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A price row cites the config for the page table.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
