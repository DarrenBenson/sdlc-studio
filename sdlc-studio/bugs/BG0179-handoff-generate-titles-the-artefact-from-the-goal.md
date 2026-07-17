# BG0179: handoff generate titles the artefact from the goal sentence verbatim and fails MD026

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

handoff.py generate used the Sprint Goal sentence (ending in a full stop) as the H1, so HO0003's heading tripped markdownlint MD026 in the generator's own repo and blocked the close commit; npm run lint:fix stripped it. Same class as BG0178: a generated artefact must pass the gates the generator's repo enforces - strip trailing punctuation when composing headings from prose.

## Steps to Reproduce

1. sprint plan --write --sprint-goal 'A sentence ending in a full stop.'; 2. handoff.py generate (or sprint close); 3. markdownlint the minted HO file - MD026 fires on the H1

## Proposed Fix

Trim trailing punctuation when a heading is composed from prose (shared helper with the BG0178 fix)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
