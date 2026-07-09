# BG0088: --format json suppresses failure exit codes on reconcile apply and verify_ac report; reconcile fields is drift-blind in both formats

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. The same command signals failure in text mode and success in JSON mode - and JSON callers are the programmatic ones that only read exit codes. reconcile.py cmd_apply json branch (:1133-1140) returns 0 unconditionally while text returns 1 on unapplied (:1175); verify_ac.py cmd_report json (:949-951) returns 0 before tallying while text returns 1 on failures (:972). Correction from adversarial verification (RV0007): cmd_fields (:1113-1123) returns 0 in BOTH formats even with drift, unlike cmd_detect which exits 1 on drift regardless of format (:593) - the family contract exists and these three verbs break it.

## Steps to Reproduce

Workspace with drift: reconcile.py apply --format json over a refused fix -> exit 0 (text path -> 1); verify_ac.py report --format json over a failing report -> exit 0.

## Proposed Fix

Compute the exit code before the format branch in all three verbs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
