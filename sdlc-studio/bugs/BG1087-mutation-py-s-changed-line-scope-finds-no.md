# BG1087: mutation.py's changed-line scope finds no lines on a machine whose git config sets diff.mnemonicprefix or diff.noprefix

> **Status:** Superseded
> **Superseded by:** BG0958
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation_diff_prefix.py, changelog.d/BG1087.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** 2026-10-19, studypc2: global git config `diff.mnemonicprefix=true`; the test fails under it and passes with GIT_CONFIG_GLOBAL=/dev/null; mutation.py:240 `if line.startswith("+++ b/")`. It passed in the full suite on devserver1, whose git config has no such key.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T17:15:12Z

## Summary

`mutants_over_changed_lines` reads `git diff` output and recognises a file only by `+++ b/<path>` (mutation.py:240). git's `diff.mnemonicprefix=true` writes `c/`, `i/` or `w/` instead of `b/`, and `diff.noprefix` writes none, so on such a machine every changed line is missed and the scope is EMPTY. A gate run over an empty scope has no mutants to survive. On this workstation (global `diff.mnemonicprefix=true`) `test_mutants_are_scoped_to_the_units_changed_lines` fails with 'the changed line produced no mutant', and passes with `GIT_CONFIG_GLOBAL`=/dev/null.

## Steps to Reproduce

`git config --global diff.mnemonicprefix true`, then `pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_mutants_are_scoped_to_the_units_changed_lines` -> AssertionError: the changed line produced no mutant.

## Proposed Fix

Run the diff with fixed prefixes (`--src-prefix=a/ --dst-prefix=b/`, or `-c diff.mnemonicprefix=false -c diff.noprefix=false`) wherever a script parses `git diff` output, and add a test that sets the user's config both ways.

## Acceptance Criteria

- [ ] **AC1** Given a user git config setting diff.mnemonicprefix or diff.noprefix, when the changed-line scope is taken, then it names the same lines as under git's defaults
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation_diff_prefix.py::DiffPrefixTests::test_the_scope_ignores_the_users_diff_prefix

## Impact

A developer whose git config differs from the default gets a vacuous changed-line mutation scope, with nothing reported.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): superseded by BG0958: duplicate of BG0958, the same diff.mnemonicprefix defect; BG0958's AC3 takes this bug's approach of setting the global config inside the test |
