# US0981: A carry bug filed at the review cap does not count against the triage cap

> **Status:** Done
> **Delivers:** CR0607
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_uncapped.py, changelog.d/CR0607.md
> **Epic:** EP0271
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A carry bug filed at the review cap does not count against the triage cap
**So that** CR0607 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A carry bug is filed past the cap and not counted

- **Given** a triage session cap of 2 with two findings already filed in the session
- **When** `critic.py record` carries a unit at the review cap
- **Then** its carry bug is filed and the session's finding count stays at 2, so a third ordinary finding is still refused. Fails on: the current code refuses the carry bug at the cap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_uncapped.py::CarryBugUncappedTests::test_a_carry_bug_is_filed_past_the_cap_and_not_counted
- **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-02 | engineering seat (orchestrator) | Groomed from CR0607's criterion (D0297) |
