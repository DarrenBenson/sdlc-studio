# US0193: flow forecast defaults to day buckets and adds a sprint-session denominator sampled from retro evidence, ISO week behind a flag

> **Status:** Ready
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0063
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the schedule forecast denominated in days and sprint-sessions rather than ISO weeks
**So that** a forecast on an agent-speed project answers "this afternoon", not a week bucket quantised to uselessness

## Acceptance Criteria

### AC1: day buckets are the forecast default

- **Given** a workspace with delivered units dated across several days (zero-delivery days included)
- **When** `flow.py forecast` runs with no bucket flag
- **Then** flow forecast defaults to day-bucket sampling (zero days included) and reports 50/85/95% dates at day precision; the ISO-week bucket remains available via flag/config
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k DayBucket

### AC2: a sprint-session denominator sampled from retro evidence

- **Given** a retro evidence ledger holding measured per-sprint delivered units, points and elapsed hours
- **When** the sprint-denominated forecast runs
- **Then** A sprint-denominated forecast samples measured per-sprint throughput from the retro evidence ledger and reports sprints-to-complete plus hours at the measured elapsed-hours-per-sprint median, refusing under a minimum sprint-history (named, never guessed)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k SprintDenominator

### AC3: the granularity rationale is documented

- **Given** the shipped reference documentation
- **When** a reader opens reference-sprint.md's schedule-and-cost section
- **Then** reference-sprint.md#schedule-and-cost states the granularity rationale (agent-speed delivery, the man-month-per-hour heuristic as descriptive context, never a target)
- **Verify:** grep "granularity" .claude/skills/sdlc-studio/reference-sprint.md

### AC4: the refusal guards hold in every bucket

- **Given** forecast inputs that are unseeded, under minimum history, all-zero, non-positive or beyond the horizon
- **When** the forecast runs against each bucket (day, week, sprint)
- **Then** Existing refusal guards (seeded, min-history, all-zero, non-positive, horizon) hold in every bucket
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k BucketGuard

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
