# US1210: The critic brief names the enclosing symbol and its line range for each diff hunk

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0678
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0330
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The critic brief names the enclosing symbol and its line range for each diff hunk
**So that** CR0678 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each diff hunk names its enclosing symbol and range

- **Given** a unit whose committed change edits the body of one function and one method in an Affects Python file
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** each hunk of the UNIT DIFF names the function or method that encloses it and that symbol's start-end line range as the file stands at HEAD. Fails on: a hunk carrying only git's own hunk header, or a range taken from the lines the symbol held before the change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefHunkSymbolTests::test_each_hunk_names_its_enclosing_symbol_and_line_range

### AC2: A hunk outside any symbol names none and the brief still prints

- **Given** a unit whose diff holds one hunk at module level above the first definition and one hunk in a Markdown file
- **When** `critic.py brief --unit <id> --seat qa` is run twice
- **Then** neither hunk names a symbol, the brief exits 0, and both runs print the same brief with the same fingerprint. Fails on: the nearest unrelated symbol named for a module-level hunk, an error on a file the repo map cannot parse, or a fingerprint that changes between two runs on one tree
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefHunkSymbolTests::test_a_hunk_outside_any_symbol_names_none

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
