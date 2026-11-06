# BG1259: The forge's Lint job has been red on main since 8a00d2cc because bandit reads the OpenCode meter's placeholder join as SQL injection

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py
> **Evidence:** GitHub Actions Lint run 42263229398 on fd1c2b5b, read 2026-11-06 before run eight's mid-run push
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:28:09Z

## Summary

GitHub's push-triggered Lint run fails its `Python security scan (bandit)` step on 8a00d2cc, fb93b20d and fd1c2b5b (run 42263229398): B608 at `.claude/skills/sdlc-studio/scripts/lib/meter_opencode.py:233`, the `store()` probe's `SELECT 1 FROM session WHERE directory IN (?, ...)`. The f-string interpolates only `?` placeholders and the directories are bound parameters, so it is a false positive, but main is red on the forge and the pre-push check never read a finished red, because each push left before the previous 45-minute run concluded.

## Steps to Reproduce

Run `bandit -r .claude/skills/sdlc-studio/scripts -ll -x '*/tests/*' -q` at fd1c2b5b.

## Proposed Fix

Mark the line `# nosec B608` with the reason (placeholders only, values bound), as the repository's other justified suppressions are.

## Acceptance Criteria

- [ ] **AC1** The CI's bandit scan over the shipped scripts reports no Medium or High issue.
  - **Verify:** shell uvx --quiet bandit==1.9.4 -r .claude/skills/sdlc-studio/scripts -ll -x '*/tests/*' -q
  - **Verified:** yes (2026-11-06)
- [ ] **AC2** The OpenCode store probe still opens read-only and binds its directories as parameters.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored for run eight |
| 2026-11-06 | Claude Opus 5.5 | Affects widened for the round-1 repair: the store probe's bound parameters need a test of their own once the nosec hides the line from bandit |
