# CR-0255: RFC0033 D2/D4/D5: build the discoverable audit command (RFC0002's accepted, unshipped command)

> **Status:** Superseded
> **Superseded-by:** CR0256 (discoverability shipped via BG0174; residual folded into CR0256)
> **Size:** L
> **Priority:** P2
> **Type:** Feature
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Depends on:** CR0254
> **Affects:** .claude/skills/sdlc-studio/scripts/review_generate.py, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/help/help.md, .claude/skills/sdlc-studio/SKILL.md

## Summary

RFC0002 (Accepted) blessed an adversarial audit command with lens profiles and an N-of-M refute panel; reference-audit.md and the audit-{finder,classify,refute}.md templates are its output, but the last mile never shipped - no help/audit.md, no Type Reference row, no catalogue entry, so the command is unreachable. Build it: the 'audit' command with repo/project/code profiles, the refute panel wired to the finder legs, help/audit.md, a Type Reference row and a help/help.md catalogue entry. Depends on the D1 script rename freeing the stem.

## Impact

The strongest weakness-hunt in the skill becomes discoverable and invokable for the first time. Every profile gets the refute panel that catches plausible-but-wrong findings (the safeguard whose absence cost BG0124 this session).

**Effort:** L

## Acceptance Criteria

- [ ] `audit` is a documented, discoverable command: `help/audit.md` exists, the command catalogue
      and the Type Reference both carry its row, and an agent reading the help finds it without
      being told it exists. It offers the repo, project and code profiles, and its output carries
      a refute panel.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
