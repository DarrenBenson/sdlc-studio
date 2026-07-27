# US0504: Mutation testing by a delegated reviewer runs in an isolated checkout, and mutation.py refuses to mutate a file with uncommitted changes

> **Status:** Ready
> **Delivers:** CR0452
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/../reference-review.md
> **Epic:** EP0177
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** author whose tree a reviewer is mutating
**I want** mutation testing to happen in an isolated checkout, and the tool to refuse a dirty one
**So that** a reviewer cannot silently revert my code, which is exactly what happened and passed a green suite

## Acceptance Criteria

### AC1: mutation refuses a file with uncommitted changes

- **Given** a target file with uncommitted edits
- **When** mutation runs
- **Then** it refuses, naming the file, because a mutation applied over uncommitted work cannot be distinguished from that work when it is restored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::IsolationTests::test_mutation_refuses_a_dirty_file

### AC2: the doctrine states where a reviewer mutates

- **Given** the review reference
- **When** it is read
- **Then** it states that a delegated reviewer mutates in an isolated checkout, never the author's tree, and states the author-side rule that follows
- **Verify:** pytest tools/tests/test_doc_claims.py::MutationIsolationTests::test_the_isolation_rule_is_documented

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
