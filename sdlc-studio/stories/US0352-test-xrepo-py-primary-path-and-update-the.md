# US0352: test_xrepo.py primary path and update the TSD coverage note

> **Status:** Draft
> **Delivers:** CR0337
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0119
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_xrepo.py, .claude/skills/sdlc-studio/scripts/xrepo.py, sdlc-studio/tsd.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: xrepo's primary path is exercised

- **Given** a fixture with two repositories
- **When** `lib/xrepo` is driven through its primary path
- **Then** the cross-repo operation completes and its effect is asserted on the resulting state of both trees
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_xrepo.py::PrimaryPathTests::test_the_primary_path_completes_across_two_trees

### AC2: the TSD coverage note matches the measurement

- **Given** the TSD sentence BG0162 corrected to say autosprint and lib/xrepo are untested
- **When** these suites land
- **Then** no sentence still calls autosprint or lib/xrepo untested, and the note states what is now covered. Greping for the word `xrepo` would be vacuous - BG0162 already put it there; the check must bind the CLAIM that changed. It anchors on the exact phrase `currently have no direct test`, because the first attempt used a `[^.]*` regex that cannot cross the line break the sentence actually contains, and passed vacuously
- **Verify:** shell grep -q 'currently have no direct test' sdlc-studio/tsd.md && exit 1 || exit 0
- **Verified:** no (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
