# US0366: a third disposition (fixed-in sha) in retro.py, the gate, the template and the tri-state close counts

> **Status:** Done
> **Delivers:** CR0362
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0128
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/templates/retro-template.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py

## User Story

**As an** operator closing a sprint that repaired findings during delivery
**I want** a third disposition that records a finding fixed in-sprint, distinct from filed and declined
**So that** a sprint that fixed eleven findings does not read as having declined eleven

## Acceptance Criteria

### AC1: a third disposition records a finding fixed within the sprint, with the commit or unit that fixed it

- **Given** a retro Actions-raised row whose disposition is `fixed-in: <sha or unit>`
- **When** the retro is validated
- **Then** a third disposition records a finding fixed within the sprint, with the commit or unit that fixed it, and it is green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::FixedInSprintIsAThirdDisposition::test_a_fixed_in_sha_is_dispositioned_as_fixed
- **Verified:** yes (2026-07-24)

### AC2: the gate accepts it as dispositioned, distinctly from filed and from declined

- **Given** a retro whose only finding is dispositioned `fixed-in: <sha>`
- **When** the gate's retro leg validates it
- **Then** the gate accepts it as dispositioned, distinctly from filed and from declined
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::FixedInSprintIsAThirdDisposition::test_fixed_is_distinct_from_filed_and_declined
- **Verified:** yes (2026-07-24)

### AC3: the counts the close reports name the three states separately, so a sprint that repaired eleven

- **Given** a retro whose findings span all three dispositioned states
- **When** the close counts are reported
- **Then** the counts the close reports name the three states separately, so a sprint that repaired eleven findings does not read as having declined eleven
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::FixedInSprintIsAThirdDisposition::test_the_close_counts_name_the_three_states_separately
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
