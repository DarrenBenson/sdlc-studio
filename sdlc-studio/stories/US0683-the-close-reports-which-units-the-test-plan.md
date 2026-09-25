# US0683: The close REPORTS which units the test-plan gate applied to and which it exempted, with the band that decided each

> **Status:** Superseded
> **Closes with:** US0911 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Delivers:** CR0555
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0218
> **Blocked by:** D0150 and CR0555. A pre-code goal review REJECTED this batch three times. The third rejection was decisive: the measurement justifying the design was taken against a throwaway script rather than the weighted pipeline `route.estimate` actually runs, and three literal readings of the criterion through the real pipeline land at 81 to 97 per cent `light` - the mirror image of the defect, in the more dangerous direction. D0150 then ruled out the class entirely: no author-declared field may gate review depth, and `Points` is author-declared. CR0555 replaces the approach - the expensive half of the gate MOVES to the terminal transition where a diff exists, rather than being banded on a signal that must be read before one does. Do not build this batch; it is kept for its review record, which cost three rounds to produce. Disposition: the close report - still wanted, re-target at CR0555's shape.
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
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: checked for supersession and kept open - the band half is gone under D0150, but recording the gate's decision at transition, reading that record at the close and naming UNRECORDED units are not carried by US0690. |
| 2026-09-21 | audit ruling | RUN-01M306PY sweep: re-parented from EP0217 to CR0555's EP0218, which the audit found already carries this work as its AC4/AC6. It stays Blocked and wanted - only its parent changes, because CR0550 is retracted and EP0217 had to derive Done so CR0547 and CR0548 could close. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0911 ships - planning: SUPERSEDED - report of test-plan gate application: gate deleted in batch 2; superseded only once US0911 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Superseded under D0264: its closing story US0911 is Done (BG0772) |
