# BG0129: review_prep counts personas/index.md as a persona (the underscore-index filter misses it)

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py

## Summary

`review_prep.py` `persona_usage` (line 136) and `required_legs` (line 169) exclude '_index.md', but the persona index file is named 'index.md' (no underscore). So index.md is parsed as a persona: its H1 'Persona Index' is reported as a defined-but-unused persona on every review. Surfaced while running the document review - a phantom third persona alongside the two real ones (Maya Okafor, Trevor Hale). Also: `persona_usage` globs personas/*.md non-recursively, so the amigos/ seat files are not counted at all - a possible related gap.

## Steps to Reproduce

`review_prep.py` prep -> 'personas defined=3 unused=3 (Persona Index, Maya Okafor, Trevor Hale)'. 'Persona Index' is personas/index.md's H1, not a persona. The filter checks p.name != '_index.md'; the file is index.md.

## Proposed Fix

Exclude index.md as well as _index.md (or normalise the index filename). Consider whether amigos/ seat files should be included in `persona_usage.` Add a test with an index.md present asserting it is not counted (LL0010).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
