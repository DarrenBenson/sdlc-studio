# BG0328: Engagement floor's id grammar enumerates the v2 4-digit form, silently exempting v3 ULID and 5-digit units

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Every floor entry point recognises only US/BG/CR plus exactly four digits, so a unit with a v3 short-ULID or 5-digit id is invisible: the floor-pending lane drops it before judging, the git leg cannot count it in a multi-id subject (mis-attributing the file set to the 4-digit unit), and the commit-msg multi-id rule never fires - on a schema-v3 project the floor reports clean while checking nothing. The shared library already widened its grammar for this exact lesson; the floor never adopted it.

## Steps to Reproduce

Evidence (Line 101 `_JUDGED_ID_RE`; pending lane ~line 350; git attribution leg ~line 183; `check_commit_message` ~line 640; .githooks/commit-msg line 96): `engagement_floor.py`:101 regex \d{4}; lib/`sdlc_md.py`:38-43 documents the widened \d{4,} plus ULID-first `ID_RE`; grep for ulid/v3 in `engagement_floor.py` returns nothing; the commit-msg hook's paste-hint grep repeats the 4-digit enumeration.

## Proposed Fix

Replace `_JUDGED_ID_RE` (and the commit-msg hint grep) with the `sdlc_md` `ID_RE` grammar - \d{4,} plus the v3 ULID alternative - so v3 and 5-digit units are judged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
