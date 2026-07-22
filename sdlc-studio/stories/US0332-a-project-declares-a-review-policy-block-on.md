# US0332: A project declares a review policy: block-on-REJECT, today's behaviour and the default, or carry-forward

> **Status:** Draft
> **Delivers:** CR0404
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0113
> **Points:** 3

## User Story

**As an** operator choosing how my team ships
**I want** to declare whether a REJECT blocks or carries forward
**So that** the project states which it is, instead of supporting only one and being silent
about the choice

## Acceptance Criteria

### AC1: the default is today's behaviour, and an absent declaration does not change a close

- **Given** a project declaring no review policy
- **When** a REJECT is recorded
- **Then** it blocks exactly as it does now, so an upgrading project sees no change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewPolicyTests::test_an_undeclared_policy_blocks_exactly_as_today

### AC2: under carry-forward a REJECT no longer blocks the sprint

- **Given** a project declaring carry-forward, and a REJECT whose findings are all filed
- **When** the sprint proceeds to close
- **Then** it is not blocked by the verdict, and `sprint_covers_independently` accepts the
  sprint review as evidence despite the REJECT
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::ReviewPolicyTests::test_a_reject_under_carry_forward_does_not_block_the_close

### AC3: an unrecognised policy value is refused, never defaulted

- **Given** a project declaring a policy string the code does not recognise
- **When** the policy is resolved
- **Then** it is refused and names the accepted values, rather than silently falling back to
  the default - a typo that quietly selects blocking is survivable, but one that quietly
  selects carry-forward ships a sprint nobody meant to ship
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewPolicyTests::test_an_unrecognised_policy_is_refused_not_defaulted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
