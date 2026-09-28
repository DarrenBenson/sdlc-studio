# BG0834: persona generate --team lets a pre-supplied or headless default stand as an answer, so its report claims questions were asked and accepted when none was

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-persona-generate.md, .claude/skills/sdlc-studio/scripts/persona_gen.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_persona_generate_answers.py, changelog.d/BG0834.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_gen.py
> **Evidence:** eval 07 rc.1 and re-run grader notes (US0963); HEAD 7e53a438 reference-persona-generate.md Step 2 (~366-382)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:39Z

## Summary

reference-persona-generate.md Step 2 caps the questions and lets 'headless runs take the defaults', but nothing records, before Step 3 writes the cards, which Step 2 answers were asked, answered or defaulted. Eval 07 (rc.1): the worker's report said 'Questions (3 of the 4 allowed) ... answered' and 'You accepted it' when no question was put; in the re-run it read 'your call, the simplest option' as accepting the team and defaulted to a compliance regime (both disclosed). The provisional stamp does not say which inferences no person confirmed.

## Steps to Reproduce

Run the eval 07 scenario headless: the cards are written and the report states the questions were answered.

## Proposed Fix

Record each Step 2 item as asked-and-answered, defaulted or pre-supplied in the discoveries table before Step 3, carry the defaulted items on the cards' provisional stamp, and forbid the report from calling a default an answer.

## Acceptance Criteria

- [ ] **AC1** Given a headless run, then the discoveries table marks each Step 2 item `defaulted`, and each card's provisional stamp lists them. Fails on: HEAD, where no record distinguishes them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_persona_generate_answers.py::PersonaGenerateAnswersTests::test_defaults_are_recorded_as_defaults

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
