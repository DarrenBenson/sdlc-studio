# EP0238: The appetite measures working time, and says what it excluded

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0551
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0551. Delivers the work CR0551 requested.

## Story Breakdown

- [ ] [US0778: The appetite reports WORKING time, derived from the evidence the run itself leaves](../stories/US0778-the-appetite-reports-working-time-derived-from-the.md)
- [ ] [US0779: An idle interval is excluded and the exclusion is NAMED rather than silent](../stories/US0779-an-idle-interval-is-excluded-and-the-exclusion.md)
- [ ] [US0780: Both figures are reported, working and calendar, so neither can stand in for the other](../stories/US0780-both-figures-are-reported-working-and-calendar-so.md)
- [ ] [US0781: An interval that cannot be classified counts as SPENT - an unmeasurable gap is not a free one](../stories/US0781-an-interval-that-cannot-be-classified-counts-as.md)
- [ ] [US0782: `retro accuracy` and the Metrics line report the working figure with the calendar beside it](../stories/US0782-retro-accuracy-and-the-metrics-line-report-the.md)
- [ ] [US0783: A run whose WORKING time exceeds the ceiling still trips the breaker, shown against a fixture](../stories/US0783-a-run-whose-working-time-exceeds-the-ceiling.md)

## Acceptance Criteria (Epic Level)

- [ ] The appetite reports working time rather than calendar age, derived from evidence the run itself leaves - commit timestamps, recorded gate runs, suite verdicts, transition stamps - rather than from `now - started_at`
- [ ] A run spanning an idle interval reports that interval as IDLE and excludes it, and the report names how much was excluded so the exclusion is visible rather than silent
- [ ] Both figures are reported, working and calendar, because a run that has been open for four days is a fact worth surfacing even when its working time is small
- [ ] An interval that cannot be classified counts as SPENT, not idle - an unmeasurable gap must not become a free one
- [ ] `retro.py accuracy` and the retro's Metrics line report the working figure with the calendar figure beside it, so the two can never again be read as the same number
- [ ] A run whose working time genuinely exceeds the ceiling still trips the breaker, demonstrated by execution against a fixture with no idle intervals

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
