# BG0910: The close pre-flight's live checklist read is unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_preflight_live_gate.py
> **Evidence:** BG0895 discharge review (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T14:54:38Z

## Summary

BG0895 passes `live_gate`=True to the close pre-flight's checklist read (sprint.py:7144, `_checklist_blockers)` so a re-close's dry run names the same unruled findings as the page; dropping it survives every test and makes a red-then-green re-close's pre-flight and close --dry-run print a stale '2 unruled'.

## Steps to Reproduce

1. Drop `live_gate`=True at sprint.py:7144. 2. The suite stays green.

## Proposed Fix

Pin it: on a red-then-green re-close, close --dry-run names only the finding the page will list.

## Acceptance Criteria

- [ ] **AC1** Given a run closed once with BG0101 carried, then BG0101 verified and approved, when sprint close --dry-run runs, then its known-issues line reads 1 unruled naming only BG0102. Fails on: a pre-flight that reads the previous attempt's frozen gate, which prints 2 unruled
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_preflight_live_gate.py::PreflightLiveGateTests::test_a_re_close_dry_run_names_only_the_page_s_findings

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
