# US0445: Close tail derives parent CRs and RFCs terminal when all their children are terminal

> **Status:** Done
> **Delivers:** CR0422
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0164
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the close tail derives a parent request when all its children are terminal

- **Given** a CR (or RFC) whose decomposed epic and stories are all terminal, left non-terminal
- **When** the sign-off close tail runs
- **Then** it transitions the request to its terminal status (Complete for a CR), so a delivered
  request is not left for a manual `reconcile apply`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffRequestDerivationTests::test_derives_parent_request_when_all_children_terminal
- **Verified:** yes (2026-07-27)

### AC2: a request with a non-terminal child is left unchanged

- **Given** a CR whose decomposed epic still has a non-terminal story
- **When** the close tail runs
- **Then** the CR is left unchanged - the rule is all-children-terminal, the same predicate the
  epic derivation uses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffRequestDerivationTests::test_leaves_request_with_a_nonterminal_child
- **Verified:** yes (2026-07-27)

### AC3: the close names each request it derived

- **Given** a derivable parent request
- **When** the close tail derives it
- **Then** the derived request id is named in the close output, as the derived epics already are
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffRequestDerivationTests::test_names_each_derived_request
- **Verified:** yes (2026-07-27)

### AC4: the derivation is safe on a batch with no parent request

- **Given** a batch whose units have no parent request to derive
- **When** the close tail runs
- **Then** it derives nothing and raises no error (idempotent, safe)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ApplySignoffRequestDerivationTests::test_no_parent_request_is_safe
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
