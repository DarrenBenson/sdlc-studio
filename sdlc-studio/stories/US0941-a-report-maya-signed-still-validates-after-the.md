# US0941: A report Maya signed still validates after the tree moves on

> **Status:** Done
> **Findings-filed-to:** CR0592
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py, changelog.d/US0941.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_findings_window.py
> **Epic:** EP0265
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer who seals each sprint with one signature
**I want** `sprint_report.py check` to judge a signed report on what the run did, not on how the backlog, the lesson store or the decisions log moved afterwards
**So that** the signature stays a record I can point to next week, rather than a page that reads INVALID within a day (RPT0006, RPT0007 and RPT0008 do at 013a46d0)

## Acceptance Criteria

- **AC1:** Given a signed fixture report, when a lesson class gains a hit and a new class is added to the store after the sign, then `sprint_report.py check --report` exits 0. Fails on: HEAD's `_lifecycle_edits`, which compares every figure outside the digest, including the `lessons` and `lane_yield` sections `SECTIONS_OUTSIDE_THE_DIGEST` excludes, and reports each move as a hand edit (RPT0008 at HEAD: `json lessons.lesson_hits_total[1]: filed 9, the run record gives 21`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_moved_lesson_store_does_not_invalidate
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a signed fixture report, when a finding the run raised is closed and a batch unit's Points line is edited after the sign, then `check` exits 0. Fails on: re-deriving the open-finding rows and unit points from today's statuses instead of the page's own window (RPT0006-RPT0008 at HEAD: `issue_priority`, `issue_detail` and `unit_points` moved)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_closed_finding_and_edited_points_do_not_invalidate
  - **Verified:** yes (2026-09-25)
- **AC3:** Given a signed fixture report whose window holds an accepted waiver, when that decision's Rationale cell is amended in place, then `check` exits 0. Fails on: freezing findings and lessons while the waiver's rationale prose is still digested (BG0743)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_an_amended_waiver_rationale_does_not_invalidate
  - **Verified:** yes (2026-09-25)
- **AC4:** Given a signed fixture report, when the delivered count in its filed JSON is edited by hand, then `check` exits 1 and names that figure. Fails on: passing AC1-AC3 by taking every figure out of the digest, which leaves a hand-edited page VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_hand_edited_figure_is_still_invalid
  - **Verified:** yes (2026-09-25)
- **AC5:** Given this repository after the change, then `sprint_report.py check --report` exits 0 for each of RPT0006, RPT0007, RPT0008 and RPT0009. Fails on: a fix that only reports signed after it lands benefit from
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/sprint_report.py check --report RPT0006 && python3 .claude/skills/sdlc-studio/scripts/sprint_report.py check --report RPT0007 && python3 .claude/skills/sdlc-studio/scripts/sprint_report.py check --report RPT0008 && python3 .claude/skills/sdlc-studio/scripts/sprint_report.py check --report RPT0009
  - **Verified:** yes (2026-09-25)

## Notes

QA proposes High: `sprint sign` is v6's one signature. Engineering call on mechanism: either replay findings and points as of the page's `generated_at` (statuses read from git at the window end), or move those figures outside the digest and check them as the lifecycle figures are; either way `_lifecycle_edits` must skip SECTIONS_OUTSIDE_THE_DIGEST. The memory note 'a signed page cannot digest a moving source' is the prior art. Closes BG0743 (transition it Fixed with AC3's selector as its Verify). Ratchet (LC-008): no new check; it narrows an existing one to what the signature covers. RPT0009 is VALID today, so AC5 is a regression guard for it and the fix for the other three.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N1) |
