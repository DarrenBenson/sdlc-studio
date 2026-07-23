# US0318: The shipped reviewer brief carries per-item repair verdicts, mutating the author's tests, and isolation re-testing, with the reason each exists beside it

> **Status:** Done
> **Delivers:** CR0396
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0108
> **Points:** 3

## User Story

**As an** adversarial reviewer arriving with no memory of the sprint
**I want** the three practices that produced this project's best findings stated in the brief
**So that** they do not depend on whoever wrote the brief happening to remember them, which
is how all three were improvised mid-sprint rather than drawn from anything shipped

## Acceptance Criteria

### AC1: all three practices are standing instructions, each with its reason

- **Given** the shipped reviewer brief
- **When** it is parsed
- **Then** it carries per-item repair verdicts, mutating the author's TESTS rather than only
  the code, and isolation re-testing of a surviving mutant, each paired with the reason it
  exists, and a brief missing any of the three is refused rather than issued
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewerBriefTests::test_a_brief_missing_any_of_the_three_practices_is_refused
- **Verified:** yes (2026-07-23)

### AC2: a surviving mutant is stated to be evidence about the harness, not the test

- **Given** the brief's instruction on a surviving mutant
- **When** a reviewer follows it
- **Then** it directs re-testing the branch in ISOLATION before drawing any conclusion,
  because a sibling guard masked a survivor three separate times in one sprint and each time
  the truth appeared only when the branch was exercised alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewerBriefTests::test_the_survivor_instruction_requires_isolation_before_a_conclusion
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
