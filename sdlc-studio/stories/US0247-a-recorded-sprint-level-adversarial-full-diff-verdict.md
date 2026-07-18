# US0247: a recorded sprint-level adversarial full-diff verdict satisfies the per-unit critiqued gate for the units in its diff range; per-unit REJECT-repairs still recorded

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Epic:** EP0080
> **Points:** 5

## User Story

**As a** reviewer running the closing adversarial full-diff pass
**I want** one recorded sprint-level verdict to satisfy the per-unit critiqued gate for the units in its range
**So that** the close does not demand a redundant per-unit evidence row for every unit the one full-diff pass already judged

## Acceptance Criteria

### AC1: a recorded sprint-level APPROVE satisfies critiqued for a covered unit with no per-unit verdict

- **Given** a Done story with no individual critic verdict, covered by a recorded independent sprint-level APPROVE
- **When** conformance is checked
- **Then** the unit's `critiqued` stage passes (verdict + evidence halves satisfied by the sprint review)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.SprintReviewCritiquedTests
- **Verified:** yes (2026-07-18)

### AC2: a per-unit REJECT is never overridden by sprint coverage

- **Given** a unit whose latest per-unit verdict is REJECT, also inside a sprint-level APPROVE's range
- **When** conformance is checked
- **Then** `critiqued` stays failed - the REJECT must be repaired per unit
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.SprintReviewCritiquedTests
- **Verified:** yes (2026-07-18)

### AC3: a sprint-level review proves independence and refuses a self-review

- **Given** `critic sprint-review` recording a batch verdict
- **When** reviewer == author, or findings/units are empty
- **Then** it is refused loudly (independence is proven, not assumed)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.SprintReviewCritiquedTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
