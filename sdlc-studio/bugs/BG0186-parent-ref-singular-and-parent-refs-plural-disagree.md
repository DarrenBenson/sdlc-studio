# BG0186: parent_ref (singular) and parent_refs (plural) disagree on a contradictory Parent record

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

For a malformed record with two Parent lines where the first is a sentinel ('> **Parent:** -' then '> **Parent:** CR0200'), singular `parent_ref` (and thus `child_parent)` returns None (it stops at the first line's '-' sentinel), while plural `parent_refs` returns ['CR0200']. `children_of` and the link-asymmetry gate use the plural path consistently, so it is inert today - but the two readers now diverge, so a future caller reading the singular would disagree with the gate. Found by the CR0322 adversarial review (finding 2).

## Steps to Reproduce

Write a record with '> **Parent:** -' followed by '> **Parent:** CR0200'; `parent_ref`/`child_parent` return None while `parent_refs` returns ['CR0200'].

## Proposed Fix

Make `parent_ref` return the FIRST NON-sentinel parent (`parent_refs[0]` if any), so the singular and plural readers agree; or document that the singular is first-line-only. Add a divergence test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
