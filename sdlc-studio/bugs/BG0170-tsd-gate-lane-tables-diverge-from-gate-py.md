# BG0170: TSD gate lane tables diverge from gate.py: doc-freshness and hook-enabled marked Blocking=Yes (both hard-coded advisory), and the shipped close-owed and review-legs lanes are missing entirely

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Two table defects, one fix. (1) tsd.md:368/371 mark doc-freshness and hook-enabled as Blocking Yes; gate.py hard-codes both to blocking: False (with the literal '# advisory: never blocks' comment) - and a blocking hook-enabled lane would turn every CI run red since lint.yml runs gate.py on a hookless fresh clone. One panel vote refuted as doc-drift-nit (advisory was the delivered CR0073/US0113 design), which supports fixing the table, not the code. (2) The lane table (14 lanes) and bound-lane table (five flags) omit the close-owed lane (--require-close, RFC0042's machine half) and the review-legs lane that --release binds (the BG0110 fix), so the release gate's document-leg check is undocumented - despite tsd.md:17's claim to cover unreleased main. Five of six panel votes not-refuted.

## Steps to Reproduce

Compare tsd.md:359-383 with gate.py: `_doc_freshness` and `_hook_enabled` return blocking: False on every path; the bound registry adds close-owed under --require-close (gate.py:628-629) and review-legs under --release (gate.py:636-638), neither of which appears anywhere in tsd.md.

## Proposed Fix

Mark doc-freshness and hook-enabled as advisory (Blocking No) in the lane table; add rows for close-owed (--require-close) and review-legs; describe --release's document-leg half alongside its verify half.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
