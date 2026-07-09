# CR-0201: Provenance-tag lint guard misses US-form and non-leading ids

> **Status:** Complete
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

tools/lint-style.sh flags internal provenance tags with a regex anchored to '(' immediately followed by CR|BG|RFC + 4 digits. It misses US-form ids and ids not directly after the paren (e.g. '(US0101/CR0186)' where US leads and CR sits after a slash). An independent critic caught such a tag reaching a shipped scripts/ comment during US0101 that the guard passed clean. Widen the pattern to cover US and to match a provenance id anywhere in a parenthetical, add a unit test, and audit shipped files for tags the old pattern let through (e.g. verify_ac.py '(US0001 was 0/7)').

## Acceptance Criteria

- [ ] The guard flags '(US0101/CR0186)' in a shipped scripts/ file
- [ ] The guard flags a provenance id not immediately after '(' (e.g. '(see CR0186)')
- [ ] A unit test locks both cases and a legitimate non-provenance parenthetical still passes
- [ ] Existing shipped files are audited and any leaked tag removed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
