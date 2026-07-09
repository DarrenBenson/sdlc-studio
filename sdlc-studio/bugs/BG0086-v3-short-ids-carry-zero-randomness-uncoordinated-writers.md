# BG0086: v3 short ids carry zero randomness: uncoordinated writers in the same ~1s window mint identical ids

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (single-writer convention masks it today; multi-agent waves and multi-clone work are the exposure). short_ulid (sdlc_md.py:800-813) returns the first 8 chars of new_ulid() - purely the base32 timestamp field with the low ~10 bits truncated (~1.024s buckets); ALL random chars are cut. Adversarially verified (RV0007): 50 rapid calls produced 1 distinct value. The 16-attempt retry (artifact.py:63-69) re-mints the identical value inside a bucket, degrading to the 12-char fallback whose extension is only 2 random chars (10 bits) and is NOT collision-checked (:68); same pattern in new_batch (:397-404). The per-clone allocation lock (a no-op on Windows, sdlc_md.py:637-650) cannot serialise two clones, contradicting RFC0024's 'collision-free across concurrent writers without coordination' exactly where v4 needs it.

## Steps to Reproduce

python3 -c loop calling sdlc_md.short_ulid() 50 times in-process -> one distinct value; two clones filing in the same second mint the same id.

## Proposed Fix

Include real random bits in the short id (e.g. 6 timestamp chars + 2 random) and collision-check the 12-char fallback.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
