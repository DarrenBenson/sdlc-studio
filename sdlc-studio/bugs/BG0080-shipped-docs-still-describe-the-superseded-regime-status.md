# BG0080: shipped docs still describe the superseded regime: status/hint version tables have no schema-3 row and SECURITY.md supports only 1.x

> **Status:** Closed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (grep-verified: schema-3 rows present in both help tables, no superseded copy remains anywhere in the payload; SECURITY.md restated; lint green)

## Summary

rc-verdict: BLOCKS v4.0 tag. The majors docs gate (release-gate.md section 8: 'no doc still describes the superseded regime as current') is falsified twice. (1) help/status.md:44-65 and help/hint.md:40-60 pre-flight tables cover only '.version exists, schema_version: 2 -> Proceed' and 'schema_version < 2 -> prompt (v1 to v2 wording)' - a fresh v4 project (schema_version: 3, the new default) has no row, so first-run guidance on the default era is wrong. (2) SECURITY.md:20-26 supported-versions table lists 1.1.x/1.0.x/<1.0 while the release is 4.0.0-rc.1 - the public security policy names no version actually in use. Found by RV0007.

## Steps to Reproduce

grep -c 'schema_version: 3' help/status.md help/hint.md -> 0 in both; sed -n '20,26p' SECURITY.md -> 1.x-only table.

## Proposed Fix

Add 'schema_version: 3 -> Proceed' rows with era-neutral prompt wording to both help tables; restate SECURITY.md support in terms of the current major.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
