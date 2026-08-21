# US0683: The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each

> **Status:** Draft
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a close over a batch, when the report is rendered, then it names which units the test-plan gate APPLIED to and which it EXEMPTED, with the band that decided each - an exemption nobody can see is one nobody can challenge
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::PlanGateReportTests::test_the_close_names_applied_and_exempted_units_with_their_bands
- [ ] **AC2** Given a batch where every unit was exempted, when the report is rendered, then it says so explicitly rather than rendering an empty section - an empty list and a batch nobody scoped must not read the same, which is the blindness-first rule the impediments row already draws
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::PlanGateReportTests::test_a_wholly_exempt_batch_says_so_rather_than_rendering_empty

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
