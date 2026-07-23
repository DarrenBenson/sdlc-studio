# US0344: The reviewer brief asks whether the approach itself is the defect, and a recorded decision to RETAIN the design is a first-class outcome

> **Status:** Review
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Delivers:** CR0410
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0106
> **Points:** 2

## User Story

**As an** adversarial reviewer of a repair plan
**I want** to be asked whether the approach itself is the defect
**So that** I improve the design when it deserves it, rather than only improving the instance -
which is what happened when a reviewed plan supplied a better approach carrying the same false
premise as the one it replaced

## Acceptance Criteria

### AC1: the brief asks whether the approach is the defect, not only whether the fix is correct

- **Given** the brief generated for a repair-plan review on a repeat-class finding
- **When** it is parsed
- **Then** it carries the approach question alongside the four existing ones, and a brief
  missing it is refused rather than issued
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::ApproachQuestionBriefTests::test_a_repeat_class_brief_missing_the_approach_question_is_refused
- **Verified:** yes (2026-07-23)

### AC2: the brief shows the reviewer what the class has already tried

- **Given** a class that has failed more than one round
- **When** the brief is generated
- **Then** it enumerates the previous approaches and why each failed, because a reviewer asked
  whether an approach is exhausted cannot answer from the current plan alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repair_plan.py::ApproachQuestionBriefTests::test_the_brief_enumerates_the_previous_approaches_and_their_failures
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
