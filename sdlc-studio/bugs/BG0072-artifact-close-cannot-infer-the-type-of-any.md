# BG0072: artifact close cannot infer the type of any v3 ULID id

> **Status:** Closed
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (red-then-green unit tests for v2/dashed/ULID forms; live CLI dry-run close of a freshly minted ULID resolves type=bug)

## Summary

rc-verdict: BLOCKS v4.0 tag. artifact.py:448-451 infers type by collecting every alphabetic character of the id (BG-01JQK3F8 -> 'BGJQKF'), so _PREFIX_TYPE lookup returns None and close raises 'cannot infer type' for every artefact minted under schema v3 - the era v4.0 makes the default for new projects. The documented close cascade (agent-instructions.md mandates artifact.py close) is broken on day one of a v3 project; transition.py set still works via find_by_id, so the gap is close-specific. Found by RV0007.

## Steps to Reproduce

On a schema_version: 3 workspace: artifact.py new --type bug ... (mints e.g. BG-01KX4FAK); artifact.py close BG-01KX4FAK -> ValueError: cannot infer type.

## Proposed Fix

Infer the type from the id's leading prefix before the first dash (or delegate to sdlc_md.find_by_id).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
