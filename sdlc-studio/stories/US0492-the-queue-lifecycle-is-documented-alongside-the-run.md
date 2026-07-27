# US0492: The queue lifecycle is documented alongside the run lifecycle, with every invocation shown taken from the shipped parser

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../help/sprint.md, .claude/skills/sdlc-studio/scripts/../reference-sprint.md
> **Epic:** EP0176
> **Points:** 3

## User Story

**As a** reader looking for how to plan several sprints and run the next
**I want** the queue lifecycle documented beside the run lifecycle, with runnable invocations
**So that** the documented surface is the shipped surface, rather than something to be discovered from argparse

## Acceptance Criteria

### AC1: every queue verb the parser defines is documented

- **Given** the shipped command parser
- **When** the coverage check runs
- **Then** each queue verb the parser defines appears in the documentation, and the expected set is read from the parser rather than from a list in the check
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_every_parser_verb_is_documented

### AC2: every invocation shown is one the parser accepts

- **Given** the invocations shown in the documentation
- **When** each is parsed by the shipped parser
- **Then** every one parses, so an example cannot document a form the command would reject
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_every_documented_invocation_parses

### AC3: the recorded reasoning for materialising late is stated where a reader looks for a queue

- **Given** a reader arriving expecting frozen queued plans
- **When** the documentation is read
- **Then** it states that charters queue intent and the batch is resolved at start, and why - so the design answer is found rather than the absence of a feature
- **Verify:** pytest tools/tests/test_help_coverage.py::QueueDocsTests::test_the_materialise_late_reasoning_is_documented

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
