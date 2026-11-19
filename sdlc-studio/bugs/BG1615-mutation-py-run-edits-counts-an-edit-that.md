# BG1615: mutation.py run --edits counts an edit that does not compile as killed and exits 0, and silently ignores --format and --max-mutations

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation_runner.py, changelog.d/BG1615.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/US1200/5a0e5843e1c9-40b4aafd.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:24Z

## Summary

Non-blocking findings from the mutation runner's qa review (run eighteen). An edit that leaves the file unable to compile or import makes the tests error, which the runner counts as killed, so a broken edit reads as a caught mutant. `--format` and `--max-mutations` are accepted in the edits mode and do nothing. The symlinked-directory guard and the `--scope`-alone dispatch have no test.

## Steps to Reproduce

Write an edits list whose replacement is a syntax error, run `mutation.py run --edits <list> --scope X`: the line reads killed and the command exits 0.

## Proposed Fix

Report an edit whose target no longer compiles as invalid, not killed; refuse or honour --format and --max-mutations in the edits mode; pin the symlink guard and the scope dispatch.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from the mutation runner's qa review (run eighteen).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write an edits list whose replacement is a syntax error, run `mutation.py run --edits <list> --scope X`: the line reads killed and the command exits 0.
- [ ] **AC3** The proposed fix lands, pinned by a test: Report an edit whose target no longer compiles as invalid, not killed; refuse or honour --format and --max-mutations in the edits mode; pin the symlink guard...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
