# US0562: sprint close REFUSES a batch containing units no independent review has covered, and names them

> **Status:** Done
> **Delivers:** CR0500
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0190
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** a maintainer who wants the close to certify rather than discover
**I want** `sprint close` to REFUSE a batch carrying units no independent review has covered, and name them
**So that** the close asserts that coverage exists rather than performing the review, so its cost is bounded

## Acceptance Criteria

### AC1: `sprint close` REFUSES while any unit in the run's batch is covered by no independent review, and NAMES every uncovered unit

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheCloseCertifiesRatherThanReviewsTests::test_the_close_refuses_and_names_uncovered_units
- **Verified:** yes (2026-07-29)

### AC2: The refusal states what would clear it, so it is actionable without reading the source

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheCloseCertifiesRatherThanReviewsTests::test_the_refusal_names_the_remedy
- **Verified:** yes (2026-07-29)

### AC3: A fully covered batch does not trip the step, so the check cannot become a blanket refusal nobody can satisfy

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheCloseCertifiesRatherThanReviewsTests::test_a_covered_batch_passes
- **Verified:** yes (2026-07-29)

### AC4: The step reports the batch-boundary against close-time split of findings, so the goal 'defects are found inside the sprint' is measurable rather than asserted

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheCloseCertifiesRatherThanReviewsTests::test_the_close_reports_where_findings_were_raised
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
