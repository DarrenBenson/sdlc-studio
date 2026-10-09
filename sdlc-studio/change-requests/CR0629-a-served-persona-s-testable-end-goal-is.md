# CR-0629: A served persona's testable End goal is run at the close as evidence for the goal verdict

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_verdict_end_goal_evidence.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Raised by the G11 breakdown of CR0621 and its panel review (D0355); framed by RFC0061 workstream 4.
> **Date:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T10:05:23Z

## Summary

The goal review names the testable End goals a Sprint Goal traces to (G11), but nothing runs them. At the close, the goal verdict judges the increment against the seats' `done_means` alone, so a goal whose End goal Verify is still red can be closed as met. Run each traced persona's executable End goal Verify at the close (and optionally at plan, to show it red before the work) and record the result beside the goal verdict: the served-goal outcome evidence RFC0061's D4 and D6 name for user personas learning from usage. Framed by RFC0061 workstream 4; decide its strength (reported or refusing) there. Depends on G11's End goal reader and goal review stories.

## Impact

A Sprint Goal can be closed as met while the persona End goal it traces to still fails.

## Acceptance Criteria

- [ ] Given a Sprint Goal that traces to a persona whose End goal carries an executable Verify, when the run closes, then the goal verdict records that Verify's result beside the seats' `done_means`, and a red result is reported by name rather than read as met.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Raised |
