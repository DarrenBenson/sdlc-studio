# US0342: Every lens cites the incident it derives from, so a reader can weigh it against evidence rather than assertion

> **Status:** Review
> **Delivers:** CR0403
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/audit-profiles/process.md,.claude/skills/sdlc-studio/reference-audit.md,.claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py
> **Epic:** EP0115
> **Points:** 2

## User Story

**As a** reader deciding whether to spend an audit on a lens
**I want** every lens to cite the recorded incident it was drawn from
**So that** I can read the failure that produced it and judge whether it applies to my
project, rather than accepting a taxonomy entry somebody invented from first principles

## Context

The `test` pack already sets the bar: each lens cites lessons registry ids, and a test
holds every citation to resolving against `lessons/_index.md` with its file present. This
story applies the same bar to the process pack, and adds the constraint the process pack
needs and the `test` pack never had to state - the incidents behind these lenses were
recorded in this repo's project-local lessons and retros, and the pack SHIPS. An id that
resolves only here is a dangling reference in every consuming project, so provenance must
be promoted into the shipped registry before it can be cited.

Whether a resolving citation actually describes the incident that produced its lens is a
reading, not a lookup. AC3 owns that and is manual.

## Acceptance Criteria

### AC1: every lens cites a lesson that resolves to a shipped entry

- **Given** the process pack and the shipped lessons registry
- **When** each lens's provenance is parsed
- **Then** every lens cites at least one lesson id, each cited id has a row in
  `lessons/_index.md`, and the file that row names is present - so a lens appended without
  provenance, and a citation whose entry was later removed, both fail
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessLensProvenanceTests::test_every_process_lens_cites_a_lesson_that_resolves
- **Verified:** yes (2026-07-23)

### AC2: provenance is citable outside this repo, so a project-local or artefact id is refused

- **Given** a lens whose provenance cell names a project-local `L-` lesson id, or an
  artefact id such as a bug or a run
- **When** the pack's provenance is checked
- **Then** the check fails naming that lens and that id, because a reader in a consuming
  project cannot open either - the pack may cite only ids the shipped registry carries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::ProcessLensProvenanceTests::test_a_project_local_or_artefact_id_is_refused_as_provenance
- **Verified:** yes (2026-07-23)

### AC3: each cited entry describes the incident that produced its lens

- **Given** every lens and the lessons its provenance cell cites
- **When** each cited entry is read against the lens beside it
- **Then** the entry records the failure that lens hunts, in enough detail for a finder to
  work from; a citation that resolves but describes an unrelated failure is re-pointed or
  the lens is dropped
- **Verify:** manual read each cited lesson against its lens row and record the judgement per lens - relevance is a reading of prose, and no lookup can settle it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
