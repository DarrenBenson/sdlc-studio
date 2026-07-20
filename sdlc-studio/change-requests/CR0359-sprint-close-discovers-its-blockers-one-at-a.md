# CR-0359: sprint close discovers its blockers one at a time, so a close takes as many runs as it has unmet prerequisites

> **Status:** In Progress
> **Decomposed-into:** EP0089
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Closing RUN-01KXVYGR took four invocations of sprint close. Each refusal was correct and well explained, but each was discovered only after the preceding ones were cleared: a stale LATEST.md, then LATEST.md current but uncommitted, then no recorded critic author to sign off against. The gate block runs 18 lanes and prints them all at once, which is exactly right; the prerequisites for apply-signoff are not part of that block and surface serially afterwards. Each cycle costs a full gate run, and the unit suites inside it take about 125 seconds, so the serial discovery cost several minutes and three avoidable re-runs. The information was all available before the first attempt.

## Impact

An operator or agent closing a sprint pays a full gate run per unmet prerequisite and cannot tell in advance how many remain. It reads as the tool moving the goalposts, which is corrosive for a gate whose value depends on being trusted rather than worked around.

## Acceptance Criteria

- [ ] sprint close runs a pre-flight that reports EVERY unmet prerequisite in one pass before executing any step
- [ ] the pre-flight covers the apply-signoff prerequisites (a recorded critic verdict, an independent principal) alongside the existing gate lanes
- [ ] the pre-flight is available standalone so it can be run before starting a close

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
