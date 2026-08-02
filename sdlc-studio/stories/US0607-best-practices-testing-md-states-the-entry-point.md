# US0607: best-practices/testing.md states the entry-point rule beside name-the-mutant-first

> **Status:** Review
> **Delivers:** CR0520
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/testing.md, tools/best_practice_rules.py, tools/tests/test_best_practice_rules.py
> **Epic:** EP0199
> **Points:** 2

## User Story

**As a** engineer about to write a test
**I want** the entry-point rule stated beside name-the-mutant-first
**So that** the rule is met where the decision is made rather than at review

## Acceptance Criteria

### AC1: the practice states the entry-point rule

- **Given** `best-practices/testing.md` as shipped
- **When** it is read
- **Then** it says to name the ENTRY POINT the test enters through before writing it, and that a library import standing in for a command is not evidence for a claim about the command
- **Verify:** pytest tools/tests/test_best_practice_rules.py::TestingPracticeTests::test_the_entry_point_rule_is_stated
- **Verified:** yes (2026-08-02)

### AC2: the guard cannot be satisfied by prose describing the change

- **Given** the stating passage deleted while a Revision History row describing it remains
- **When** the guard runs
- **Then** it goes red, because a whole-file substring satisfied by its own changelog row is BG0457's shape
- **Verify:** pytest tools/tests/test_best_practice_rules.py::TestingPracticeTests::test_deleting_the_passage_reddens_the_guard
- **Verified:** yes (2026-08-02)

### AC3: the guard is a runnable command, not only a test

- **Given** `tools/best_practice_rules.py`
- **When** it is run against a practice missing the rule and against the shipped one
- **Then** it exits 1 and 0 respectively, so the rule is enforceable by a gate rather than only where a test runner happens to look
- **Verify:** pytest tools/tests/test_best_practice_rules.py::TestingPracticeTests::test_the_command_exits_non_zero_when_the_rule_is_absent
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
