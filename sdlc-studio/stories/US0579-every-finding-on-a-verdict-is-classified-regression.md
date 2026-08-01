# US0579: Every finding on a verdict is classified REGRESSION, NEW or PRE-EXISTING, and an unclassified verdict is refused

> **Status:** Draft
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0194
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: every finding carries a classification

- **Given** a verdict whose findings are each marked REGRESSION, NEW or PRE-EXISTING
- **When** it is recorded and read back
- **Then** each finding's classification survives the round trip
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_a_classification_survives_the_round_trip

### AC2: an unclassified finding is refused

- **Given** a verdict carrying a finding with no classification
- **When** recording is attempted
- **Then** it exits non-zero naming that finding, because an unsorted finding is the one a close cannot price against the batch that caused it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_an_unclassified_finding_is_refused

### AC3: a verdict with no findings at all is still valid

- **Given** an APPROVE recording `none blocking`
- **When** it is recorded
- **Then** it succeeds, so the rule cannot be satisfied by refusing every clean pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::FindingClassTests::test_a_clean_pass_needs_no_classification

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
