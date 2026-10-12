# BG1023: verify_ac's vitest and jest verbs fold the whole tail into the -t pattern and call a bare binary, so `vitest <file> -t "name"` can never select its test

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py, .claude/skills/sdlc-studio/help/verify.md, changelog.d/BG1023.md
> **Created:** 2026-10-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-10T23:07:37Z

## Summary

`_parse_dsl` (`verify_ac.py` ~1497-1500 on the installed 6.1.x) maps `vitest <tail>` to ['vitest','run','-t', tail] and `jest <tail>` to ['jest','-t', tail]. The documented-looking form `vitest src/x.test.ts -t "name"` therefore becomes `vitest run -t 'src/x.test.ts -t "name"'`: the file argument is lost into the pattern, so nothing matches (all tests skipped - vacuous), and the binary is invoked bare, which is not on PATH in a typical Node project (npx is). A consuming project's release gate (a consuming project) found ~200 Verify lines in this form that could never pass. The working form today is `shell npx vitest run <file> -t "<escaped name>"`.

## Steps to Reproduce

Verify line `vitest src/__tests__/a.test.ts -t "some name"` in a Node project without a global vitest: `verify_ac` reports it red/vacuous although the test passes with npx vitest run.

## Proposed Fix

Parse the tail with shlex: positional args are files, -t/--testNamePattern is the name; invoke through npx (or the project's `node_modules`/.bin) when no global binary exists; escape regex metacharacters in a literal -t name (or document that -t is a regex). Add tests for the file+name form.

## Acceptance Criteria

- [ ] **AC1** `vitest <file> -t "name"` and `jest <file> -t "name"` pass the file as a positional argument and only the name to `-t`, invoking through the project's `node_modules/.bin` or npx when the bare binary is not on PATH
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py::VitestFileAndNameTests::test_file_and_name_are_separate_arguments
- [ ] **AC2** A regex metacharacter in a literal `-t` name is matched literally, or the Verify lint warns that `-t` takes a regex
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_file_and_name.py::VitestFileAndNameTests::test_a_metacharacter_in_the_name_is_literal_or_warned

## Impact

The executable AC gate silently cannot run the most natural vitest/jest Verify lines.

## Triage

- Confirmed at 0c7e4d90 by the code path: `_parse_dsl` returns `["vitest", "run", "-t", tail]` and `["jest", "-t", tail]` (verify_ac.py:1497-1499), so a file in the tail is folded into the name pattern, and the bare binary is invoked. Pre-existing.
- Severity Medium stands: the most natural Node Verify form can never pass. Private project name generalised; changelog fragment added to Affects.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-11 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed on current code; changelog fragment named for the unit; Verify on a new test module (BG0980) |
