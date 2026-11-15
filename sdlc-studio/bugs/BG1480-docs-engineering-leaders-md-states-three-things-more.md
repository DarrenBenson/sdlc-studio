# BG1480: docs/engineering-leaders.md states three things more strongly than the code does: pricing, the evidence pack's refusals and author stamping

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** docs/engineering-leaders.md, tools/tests/test_engineering_leaders_page.py, changelog.d/BG1480.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1162/88ce9a77df4e-24bffc8d.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:22:40Z

## Summary

US1162's QA review (verdict 88ce9a77df4e-24bffc8d) approved the page with three wording findings on facts. (1) Lines 136-137 say a run that mixes models is never priced at one model's rate; that holds for the dollar actual, but the report's forecast column is priced at one model's input rate (CR0703). (2) Lines 65-67 link `release_cut.py` for the evidence pack's refusals, which live in `evidence_pack.py.` (3) Lines 84-86 say every review verdict stamps the author beside the reviewer by name and role; the writer only warns on an author with no role, and older ledger rows carry neither. On a page a head of engineering reads to judge the evidence, each overclaim costs the trust the page is built to earn.

## Steps to Reproduce

Read docs/engineering-leaders.md lines 65-67, 84-86 and 136-137 against RPT0032's forecast row, `evidence_pack.py` and reference-scripts-review.md.

## Proposed Fix

Say the dollar actual is priced per model and the forecast at one model's rate until CR0703; link `evidence_pack.py` for the refusals; say a verdict records the author beside the reviewer and the brief asks for both by name and role. Pin each sentence in tools/tests/`test_engineering_leaders_page.py.`

## Acceptance Criteria

- [ ] **AC1** Given docs/engineering-leaders.md, when its pricing sentence is read, then it limits the per-model pricing to the dollar actual and says the forecast is priced at one model's rate. Fails on: a sentence that covers both columns.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given the page, when the evidence pack's refusals are named, then the link points at `evidence_pack.py`, and the author-stamping sentence claims no more than the writer enforces. Fails on: a link to `release_cut.py` for the refusals or 'every verdict stamps'.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py
  - **Verified:** yes (2026-11-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
