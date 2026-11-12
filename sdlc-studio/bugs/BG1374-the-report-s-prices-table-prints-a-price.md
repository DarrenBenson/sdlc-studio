# BG1374: The report's Prices table prints a price source URL bare in the Markdown twin, so a filed report fails markdownlint MD034 and its close paperwork cannot be committed

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, changelog.d/BG1374.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:24:26Z

## Summary

US1000 added a Prices table to the sprint report whose Source cell carries the price table's source, which for the shipped prices is a URL ('`https://platform.claude.com/docs/en/about-claude/pricing` (Model pricing table, read 2026-11-06)'). The Markdown twin prints it bare, so RPT0029 fails markdownlint MD034 (no-bare-urls) at lines 161 and 162, the pre-commit markdown lane refuses the close paperwork, and the run had to be reopened. The HTML page is unaffected. Evidence: RUN-01M77177 close, 2026-11-12: RPT0029 lines 161-162; the close-paperwork commit refused by the markdown lane.

## Steps to Reproduce

Close a run whose Dollar cost row priced a model from templates/model-prices.json, then run markdownlint over the filed sdlc-studio/reports/RPTxxxx-*.md: MD034 at each Prices row.

## Proposed Fix

Render a source that is a URL as a Markdown autolink (<https://...>) in the Markdown twin's Source cell, leaving the HTML page and any non-URL source as they are, and pin it.

## Acceptance Criteria

- [ ] **AC1** Given a report whose price table source is a URL, when the close files it, then the Markdown twin's Source cell carries the URL as an autolink and the filed page passes markdownlint MD034, while a non-URL source and the HTML page render as before. Fails on: a bare URL in the Markdown Source cell.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_url_source_is_an_autolink_in_the_markdown_twin

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
