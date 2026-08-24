# US0683: The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each

> **Status:** Draft
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit transitioning past the entry gate, when the gate decides, then the band it used and the decision it reached are RECORDED at that moment - a band recomputed at close time is a different number from the one that decided, because `Affects` may have changed since
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_the_gate_records_the_band_it_decided_on
- [ ] **AC2** Given a close over a batch, when the report is rendered, then it names which units the gate APPLIED to and which it EXEMPTED, reading the RECORDED decision rather than re-deriving one - an exemption nobody can see is one nobody can challenge, and a figure that can disagree with the decision it reports is worse than none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::PlanGateReportTests::test_the_report_reads_the_recorded_decision
- [ ] **AC3** Given a batch where every unit was exempted, when the report is rendered, then it says so explicitly rather than rendering an empty section - an empty list and a list nobody built are different facts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::PlanGateReportTests::test_a_wholly_exempt_batch_says_so
- [ ] **AC4** Given a unit whose recorded decision is absent - transitioned before this shipped - when the report is rendered, then it is named as UNRECORDED rather than silently omitted or re-derived
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::PlanGateReportTests::test_a_unit_with_no_recorded_decision_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |

| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
