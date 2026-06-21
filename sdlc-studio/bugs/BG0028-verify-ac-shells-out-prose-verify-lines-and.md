# BG0028: verify_ac shells out prose Verify lines and times out reporting failed not manual

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

verify_ac routed an unrecognised Verify expression to a shell (the documented fallback). A prose/manual line (e.g. `Verify: manual against a live agent`) was shelled out, hung/timed out, and was reported as **failed** rather than manual/unverified - turning a human-checked AC into a false failure.

## Steps to Reproduce

A story whose Verify line is prose/manual (e.g. "manual confirm X", or "manual + pnpm test"):
`reconcile --verify` / `verify_ac` shells it, times out (exit 124), counts it failed.

## Proposed Fix

verify_story now counts a Verify line led by `manual`/`manually` as MANUAL (never executed), like an AC with no verifier. Real commands (`pnpm test`, `shell ...`, pytest...) are unaffected. Documented `Verify: manual <description>` in reference-verify.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
