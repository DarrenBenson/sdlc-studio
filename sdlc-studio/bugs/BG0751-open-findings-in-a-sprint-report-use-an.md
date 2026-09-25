# BG0751: Open findings in a sprint report use an inclusive window end

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_findings_window.py
> **Evidence:** US0885 review finding 4 (read, not executed), RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_open_findings` compares a finding's stamp with `window_end` using `when > hi`, so a finding stamped in the generation second after the page enters only the re-derivation; a finding with only a date-level Created fallback races across the whole day. It feeds the fingerprint through known issues.

Why the proposed fix changed: the bug first proposed excluding date-only stamps on the generation day. That trades the race for an under-count, because a finding filed outside a batch during the run's last day, BEFORE the page was generated, would drop off the page. The filer writes no moment for such a finding (`none open - raised outside a delivery batch`, and `Created` is a date), so no comparison can place it. The fix gives that stamp a moment. Legacy date-only stamps keep today's date-level rule, so pages already signed re-derive as they did; RPT0008's invalidation by BG0762 is recorded, not repaired.

## Steps to Reproduce

1. File a report. 2. In the same second (or the same day, for a Created-only finding) file a bug. 3. `check` can read INVALID.

Re-run at 65cdf1ca on 2026-09-25: `sprint_report.py check --report RPT0008`, run in a scratch copy of the tree, reports `issue_id[12]: signed 'CR0595', now 'BG0762'`, and `findings_scan` reads 15 open findings signed, 16 now. BG0762 was filed after the seal on the seal's day, and entered through the date-level Created fallback.

## Proposed Fix

Compare timestamped stamps with the half-open bound (`when >= hi` excludes). Have `file_finding` write the moment into the outside-a-batch stamp, so every new finding is placed by its moment rather than its day.

## Acceptance Criteria

- [ ] **AC1** Given a report generated at instant T during a run, when a bug is filed whose `Raised-in-batch` stamp carries T's own second, then `sprint_report.py check` still reads VALID, and a bug stamped one second before T is on the page. Fails on: HEAD's inclusive `when > hi`, under which the T-second finding enters only the re-derivation.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_findings_window.py::FindingsWindowTests::test_a_finding_stamped_in_the_generation_second_leaves_the_page_valid
- [ ] **AC2** Given a run whose report is generated at T, when one bug is filed by `file_finding.py file` with no batch open after the run starts and before T, and a second the same way after T on the same day, then the first is in the page's known issues and `check` still reads VALID after the second. Fails on: HEAD's date-level `Created` fallback, which admits the second (measured on RPT0008); excluding every date-only stamp on the generation day, which drops the first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_findings_window.py::FindingsWindowTests::test_a_finding_filed_outside_a_batch_is_placed_by_its_moment_not_its_day

## Impact

`_open_findings` compares a finding's stamp with `window_end` using `when > hi`, so a finding stamped in the generation second after the page enters only the re-derivation; a finding with only a date-level Created fallback races across the whole day.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Recurred after a seal: RPT0008 checked VALID at dcbee3d4, then BG0762, filed the same day after the seal, entered the re-derivation's known issues through the date-level Created fallback, and `check` now reads the signed page INVALID. Nothing about the run changed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (`check --report RPT0008` names BG0762 as a new issue row); proposed fix changed from excluding same-day date-only stamps, which under-counts, to stamping the moment at filing; criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each naming the wrong fix it fails on; Affects adds file_finding.py; 2 points resized to 3 |
