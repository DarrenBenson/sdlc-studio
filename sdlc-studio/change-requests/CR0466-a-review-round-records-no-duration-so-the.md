# CR-0466: A review round records no duration, so the overhead ratio can only ever be a lower bound

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

US0523 reports delivery time against overhead time, and review rounds are recorded without any duration. The ratio therefore excludes the single largest overhead component of the last two sprints. An unmeasured component reads as unmeasured rather than zero, which is correct, but the headline number is a lower bound and should say so until reviews are timed.

## Impact

US0523 reports delivery time against overhead time, and review rounds are recorded without any duration. The ratio therefore excludes the single largest overhead component of the last two sprints. An unmeasured component reads as unmeasured rather than zero, which is correct, but the headline number is a lower bound and should say so until reviews are timed.

## Acceptance Criteria

- [ ] The behaviour in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Raised |
