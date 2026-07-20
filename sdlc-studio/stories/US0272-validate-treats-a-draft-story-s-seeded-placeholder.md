# US0272: validate treats a Draft story's seeded placeholder ACs as a warning, so the refine commit lands while conformance still keeps it out of delivery

> **Status:** Done
> **Delivers:** CR0342
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Epic:** EP0088
> **Points:** 2

## User Story

**As a** developer refining a large discovery backlog into delivery work
**I want** the commit that creates ungroomed Draft stories to pass the pre-commit gate
**So that** I can decompose a backlog without either grooming weeks of work up front or
bypassing an un-skippable gate with `--no-verify`

## Acceptance Criteria

### AC1: an ungroomed Draft story's placeholder AC is a warning, so the refine commit lands

- **Given** a story at Draft whose acceptance criteria are still the seeded `{{...}}` scaffolds
  that `refine` writes
- **When** `validate` checks it
- **Then** the placeholder is still REPORTED, but at `warn` severity, so the refine commit that
  creates a Draft backlog passes the pre-commit gate instead of forcing premature grooming or a
  `--no-verify` bypass of an un-skippable gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k test_draft_story_placeholder_ac_is_a_warning_not_error
- **Verified:** yes (2026-07-20)

### AC2: a groomed story's placeholder AC stays a hard error

- **Given** a story at Ready or later carrying a placeholder acceptance criterion
- **When** `validate` checks it
- **Then** it is an ERROR, because a story claiming Ready must have executable ACs - the
  relaxation is scoped to the pre-Ready state and nowhere else
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k test_placeholder_ac_flagged
- **Verified:** yes (2026-07-20)

### AC3: nothing ungroomed can be delivered

- **Given** an ungroomed story with placeholder ACs moved to Ready
- **When** the gate runs
- **Then** conformance refuses it as `missing specified, verifiable`, so the warning relaxes only
  what the gate tolerates at Draft and never what it will accept as delivered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py -k "test_ready_story_still_requires_specified_and_verifiable or test_draft_story_is_conformant_on_decomposed_alone"
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
