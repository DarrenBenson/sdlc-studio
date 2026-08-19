# BG0578: test-file attribution is decided by name frequency, so mentioning one more module silently changes a file's owner

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/test_census.py, tools/tests/test_test_census.py
> **Evidence:** RUN-01KZQ03V, 2026-08-14, while delivering BG0556 - the full suite went red on an attribution change caused by adding an inventory of script names to a test module.
> **Created:** 2026-08-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-14T01:30:38Z

## Summary

`test_census.attribute` places a test file by counting how often it names each sibling module and taking the most-mentioned. That makes the owner a property of the prose rather than of the subject. `test_cli_grammar.py` was attributed to `transition.py` on a count; BG0556 added an inventory naming 21 scripts, `sprint.py` among them, the count tied, and the file became unattributed - tripping a ratchet that is documented as never being raised. Nothing about what the file tests changed.

## Steps to Reproduce

1. `python3 -c "import sys; sys.path.insert(0,'tools'); import test_census as tc, pathlib; print(tc.attribute(pathlib.Path('.').resolve(), '.claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py'))"` 2. Add one more mention of any sibling module to that file. 3. Re-run: the owner changes, or the file becomes unattributed on a tie. Observed 2026-08-14: transition.py -> unattributed, on a diff that added no coverage of transition.py at all.

## Proposed Fix

Attribution should prefer a DECLARED owner over a counted one: a unit's `Affects` already names the file, and a module-level marker in the test would state its subject outright. Counting stays as the fallback for files that declare nothing. A tie should also report the candidates rather than dropping the file, so the ratchet moves on a real coverage change and not on prose.

## Acceptance Criteria

- [ ] **AC1** Given a test file carrying a module-level subject marker, when `test_census.attribute` places it, then it returns the declared subject regardless of which sibling module the file names most often
- [ ] **AC2** Given a test file with no marker whose unit declares it in `Affects` alongside exactly one script, when attribute places it, then it returns that script - the declared owner is read from the artefact before any counting happens
- [ ] **AC3** Given a test file with neither a marker nor a declaring unit, and one sibling module named more often than any other, when attribute places it, then it returns that module - counting survives as the fallback, not as the rule
- [ ] **AC4** Given a test file whose two most-mentioned siblings tie, when attribute places it, then it names the tied candidates in its result rather than reporting the file as unattributed
- [ ] **AC5** Given `test_cli_grammar.py` as it stands on disk, when a mention of any sibling module is added to it and attribution is re-run, then the owner is unchanged - the exact edit that moved it to unattributed on 2026-08-14
- [ ] **AC6** Given the attribution ratchet driven through its shipped entry point over the real corpus, when a prose-only edit is made to a test file, then the ratchet count does not move

## Impact

The ratchet is the guard on test attribution and it fires on edits that change no coverage, which trains raising the baseline - the one action its own comment forbids. A file that legitimately has no owner (a cross-cutting family sweep) is indistinguishable from one that lost its owner to a wording change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-14 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Groomed: acceptance criteria authored so the unit is plannable |
