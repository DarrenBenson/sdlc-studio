# CR-0649: Extend the doc_freshness census from the TRD to the PRD and TSD, so a pinned count or stale baseline in either is caught when it drifts

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py, changelog.d/CR0649.md
> **Evidence:** RV0028 findings PRD-12, TSD-3, TSD-4; doc_freshness.py:144 census reads only sdlc-studio/trd.md.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:50:04Z

## Summary

`doc_freshness.py` checks LATEST.md and the TRD's counts and version, which is why the TRD's bands still hold; the PRD and TSD are checked by nothing, and RV0028 found both carrying pinned counts (the PRD's 52 references, 41 help files, 58 scripts and 2151 tests; the TSD's eight-check lint chain and 82% coverage) months stale. LL0027: gate the rule in the command people run, rather than finding the drift at the next unified review.

## Impact

PRD and TSD drift accumulates silently between unified reviews, the last of which was three months before this one.

## Acceptance Criteria

- [ ] `doc_freshness` reports a count or version stated in the PRD or TSD that no longer matches the tree, as it does for the TRD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
