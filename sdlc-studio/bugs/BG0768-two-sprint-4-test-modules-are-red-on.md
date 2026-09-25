# BG0768: Two Sprint 4 test modules are red on main: an unconfined git call and a gate-lane floor the deletions tripped

> **Status:** In Progress
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_no_two_role.py, tools/tests/test_lean_spec_restatements.py, changelog.d/BG0768.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T09:06:34Z

## Summary

At main 1fbacd0f: `test_gitutil`'s unconfined-git sweep flags `test_lean_no_two_role.py` (US0916), whose derived-deletion check runs git show outside the confined helper; and `test_lean_spec_restatements.py` (US0933) asserts `gate.DEFAULT_CHECKS` parses to more than 10 lanes, a floor US0910 and US0920 tripped by deleting two lanes as designed (12 to 10). The push's full suite refuses on both.

## Steps to Reproduce

python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/`test_gitutil.py` tools/tests/`test_lean_spec_restatements.py` at main: 2 failed, naming `test_lean_no_two_role` and 10 not greater than 10.

## Proposed Fix

Route `test_lean_no_two_role.py`'s git calls through tests/gitutil; lower the spec-restatements lane floor to one that only guards an empty parse, never a count EP0263 deletes by design.

## Acceptance Criteria

- [ ] **AC1** Given main after this fix, then the unconfined-git sweep passes: `test_lean_no_two_role.py` runs git only through the confined helper; raising the frozen count fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests
- [ ] **AC2** Given the gate's lanes as EP0263 leaves them, then `test_lean_spec_restatements.py` passes, its floor guarding only an empty parse, not a lane count the deletions reduce by design
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Claude Opus 5.5 | Criteria authored with Verify lines; joined the Sprint 4 batch |
