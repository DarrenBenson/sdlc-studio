# CR-0332: DoR/DoD near-miss check tags must error, not silently parse as no tag

> **Status:** Superseded
> **Superseded-by:** BG0185 (refiled as a Bug - silent control failure)
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_dor_dod.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`CHECK_TAG_RE` matches only the exact lowercase '[check: <id>]' shape, so a near-miss - '[CHECK: grooming.affects]', '[check: Vibes.Good]', or a tag with trailing junk - parses as NO tag and validate exits 0. That is the 'human intent silently unenforced' failure mode at the syntax boundary the registry was built to close. Match anything tag-shaped (case-insensitive '[check...]' with any bracket body) and error on whatever is not exactly a registered id. Found by the US0195 adversarial review (live probe: case-variant tag, rc=0).

## Impact

A project that typos or capitalises a tag believes the criterion is enforced; nothing enforces it and nothing says so - the silent-weakening class the DoR/DoD documents exist to prevent.

## Acceptance Criteria

- [ ] Any bracketed token starting with 'check' (case-insensitive) that is not exactly a registered '[check: <id>]' is a loud validation error naming the near-miss
- [ ] The exact registered form keeps parsing; the shipped templates stay clean

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
