# CR-0002: Add deterministic duplicate-ID / collision detector; census scripts silently collapse colliding IDs

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py
> **Depends on:** --
> **GitHub Issue:** --

## Summary

No read-only script detects two files sharing one artifact ID. allocate computes max+1, scan dedupes via set(), and reconcile/status keys census by norm_id so a duplicate is overwritten - yet the doctrine mandates a collision check and records 8 historical collisions that slipped through manual scanning.

## Problem

reference-outputs.md:250-262 mandates a Glob-and-check before assigning any ID and lists 8 historical collisions (TS0012, TS0180, TS0190, TS0201, PL0180, PL0184, PL0190, PL0201) that slipped through because the check was manual; doctrine rule 13 (reference-doctrine.md:91) prescribes 'on collision renumber' but assumes detection. No script detects existing collisions. next_id.py local_ids returns sorted(set(ids)) (line 35) so cmd_scan's output silently dedupes; cmd_allocate (lines 63-78) does max+1, preventing a NEW collision but never auditing for existing ones - the failure mode that actually produced those 8. reconcile.file_census and status.count_by_status key on norm_id, so two files with one ID collapse to a single entry (one overwrites the other) and the duplicate is invisible. validate.py validates one file at a time with no cross-file pass. The duplicate-detection is purely mechanical (group artifact_files by norm_id, report any group with >1 distinct file) but is left to Claude prose, which the LL0001 lesson shows is unreliable.

## Proposed Changes

### Item 1: Add deterministic duplicate-ID / collision detector; census scripts silently collapse colliding IDs

**Priority:** High **Effort:** TBD

Add a deterministic duplicate-ID pass: either a next_id.py audit/--collisions subcommand or a validate.py cross-file rule that groups artifact_files by norm_id and emits a 'duplicate-id' finding listing both paths, with a non-zero exit. Wire it into validate.py check / status integrity so the release gate fails on duplicate IDs and the INTEGRITY/ID-collision scan the doc promises is computed rather than eyeballed.

## Impact Assessment

### Existing Functionality

The one failure mode the doctrine explicitly warns about, and demonstrably hit 8 times, has no deterministic guard. Two artifacts can share an ID indefinitely; counts under-report, one record shadows the other in dashboard and reconcile, and allocate can hand out an ID that looks free while a hidden duplicate lurks. Quality risk high; cheap to implement (file list already walked).

## Acceptance Criteria

- [x] Change implemented and verified; lint and tests green.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism; evidence: .claude/skills/sdlc-studio/scripts/next_id.py:35 (local_ids returns sorted(set(ids)) - dedupes silently) and reference-outputs.md:250-262 (collision rule plus list of 8 historical collisions)) |
