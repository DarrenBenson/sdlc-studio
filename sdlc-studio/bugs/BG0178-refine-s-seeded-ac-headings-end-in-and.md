# BG0178: refine's seeded AC headings end in '...' and fail markdownlint MD026

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

refine.py truncates a long seeded criterion into the AC heading with a trailing '...' (e.g. '### AC1: sprint close runs the chain in order and STOPS loudly at the first failing gate, naming the remed...'). MD026 (no-trailing-punctuation) rejects it, so in any repo that markdownlints its workspace - including this one - the planning paperwork commit is blocked by the tool's own output. Observed on all 8 stories minted for RUN-01KXPJG9; npm run lint:fix strips the dots as a workaround.

## Steps to Reproduce

1. refine.py apply with a --story whose seeded request criterion exceeds the heading truncation width; 2. run markdownlint over the minted story; 3. MD026 fires on every truncated AC heading

## Proposed Fix

Truncate without trailing punctuation (drop the ellipsis, or use a word-boundary cut); a generated artefact must pass the gates the generator's own repo enforces

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Filed |
