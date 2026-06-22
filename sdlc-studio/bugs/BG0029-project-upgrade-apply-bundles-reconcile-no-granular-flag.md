# BG0029: project upgrade apply bundles reconcile no granular flag can corrupt indexes

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** High

## Summary

`project_upgrade.apply()` ran `reconcile.apply_type` over every type unconditionally - so `project upgrade --apply` rewrote indexes. On a project with reconcile false-positives (multi-schema/inline rows) that corrupts them. agent-bridge had to bypass the whole script.

## Steps to Reproduce

`project upgrade --apply` on a project with index quirks -> reconcile rewrites/clobbers index rows as part of the 'upgrade'.

## Proposed Fix

apply() does the safe deterministic set only (config + .version); reconcile is opt-in via `--with-reconcile` (default off). The audit reports index-drift as a manual 'review with reconcile' item, not auto. Verified read-only on agent-bridge: audit AUTO=[], index-drift now manual.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
