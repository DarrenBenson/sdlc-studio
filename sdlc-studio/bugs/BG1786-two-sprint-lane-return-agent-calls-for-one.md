# BG1786: Two `sprint lane return --agent` calls for one agent transcript count its priced spend twice in the run

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_return_agent_prefix.py, changelog.d/BG1786.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run twenty-eight, US1353 qa round 2 (2026-11-28, about 03:20Z): two `lane return` calls on a fixture recorded 10,880 for one 5,440 reading; sprint.py is unchanged by US1353.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T04:03:09Z

## Summary

`sprint lane return --agent <id>` adds the agent transcript's priced spend to the run each time it runs, so returning the same agent twice (a retried return, or a return after `critic.py approach spend` already recorded that transcript) counts one reading twice: US1353's qa seat measured 10,880 recorded for one 5,440 reading. `critic.py approach spend` now refuses a second record of one transcript (US1353, 41fed6f03), but `lane return` has no such guard, so the sprint report's tokens and cost per point overstate a unit whose builder was returned twice.

## Steps to Reproduce

1. Open a run with one unit and a builder transcript of known priced spend.
2. Run `sprint lane return --agent <id>` twice for the same agent.
3. The run's delegated spend holds the transcript twice.

## Proposed Fix

Record a transcript once per run in `lane return`, as `approach spend` now does: a second return of a transcript already recorded refuses or replaces, naming the unit it is recorded against, and the report counts it once.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint lane return --agent <id>` adds the agent transcript's priced spend to the run each time it runs, so returning the same agent twice (a retried return...
- [ ] **AC2** The proposed fix lands, pinned by a test: Record a transcript once per run in `lane return`, as `approach spend` now does: a second return of a transcript already recorded refuses or replaces, naming...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
