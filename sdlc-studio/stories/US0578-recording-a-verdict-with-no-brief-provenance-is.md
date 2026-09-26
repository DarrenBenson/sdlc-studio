# US0578: Recording a verdict with no brief provenance is REFUSED, and the refusal names critic.py brief

> **Status:** Done
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
- **Verify:** manual - retired by US0923: `critic.py record` no longer refuses a verdict carrying no `--brief`; the brief is used because it is useful, and `critic.py brief` still briefs the seat
- **Verified:** manual (2026-09-25) - retired, superseded by US0923

### AC2: a tool-briefed verdict records without complaint

- **Given** a verdict carrying the fingerprint `critic.py brief` emitted
- **When** it is recorded
- **Then** it succeeds silently, so the gate cannot be satisfied by one that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefProvenanceTests::test_a_briefed_verdict_records_cleanly
- **Verified:** yes (2026-08-01)

### AC3: the escape is a recorded decision, never an omission

- **Given** a project that has stood the requirement down through a recorded config decision
- **When** an unbriefed verdict is recorded
- **Then** it is accepted and the stand-down is stated on the output, so switching the rule off and forgetting it are different events in the record
- **Verify:** manual - retired by US0923: the `review.require_brief_provenance` key and its stand-down note went with the refusal, so there is nothing to stand down
- **Verified:** manual (2026-09-25) - retired, superseded by US0923

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Claude Opus 5.5 | AC1, AC3 retired by US0923 (D0259 pattern): `critic.py record` accepts a verdict with or without `--brief`, and `review.require_brief_provenance` is gone |
