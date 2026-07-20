# US0263: On a repair regression, escalate to a revert / redesign / accept-and-file decision instead of another patch round

> **Status:** Done
> **Delivers:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0085
> **Points:** 3

## User Story

**As an** operator whose repair loop has started manufacturing its own findings
**I want** the loop to stop patching and put a revert / redesign / accept-and-file choice in front of me
**So that** the escape from a self-feeding loop is a decision someone makes, not a round nobody chose

## Acceptance Criteria

### AC1: A repair regression stops the patch path and presents three named options

- **Given** a round whose finding US0262 classified as a repair regression
- **When** the loop reaches its next-step decision
- **Then** it presents revert, redesign and accept-and-file as named options with their consequences, and does not offer another patch round as the default
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_repair_regression_presents_the_three_options
- **Verified:** yes (2026-07-20)

### AC2: The choice is recorded, not just acted on

- **Given** the operator chooses one of the three
- **When** the choice is taken
- **Then** it is recorded against the run with the regression that triggered it, so the retro can read why the loop stopped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_escalation_choice_is_recorded_against_the_run
- **Verified:** yes (2026-07-20)

### AC3: Accept-and-file mints a real linked artefact

- **Given** the operator chooses accept-and-file
- **When** the choice is applied
- **Then** the finding is filed through the existing finding filer as a bug or CR linked to the run, and the id is reported - never a prose note claiming it was filed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_accept_and_file_mints_a_linked_artefact
- **Verified:** yes (2026-07-20)

### AC4: Revert names exactly what it would revert before doing it

- **Given** the operator is offered revert
- **When** the option is presented
- **Then** it names the round whose repair would be reverted and the files involved, so the choice is not blind
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_revert_option_names_its_scope
- **Verified:** yes (2026-07-20)

### AC5: The autonomous path records and blocks, never picks for you

- **Given** an autonomous run hits a repair regression
- **When** the escalation is reached
- **Then** the decision is recorded as pending and the run blocks on it, matching the deferred-decision contract - it never selects an option on the operator's behalf
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_autonomous_regression_blocks_rather_than_chooses
- **Verified:** yes (2026-07-20)

## Notes

AC5 mirrors the contract US0280/US0281 established for `sprint decision defer`: an
autonomous run records and blocks, never defaults. Reuse that queue rather than adding a
second pending-decision mechanism.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: user story and ACs authored; reuses the deferred-decision queue |
