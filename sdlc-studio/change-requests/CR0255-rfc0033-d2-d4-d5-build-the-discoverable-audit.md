# CR-0255: RFC0033 D2/D4/D5: build the discoverable audit command (RFC0002's accepted, unshipped command)

> **Status:** Proposed
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

RFC0002 (Accepted) blessed an adversarial audit command with lens profiles and an N-of-M refute panel; reference-audit.md and the audit-{finder,classify,refute}.md templates are its output, but the last mile never shipped - no help/audit.md, no Type Reference row, no catalogue entry, so the command is unreachable. Build it: the 'audit' command with repo/project/code profiles, the refute panel wired to the finder legs, help/audit.md, a Type Reference row and a help/help.md catalogue entry. Depends on the D1 script rename freeing the stem.

## Impact

The strongest weakness-hunt in the skill becomes discoverable and invokable for the first time. Every profile gets the refute panel that catches plausible-but-wrong findings (the safeguard whose absence cost BG0124 this session).

**Effort:** L

## Acceptance Criteria

- [ ] 'audit' is a documented command (help/audit.md exists, catalogue + Type Reference rows present) with repo/project/code profiles and a refute panel. Verify: test -f .claude/skills/sdlc-studio/help/audit.md && rg -q 'sdlc-studio audit' .claude/skills/sdlc-studio/help/help.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
