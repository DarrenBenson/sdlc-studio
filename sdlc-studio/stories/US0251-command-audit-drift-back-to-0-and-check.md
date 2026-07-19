# US0251: command_audit drift back to 0 and check_links + validate_skill green

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/reviews/command-audit.md
> **Epic:** EP0081
> **Points:** 2

## User Story

**As a** maintainer closing the cleanup slice
**I want** the checked-in command audit regenerated to zero drift with the link and
skill-spec guards green
**So that** the evidence that the surface is clean is current, not a stale snapshot

## Acceptance Criteria

### AC1: The regenerated audit reports zero drift

- **Given** the promotions and retirements have landed in SKILL.md and `help/help.md`
- **When** `command_audit.py --write --check-tools` regenerates
  `sdlc-studio/reviews/command-audit.md`
- **Then** its summary line reads zero unmapped, zero drift and zero broken tools
- **Verify:** grep "0 unmapped, 0 drift, 0 broken tool" sdlc-studio/reviews/command-audit.md
- **Verified:** yes (2026-07-19)

### AC2: The checked-in report matches a fresh run

- **Given** a generated report can drift from the tree it describes
- **When** the audit is regenerated over the current working tree
- **Then** the file is byte-identical to the committed copy, so the report cannot claim
  a surface state the tree no longer has
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/command_audit.py --write --check-tools && git diff --exit-code -- sdlc-studio/reviews/command-audit.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
