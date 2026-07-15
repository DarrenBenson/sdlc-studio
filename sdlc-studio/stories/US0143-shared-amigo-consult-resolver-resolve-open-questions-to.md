# US0143: Shared amigo-consult resolver: resolve open questions to named seat cards with the amigo frame

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py
> **Epic:** EP0040
> **Points:** 5

## User Story

**As** refine and triage
**I want** a shared helper that resolves open questions to named amigo seats
**So that** both ceremonies name the same seats the same way, framed and lead-first.

## Acceptance Criteria

### AC1: consult resolves a panel of named seats, lead-first, and honours --skip-personas

- **Given** `persona_resolve.consult(root, panel, questions)`
- **When** it resolves the refine (engineering-led) and triage (QA-led) panels, and the skip-personas path
- **Then** each role resolves to its named seat with the review-render framing, the lead is first, and `--skip-personas` yields role-label seats with no framing (byte-equivalent); blank questions are dropped and the panel still resolves
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_amigo_consult.ResolverTests
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
