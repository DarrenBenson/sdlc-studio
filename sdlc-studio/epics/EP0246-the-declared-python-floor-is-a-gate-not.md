# EP0246: The declared Python floor is a gate, not a sentence in six documents

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0561
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0561. Delivers the work CR0561 requested.

## Story Breakdown

- [ ] [US0811: A tracked script using syntax newer than the declared floor is REFUSED, with its file and line named](../stories/US0811-a-tracked-script-using-syntax-newer-than-the.md)
- [ ] [US0812: The floor lane is silent when every script parses, so it is not a check that always fires](../stories/US0812-the-floor-lane-is-silent-when-every-script.md)
- [ ] [US0813: sprint_report.py is repaired, so the lane's first run over the real tree has something to find](../stories/US0813-sprint-report-py-is-repaired-so-the-lane.md)
- [ ] [US0814: The floor lane is bound into the pre-commit gate, so it runs in the command people actually run](../stories/US0814-the-floor-lane-is-bound-into-the-pre.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a tracked script using syntax newer than the declared floor, when the gate runs, then it is REFUSED and the file and line are named - the floor is stated in six shipped places and this is what makes any of them true
- [ ] Given every tracked script parses at the floor, when the lane runs, then it is silent - the paired control, so a lane that always fires does not get switched off
- [ ] Given `sprint_report.py` as it stands at HEAD, when the lane first runs, then it FAILS on it - a floor guard whose first execution over the real tree finds nothing has not been shown to look

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
