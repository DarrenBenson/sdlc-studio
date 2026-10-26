# CR-0654: The builder brief tells the builder to write its story file and the self-check log, then commit only its Affects, without saying who commits those two

> **Status:** Proposed
> **Priority:** Low
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US1093 QA review, qa-seat-US1093-r1, 2026-10-26: new finding 2.
> **Date:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T12:21:47Z

## Summary

US1093's QA review (2026-10-26). `sprint.py lane brief` tells the builder to run `verify_ac.py run --id <id>`, which ticks the unit's own story file, and `critic.py self-check record`, which appends to sdlc-studio/reviews/author-self-checks.md; its commit step stages only the Affects (US1093 AC1). Neither file is in Affects and the brief does not say who commits them. In this repository's run three the orchestrator carried them.

## Impact

A builder following the brief exactly leaves two modified files uncommitted, or commits them outside the unit's declared scope.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Name the hand-off in the brief: either a second step committing the story file and the self-check log as paperwork, or a line saying the orchestrator records and commits them, chosen by a setting.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Raised |
