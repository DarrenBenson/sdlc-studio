# US0578: Recording a verdict with no brief provenance is REFUSED, and the refusal names critic.py brief

> **Status:** Draft
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0194
> **Points:** 3

## User Story

**As a** maintainer of the review gate
**I want** an unbriefed verdict refused at the point of recording
**So that** the seat-brief rule is a refusal rather than doctrine that gets skipped

## Acceptance Criteria

### AC1: a verdict with no brief provenance is refused

- **Given** a `critic.py record` invocation carrying no brief fingerprint
- **When** it runs
- **Then** it exits non-zero and the refusal names `critic.py brief --unit <id> --seat <seat>` as the way to obtain one, because a hand-written prompt silently substitutes an unbounded surface for a unit review
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_a_verdict_without_provenance_is_refused

### AC2: a tool-briefed verdict records without complaint

- **Given** a verdict carrying the fingerprint `critic.py brief` emitted
- **When** it is recorded
- **Then** it succeeds silently, so the gate cannot be satisfied by one that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_a_briefed_verdict_records_cleanly

### AC3: the escape is a recorded decision, never an omission

- **Given** a project that has stood the requirement down through a recorded config decision
- **When** an unbriefed verdict is recorded
- **Then** it is accepted and the stand-down is stated on the output, so switching the rule off and forgetting it are different events in the record
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_the_stand_down_is_stated_not_silent

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
