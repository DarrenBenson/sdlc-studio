# US0561: A batch-review finding is filed as a delivery unit against the batch that caused it, so its cost is priced where the work was

> **Status:** Review
> **Delivers:** CR0500
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0190
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** a maintainer trying to tell whether the review placement actually changed anything
**I want** a finding raised while a batch is open to record that batch on the artefact
**So that** the sprint can report WHERE its defects were found instead of asserting it, and the cost lands on the batch that caused it

## Acceptance Criteria

### AC1: A finding filed while a batch is open records that batch and run on the artefact, so its cost is attributable to the batch that caused it rather than to the close

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AFindingIsPricedWhereTheWorkWasTests::test_a_finding_records_the_open_batch
- **Verified:** yes (2026-07-29)

### AC2: The batch span carries the ids raised against it, so the batch can be read back as work-plus-findings rather than work alone

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_findings_raised_against_a_batch_are_recorded_on_it
- **Verified:** yes (2026-07-29)

### AC3: A finding filed with NO open batch is recorded as such rather than silently attributed to the last one - an absence is stated, never guessed

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AFindingIsPricedWhereTheWorkWasTests::test_no_open_batch_is_stated_not_guessed
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
