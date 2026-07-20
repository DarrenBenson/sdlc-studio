# BG0220: verify_ac writes its report and history relative to the current directory

> **Status:** Fixed
> **Severity:** Medium
> **Verification depth:** functional (8 tests, every one run from a cwd that is NOT the root; 8 mutants each confirmed applied by md5 and all killed - including the original defect re-introduced both ways; one mutant initially SURVIVED, exposing that nothing pinned a named root being honoured rather than re-pointed by discovery, and a test was added for it)
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Same class as BG0219, in a different script. `verify_ac` writes verify-report.json, verify-report.dry-run.json and verify-history.jsonl under a path resolved from the current directory rather than from the project root it was given, so running it from anywhere but the root creates a stray sdlc-studio/.local tree beside the cwd. Observed repeatedly: a scripts/sdlc-studio/.local directory keeps reappearing inside the skill source whenever `verify_ac` runs with that as the cwd, and it survives cleanup because it is regenerated. It then gets forward-ported into the installed skill copy, where the porting tool cannot delete it - its only contents are under .local, which the port deliberately preserves, so the directory shell is stranded there permanently.

## Steps to Reproduce

1. From a directory that is not the project root, run `verify_ac.py` run --story <id> against a project. 2. A sdlc-studio/.local tree appears beside the CURRENT directory rather than under the project root. 3. Delete it and run the command again from that directory: it returns.

## Proposed Fix

Resolve the report and history paths against the project root, the way BG0219 resolved the lessons paths - reuse a single root-aware helper rather than adding a second one. Add a test that runs the verifier from a cwd that is not the root and asserts nothing is written beside the cwd. Worth auditing every script that accepts --root for the same pattern: BG0219 and this one are the same defect found twice, so a third is likely.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
