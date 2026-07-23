# US0319: A repair review is briefed with the previous round's findings enumerated and returns a CLOSED / OVER-CLAIMED / MOVED verdict per item

> **Status:** Done
> **Delivers:** CR0396
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0108
> **Points:** 3

## User Story

**As an** operator reading round two of a review
**I want** each previous finding ruled on individually
**So that** I can see which repairs closed, which over-claimed and which moved the defect,
instead of one impression covering all of them

## Acceptance Criteria

### AC1: a repair review is briefed with the previous round's findings enumerated

- **Given** a review round that follows a recorded REJECT
- **When** its brief is generated
- **Then** the brief lists every finding of the previous round individually, so the reviewer
  cannot answer in aggregate about a set they were never shown item by item
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairVerdictTests::test_a_repair_brief_enumerates_every_previous_finding
- **Verified:** yes (2026-07-23)

### AC2: a repair verdict is refused unless every finding carries its own ruling

- **Given** a repair-round verdict answering three of the previous round's four findings
- **When** it is recorded
- **Then** it is refused and names the unruled finding, and each ruling is one of CLOSED,
  OVER-CLAIMED or MOVED - three categories a general 'review the repair' answer would blur
  into one, which is what made this the most useful artefact of RUN-01KY3MFX
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairVerdictTests::test_a_verdict_leaving_a_finding_unruled_is_refused
- **Verified:** yes (2026-07-23)

### AC3: MOVED is not counted as closed

- **Given** a repair round ruling one finding MOVED
- **When** the round's outcome is summarised
- **Then** the finding is reported as still open, because a defect that moved is a defect
  that survived - counting it closed is how a repair masks the defect beside it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairVerdictTests::test_a_moved_finding_is_not_counted_as_closed
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
