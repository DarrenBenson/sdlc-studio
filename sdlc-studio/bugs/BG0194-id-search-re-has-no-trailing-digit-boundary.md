# BG0194: ID_SEARCH_RE has no trailing-digit boundary, so a 5-digit id truncates to a 4-digit one

> **Status:** Fixed
> **Severity:** Low
> **Points:** 3
> **Verification depth:** functional (unit tests over both regexes and id_number, three mutants executed and killed with bytecode purged)
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`sdlc_md.ID_SEARCH_RE` matches -?\\d{4} with no boundary after the digits, so US01010 is read as US0101. Any consumer matching ids by this regex can therefore attribute a 5-digit artefact to its 4-digit prefix. Surfaced by the closing review of RUN-01KXT0YV against `sprint._declared_breakdown_ids`: a run touching US0101 derived an untouched epic whose sole child was a Done US01010. Same substring-collision class as the CR0053 HIGH finding against `_wire_story_to_epic` (US0001 vs US00012), which was fixed locally with an exact match rather than at the regex.

## Steps to Reproduce

1. In a workspace, have a run touch US0101. 2. Create an untouched epic whose only breakdown child is a Done US01010 with a backing file. 3. Run sprint close --apply-signoff. 4. Observe the untouched epic derived Done, because `_declared_breakdown_ids` read US01010 as US0101.

## Proposed Fix

Add a trailing boundary to `ID_SEARCH_RE` so a 4-digit match cannot be a prefix of a longer id, then re-check every call site that relies on the current loose behaviour. Consider whether the CR0053 local fix in `_wire_story_to_epic` can then be folded back into the shared regex.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
| 2026-07-18 | sdlc-studio | Fixed: the digit run is `\d{4,}` and the v3 alternative is tried first, so a 5-digit id parses whole and a digit-leading ULID is not truncated; `id_number` widened to 4-7 digits so a long sequential id stays visible to the max+1 allocator |
