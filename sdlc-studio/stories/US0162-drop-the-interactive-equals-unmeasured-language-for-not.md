# US0162: Drop the interactive-equals-UNMEASURED language for not-yet-captured, preserving CR0273 guards

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-retro.md
> **Epic:** EP0045
> **Points:** 3

## User Story

**As a** reader of the retro doctrine
**I want** the "interactive = UNMEASURED" language corrected to "not-yet-captured"
**So that** the doctrine stops calling a knowable token count unmeasurable.

## Acceptance Criteria

### AC1: the retro template, retro.py doctrine and reference-retro say not-yet-captured (with --tokens), preserving CR0273's guard; links + style pass

- **Given** the retro doctrine surfaces
- **When** they are read
- **Then** the template, retro.py module docstring, and reference-retro frame an interactive sprint's tokens as harness-tracked / not-yet-captured (supply via `accuracy --tokens N`), keep the descriptive-never-a-target guard, and all markdown links + style pass
- **Verify:** shell grep -q 'not-yet-captured' .claude/skills/sdlc-studio/templates/reviews/retro.md && grep -q 'not-yet-captured' .claude/skills/sdlc-studio/reference-retro.md && python3 tools/check_links.py && bash tools/lint-style.sh
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
