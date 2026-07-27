# BG0349: Four modules still carry the naive fence toggle the parser fix replaced

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, tools/check_links.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers); agent; skill v5.0.0

## Summary

The closing review replaced the fence walker in `verify_ac.py` and validate.py with one shared CommonMark tracker. The reviewer confirmed the naive toggle survives in lib/`sdlc_md.py` (lines 392 and 1603), `file_finding.py` (482), `persona_resolve.py` (192) and tools/`check_links.py` (191 and 294). Each treats any three-character run as a closer, so an inner fence inside a longer one releases the block early and content after it is read as document.

## Steps to Reproduce

1. Read each cited line. 2. Feed each a document with a four-backtick block containing an inner three-backtick opener, or a fence line carrying an info string. 3. Observe the block released early.

## Proposed Fix

Call the shared `sdlc_md.fence_step` from each, deleting the local rule. `sdlc_md.py`:392 is the widest and should go first: it governs table-row counting that reconcile consumes, which is the index-corruption class.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers) | Filed |
