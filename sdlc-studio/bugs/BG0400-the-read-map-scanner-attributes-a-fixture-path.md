# BG0400: The read-map scanner attributes a fixture path to the real tree, so one module's tmpdir read blocks a listing-only narrowing

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`_module_read_paths` measures path expressions statically, so a fixture path built under a tmpdir root and a real read of the repository are indistinguishable when the literal segment matches. `test_lessons.py` reaches the bare `sdlc-studio` entry through one genuine `is_dir()` on the workspace root, and every other `sdlc-studio` literal in that module is fixture-local. With the unanimity rule from BG0398 in force, that single reader withholds the listing-only narrowing `test_root_census.py` declares, which suspends the saving US0554 delivered: filing an artefact is structural again and every close-phase commit pays the full suites.

## Steps to Reproduce

1. `gate.suite_read_map('.')` - two modules carry the bare `sdlc-studio` entry.
2. `gate.listing_only_scopes('.')` returns `{}` - unanimity correctly withholds the narrowing.
3. Read `test_lessons.py`: its only real read of that entry is `(repo / 'sdlc-studio').is_dir()`, an existence check no artefact can change.

## Proposed Fix

Either teach the scanner to distinguish a read anchored at the REPO from one anchored at a fixture root (the reads that matter are anchored at `Path(__file__).resolve().parents[N]`), or give a module a way to declare an existence-only read - a shape question that no file under the directory can change. Do NOT simply add a declaration to `test_lessons.py`: its dependency is genuinely different from the census's, and papering over that is how a declaration stops meaning anything.

## Acceptance Criteria

- [ ] A path built under a fixture root is not attributed to the repository tree.
- [ ] With the attribution corrected, `sdlc-studio` is listing-only again for the ids the census names, so filing an artefact stops being structural.
- [ ] The fail-safe direction is preserved: an unresolvable anchor is attributed to the tree, never dropped.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
