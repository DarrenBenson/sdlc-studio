# US0503: A delegated task that stops without a result is reported as unfinished, never as pending, and the audit quorum rule cross-references it

> **Status:** Review
> **Delivers:** CR0450
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-audit.md, .claude/skills/sdlc-studio/scripts/../reference-agent-prompt-template.md, tools/tests/test_doc_claims.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** agent collecting verdicts from a panel
**I want** a delegated task that stops without a result reported as unfinished rather than pending
**So that** an outage cannot masquerade as work still in progress, the same way a dead vote must not masquerade as a refutation

## Acceptance Criteria

### AC1: an unfinished delegate is reported as unfinished

- **Given** a panel in which one delegate returns no result
- **When** the run reports
- **Then** that delegate is counted unfinished and named, never folded into a pending count that implies it may still answer
- **Verify:** pytest tools/tests/test_doc_claims.py::StallDoctrineTests::test_an_unfinished_delegate_is_reported_as_unfinished

### AC2: the audit quorum rule cross-references it

- **Given** the audit reference's dead-vote quorum section
- **When** it is read
- **Then** it points at the stall rule, so the two halves of one class - an absent vote and an absent agent - are read together
- **Verify:** pytest tools/tests/test_doc_claims.py::StallDoctrineTests::test_the_quorum_rule_cross_references_the_stall_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
