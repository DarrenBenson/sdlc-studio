# BG0051: verify_ac back-annotation inserts Verified: lines out of canonical order

> **Status:** Closed
> **Verification depth:** functional (regression: 3-AC multi-insert canonical order; live: US0051-54 repaired and re-verified 0 misplaced)
> **Severity:** low
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

verify_ac run's write-back places the '- **Verified:**' line mid-AC-block or before the Verify line it belongs under. Live evidence in the workspace right now: US0051 AC3/AC4, US0052 AC2-AC4, US0053 AC2/AC3, US0054 AC2/AC3 all read Given/When/Verified/Then/Verify or similar after the 2026-07-C close ran the verifier. Every annotation is truthful - the defect is placement: the canonical bullet order (Given/When/Then/Verify/Verified) is the tool's own documented rule, and the insert_after anchor appears to bind to the last bullet seen rather than the Verify line when the Verify line arrives later in the block or the block's bullets continue past it.

## Steps to Reproduce

1. Author an AC whose Verify line is not the final bullet (or run verify_ac over a story where Then follows When after a blank-ordered block). 2. Run verify_ac run --id <story>. 3. The Verified line lands mid-block (see US0051-US0054 in this workspace for live instances).

## Proposed Fix

insert_after must always resolve to the Verify line's index when one exists in the block, re-evaluated at write time (not first-seen); add a regression test whose AC carries bullets after the Verify line and one whose Verify precedes Then, asserting canonical order post-annotation. Consider a one-off reconcile pass to reorder the existing mis-placed lines.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
| 2026-07-04 | operator | Review: CONFIRMED with live evidence (US0051 AC2/AC3/AC4 show three distinct wrong positions; AC1 with Verify-last is correct - matches the insert_after root cause). Low, well-diagnosed; the one-off reorder pass endorsed |
| 2026-07-04 | claude | Fixed - root cause REFINED from the filed hypothesis: insert_after resolves correctly at parse; the drift came from applying multiple insertions top-down from ONE parse, shifting every later block's cached indices by one per prior insert (matches the 1/2/3-early pattern exactly). Write-backs now apply bottom-up. US0051-54 repaired by strip + regenerate; 0 misplaced. Regression seen RED first |
