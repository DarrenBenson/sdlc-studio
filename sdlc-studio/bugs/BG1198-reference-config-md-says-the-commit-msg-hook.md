# BG1198: reference-config.md says the commit-msg hook refuses a commit without a Refs: trailer per owning id, and does not name the Mentions: trailer US1115 added

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, changelog.d/BG1198.md
> **Evidence:** US1115 builder report, 2026-11-04.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T11:14:41Z

## Summary

2026-11-04, US1115's build (run five). US1115 and US1116 let a `Mentions:` trailer account for an id the subject only mentions. reference-config.md:173 still describes the message rule as refusing a commit without a `Refs:` trailer per owning id. That is still true, but a reader of the config reference is not told the second trailer exists.

## Steps to Reproduce

1. `sed -n 170,176p .claude/skills/sdlc-studio/reference-config.md`.

## Proposed Fix

Name both trailers there, with the rule for when each applies.

## Acceptance Criteria

- [ ] **AC1** reference-config.md's message-rule sentence names the Mentions: trailer.
  - **Verify:** shell grep -n 'Mentions:' .claude/skills/sdlc-studio/reference-config.md

## Impact

A reader of the config reference adds a false Refs: for a mention-only id, the friction CR0659 was raised to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
