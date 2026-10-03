# BG0933: Three texts still say what the code does not: the empty-seats refusal, BG0930's docstring and help/gate.md's lane count

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_texts_true.py, changelog.d/BG0933.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:08:03Z

## Summary

A goal-review fields file with an empty seats list is refused naming the --seat flag rather than the 'seats' key; transition.py's appetite docstring (~1418) says a run whose outcome is no longer running is sealed, but a run with no outcome still warns; help/gate.md says the push runs 'the full suite plus the three lanes below' and describes two. Found by the v6.1 reviews and the lane 2 build (D0326).

## Steps to Reproduce

Read each text beside the behaviour it describes.

## Proposed Fix

Make each text say what the code does. No behaviour change.

## Acceptance Criteria

- [ ] **AC1** Given a goal-review fields file whose seats list is empty, when record refuses it, then the message names the 'seats' key, and help/gate.md's lane count equals the lanes it describes. Fails on: the current refusal naming --seat and the 'three lanes' sentence
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_texts_true.py::V61TextsTrueTests::test_each_text_says_what_the_code_does

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
