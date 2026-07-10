# BG0085: sprint plan origin-drift preflight silently dies for --order manual and empty batches; --strict cannot refuse

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (red-then-green end-to-end: behind-origin clone + --order manual --strict exits 2 with the behind warning; empty batch likewise; suite 1491 green)

## Summary

rc-verdict: post-v4 (priority/wsjf defaults still get the check). build_plan always emits waves=None unless order is priority/wsjf with a non-empty batch (sprint.py:386-388,:408), so data.get('waves', []) at :592 returns None, the iteration raises TypeError, and the blanket 'except Exception: pass' (:598-599) swallows it before the behind-origin warning is computed - the documented --strict refusal (help text :659-660) never fires on those paths. Adversarially verified on a real behind-origin clone (RV0007): --order priority --strict exits 2 with the drift warning; --order manual --strict on the SAME checkout is silent, exit 0. Masks the AGENTS.md 'fetch before trusting local state' safety doctrine.

## Steps to Reproduce

Clone 1 commit behind its origin; sprint.py plan --order manual --strict -> exit 0, no warning; --order priority --strict -> origin-drift refusal, exit 2.

## Proposed Fix

Use (data.get('waves') or []) and narrow the except to the specific expected errors.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
