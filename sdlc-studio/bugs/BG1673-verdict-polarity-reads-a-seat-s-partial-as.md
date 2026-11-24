# BG1673: verdict_polarity reads a seat's 'partial' as unclear, so a goal clause every seat answered partial reads UNANSWERED at the close

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_partial_clause_verdict.py, changelog.d/BG1673.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:48:51Z

## Summary

In run twenty's close-time goal review (RUN-01M7VNR0), all three seats answered the clause 'Persona cards meet an enforced standard' with 'partial - ...', and product answered 'persona docs match the code' the same way. `sprint.verdict_polarity` knows only yes and no words (`_VERDICT_YES`, `_VERDICT_NO)`, so 'partial' reads unclear, `_recorded_clause_verdicts` drops it, and the close's goal panel reports the clause UNANSWERED though three seats answered it. The goal-review prompts in this repository ask seats for yes, partial or no.

Reproduced at cecc9dfe7 (2026-11-24): `verdict_polarity("partial - two cards lack a lens")` and `verdict_polarity("partly")` both return `unclear`, and `_recorded_clause_verdicts` over a round whose three seats answer one clause `partial - ...` and another `yes` returns only the `yes` clause. Correction to the filing: the panel does know partial. `critic.GOAL_VERDICTS` is `("achieved", "partial", "missed")` and `critic.goal_panel` accepts it, so the fix is in `sprint.py` alone: `_recorded_clause_verdicts` maps every polarity that is not yes to `missed` and drops `unclear`, and has no partial to pass on.

## Steps to Reproduce

Record a goal-review round whose seats answer one clause 'partial - <reason>', then read `sprint._recorded_clause_verdicts` for the goal's clauses: the clause is absent, and sprint close prints it UNANSWERED.

## Proposed Fix

Give `verdict_polarity` a third polarity, `partial`, for an answer whose first word is partial, partly or partially, and have `_recorded_clause_verdicts` carry it to the panel as `partial`, so the close reports the clause as partially achieved by the seats that said so. The callers that test `== "no"` are unchanged, so a seat answering achievable `partial` is still not an objection. Pin it beside yes, no and an unclear answer.

## Acceptance Criteria

- [ ] **AC1** Given the answers `partial - two cards lack a lens`, `Partly` and `partially, see notes`, when `sprint.verdict_polarity` reads each, then it returns `partial`, while `yes`, `no - not at the stated appetite` and `maybe later` still read `yes`, `no` and `unclear`. Fails on: every partial answer read as `unclear`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_clause_verdict.py::PartialClauseVerdictTests::test_partial_reads_as_its_own_polarity
- [ ] **AC2** Given a goal-review round whose three seats answer clause A `partial - <reason>`, clause B `yes` and clause C `no`, and one seat answers clause D `maybe`, when `sprint._recorded_clause_verdicts` reads the four clauses, then A is `partial` for each seat, B `achieved`, C `missed`, and D absent. Fails on: clause A absent, so the panel reads it UNANSWERED.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_clause_verdict.py::PartialClauseVerdictTests::test_a_clause_answered_partial_reaches_the_panel_as_partial
- [ ] **AC3** Given a run whose goal has that clause A and a round answering it partial, when `sprint.close_goal_judgement` runs, then the panel line reports A as `partial` and does not print `UNANSWERED` for it. Fails on: `UNANSWERED (3 seat(s) silent): <clause A>` at the close.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_clause_verdict.py::PartialClauseVerdictTests::test_the_close_reports_a_partial_clause_not_unanswered
- [ ] **AC4** Given a whole-goal seat verdict whose achievable answer is `partial - the appetite is tight`, when `sprint.goal_review_status` reads it, then the seat is not listed in `objections`. Fails on: a mutant mapping partial to `no`, which turns a hedge into an objection on the plan.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_partial_clause_verdict.py::PartialClauseVerdictTests::test_a_whole_goal_partial_is_not_an_objection

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; corrected the claim that the panel has no partial (critic.GOAL_VERDICTS carries it); four executable criteria in a new test module; Affects adds changelog.d/BG1673.md and drops test_goal_review_testable_goals.py and test_sprint.py; Points 2 to 1 |
