# BG0750: A same-day waiver flips a filed sprint report INVALID

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** US0885 review, probe s2/rv885_probe3.py, RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_waivers_in_force` compares waiver dates to the report window by date only (`[:10]`, `when > hi`), and the count feeds the fingerprint. A waiver recorded later on the report's generation day enters the re-derivation but not the page, so `check` reads INVALID.

## Steps to Reproduce

1. File a report. 2. Later the same day, `decisions.py waive --subject rule:engagement-floor`. 3. `sprint_report.py check` reads INVALID (`waivers_count`: signed 0, now 1).

## Proposed Fix

Compare waiver moments below the page's generation instant with the same half-open bound the DORA window uses, or stamp waivers to the second.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_waivers_in_force` compares waiver dates to the report window by date only (`[:10]`, `when > hi`), and the count feeds the fingerprint.
- [ ] **AC2** The proposed fix lands, pinned by a test: Compare waiver moments below the page's generation instant with the same half-open bound the DORA window uses, or stamp waivers to the second.

## Impact

`_waivers_in_force` compares waiver dates to the report window by date only (`[:10]`, `when > hi`), and the count feeds the fingerprint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
