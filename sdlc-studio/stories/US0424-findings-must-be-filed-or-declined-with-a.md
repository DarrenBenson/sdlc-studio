# US0424: findings must be filed or declined with a reason before --write proceeds; silence is refused

> **Status:** Done
> **Delivers:** RFC0050
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0158
> **Points:** 3

## User Story

**As an** operator about to open a run
**I want** `--write` refused while plan-critic findings are undispositioned
**So that** findings must be filed or declined with a reason, and silence cannot pass for agreement

## Acceptance Criteria

### AC1: silence is refused

- **Given** a plan critic pass that produced findings, none of them dispositioned
- **When** `--write` is attempted
- **Then** it is REFUSED and names the undispositioned findings - the retro already enforces file-or-decline, and a plan critic whose findings can be ignored is advice nobody has to take
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFindingDispositionTests::test_write_is_refused_while_a_finding_is_undispositioned
- **Verified:** yes (2026-07-24)

### AC2: a decline needs a reason, not a marker

- **Given** a finding declined with an empty or placeholder reason
- **When** the disposition is validated
- **Then** it is refused - a decline whose reason is `{{why}}` records that someone clicked past it, which is worse than no record because it looks like a decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFindingDispositionTests::test_a_decline_without_a_real_reason_is_refused
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
