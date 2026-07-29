# BG0374: The markdownlint path fixed in BG0341 still cannot see every tracked markdown file

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/lint-style.sh, package.json
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

BG0341 widened the per-commit markdownlint lanes so tracked .github markdown is linted. The widening is an added path rather than a derivation, so markdown tracked outside both the original glob and the added path remains unlinted, and the same failure recurs the next time a tracked directory is added. This is the enumerated-list shape the carried lessons already name.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review of BG0341's repair. Compare the linted set against git ls-files '*.md': the sets differ.

## Proposed Fix

Derive the linted set from the tracked set rather than from globs, as the corpus lane already does, so a new tracked directory is covered without list maintenance.

## Acceptance Criteria

### AC1: both markdown lanes read one derived enumeration

- **Given** `npm run lint:md` and `lint:fix`
- **When** it runs
- **Then** each delegates to `tools/lint-md.sh` and names no glob of its own, because a glob cannot enter a dot-directory - which is the whole defect
- **Verify:** pytest tools/tests/test_precommit_markdown_scope.py::NpmLaneSeesEverythingTheHookDoesTests::test_the_npm_lanes_delegate_to_the_derived_enumeration
- **Verified:** yes (2026-07-29)

### AC2: the linted set is derived from the tracked set

- **Given** the shared script's executable lines
- **When** it runs
- **Then** it reads `git ls-files` and names no glob, so a newly tracked directory is covered without list maintenance
- **Verify:** pytest tools/tests/test_precommit_markdown_scope.py::NpmLaneSeesEverythingTheHookDoesTests::test_the_script_reads_the_tracked_set
- **Verified:** yes (2026-07-29)

### AC3: every tracked markdown file falls into a lane

- **Given** this repository's tracked markdown, measured rather than asserted about
- **When** it runs
- **Then** every file is in one of the two partitions and the `.github/` files this bug is about are present, so the check cannot pass by having lost its own fixture
- **Verify:** pytest tools/tests/test_precommit_markdown_scope.py::NpmLaneSeesEverythingTheHookDoesTests::test_every_tracked_markdown_file_is_covered_by_one_lane
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
