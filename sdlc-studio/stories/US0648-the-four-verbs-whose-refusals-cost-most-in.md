# US0648: The four verbs whose refusals cost most in the measured session answer the contract reporter

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py, .claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0210
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The four verbs whose refusals cost most in the measured session answer the contract reporter
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: each of the four answers the reporter

- **Given** critic record, file_finding file, goal-review record and mutation register
- **When** the contract reporter is asked about each
- **Then** every one returns its demands, derived from its own guard - these four were chosen because they refused most in the measured session, not because they were easiest
- **Mutant:** wire three and leave one - the verb left out is the one whose refusal is still discovered by hitting it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_all_four_answer_the_reporter

### AC2: the answer names the field shape, not just the field

- **Given** a verb demanding a structured value - an origin-tagged finding, a seat spec
- **When** the reporter is asked
- **Then** it reports the SHAPE the guard accepts, because knowing a flag is required and not what it accepts costs the same round trip
- **Mutant:** report the flag name alone - the caller is refused a second time on the same flag
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_the_shape_is_reported_not_only_the_field

### AC3: the reported shape is the one the guard accepts

- **Given** a value built from what the reporter said
- **When** the verb is invoked with it
- **Then** it is accepted - a contract report that does not round-trip is documentation with a different name
- **Mutant:** report a shape the guard rejects - the report is confidently wrong, which is worse than absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::TheFourCostliestVerbsTests::test_the_reported_shape_round_trips

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
