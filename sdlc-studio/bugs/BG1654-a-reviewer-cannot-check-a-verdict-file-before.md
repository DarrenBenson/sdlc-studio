# BG1654: A reviewer cannot check a verdict file before hand-back: critic.py record refuses an odd backtick count only when the operator records it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:35:27Z

## Summary

In run twenty (RUN-01M7VNR0), critic.py record refused US1039's engineering verdict because one finding held an odd number of backticks (critic.py:374-392). critic.py has no dry-run or verdict check a reviewer can run on its own file, so the refusal surfaced after hand-back and cost a resumed reviewer round. The rule was right; only its timing was wrong.

## Steps to Reproduce

Write a verdict whose ISSUES field holds one unclosed backtick span and hand it back; critic.py record --from-verdict refuses it. Run critic.py record --help: no --dry-run or check subcommand exists.

## Proposed Fix

Add critic.py record --dry-run (or a verdict check subcommand) running every value check record runs, and have the reviewer contract run it before hand-back.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run twenty (RUN-01M7VNR0), critic.py record refused US1039's engineering verdict because one finding held an odd number of backticks (critic.py:374-392).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write a verdict whose ISSUES field holds one unclosed backtick span and hand it back; critic.py record --from-verdict refuses it.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add critic.py record --dry-run (or a verdict check subcommand) running every value check record runs, and have the reviewer contract run it before hand-back.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
