# BG0368: init's derived artefact tree creates a type's directory without its index, regressing what US0529 fixed for issues

> **Status:** Fixed
> **Verification depth:** functional (premise re-measured; pairing pinned)
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

### AC1: every derived type directory carries an index

- **Given** a freshly initialised project
- **When** the tree is derived
- **Then** no type directory exists without its `_index.md`, so no type arrives in the state a directory-with-no-index was established as being
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::EveryTypeDirectoryGetsItsIndexTests::test_every_derived_type_directory_carries_an_index
- **Verified:** yes (2026-07-29)

### AC2: both derivations read the same table

- **Given** `index_types()` and `tree_dirs()`
- **When** the tree is derived
- **Then** each type in the shipped table yields both a directory and an index, because two lists deriving separately is how the second comes to be forgotten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::EveryTypeDirectoryGetsItsIndexTests::test_the_two_derivations_read_the_same_table
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Severity Medium -> Low: artifact.py creates a missing index on demand, verified on a fresh init: no user is blocked, so this is tidiness not breakage. Severity corrected DOWN after testing rather than asserting. |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-29 | Claude Opus 5 | DID NOT REPRODUCE, and recorded as such rather than quietly closed. `index_types()` and `tree_dirs()` already derive from one table and step 2 creates an index per type; a fresh `init` leaves no type directory without its index. The premise was checked before any repair was attempted. What was genuinely missing is a guard: nothing asserted the pairing, so the two derivations could drift apart in silence. That guard is the delivery. |
