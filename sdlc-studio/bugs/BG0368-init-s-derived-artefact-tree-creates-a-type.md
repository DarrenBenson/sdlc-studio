# BG0368: init's derived artefact tree creates a type's directory without its index, regressing what US0529 fixed for issues

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0529 made init create the issues directory AND its index, because a directory with no index is not a usable artefact type. US0530 then derived the whole tree from the shipped type list, and the derivation creates directories only - so every type it now covers arrives in the state US0529 had just established as broken, and the two stories shipped in the same batch.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review by reading the derived-tree creation against US0529's repair. The derivation enumerates the type list and makes a directory per type; nothing writes the per-type index that every other artefact directory carries.

## Proposed Fix

Derive the index alongside the directory from the same type list, so a type added to the shipped list arrives complete. Assert on a freshly initialised project that every created directory has an index.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Severity Medium -> Low: artifact.py creates a missing index on demand, verified on a fresh init: no user is blocked, so this is tidiness not breakage. Severity corrected DOWN after testing rather than asserting. |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
