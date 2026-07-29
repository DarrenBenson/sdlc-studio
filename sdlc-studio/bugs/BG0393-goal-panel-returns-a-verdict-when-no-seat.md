# BG0393: goal_panel returns a verdict when no seat answered, and silently discards a verdict under a mismatched clause key

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

A panel where nothing was answered returns overall `partial` rather than None - the function raises on an empty seat list precisely because 'an empty panel returns a verdict nobody gave', then does exactly that. Worse, `supplied.get(clause)` is keyed by the stripped clause, so a key differing by case or whitespace drops a seat's verdict without error and a `missed` becomes `partial`.

## Steps to Reproduce

`goal_panel(`'.',['c1','c2'],['qa','arch'],'author') -> verdict 'partial' with no answers given.

## Proposed Fix

Overall None when no clause is answered; raise on a verdicts key matching no clause, as an unrecognised verdict word already does.

## Acceptance Criteria

### AC1: a panel nobody answered returns no verdict

- **Given** a panel of seats where no clause was answered
- **When** it runs
- **Then** the overall verdict is None, not `partial` - the function refuses an empty seat list for this exact reason and must not reach the same place by another route
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnansweredPanelTests::test_a_panel_nobody_answered_returns_no_verdict
- **Verified:** yes (2026-07-29)

### AC2: a partly answered panel still reports

- **Given** one clause answered and one silent
- **When** it runs
- **Then** the answered clause keeps its verdict and the silent one is None, so silence does not blank a real judgement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnansweredPanelTests::test_a_partly_answered_panel_still_reports
- **Verified:** yes (2026-07-29)

### AC3: a verdicts key matching no clause is refused

- **Given** a verdicts key differing from the clause by case or whitespace
- **When** it runs
- **Then** the panel is refused, rather than dropping the seat's verdict without a word and turning a `missed` into a `partial`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::UnansweredPanelTests::test_a_verdict_key_matching_no_clause_is_refused
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
