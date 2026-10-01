# BG0878: config.py show prints null for keys whose default lives only in a reader's code

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Evidence:** US0759 QA review (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:41Z

## Summary

21 of the 42 dotted config keys the scripts read have no entry in config-defaults.yaml (`review.max_rounds`, `sprint.points_split_above`, `gate.budget_seconds`, `quality.done_requires_verified`, lessons.loop, report.enabled and others), so config.py show --key `review.max_rounds` prints null while 2 is in force, and show --sources lists no line for them.

## Steps to Reproduce

1. A project whose .config.yaml sets only coverage.unit. 2. config.py show --key `review.max_rounds` -> null (critic.py uses 2).

## Proposed Fix

Declare each code-owned default in config-defaults.yaml and have the readers take it from there, or have show report the reader's default.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: 21 of the 42 dotted config keys the scripts read have no entry in config-defaults.yaml (`review.max_rounds`, `sprint.points_split_above`...
- [ ] **AC2** The proposed fix lands, pinned by a test: Declare each code-owned default in config-defaults.yaml and have the readers take it from there, or have show report the reader's default.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
