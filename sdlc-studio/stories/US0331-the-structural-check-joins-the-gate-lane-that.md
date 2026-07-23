# US0331: The structural check joins the gate lane that already binds changelog fragments, and a hand-edit of Unreleased while changelog.d is live is made visibly wrong

> **Status:** Done
> **Delivers:** CR0405
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py,.claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0112
> **Points:** 2

## User Story

**As an** author about to commit a changelog entry
**I want** the gate to fail my commit when I have edited `[Unreleased]` by hand while
`changelog.d/` is live, or left the file's headings in a shape a bad insert produces
**So that** the deterministic writer is the path of least resistance rather than a convention I
can forget twice in one run and then file a change request about

## Context

CR0405 asks the structural check to join the lane that already binds changelog fragments rather
than invent one. That lane, `changelog-fragments` in `gate.py`, is bound only under `--release`,
deliberately: a stray fragment between releases is the normal state and the standard gate must
not nag about it. A structural fault is not like that. It is committed, not tagged, and a check
that waits for the cut would not have caught either RUN-01KY3MFX incident at the moment it
happened. So the lane keeps its name and gains a mode: bound in both gates, with the
stray-fragment reading still release-only. AC2 is where that split is pinned.

The hand-edit guard reads the staged diff, as the rewrite-window lane already does, so it judges
what this commit is about to do rather than the state of the tree.

## Acceptance Criteria

### AC1: the structural fault fails the lane that already exists, under its existing name

- **Given** a CHANGELOG.md carrying a repeated subsection heading inside one release, and no
  stray fragments
- **When** the release gate runs
- **Then** the `changelog-fragments` lane fails, its detail naming the structural fault, and the
  gate's set of check names is unchanged - no second changelog lane appears in the registry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ChangelogStructureLaneTests::test_the_structural_fault_fails_the_existing_lane_under_its_existing_name
- **Verified:** yes (2026-07-23)

### AC2: the lane runs at commit time for structure and at the cut for strays

- **Given** the same repeated heading, and separately an uncomposed fragment with a
  structurally sound CHANGELOG
- **When** the standard gate runs over each, and then the release gate runs over each
- **Then** the structural fault fails BOTH, while the stray fragment fails only the release gate
  - so the fault an author commits is caught when they commit it, and the standard gate still
  never nags about the normal between-releases state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ChangelogStructureLaneTests::test_structure_binds_in_both_gates_while_strays_stay_release_only
- **Verified:** yes (2026-07-23)

### AC3: a hand-edit of Unreleased while changelog.d is live fails the commit

- **Given** a repository using fragments, with a commit staging a change inside CHANGELOG.md's
  `[Unreleased]` section and consuming no fragment in the same commit
- **When** the gate runs
- **Then** it fails, naming CHANGELOG.md and the `changelog.py` command that would have made the
  edit; the same staged edit accompanied by a fragment the commit consumes passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::HandEditedChangelogTests::test_a_staged_unreleased_edit_without_a_consumed_fragment_fails
- **Verified:** yes (2026-07-23)

### AC4: edits outside Unreleased are not touched by the guard

- **Given** a commit staging a change to an already-released section, to the file's header, or
  the section rename a release cut performs
- **When** the gate runs
- **Then** it passes, so cutting a release and correcting published history stay hand-editable
  and the guard cannot be dismissed as blanket obstruction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::HandEditedChangelogTests::test_an_edit_outside_unreleased_is_not_refused
- **Verified:** yes (2026-07-23)

## Open Questions

- CR0405 assumes the structural check belongs in the release-bound lane. AC2 binds it in the
  standard gate as well, on the argument that the fault is committed rather than tagged. If the
  release-only reading is wanted instead, AC2 changes and the incident this work comes from
  would still not be caught at commit time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0405's CORRECTED summary: 4 acceptance criteria plus the open question about binding a release-only lane at commit time; `Affects` extended with the test file |
