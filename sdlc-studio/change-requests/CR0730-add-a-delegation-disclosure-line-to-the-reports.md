# CR-0730: Add a delegation disclosure line to the reports already signed under a per-trip authorisation

> **Status:** Complete
> **Decomposed-into:** EP0367
> **Parent:** RFC0065
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/reports, docs/evidence.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RFC0065 decision of 2026-11-17, operator ruling D0504
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T17:15:20Z

## Summary

Reports RPT0030 to RPT0034 were signed by the orchestrator in the operator's name under decisions D0467, D0472, D0475, D0479 and D0493, and none of them says so. The 6.4.0 evidence pack is built from those reports. The operator ruled that the signatures stand and that each report, and the evidence pack, gains a line naming the decision that authorised the delegated signature.

## Impact

A reader of the 6.4.0 evidence pack takes five delegated signatures for signatures the operator entered. The decisions log holds the truth, but the records a change board reads do not.

## Acceptance Criteria

- [ ] Every report signed under a delegation decision carries a disclosure line naming that decision, and the report check still reads each one VALID
- [ ] The 6.4.0 evidence pack and docs/evidence.md state which signatures were delegated and under which decision
- [ ] The amendment is made through a shipped command, not by hand-editing a sealed page

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
