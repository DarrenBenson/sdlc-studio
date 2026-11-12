# BG1379: The report's Markdown twin still prints a `www.` or upper-case-scheme price source bare

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, changelog.d/BG1379.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-BG1374-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:50:06Z

## Summary

BG1374 links only lower-case http(s) addresses, so a source written `www.example.com` or `HTTPS://`... still trips MD034, and BG1374's changelog says every web address is linked. Reported non-blocking at review.

## Steps to Reproduce

Render the case the review names into the Markdown twin.

## Proposed Fix

Handle and pin the case.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the twin renders it as documented. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_www_and_upper_case_sources_are_linked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
