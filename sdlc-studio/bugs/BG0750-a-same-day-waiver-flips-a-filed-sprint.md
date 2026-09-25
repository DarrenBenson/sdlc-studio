# BG0750: A same-day waiver flips a filed sprint report INVALID

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py
> **Evidence:** US0885 review, probe s2/rv885_probe3.py, RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_waivers_in_force` compares waiver dates to the report window by date only (`[:10]`, `when > hi`), and the count feeds the fingerprint. A waiver recorded later on the report's generation day enters the re-derivation but not the page, so `check` reads INVALID.

A second face of the same defect, found while reproducing (read from the code, not yet executed): `decisions.py waive` writes the LOCAL date, while `window_end[:10]` is the date in whatever offset the window was stored in. Near midnight a waiver can therefore fall a day outside a window it sits inside. The Date cell records no moment, so no date-level rule can be right on the generation day. The fix records the waiver's moment. Legacy date-only rows keep today's rule, so pages already signed re-derive as they did.

## Steps to Reproduce

1. File a report. 2. Later the same day, `decisions.py waive --subject rule:engagement-floor`. 3. `sprint_report.py check` reads INVALID (`waivers_count`: signed 0, now 1).

Re-run at 65cdf1ca on 2026-09-25 in a scratch fixture: `_waivers_in_force(root, window_end=<local now - 10 min>, window_start=<local now - 20 min>)` counted 0. After `decisions.py waive --subject rule:engagement-floor` it counted 1, though the waiver was recorded ten minutes after the window's end.

## Proposed Fix

Have `decisions.py waive` record the waiver's moment, as an ISO timestamp with its offset, and compare it below the page's generation instant with the same half-open bound the DORA window uses.

## Acceptance Criteria

- [ ] **AC1** Given a report generated at instant T, when `decisions.py waive` records a waiver after T on the same day, then `sprint_report.py check` still reads VALID and the page's waiver count is unchanged. Fails on: HEAD's date-only comparison, which counts the later waiver (measured).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py::WaiverWindowTests::test_a_waiver_recorded_after_the_page_leaves_it_valid
- [ ] **AC2** Given a run whose report is generated at T, when `decisions.py waive` records a waiver after the run starts and before T on the generation day, then it is in the page's waivers section. The same holds when the window is stored in UTC and the waiver was recorded after local midnight. Fails on: excluding every waiver dated the generation day, which is the cheap fix to AC1; comparing the local date cell with the UTC window date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py::WaiverWindowTests::test_a_waiver_recorded_before_the_page_on_its_day_is_disclosed

## Impact

`_waivers_in_force` compares waiver dates to the report window by date only (`[:10]`, `when > hi`), and the count feeds the fingerprint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (a waiver recorded 10 minutes after a window's end was counted in it); a UTC-against-local-date variant, found by reading, was added to AC2; criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each naming the wrong fix it fails on; Affects adds decisions.py; 3 points stand |
