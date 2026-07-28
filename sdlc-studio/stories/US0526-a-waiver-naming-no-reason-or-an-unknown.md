# US0526: A waiver naming no reason or an unknown rule is refused at record time rather than silently doing nothing

> **Status:** Ready
> **Delivers:** CR0460
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Epic:** EP0180
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator recording a waiver and expecting it to mean something
**I want** a waiver with no reason or an unknown rule refused at record time
**So that** a waiver that will do nothing is refused when it is written, not discovered when it fails to help

## Acceptance Criteria

### AC1: a waiver naming an unknown rule is refused when recorded

- **Given** a waive naming a rule no checker declares
- **When** it is recorded
- **Then** it is refused, naming the rules that exist, so a waiver cannot be written against nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverValidationTests::test_an_unknown_rule_is_refused

### AC2: a waiver with no rationale is refused

- **Given** a waive carrying no reason
- **When** it is recorded
- **Then** it is refused - an unexplained waiver is indistinguishable from forgetting the rule exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverValidationTests::test_a_waiver_without_a_reason_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
