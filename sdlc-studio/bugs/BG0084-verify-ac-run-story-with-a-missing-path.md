# BG0084: verify_ac run --story with a missing path exits 0 (false success)

> **Status:** Fixed
> **Verification depth:** functional (red-then-green: missing --story path exits 2 not 0)
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. A missing --story path prints 'skip: ... not found' to stderr and returns 0 (verify_ac.py:708-711, 744), writing an empty-stories report when none existed (merge=True preserves an existing one); the sibling --id path returns 2 for an unknown id (:689-690). A typo'd path reads as all-green to any gate or orchestrator checking the exit code. Reproduced and adversarially verified (RV0007).

## Steps to Reproduce

verify_ac.py run --story /nonexistent/US9999.md -> exit 0; verify_ac.py run --id US9999 -> exit 2.

## Proposed Fix

Return 2 when an explicitly named story path does not exist.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
