# CR-0551: The appetite ceiling measures WALL-CLOCK since the run opened, so a run left open overnight reports spend it never incurred

> **Status:** In Progress
> **Decomposed-into:** EP0238
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/loop_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Date:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`loop_guard.elapsed_minutes` returns wall-clock minutes since `started_at`, and the appetite breaker compares that against `capacity.minutes`. Nothing subtracts the time in which no work happened. A run opened on Wednesday morning and closed on Friday morning reports every minute of both intervening nights as spent.

RUN-01M0CT8P reported 2,839 minutes against a 960-minute ceiling - a 3x overrun - and reported SPENT six times in a row without stopping anything. Its actual working time was a fraction of that: the run spanned two nights during which no process ran at all. The number is not wrong for what it measures, but what it measures is the run's CALENDAR AGE, and it is being read, in the retro and by the operator, as the run's COST.

The two readings diverge without limit. A run that is genuinely expensive and a run that is merely old are indistinguishable, and the cheap fix - raise the ceiling - makes the instrument useless in the other direction, because a ceiling set to accommodate calendar drift can never fire on real overspend.

This matters more now than it did, because the ceiling has begun to be ignored. It fired six times on one run and stopped nothing, which is exactly how a gate becomes noise - the failure mode AGENTS.md names as this repository's actual one.

## Impact

Every project using the skill. The appetite is one of the few instruments that bounds a run rather than judging an artefact, and it is currently unusable for the decision it exists to inform: whether to stop.

The token side of the same question is already measured properly - `run_state.session_tokens` sums real usage records and explicitly excludes cache reads because they re-bill the same context. Elapsed time has no equivalent and falls back to subtraction of two timestamps.

What breaks if this is done carelessly: an activity-derived figure that reads zero for a run legitimately waiting on something external, and a breaker that then never fires at all. The fix must distinguish IDLE from BLOCKED, and an unmeasurable interval must fail towards reporting rather than towards silence.

## Acceptance Criteria

- [ ] The appetite reports working time rather than calendar age, derived from evidence the run itself leaves - commit timestamps, recorded gate runs, suite verdicts, transition stamps - rather than from `now - started_at`
- [ ] A run spanning an idle interval reports that interval as IDLE and excludes it, and the report names how much was excluded so the exclusion is visible rather than silent
- [ ] Both figures are reported, working and calendar, because a run that has been open for four days is a fact worth surfacing even when its working time is small
- [ ] An interval that cannot be classified counts as SPENT, not idle - an unmeasurable gap must not become a free one
- [ ] `retro.py accuracy` and the retro's Metrics line report the working figure with the calendar figure beside it, so the two can never again be read as the same number
- [ ] A run whose working time genuinely exceeds the ceiling still trips the breaker, demonstrated by execution against a fixture with no idle intervals

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Raised |
