# BG0094: plan_review resolves stories with a case-sensitive US*.md glob: lowercase stories get a null fingerprint and an unclearable false block

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (red-then-green: lowercase story resolves via find_by_id; record on a miss raises; pathless gate not-found is non-ok; suite 1494 green)

## Summary

rc-verdict: post-v4 (needs the tolerated lowercase naming convention). _resolve_story re-implements artefact lookup with d.glob('US*.md') plus a case-sensitive compare (plan_review.py:225-226) instead of sdlc_md.find_by_id (lib :767, the CR0187 consolidation), so us0101.md never resolves. Verified adversarially (RV0007): record_review then stamps ac-hash 000000000000 (:169-171), and the later gate with the real path returns ok=False despite the recorded APPROVE - an unclearable false block (:186-189). The not-found fail-open (:198-200, ok:True 'gate skipped') is reachable only from direct gate() calls without a path since transition always passes one (:306) - net effect for lowercase repos is fail-closed availability damage, plus a vacuous-PASS lane for pathless callers.

## Steps to Reproduce

Story file us0101-x.md; plan_review.py record --story US0101 ... -> verdict stamped with fingerprint 000000000000; plan_review gate on the real path -> blocked despite APPROVE.

## Proposed Fix

Replace _resolve_story with sdlc_md.find_by_id and make the not-found gate result loud (warn or non-ok).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
