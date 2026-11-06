# BG1251: Three lane frictions each cost a hand-fix: an in-flight warning per sibling lane on every brief, a hand-in fragment not linted before the commit, and a hand-in line that names its fields but not the values the record accepts

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** the orchestrator's friction log, run seven (RUN-01M6RAP7) F8, F9 and F14
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:37:46Z

## Summary

Run seven, the orchestrator's friction log (F8, F9 and the part of F14 no open item covers). (1) F9: on every `lane brief`, `sprint.py:9137-9141` prints a restart WARNING for each row of `lanes_in_flight`. In a parallel wave every sibling lane is in flight by design, and `lane accept` returns a lane only on APPROVE, so each reviewed-but-rejected and each unreviewed lane warns too: six warnings in US1124's repair brief, a brief for one unit. (2) F8: a changelog fragment line that wraps to begin with `+` (US0988, an arithmetic expression) is read by markdownlint as a list item (MD004), and the refusal arrives at the integration commit rather than in the builder's worktree; neither the lane brief nor `lane land` checks the hand-in's markdown before the commit runs. (3) F14, the brief's part: the hand-in line (`sprint.py:2860-2862`) names `{surface, claim, ruling}` and `{mutant, test, result, answer}` but not that a ruling is one of `CLAIM_RULINGS` (TRUE, FALSE, UNVERIFIABLE; `critic.py:3765`) written bare, nor that each mutant's test is a `path::name` in a test file the unit's Affects declares (`critic.py:2962`, :4595). US1123's builder appended evidence to rulings (`TRUE (test_x; holds only with ...)`) and pointed mutants at tests outside the Affects, and the record refused both. CR0683 moves that refusal ahead of the commit and BG1229 accepts a `TRUE: evidence` ruling; neither changes what the brief tells the builder.

## Steps to Reproduce

1. Brief two lanes and leave both in flight, then run `sprint.py lane brief` for a third unit: one WARNING per in-flight lane is printed. 2. Hand in a fragment with a wrapped line opening `+ 3` and run `sprint.py lane land`: the commit hook's markdown lane refuses at the commit. 3. Read the lane brief's hand-in line: no accepted ruling value or test-file rule is named.

## Proposed Fix

Print one line naming the units in flight, with the full restart warning only for the unit being briefed; have `lane land` run markdownlint over the hand-in's staged markdown before it commits (and, with CR0676's generator, wrap fragment prose so no line opens with a list marker); state in the hand-in line the accepted rulings, written bare, and that each mutant's test must sit in one of the unit's Affects test files, naming them.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, the orchestrator's friction log (F8, F9 and the part of F14 no open item covers).
- [ ] **AC2** The proposed fix lands, pinned by a test: Print one line naming the units in flight, with the full restart warning only for the unit being briefed; have `lane land` run markdownlint over the hand-in's...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
