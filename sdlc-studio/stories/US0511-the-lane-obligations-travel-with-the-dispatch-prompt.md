# US0511: The lane obligations travel with the dispatch prompt, so they do not depend on who wrote that sprint's brief

> **Status:** Review
> **Delivers:** CR0463
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/../reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, tools/tests/test_doc_claims.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator whose sprint quality should not depend on who wrote the brief
**I want** the lane obligations carried by the dispatch itself
**So that** the checks travel with the work rather than relying on the author of that sprint's prompt remembering them

## Acceptance Criteria

### AC1: the dispatch carries the obligations without the caller restating them

- **Given** a sprint dispatching lanes
- **When** the brief is built
- **Then** it carries the refuse-without-criteria, verify-before-returning and return-the-proof obligations, from the shared template rather than from the caller
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneContractTests::test_the_dispatch_carries_the_obligations
- **Verified:** yes (2026-07-28)

### AC2: the reference states them where an author of a new harness will read them

- **Given** the agent-prompt reference
- **When** it is read
- **Then** the obligations appear there, so a project building its own dispatch inherits them rather than rediscovering them
- **Verify:** pytest tools/tests/test_doc_claims.py::LaneObligationDocsTests::test_the_obligations_are_documented
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
