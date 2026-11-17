# CR-0729: A run closed while the operator is away waits for signature, and a delegated signature is disclosed

> **Status:** In Progress
> **Decomposed-into:** EP0366
> **Parent:** RFC0065
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RFC0065 decision of 2026-11-17, operator ruling D0503
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T17:15:15Z

## Summary

RFC0065 is decided: the deferred signature is the default, and delegation is allowed only with disclosure. Today a closed run that is not signed blocks the next, which is the pressure that produced a per-trip authorisation for the orchestrator to type the operator's name into sprint sign. The sign check compares the typed principal string only, and the report carries a bare signature row. This request makes a run awaiting signature a normal state the next run can open on top of, and makes a delegated signature carry the decision that authorised it, in the signature block, the report and the evidence pack.

## Impact

A change board reading a signed report or the evidence pack cannot tell a signature the operator entered from one the authoring session entered under delegation. The operator, away for days, must either authorise that or stop delivery.

## Acceptance Criteria

- [ ] A new run can be planned and opened while an earlier closed run awaits signature, and status names every run awaiting signature
- [ ] sprint sign entered under delegation requires the id of an accepted decision that authorises the span, and refuses a delegated signature without one
- [ ] The signature block, the report page and the evidence pack each state that a delegated signature was delegated and name the authorising decision
- [ ] The TRD records the ruling as an ADR and RFC0060's open decision D6 is closed with a pointer to RFC0065

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
