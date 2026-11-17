# EP0339: A head of engineering reads change failure rate per release beside escapes per 100 points

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0695. Delivers the work CR0695 requested.

## Story Breakdown

- [ ] [US1233: The release cut writes a committed record of each release, with its date and the reports it shipped](../stories/US1233-the-release-cut-writes-a-committed-record-of.md)
- [ ] [US1234: A command derives change failure rate from release records and linked incidents, never reading 0% unmeasured](../stories/US1234-a-command-derives-change-failure-rate-from-release.md)
- [ ] [US1235: The sprint report and the seat scorecard show the release change failure rate, naming its source records](../stories/US1235-the-sprint-report-and-the-seat-scorecard-show.md)

## Acceptance Criteria (Epic Level)

- [ ] A command derives change failure rate from the committed release records and the incident issues linked to them, naming the releases counted and the window
- [ ] The sprint report and the scorecard show change failure rate beside escapes per 100 points, each naming its source records
- [ ] A release younger than a stated settling period is shown as pending, not counted as a success
- [ ] With no incident record or no release in the window, the row reads 'not measured: <reason>', never 0%

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
