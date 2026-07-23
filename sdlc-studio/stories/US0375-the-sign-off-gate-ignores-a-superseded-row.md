# US0375: the sign-off gate ignores a superseded row while it stays visible

> **Status:** Draft
> **Delivers:** CR0372
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0133
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md

## User Story

**As an** operator who is the reviewer of record on a unit whose verdict log wrongly names me as its adversarial reviewer
**I want** the sign-off gate to read a superseded row as retired while the row stays in the file
**So that** a corrected mis-entry stops stranding the unit, without the audit trail losing the record that it happened

## Acceptance Criteria

### AC1: a superseded reviewer no longer disqualifies that person as principal

- **Given** a `US0276` verdict row naming `Darren Benson (operator)` as reviewer, and a recorded supersession retiring that row
- **When** `record_signoff` is called for `US0276` with `Darren Benson (operator)` as principal and `sdlc-studio; agent; v1` as author
- **Then** `_session_reviewer_ids` no longer returns the superseded reviewer, the sign-off is written, and `is_independent_signoff` reads it as independent - the unit can reach a conformant Done
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_superseded_reviewer_no_longer_blocks_the_principal

### AC2: latest-row-wins skips a superseded verdict and falls back to the live one

- **Given** a unit with an APPROVE row, then a later REJECT row, and a supersession retiring the REJECT
- **When** `verdict_for` is asked for that unit
- **Then** it returns the earlier live APPROVE rather than the retired REJECT, and a unit whose only row is superseded reads as having no verdict rather than as approved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_verdict_for_skips_the_superseded_row_and_falls_back

### AC3: the superseded row stays visible and is marked, never dropped

- **Given** the same superseded row
- **When** `read_verdicts` reads the log and `critic show` prints it, in both text and json form
- **Then** the row is still returned and printed, flagged as superseded with its reason and authoriser, so a reader sees both that it was recorded and that it was retired
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SupersededGateTests::test_superseded_row_stays_visible_and_flagged_in_show

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
