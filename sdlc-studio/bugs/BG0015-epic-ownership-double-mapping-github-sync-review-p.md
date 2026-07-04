# BG-0015: Epic ownership double-mapping: github_sync, review_prep and next_id are each claimed by two epics

> **Status:** Closed
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

EP0008 independently claims github_sync (also EP0006's breakdown), review_prep (PRD-mapped to EP0005, owned by US0003), and next_id (US0005 is in EP0005 but the PRD/EP0008 own next_id), inflating story counts and producing duplicate/ambiguous story ownership; EP0005's 'All four scripts' AC also excludes its own fifth story (next_id).

## Problem

github_sync is mapped to EP0008 (prd.md:154) and listed in EP0008's breakdown, yet EP0006-change-management.md:59 also lists 'US: GitHub Issue sync for CR/story/epic'. review_prep is mapped to EP0005 (prd.md:149, owned by US0003) yet EP0008-tooling-scripts.md:27,65 also claims it ('US: Review prep data helper'). next_id (mapped to EP0008 per prd.md:155) appears as US0005 inside EP0005, whose Scope names only four scripts and whose epic AC 'All four scripts ... unit-tested' (EP0005:45) therefore excludes US0005 even though Estimated Story Count is 5. Each duplication inflates an epic's count by one and leaves a capability double-owned.

## Proposed Fix

Pick one owner per script matching the PRD. Remove 'US: GitHub Issue sync' from EP0006's breakdown (4->3 stories), keep EP0006's epic AC reference as a cross-epic dependency note. Remove review_prep from EP0008 scope and drop 'Review prep data helper' (EP0008 6->5). For next_id, move US0005 to EP0008 (preferred): drop it from EP0005's breakdown, set EP0005 Estimated Story Count back to 4 so the 'All four scripts' AC is self-consistent; alternatively keep US0005 in EP0005 and change the AC to 'All five scripts' plus add next_id.py to scope.

## Evidence

prd.md:154 maps GitHub sync to EP0008 vs EP0006-change-management.md:59 'US: GitHub Issue sync for CR/story/epic'; plus prd.md:149 (review->EP0005) vs EP0008-tooling-scripts.md:65, and EP0005-quality-drift.md:45 'All four scripts' vs :57 'Estimated Story Count: 5'

## Impact

Duplicate story ownership inflates EP0006/EP0008 counts and double-counts capabilities; reconcile/validate cross-checking story counts against scope will flag drift; an agentic 'epic implement' run would generate the same story twice or pick a parent at random; and EP0005 can never be coherently marked Done because its AC does not cover one of its own stories.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: traceability) |
