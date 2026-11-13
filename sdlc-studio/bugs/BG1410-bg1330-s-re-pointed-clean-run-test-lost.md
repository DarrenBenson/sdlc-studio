# BG1410: BG1330's re-pointed clean-run test lost its known-issues assertion, unpriced_units' filter is untested, and lane land with no run open names lane return's --tokens flag

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_unpriced_units_pin.py, changelog.d/BG1410.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review land, BG1330
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:56Z

## Summary

The only assertion on the page's empty known-issues sentence was dropped. `unpriced_units`' `in_plan`/measured filter is untested.

## Steps to Reproduce

Delete the sentence.

## Proposed Fix

Restore the assertion and word the lane land message.

## Acceptance Criteria

- [ ] **AC1** Given a clean run, when the page prints, then the empty known-issues sentence is asserted. Fails on: the sentence removed with the suite green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_unpriced_units_pin.py::UnpricedUnitsPinTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
