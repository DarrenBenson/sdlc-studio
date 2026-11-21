# BG1685: BG1107 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_end_goals_wrap.py, changelog.d/BG1107.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T17:30:00Z

## Summary

BG1107 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's heading test is pinned on one side only. `_whole_end_goals` now ends a goal at `re.match(r"^#{1,6}\s", line)` (sprint.py:11915, added by b8839c73 per `git log -S`), and `test_a_deeper_heading_ends_the_goal_above_it` (test\_end\_goals\_wrap.py:76) pins that a `###` and a `####` heading end it, but nothing pins that a `#`-led line which is not a heading is still joined. The mutant `re.match(r"^#", line)` survives test\_end\_goals\_wrap.py and every goal-reading module (`test_goal_review*.py`, `test_lean_goal*.py`, test\_persona\_goal\_lines.py, test\_close\_goal\_judgement\_in\_report.py, test\_persona\_review\_block.py: 77 passed). Re-tested alone on a card whose goal `1. Close every bug the release names in` wraps onto `#123 before the tag is cut`, HEAD returns the whole goal and the mutant returns `Close every bug the release names in`, the goal cut off mid-sentence that this unit exists to fix. The repair is to add a `#`-led continuation line that is not a heading (such as `#123 before the tag is cut`) to the deeper-heading test and assert it is joined into the goal; RULINGS: Round-1 finding "`_whole_end_goals` reads a level-3-or-deeper heading, and the lines under it, into the End goal above" CLOSED: sprint.py:11915 ends the join at any `#{1,6}` ATX heading and the new test pins a `###` and a `####` heading, with goal 2 still read after each. My mutants in a throwaway clone: only levels 1 to 3 end the join KILLED, the heading check dropped KILLED, a deeper heading closing the section KILLED. An empty `###` line and a `### X` heading indented by two spaces still join, which matches `persona_goals._HEADING_RE` (persona\_goals.py:32, `^#{1,2}\s`, column 0 and text required), the reader's own notion of a heading, so that is not ruled a finding. The new finding is the opposite side of the same new condition. AC1 green through verify\_ac dry run (pass=1). The author's six mutants replay killed. Claim inventory: the docstring and changelog.d/BG1107.md sentence that a heading ends the goal TRUE for every heading the reader calls one, the test docstring's mutant (5) TRUE by execution. No open bug covers the finding (BG1650 is the comment and fence reading). lint-style clean.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1107 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1107 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's heading test is pinned on one side only. `_whole_end_goals` now ends a goal at `re.match(r"^#{1,6}\s", line)` (sprint.py:11915, added by b8839c73 per `git log -S`), and `test_a_deeper_heading_ends_the_goal_above_it` (test\_end\_goals\_wrap.py:76) pins that a `###` and a `####` heading end it, but nothing pins that a `#`-led line which is not a heading is still joined. The mutant `re.match(r"^#", line)` survives test\_end\_goals\_wrap.py and every goal-reading module (`test_goal_review*.py`, `test_lean_goal*.py`, test\_persona\_goal\_lines.py, test\_close\_goal\_judgement\_in\_report.py, test\_persona\_review\_block.py: 77 passed). Re-tested alone on a card whose goal `1. Close every bug the release names in` wraps onto `#123 before the tag is cut`, HEAD returns the whole goal and the mutant returns `Close every bug the release names in`, the goal cut off mid-sentence that this unit exists to fix. The repair is to add a `#`-led continuation line that is not a heading (such as `#123 before the tag is cut`) to the deeper-heading test and assert it is joined into the goal
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1107 AC1 still passes: A card whose numbered End goals wrap across lines yields each goal's whole text from `_end_goals`, and the goal-review brief prints it whole
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_end_goals_wrap.py::EndGoalsWrapTests::test_a_wrapped_end_goal_is_returned_whole

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG1107 was reviewed again in round three under D0570 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG1107 is Fixed |
