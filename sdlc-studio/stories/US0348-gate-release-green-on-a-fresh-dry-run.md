# US0348: gate --release green on a fresh dry-run, cut the CHANGELOG 5.0.0 section, tag

> **Status:** Draft
> **Delivers:** CR0319
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0117
> **Points:** 3
> **Affects:** CHANGELOG.md, .claude/skills/sdlc-studio/scripts/gate.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: gate --release is green on a fresh dry-run

- **Given** a clean checkout at the release commit
- **When** `gate.py --release` runs, judging the WHOLE workspace rather than a diff
- **Then** every blocking lane passes - the release gate is the one run that may not rely on diff scoping, which is the defect BG0284's sibling exposed
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/gate.py --release

### AC2: the CHANGELOG 5.0.0 section is cut from the fragments, not hand-written

- **Given** an [Unreleased] section holding this release's fragments
- **When** the release cut runs
- **Then** a 5.0.0 section exists carrying those fragments, [Unreleased] is emptied, and the changelog-fragments lane still passes - a hand-edited [Unreleased] is what that lane refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_the_section_is_cut_from_fragments_and_unreleased_is_emptied

### AC3: the tag is refused unless the gate was green on the tagged commit

- **Given** a release attempt whose gate run predates the commit being tagged
- **When** the tag step runs
- **Then** it is refused and says which commit was actually judged - a tag asserting a green that was measured on a different tree is the false claim this story exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::ChangelogCutTests::test_a_tag_is_refused_when_the_green_was_measured_elsewhere

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
