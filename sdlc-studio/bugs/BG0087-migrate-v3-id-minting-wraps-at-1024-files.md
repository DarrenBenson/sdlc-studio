# BG0087: migrate_v3 id minting wraps at 1024 files (silent rename overwrite) and pollutes slugs of dash-named files

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (operator-run, rare; the data loss is silent when it hits). (a) `suffix = ts[:6] + _b32(i, 2)` (migrate_v3.py:97-98): `_b32(i, 2)` keeps only the low 10 bits of the file counter - verified `_b32(1024,2) == _b32(0,2) == '00'` - so two files in the same ~17-minute ts[:6] bucket whose indices differ by 1024 mint the SAME id; there is no uniqueness check over the minted map, and old_path.rename(new_path) then silently overwrites the first file (data loss). (b) `slug = p.stem.split('-', 1)[1]` (:145 area) turns CR-0001-add-auth.md into CR-<ulid>-0001-add-auth.md, embedding the stale v2 number in every migrated dashed filename. Found by RV0007.

## Steps to Reproduce

(a) code-verified: python3 -c '`sdlc_md._b32(0,2) == sdlc_md._b32(1024,2)`' -> True; a >1024-artefact project migrated in one run risks same-bucket collisions. (b) any dash-named v2 file exhibits the slug pollution on plan output.

## Proposed Fix

Assert minted ids unique before any write (fail loud); compute slug as `p.stem[len(rec):].lstrip('-')`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
