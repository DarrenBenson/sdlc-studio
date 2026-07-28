# US0525: The conformance lane reads recorded waivers and reports a waived unit as waived, naming the decision

> **Status:** Done
> **Delivers:** CR0460
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Epic:** EP0180
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator whose recorded waiver does nothing
**I want** the conformance lane to read recorded waivers and report a waived unit as waived
**So that** the escape hatch the gate itself recommends actually clears the lane it recommends it for

## Acceptance Criteria

### AC1: a waived unit reports as waived, naming the decision

- **Given** a unit covered by a recorded waiver
- **When** the conformance check runs
- **Then** it reports the unit as waived and names the decision that waived it, rather than counting it non-conformant
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverTests::test_a_waived_unit_reports_as_waived_naming_the_decision
- **Verified:** yes (2026-07-28)

### AC2: a unit outside the waiver is unaffected

- **Given** a non-conformant unit no waiver covers
- **When** the check runs
- **Then** it is still reported, so a waiver narrows the finding rather than silencing the lane
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverTests::test_an_unwaived_unit_is_still_reported
- **Verified:** yes (2026-07-28)

### AC3: the lane behaves the same whether or not a diff exists to scope to

- **Given** a clean tree and a dirty one
- **When** the check runs in each
- **Then** the waiver is honoured in both, because a close runs on a clean tree and that is exactly when the waiver was needed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::WaiverTests::test_the_waiver_holds_on_a_clean_tree
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
