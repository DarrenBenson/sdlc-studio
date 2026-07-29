# BG0390: The seam map misses a shared file written in the two Affects spellings this repo accepts

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`sdlc_md.resolve_affects` deliberately resolves both repo-relative and skill-relative paths and the corpus uses both (149 `.claude/skills/sdlc-studio/scripts/sprint.py` against 1 `scripts/sprint.py`). `seam_map` intersects raw strings, so the same file under two spellings is not a seam.

## Steps to Reproduce

US0001 Affects .claude/skills/sdlc-studio/scripts/critic.py; US0002 Affects scripts/critic.py -> `seam_map` returns [].

## Proposed Fix

Normalise through `sdlc_md.resolve_affects` before intersecting.

## Acceptance Criteria

### AC1: one file in two accepted spellings is one seam

- **Given** two units naming `.claude/skills/sdlc-studio/scripts/sprint.py` and `scripts/sprint.py`
- **When** the seam map runs
- **Then** the pair is a seam, because paths are resolved through `sdlc_md.resolve_affects` before intersecting
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_the_same_file_in_two_accepted_spellings_is_one_seam
- **Verified:** yes (2026-07-29)

### AC2: two genuinely different files are still not a seam

- **Given** two units naming `src/a.py` and `src/b.py`
- **When** the seam map runs
- **Then** no seam is reported, so normalising does not collapse distinct files into a false pair
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_two_genuinely_different_files_are_still_not_a_seam
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
