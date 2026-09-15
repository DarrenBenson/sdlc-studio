# CR-0574: Units abandoned or forced past an unanswered delivery REJECT within a run are not listed at the close

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0627 AC12 only prints a warning when a unit is abandoned (Won't Implement, Superseded, Won't Fix) or forced past a REJECT; US0823 covers stop --force but not transition-level forces. The close report and handoff do not list them, so the escape is invisible afterwards.

## Impact

Reviewers of record reading a close: a REJECT stepped round mid-run reads as a clean close.

## Acceptance Criteria

- [ ] The close report and the handoff list every unit abandoned or forced past an unanswered delivery REJECT within the run's window, with who and when
- [ ] A run with no such unit prints that it has none rather than omitting the section

## Recommendation

List, in the close report and the handoff, every unit in the run's window abandoned or --forced past an unanswered delivery REJECT, with who and when.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
