# BG0485: the goal-review panel maps a seat's no to partial, and fans a whole-goal answer across every clause

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch
> **Verification depth:** functional

## Summary

Carved out of BG0402, which stood at Fixed while two of its four criteria were labelled NOT YET FIXED - a status the artefact's own body contradicted. BG0402 now describes only what shipped; these two halves live here, where their status is honest.

(1) A seat answering `no` is recorded `partial` via a second polarity mapping in the same module, rather than `missed` via `verdict_polarity`. Two mappings of the same question in one file is the drift shape this project keeps meeting: they will disagree, and the one that disagrees is the one nobody reads.

(2) A single plan-time answer about the WHOLE goal is fanned across every clause, so a clause no seat answered per-clause reads as answered. The panel already knows how to report UNANSWERED, which is the honest reading and the one a reader can act on.

## Steps to Reproduce

1. Record a goal-review seat verdict answering `no`.
2. Derive the clause verdicts; the seat reads `partial` rather than `missed`.
3. Record one whole-goal answer at plan time and assemble per-clause verdicts; every clause reads answered.

## Proposed Fix

Route the seat's answer through `verdict_polarity` so there is ONE mapping, and leave a clause no seat answered per-clause as UNANSWERED rather than fanning a whole-goal answer across it.

## Acceptance Criteria

- [x] **AC1: a seat's answer is mapped in ONE place.**
  - **Given** a seat verdict of `no`
  - **When** the goal-review panel records it
  - **Then** it is routed through `verdict_polarity` and stored as `no`, not downgraded to
    `partial` by a second mapping - two mappings answering one question is how a refusal became
    a qualified yes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AGoalClauseIsNotAnsweredByGuessworkTests::test_a_seat_answering_no_is_recorded_missed_not_partial
  - **Verified:** yes (2026-08-04)

- [x] **AC2: a clause no seat answered is UNANSWERED, never inherited.**
  - **Given** a goal of several clauses and a seat that answered the goal as a whole
  - **When** the per-clause view is derived
  - **Then** each clause the seat did not address reads `unanswered`, because fanning one
    whole-goal answer across every clause reports a verdict nobody gave
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AGoalClauseIsNotAnsweredByGuessworkTests::test_a_whole_goal_answer_is_not_fanned_across_clauses
  - **Verified:** yes (2026-08-04)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | Claude Opus 5 | Filed |
