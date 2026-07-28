# US0537: A lane writing a changelog fragment is accepted and a lane hand-editing [Unreleased] is refused with the fragment command in the refusal

> **Status:** Draft
> **Delivers:** CR0467
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py
> **Epic:** EP0183
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a lane writing a fragment is accepted and a hand-edit is refused with the remedy

- **Given** two lanes each owing a changelog entry
- **When** one writes a fragment and the other hand-edits the [Unreleased] section
- **Then** the fragment is accepted, the hand-edit is refused, and the refusal names the fragment command so the author can act on it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog.py::ParallelLaneRuleTests::test_a_fragment_is_accepted_and_a_hand_edit_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
