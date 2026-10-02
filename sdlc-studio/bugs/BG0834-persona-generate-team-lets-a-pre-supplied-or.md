# BG0834: persona generate --team lets a pre-supplied or headless default stand as an answer, so its report claims questions were asked and accepted when none was

> **Status:** Fixed
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: reference-persona-generate.md Step 1 marks discoveries only `inferred` or `unknown`, and Step 2 ends `Headless runs take the defaults and keep the provisional stamp` with nothing telling the report a default is not an answer (eval 07 rc.1 is the behavioural evidence; an eval re-run is not repeated here). Narrowed to the instruction: the card-stamp list (a persona_gen.py change) is dropped as new record machinery; resized 2 -> 1
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-persona-generate.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_persona_generate_answers.py, changelog.d/BG0834.md
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

One instruction, no new record: Step 1's discoveries table gains a third mark, `defaulted`, which a headless run puts on every Step 2 item it took without asking, and the Step 2 text says the report names a defaulted item as a default, never as an answer the user gave.

## Acceptance Criteria

- [ ] **AC1** Given the shipped `reference-persona-generate.md`, when Step 1 and Step 2 are read, then the discoveries table admits `defaulted` beside `inferred` and `unknown`, and Step 2 tells a headless run to mark each item it did not ask `defaulted` and never to report a default as answered or accepted. Fails on: HEAD, whose table admits only `inferred` and `unknown` and whose headless line says only `take the defaults`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_persona_generate_answers.py::PersonaGenerateAnswersTests::test_defaults_are_recorded_as_defaults
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
