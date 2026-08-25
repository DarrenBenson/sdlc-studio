# US0690: The close names which units had the approval demanded at terminal and which the cutoff exempted

> **Status:** Blocked
> **Delivers:** CR0555
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0218
> **Blocked by:** a pre-code goal review, and then by a measurement that invalidated the request's premise. `transition.py:961` gates the two-role delivery review as story-and-Done only, so a bug pays no second review cycle for this batch to merge - and a further dry-run across all 23 open bugs found that NONE owes an independent review at all, because the entry gate never fires for a bug. CR0555 is narrowed to STORIES, where the two-cycle saving is real. These units are kept for their review record: eleven further findings, including that all twenty of their criteria were library tests rather than lane tests (LL0040). Re-groom against the narrowed request before building. Disposition: the close report - survives; must declare the shared-predicate dependency.
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The close names which units had the approval demanded at terminal and which the cutoff exempted
**So that** CR0555 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a close over a batch, when the report is rendered, then it names which units had the approval demanded at terminal and which the cutoff exempted - an exemption nobody can see is one nobody can challenge
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ApprovalMoveReportTests::test_the_report_names_demanded_and_exempted_units
- [ ] **AC2** Given a batch where every unit was exempted by the cutoff, when the report is rendered, then it SAYS so rather than rendering an empty section - an empty list and a list nobody built are different facts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ApprovalMoveReportTests::test_a_wholly_exempt_batch_says_so
- [ ] **AC3** Given more units than the report prints, when it truncates them, then it says how many it dropped - a silent truncation reads as "that was all of them", which this repository has already shipped once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ApprovalMoveReportTests::test_the_report_states_what_it_truncated

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Created via `new` (deterministic) |
