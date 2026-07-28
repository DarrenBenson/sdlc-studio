# BG0359: Nothing keeps the RFC index's spawned-work column true once it has been backfilled

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, sdlc-studio/rfcs/_index.md, .claude/skills/sdlc-studio/templates/indexes/rfc.md
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery, split from BG0319); agent; skill v5.0.0

## Summary

BG0319's backfill corrected 33 false cells in the RFC index by deriving them from the RFC files. Nothing keeps them true: reconcile does not check the column, so the next decomposition leaves a stale cell exactly as before. The column header also still reads Spawned CRs while most cells now hold epic ids, and the header is fixed by the shipped index template and asserted by three test files, so renaming it is a cross-file change rather than an edit.

## Steps to Reproduce

Refine an RFC into an epic. Read the RFC index: its spawned-work cell for that RFC is unchanged. Run reconcile detect: it reports no drift, because the column is outside every check it performs.

## Proposed Fix

Derive the column in reconcile from the RFC files, preserving a cell the derivation cannot answer for rather than emptying it. Rename the header to match what the cells hold, which requires the shipped template and the three asserting test files to move together.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery, split from BG0319) | Filed |
