# BG0168: PRD says extracted specs are tracked 'Ready (awaiting test validation)' and the epic index's note says 'all epics are Ready' directly above 48 Done rows

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/epics/_index.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

prd.md:6 and its Complete-vs-Ready note (153-159) still describe the retired Ready-tracking model, while epics/_index.md shows Done 48/Ready 0 and stories 175/176 Done. The panel established the Done transitions were legitimate (commit 841471e, verified close-out 2026-07-09), so this is doc staleness, not a validation bypass - but the self-contradiction is concrete: the epic index's generate-mode note ('all epics are Ready... not Done. The features themselves exist and ship at v2.0.0') sits directly above a table of 48 Done rows, its Last Updated reads 2026-06-20 against rows dated 2026-07-16, and prd.md's Untested Areas simultaneously admits the markdown behaviours have no executable tests. reconcile cannot auto-fix prose. Panel downgraded severity to low doc-staleness; survives 3x.

## Steps to Reproduce

Read prd.md:6 and lines 153-159, then epics/_index.md summary (Done 48, Ready 0), the generate-mode note directly below, and the Last Updated header vs the row dates.

## Proposed Fix

Rewrite the PRD status-model note and header to record the verified 2026-07-09 close-out (Ready->Done via the test-suite verification in 841471e); delete or historicise the epic index's stale generate-mode note; refresh the index's Last Updated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
