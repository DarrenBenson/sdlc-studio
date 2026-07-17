# CR-0314: Forecast in sprints and hours, not ISO weeks: AI-speed delivery needs sprint-session buckets with days as the calendar floor

> **Status:** Complete
> **Decomposed-into:** EP0063
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator direction 2026-07-16

## Summary

Operator direction at the CR0310 sprint close: the MC forecast buckets throughput by ISO week, a granularity inherited from human-team Kanban literature. Measured reality here: 326 units delivered in 4 weeks, median cycle 0 days, 20 points per ~1.5 elapsed hours, sprints are sessions measured in hours. Rework the forecast's denominators: (1) primary = SPRINT-SESSIONS - sample the retro evidence's per-sprint delivered units/points (batch history already in retros/evidence) and report 'N sprints to clear the batch, ~H hours at the measured elapsed-hours-per-sprint'; (2) calendar floor = DAYS (bucket delivered dates per day, zero days included, same honesty guards) replacing weeks as the default; week stays available for slow-moving projects via a flag or config. Same seeded/refusal contract throughout. Lesson filed with the retro: calibrate an instrument's units to the measured process, not the literature's default.

## Impact

On an agent-speed project the weekly Monte Carlo forecast is quantised to uselessness: this repo's median cycle time is 0 days and a 19-unit batch reads '50% by next week' when the measured answer is 'this afternoon' - the operator's working heuristic is ~1 man-month of delivery per hour.

## Acceptance Criteria

- [ ] flow forecast defaults to day-bucket sampling (zero days included) and reports 50/85/95% dates at day precision; the ISO-week bucket remains available via flag/config
- [ ] A sprint-denominated forecast samples measured per-sprint throughput from the retro evidence ledger and reports sprints-to-complete plus hours at the measured elapsed-hours-per-sprint median, refusing under a minimum sprint-history (named, never guessed)
- [ ] reference-sprint.md#schedule-and-cost states the granularity rationale (agent-speed delivery, the man-month-per-hour heuristic as descriptive context, never a target)
- [ ] Existing refusal guards (seeded, min-history, all-zero, non-positive, horizon) hold in every bucket

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
