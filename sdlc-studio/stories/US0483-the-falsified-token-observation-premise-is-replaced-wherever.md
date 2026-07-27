# US0483: The falsified token-observation premise is replaced wherever the tracked tree asserts it

> **Status:** Won't Implement
> **Delivers:** CR0446
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-config.md, .claude/skills/sdlc-studio/scripts/../reference-sprint.md, tools/tests/test_token_premise.py
> **Epic:** EP0174
> **Points:** 3

## User Story

**As a** consuming project reading the shipped payload to learn what the tooling can measure
**I want** the claim that a script cannot observe token spend removed wherever it is still asserted
**So that** nobody designs around an absent capability that run_state.session_tokens has provided all along

## Acceptance Criteria

### AC1: no live assertion of the premise survives outside a historical record

- **Given** the tracked tree
- **When** the sweep runs
- **Then** it finds no live assertion of the premise, and an assertion inside a dated historical record is distinguished from a live one rather than counted with it
- **Verify:** pytest tools/tests/test_token_premise.py::TokenPremiseTests::test_no_live_assertion_survives

### AC2: the targets are found by searching the tree, not from a list

- **Given** a new file added asserting the premise
- **When** the sweep runs with no edit to it
- **Then** the new file is reported, because the search enumerates the tracked tree rather than a recorded set of paths
- **Verify:** pytest tools/tests/test_token_premise.py::TokenPremiseTests::test_a_new_assertion_is_found_without_editing_the_sweep

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
