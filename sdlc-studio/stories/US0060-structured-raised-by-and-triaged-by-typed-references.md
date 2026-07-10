# US0060: Structured raised_by and triaged_by typed references with backfill

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0169

## User Story

**As a** skill maintainer
**I want** raised_by and triaged_by as typed references (name, type, version), persona-resolved today
**So that** swapping personas for agentic entities later is a resolver change, not a schema migration

## Acceptance Criteria

### AC1: Typed authorship, resolver-backed

- **Given** a schema-v3 artefact
- **When** validate runs
- **Then** a bare-string author fails, and a `type: persona` name must resolve to a persona doc
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k authorship
- **Verified:** yes (2026-07-10)

### AC2: History backfilled, honestly marked

- **Given** existing artefacts (including archives)
- **When** the backfill runs
- **Then** every artefact gains a `raised_by` block, ambiguous ones marked `inferred: true`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_authorship.py
- **Verified:** yes (2026-07-10)

### AC3: Resolver swap needs no frontmatter change

- **Given** a stub agent resolver replacing the persona resolver
- **When** it is swapped in
- **Then** no artefact frontmatter changes (the seam holds)
- **Verify:** manual confirm a stub agent resolver can replace sdlc_md.resolve_author without any artefact frontmatter change (typed refs keep resolution behind that one seam; no executable seam test was ever written)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
