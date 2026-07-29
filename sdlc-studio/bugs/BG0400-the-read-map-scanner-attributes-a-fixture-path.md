# BG0400: The read-map scanner attributes a fixture path to the real tree, so one module's tmpdir read blocks a listing-only narrowing

> **Status:** Fixed
> **Verification depth:** functional (tests red-first, each fix verified by applying its mutant)
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

- [x] A module whose only read of a directory is an EXISTENCE probe does not count as a content reader for the unanimity rule.
- [x] With the electorate corrected, `sdlc-studio` is listing-only again for the ids the census names, so filing an artefact stops being structural.
- [x] The fail-safe direction is preserved: the path stays in the read map, so deleting the directory still selects the module that probes it.
- [x] A module that probes AND reads the contents keeps its vote, so an `exists()` beside a `glob()` cannot launder a real dependency.
- [x] The subtraction has ONE implementation (`gate.content_readers`), which the rule and its tests both use rather than each re-deriving it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
| 2026-07-29 | sdlc-studio | Criteria rewritten: the filed premise was wrong. The path is not fixture-local - it is `Path(__file__).resolve().parents[5] / "sdlc-studio"`, a genuine repo-anchored read in `test_lessons.py`. What made it a false veto is that the read is `is_dir()`, an EXISTENCE probe no artefact under the directory can change. Fixed by the second route this bug's own Proposed Fix names, and the criteria now describe that. |
| 2026-07-29 | sdlc-studio | Fixed. Two of this repo's own tests were asserting the SUSPENDED state, each re-deriving the reader set from the raw read map - so they agreed with the defect by construction and went red on the repair. Both now read `gate.content_readers`. |
