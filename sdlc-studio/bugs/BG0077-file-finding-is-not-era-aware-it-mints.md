# BG0077: file_finding is not era-aware: it mints v2 sequential ids on schema-v3 projects

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (red-then-green era tests: v3 fixture mints a ULID finding id, v2 stays sequential; full suite green)

## Summary

rc-verdict: BLOCKS v4.0 tag. file_finding.py:167 calls `_next_number` unconditionally, while artifact.py:57-71 (`_alloc_ids`) and triage_noise.py:165-177 (`_alloc_cr_id`) are era-aware. On a schema_version: 3 project the review/triage filing path mints BG0002-style sequential ids alongside ULIDs (reproduced, RV0007), reintroducing the id-race v3 exists to remove and undermining v4's headline on day one - the review protocol itself mandates filing through this tool.

## Steps to Reproduce

schema_version: 3 fixture; file_finding.py file --type bug ... -> BG0002 (sequential); artifact.py new on the same workspace -> BG-01KX4EK4 (ULID).

## Proposed Fix

Route file_finding id allocation through the shared era-aware allocator (artifact._alloc_ids or a lib equivalent).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
