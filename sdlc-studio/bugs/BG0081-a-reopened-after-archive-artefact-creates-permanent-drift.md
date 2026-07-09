# BG0081: a reopened-after-archive artefact creates permanent drift: archive rows shadow live index rows

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4. parse_index merges archive sub-index rows with 'if v[1] != "Unknown" or k not in result["rows"]' (reconcile.py:313), so a known-status archive row unconditionally overwrites the live row. A story archived at Done then legitimately reopened (transition.py:362 treats reopen as a valid cycle) shows status-mismatch drift forever: apply claims 'set story US0001: Done -> In Progress / changed 1 row(s)' on EVERY run while rewriting the live row to the value it already holds, a spurious count-mismatch fires too, and there is no unarchive tooling. Breaks the drift-0 gate and sprint plan --strict permanently. Reproduced and verified adversarially (RV0007).

## Steps to Reproduce

Archive a Done story (row lands in stories/archive/<release>.md); reopen it (file + live row In Progress); reconcile detect -> status-mismatch + count-mismatch; apply -> claims a change; detect again -> same drift, exit 1.

## Proposed Fix

Live rows win: merge an archive row only when its id is absent from the live table (k not in result['rows']).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
