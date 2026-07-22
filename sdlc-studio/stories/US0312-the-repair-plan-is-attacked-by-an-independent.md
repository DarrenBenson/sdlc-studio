# US0312: The repair plan is attacked by an independent pass before any code is written, briefed with the four questions this loop keeps failing

> **Status:** Draft
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/templates/reviewer-brief.md
> **Epic:** EP0106
> **Points:** 5

## User Story

**As an** operator whose last sprint spent ten review rounds
**I want** the repair plan attacked by someone who did not write it, before any code changes
**So that** an approach that will fail is refuted while it is still a paragraph, rather than
after it has been built and reviewed

## Acceptance Criteria

### AC1: a repair executed with no plan-review record is refused

- **Given** a repair plan carrying no independent verdict
- **When** the repair is recorded against the sprint
- **Then** it is refused, naming the plan and the review it lacks
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanReviewTests::test_a_repair_without_a_plan_verdict_is_refused

### AC2: the author of a plan cannot record its verdict

- **Given** a plan review whose reviewer identity equals the plan's author
- **When** the verdict is recorded
- **Then** it is refused on the same self-approval rule the story-plan gate already applies,
  so the independence is mechanical rather than a convention the author is asked to honour
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanReviewTests::test_the_plan_author_cannot_record_its_own_verdict

### AC3: the brief puts the four questions this loop kept failing

- **Given** the brief generated for a repair-plan review
- **When** it is parsed
- **Then** it carries all four questions as separate items - does the fix introduce the class
  it repairs; is it a restatement of a rule living in code elsewhere, and could it be
  DERIVED; what did the previous attempt believe that turned out false; what does this change
  make it harder to notice - and a brief missing any of them is refused rather than issued
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanReviewTests::test_a_brief_missing_any_of_the_four_questions_is_refused

### AC4: the review happens before the diff, not beside it

- **Given** a plan whose verdict was recorded after the repair commit it authorises
- **When** the gate checks it
- **Then** the verdict does not satisfy the gate, because a review that followed the work is
  a description of it rather than an attack on it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanReviewTests::test_a_verdict_recorded_after_the_repair_does_not_satisfy_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
