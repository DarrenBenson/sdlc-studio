# BG-0005: PRD Performance NFR falsely claims all scripts are read-only over the workspace

> **Status:** Closed
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The Performance NFR asserts scripts are read-only over the workspace, contradicting the PRD's own Reconcile auto-fix feature and verify_ac/reconcile code that write artifact files in place.

## Problem

prd.md:233 states 'Scripts are pure stdlib and read-only over the workspace'. This is contradicted by the same PRD (line 124 'applying reconcile auto-fixes', line 175 'Auto-fixes mechanical drift') and by code: verify_ac.py rewrites the story file in place and reconcile applies bounded writes. The blanket claim is materially wrong and undermines the Security/Performance section.

## Proposed Fix

Reword prd.md:233 to scope read-only-ness correctly, e.g. 'Read-path scripts (status, repo map, next-id, review_prep) are read-only; reconcile and verify_ac perform bounded, opt-in writes (auto-fixes and Verified: back-annotation respectively).' Do not claim all scripts are read-only over the workspace.

## Evidence

prd.md:233 'Scripts are pure stdlib and read-only over the workspace' vs verify_ac.py:338 story_path.write_text(...)

## Impact

A migration team rebuilding on another harness would mis-design reconcile/verify_ac as read-only, dropping the auto-fix and AC back-annotation writes that are core to the product's value.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: prd) |
