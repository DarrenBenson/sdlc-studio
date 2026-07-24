# US0365: state the overage explicitly and name the longest sections by line count

> **Status:** Review
> **Delivers:** CR0360
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0127
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py, tools/check_budgets.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the refusal states the overage explicitly, for example 2 lines over the 80-line ceiling

- **Given** a LATEST.md two lines past the 80-line ceiling
- **When** doc_freshness flags the anchor-ledger finding
- **Then** the refusal states the overage explicitly, for example 2 lines over the 80-line ceiling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::AnchorWindowCeilingTests::test_overage_stated_explicitly
- **Verified:** yes (2026-07-24)

### AC2: the message names the longest sections by line count so the trim can be aimed rather than guessed

- **Given** a LATEST.md over the ceiling with sections of differing length
- **When** doc_freshness flags the anchor-ledger finding
- **Then** the message names the longest sections by line count so the trim can be aimed rather than guessed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py::AnchorWindowCeilingTests::test_longest_sections_named_by_line_count
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
