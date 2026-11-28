# BG1780: `critic.recorded_seat` reads a reviewer's first role group, so a persona named with a parenthetical can be recorded as another seat

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py, changelog.d/BG1780.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1350's qa review in run twenty-eight (RUN-01M8B7DJ, 2026-11-27), verdict 948e9e1613f5-0162345b, by execution; US1351's builder left it for its own unit because the fix changes how two ledger cells read.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T00:13:07Z

## Summary

`critic.recorded_seat` takes the first `(<role>)` group in a reviewer cell. For a unit whose Persona carries a parenthetical, such as "Sam Eriksson (QA)", the stakeholder who writes the reviewer as "Sam Eriksson (QA) (persona)" is recorded by `critic.py approach record` as the qa seat. Under `review.solution_review.panel: [qa, persona]`, that row plus a second persona row makes `approach_agreed` report every seat agreed, with no qa review recorded. No open unit names such a Persona, so the defect is latent. Reading the last group instead changes how two existing three-seat cells in sdlc-studio/reviews/critic-verdicts.md read, so the fix must keep those rows' meaning.

## Steps to Reproduce

1. In a fixture project, give a story the Persona "Sam Eriksson (QA)" and set `review.solution_review.panel: [qa, persona]` with `min_points: 1`.
2. Record a GO with `--reviewer 'Sam Eriksson (QA) (persona)'`, then a GO with `--reviewer 'Sam Eriksson QA (persona)'`.
3. `critic.approach_agreed` reports the approach agreed, naming qa at round 1, though no qa seat reviewed.

## Proposed Fix

Read the seat from the last `(<role>)` group, or refuse a reviewer cell with more than one role group, keeping the existing "+"-joined three-seat cells in critic-verdicts.md read as they are today; pin both with tests.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `critic.recorded_seat` takes the first `(<role>)` group in a reviewer cell.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_a_persona_with_a_parenthetical_sits_as_the_persona
- [ ] **AC2** The proposed fix lands, pinned by a test: Read the seat from the last `(<role>)` group, or refuse a reviewer cell with more than one role group, keeping the existing "+"-joined three-seat cells in...
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_the_seat_is_the_first_reviewer_s_last_role_group
- [ ] **AC3** `critic.py approach record` refuses an unreadable note (a permission error or a non-UTF-8 file) in words naming the note and saying it cannot be read, as its other refusals do, not with the raw OSError text ("approach record refused: [Errno 13] Permission denied: '<path>'"); exit 2 and nothing written still hold. Folded in from US1344's product review (verdict 0eac43e39f0e-5afe8509), which found it owned by no open unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_panel.py::SolutionReviewPanelTests::test_an_unreadable_note_is_refused_in_words

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
