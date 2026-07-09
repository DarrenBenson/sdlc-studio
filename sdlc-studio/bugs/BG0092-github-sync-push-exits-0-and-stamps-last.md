# BG0092: github_sync push exits 0 and stamps last_push even when every gh create/edit failed

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. cmd_push stamps state['last_push'] unconditionally after the loop (github_sync.py:502-505) and returns '1 if blocked else 0' (:508) where blocked counts only secret-scan refusals; create failures return None and continue (:441-443), edit failures just print to stderr (:489). Adversarially verified with a stub failing gh (RV0007): 'created=0 updated=0 blocked=0', exit 0, state stamped with a fresh last_push. Mappings are not updated on failure so a retry re-attempts (no permanent loss) - the harm is the lying exit code plus a freshened last_push misleading anything gating on push success/recency. BG0064 fixed exactly this on the pull side (:556-560); push was not given the same treatment.

## Steps to Reproduce

Put a stub 'gh' that exits 1 on PATH; github_sync.py push -> created=0, exit 0; cat .local sync state -> fresh last_push.

## Proposed Fix

Track a failed flag as cmd_pull does; skip the last_push stamp and return non-zero on any gh failure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
