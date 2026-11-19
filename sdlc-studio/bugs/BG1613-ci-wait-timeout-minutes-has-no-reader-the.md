# BG1613: ci.wait_timeout_minutes has no reader: the trunk guidance's wait fence hardcodes `timeout 30m`, so a project's override changes nothing

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-code.md, .claude/skills/sdlc-studio/templates/agent-instructions.md, .claude/skills/sdlc-studio/scripts/tests/test_trunk_ci_wait_guidance.py, changelog.d/BG1613.md
> **Evidence:** run eighteen, 2026-11-19: US1237 QA verdict sdlc-studio/reviews/verdicts/US1237/7161895a780d-4fb090fa.txt; goal-review round 14, qa seat note
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T13:23:46Z

## Summary

US1237 added `ci.wait_timeout_minutes` to config-defaults.yaml and reference-config.md, but no shipped code or template reads it: the blocking `gh run watch` fence in reference-code.md (around line 761) and the agent-instructions template hardcode `timeout 30m`. The rerun limit, the same story's other key, is read by gate.py. Found by run eighteen's goal review and US1237's QA review, both non-blocking.

## Steps to Reproduce

Set `ci: {wait_timeout_minutes: 5}` in sdlc-studio/.config.yaml and read the wait instruction the trunk guidance gives: it still says `timeout 30m`.

## Proposed Fix

Have the trunk guidance name the key and its default instead of a literal, or have a shipped helper print the wait command with the configured timeout.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1237 added `ci.wait_timeout_minutes` to config-defaults.yaml and reference-config.md, but no shipped code or template reads it: the blocking `gh run watch`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Set `ci: {wait_timeout_minutes: 5}` in sdlc-studio/.config.yaml and read the wait instruction the trunk guidance gives: it still says `timeout 30m`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the trunk guidance name the key and its default instead of a literal, or have a shipped helper print the wait command with the configured timeout.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
