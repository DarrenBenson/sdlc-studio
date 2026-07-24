# US0368: extend the CR0340 test-relevant set to every path a shipped test reads

> **Status:** Draft
> **Delivers:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0129
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the test-relevant set covers every path a shipped test reads

- **Given** the CR0340 test-relevant set, which today names only scripts/, templates/ and tools/
- **When** the set is computed
- **Then** it includes every path a shipped test actually reads - measured from the suites, not enumerated by hand, because an enumeration is a lower bound
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestRelevantSetTests::test_every_path_a_shipped_test_reads_is_in_the_set

### AC2: a docs-only skip is refused when a test reads that doc

- **Given** a commit touching only a documentation file that a shipped test asserts against
- **When** the pre-commit gate decides whether to skip the suites
- **Then** it does NOT skip - the docs-only fast path is exactly where a test reading a doc gets silently bypassed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestRelevantSetTests::test_a_doc_a_test_reads_defeats_the_docs_only_skip

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
