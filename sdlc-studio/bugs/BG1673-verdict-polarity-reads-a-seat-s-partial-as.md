# BG1673: verdict_polarity reads a seat's 'partial' as unclear, so a goal clause every seat answered partial reads UNANSWERED at the close

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:48:51Z

## Summary

In run twenty's close-time goal review (RUN-01M7VNR0), all three seats answered the clause 'Persona cards meet an enforced standard' with 'partial - ...', and product answered 'persona docs match the code' the same way. `sprint.verdict_polarity` knows only yes and no words (`_VERDICT_YES`, `_VERDICT_NO)`, so 'partial' reads unclear, `_recorded_clause_verdicts` drops it, and the close's goal panel reports the clause UNANSWERED though three seats answered it. The panel's own vocabulary (achieved, missed) has no partial either, and the goal-review prompts in this repository ask seats for yes, partial or no.

## Steps to Reproduce

Record a goal-review round whose seats answer one clause 'partial - <reason>', then read `sprint._recorded_clause_verdicts` for the goal's clauses: the clause is absent, and sprint close prints it UNANSWERED.

## Proposed Fix

Read partial (and words like 'partly') as its own polarity and carry it to the panel as partial, so the close reports the clause as partially achieved by the seats that said so; pin it beside yes, no and an unclear answer.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run twenty's close-time goal review (RUN-01M7VNR0), all three seats answered the clause 'Persona cards meet an enforced standard' with 'partial - ...', and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a goal-review round whose seats answer one clause 'partial - <reason>', then read `sprint._recorded_clause_verdicts` for the goal's clauses: the clause...
- [ ] **AC3** The proposed fix lands, pinned by a test: Read partial (and words like 'partly') as its own polarity and carry it to the panel as partial, so the close reports the clause as partially achieved by the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
