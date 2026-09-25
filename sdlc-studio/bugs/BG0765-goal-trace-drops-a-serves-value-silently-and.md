# BG0765: goal_trace drops a --serves value silently, and reads unfilled template placeholders as real outcomes

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace_followups.py, changelog.d/BG0765.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

From the US0927 review: (1) with no Outcomes section and no persona cards, `goal_trace` returns before reading --serves, so --serves O1 prints nothing though the changelog says an unnamed value is reported; (2) the shipped PRD and persona templates, unfilled, trace as real outcomes and personas ({{`outcome_1`}}, {{`full_name`}}); (3) the test fixture's out-of-section O7 bait is never asserted, so a parser that ignores section bounds survives.

## Steps to Reproduce

sprint.py plan --serves O1 on a project with no PRD Outcomes and no persona cards prints no goal line; on the unfilled template PRD, --serves O1 prints goal serves: O1 - {{`outcome_1`}}.

## Proposed Fix

Skip the early return when --serves is given and name each value as unknown; skip outcome items and persona headings holding {{; assert O7 is absent from `could_serve.`

## Acceptance Criteria

- [ ] **AC1** Given a project with no PRD Outcomes section and no persona cards, when `sprint.py plan --serves O1,Maya` runs, then each value is named as unknown on its own line and the plan exits 0 with its batch unchanged; returning early before reading `--serves` (today's code) fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace_followups.py::GoalTraceFollowupTests::test_serves_is_reported_with_nothing_to_trace_against
- [ ] **AC2** Given the shipped PRD and persona templates left unfilled, then no outcome whose text holds `{{` and no persona whose heading holds `{{` is traced or offered; reading placeholders as answers fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace_followups.py::GoalTraceFollowupTests::test_unfilled_placeholders_are_not_outcomes_or_personas
- [ ] **AC3** Given an `- **O7:**` item outside the `## Outcomes` section, then it is not an outcome; a parser that ignores section bounds fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace_followups.py::GoalTraceFollowupTests::test_an_outcome_outside_the_section_is_ignored

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Claude Opus 5.5 | Criteria authored with executable Verify lines for the Sprint 4 batch |
