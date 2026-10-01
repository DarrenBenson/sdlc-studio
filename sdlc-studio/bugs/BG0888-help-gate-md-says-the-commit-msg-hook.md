# BG0888: help/gate.md says the commit-msg hook snippet degrades honestly with no script, but it blocks

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/gate.md
> **Evidence:** US0973 QA review (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T19:02:09Z

## Summary

help/gate.md:350 says the commit-msg hook snippet exits without blocking when its script is missing; python3 exits 2 on the missing file and the commit is blocked.

## Steps to Reproduce

1. Install the help/gate.md commit-msg snippet with `CLAUDE_SKILL_DIR` pointing at a folder with no scripts. 2. git commit -> blocked, exit 2.

## Proposed Fix

Guard the call on the script existing, or reword the sentence to say it blocks.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: help/gate.md:350 says the commit-msg hook snippet exits without blocking when its script is missing; python3 exits 2 on the missing file and the commit is...
- [ ] **AC2** The proposed fix lands, pinned by a test: Guard the call on the script existing, or reword the sentence to say it blocks.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
