# BG1324: No test replays a page filed before the Copilot billing basis existed, a mixed run's page drops the 'plan bills by request' reason, and US1145's lane-return test copies the call instead of running it

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** US1145-verdict-r1 (RUN-01M7061X), findings 1, 2 and 4
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T18:08:40Z

## Summary

From US1145's QA review (qa-seat-US1145-r1, non-blocking, 2026-11-09). (1) A v6.3.0 sprint page with premium requests, filed before `pricing.copilot_billing` existed, re-derives correctly today, but a mutant at `sprint_report.py`:3867 that breaks that replay survives the suite (LC-017). (2) In a mixed run (a priced orchestrator with Copilot lanes) `_usd_reach` (`sprint_report.py`:3785) leaves out the 'plan bills by request' reason, so the page does not say why the Copilot share is priced by request. (3) The lane-return test copies the call it exercises rather than running `sprint lane return`; run through the shipped verb, the reason is right.

## Steps to Reproduce

1. Apply the `sprint_report.py`:3867 mutant from US1145-verdict-r1 and run the suite: it passes.
2. Render a page for a run with a priced orchestrator and Copilot lanes under request billing: the request-billing reason is absent.

## Proposed Fix

Add a replay test of a pre-basis page that the :3867 mutant fails; carry the billing reason through `_usd_reach` for a mixed run; run the lane-return case through the `sprint lane return` entry point.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1145's QA review (qa-seat-US1145-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a replay test of a pre-basis page that the :3867 mutant fails; carry the billing reason through `_usd_reach` for a mixed run; run the lane-return case...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
