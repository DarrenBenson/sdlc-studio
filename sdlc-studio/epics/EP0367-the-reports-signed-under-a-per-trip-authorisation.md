# EP0367: The reports signed under a per-trip authorisation disclose the decision that authorised each signature

> **Status:** In Progress
> **Derived Point Total:** 7
> **Parent:** CR0730
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0730. Delivers the work CR0730 requested.

## Story Breakdown

- [x] [US1294: A shipped command adds a delegation disclosure line to a signed report, and the report check still reads it VALID](../stories/US1294-a-shipped-command-adds-a-delegation-disclosure-line.md)
- [ ] [US1295: RPT0029 to RPT0034 and the 6.4.0 evidence pack name the decision behind each delegated signature](../stories/US1295-rpt0029-to-rpt0034-and-the-6-4-0.md)

## Acceptance Criteria (Epic Level)

- [ ] Every report signed under a delegation decision carries a disclosure line naming that decision, and the report check still reads each one VALID
- [ ] The 6.4.0 evidence pack and docs/evidence.md state which signatures were delegated and under which decision
- [ ] The amendment is made through a shipped command, not by hand-editing a sealed page

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
