# BG1107: sprint._end_goals keeps only the first line of a wrapped End goal, so the goal-review brief and the goal trace show Rowan's goals cut off mid-sentence

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_end_goals_wrap.py, changelog.d/BG1107.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Goal review for run three, 2026-10-21. The product seat noted 'the brief cuts Rowan's wrapped End goals short'. The brief's lines 27-30 end mid-sentence, and sprint.py:9997 matches a single line per item.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T07:02:00Z

## Summary

`_end_goals` (sprint.py:9988) matches each numbered line of a card's `## End Goals` section and drops its continuation lines. Rowan Achterberg's card wraps every End goal, so the goal-review brief gives the seats four half-sentences ending in a comma ('1. A push is judged against exactly the commit pushed in about the ten minutes a gate host takes,'). Every reader of `persona_cards` sees the same cut text: the brief, the goal trace and the product seat's lens (BG1066). A seat judging a goal against half of it does so silently (LL0009).

## Steps to Reproduce

Run `sprint.py goal-review brief --seat qa --goal <any> --brief-worklist <file>` in this repository: the four Rowan Achterberg End goals end mid-sentence, while his card (sdlc-studio/personas/rowan-achterberg-skill-maintainer.md) continues each on the next line.

## Proposed Fix

Join a numbered item's continuation lines (indented, or not starting a new number, a heading or a blank line) into its text before returning it. A test should take a card whose End goals wrap.

## Acceptance Criteria

- [ ] **AC1** A card whose numbered End goals wrap across lines yields each goal's whole text from `_end_goals`, and the goal-review brief prints it whole
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_end_goals_wrap.py

## Impact

The seats and the trace read a Primary's End goals truncated, and can approve or reject a goal against a clause they never saw.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
