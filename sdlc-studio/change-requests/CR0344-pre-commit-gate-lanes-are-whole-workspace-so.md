# CR-0344: Pre-commit gate lanes are whole-workspace, so pre-existing backlog debt blocks every unrelated commit

> **Status:** Complete
> **Decomposed-into:** EP0121
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The gate's conformance/validate lanes scan the ENTIRE workspace, not the commit's diff. So one incomplete artifact anywhere (RUN-01KXQH64: a large refined Draft backlog; CR0342 fixed the Draft-story case) makes the gate red for EVERY subsequent commit, even ones that touch unrelated files - a single doc typo commit is blocked by backlog debt it did not create. CR0338 addresses the doc-coverage attribution; this is the broader design question.

## Impact

A workspace carrying legitimate in-flight debt (ungroomed or in-progress units) cannot commit ANY unrelated change until the debt clears - the gate holds unrelated work hostage, pushing toward --no-verify bypasses that erode the un-skippable-gate principle.

## Acceptance Criteria

- [ ] The blocking conformance/validate lanes offer a diff-scoped mode (gate only on artifacts the commit touches, plus the global census/link checks) so pre-existing debt is reported (advisory) but does not block an unrelated commit; the release gate stays whole-workspace.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
