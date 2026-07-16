# CR-0310: Deterministic flow metrics and Monte Carlo forecasting: cycle time, throughput, WIP age, blocked age from the census + git log - zero-token measurement

> **Status:** Complete
> **Decomposed-into:** EP0052
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; agile-practice gap analysis 2026-07-16

## Summary

Gap analysis vs proven practice (research sweep 2026-07-16): Vacanti's flow metrics (WIP, cycle time, throughput, work-item age) plus Monte Carlo simulation over historical throughput are the STRONG-evidence forecasting stack - probabilistic ('85% confidence by date X') rather than deterministic single dates, mathematically grounded in Little's law, and the direction elite orgs are moving (State of Agile 17/18: flow + DORA over framework compliance). Every input already exists deterministically in this workspace: Created: dates in artefact headers, status transitions in git log per file, Blocked in the status vocabulary, terminal dates in revision history. A new flow module (or status/`sprint_report` extension) computes per-unit cycle time, weekly throughput, age of every non-terminal In Progress/Blocked unit, and an MC completion forecast for a named batch - pure stdlib, zero model tokens, replacing token-burning status narration with computed numbers. Explicitly COMPLEMENTARY to RFC0038: points x measured rate stays the COST model (r=+0.68 proven); flow metrics answer SCHEDULE, which points were never validated for. Velocity remains descriptive-never-a-target.

## Impact

The skill measures cost (points x tokens) but has no schedule instrument at all: no cycle time, throughput, work-item age or blocked age anywhere, so 'when will this batch land' is answered by narration or a single-point guess - the exact practice current evidence rates statistically unreliable.

## Acceptance Criteria

- [ ] A flow subcommand computes per-unit cycle time (Created -> terminal, from file dates + git log), weekly throughput, and work-item age for every non-terminal unit, pure stdlib, no model tokens
- [ ] Blocked units report blocked-age separately; an In Progress unit older than a configurable ageing threshold is flagged in status output
- [ ] A Monte Carlo forecast (seeded, reproducible) over measured weekly throughput gives 50/85/95% completion dates for a named batch of units, refusing (not guessing) when history is under a minimum sample size
- [ ] `sprint_report.py` show and status.py surface the flow numbers; documentation states flow = schedule instrument, points x rate = cost instrument, and neither feeds a gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
