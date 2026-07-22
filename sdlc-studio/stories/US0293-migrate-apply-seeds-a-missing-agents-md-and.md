# US0293: migrate --apply seeds a missing AGENTS.md and CLAUDE.md from the template, preserving project sections

> **Status:** Done
> **Delivers:** CR0352
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py,.claude/skills/sdlc-studio/scripts/project_upgrade.py
> **Epic:** EP0096
> **Points:** 3

## User Story

**As a** maintainer adopting the skill on an existing repo that has no agent-instructions file
**I want** `migrate --apply` to write AGENTS.md and CLAUDE.md from the shipped templates when they are absent
**So that** the command whose whole purpose is bringing a project up to date establishes the working model, instead of handing back a task I have to do by hand

## Context

`migrate` classifies from `project_upgrade.audit()` in BOTH modes and only calls
`project_upgrade.apply()` when `--apply` is passed, so a seed must appear in `audit()`'s `auto`
bucket for the dry run and the apply to agree on what is deterministic. Today the instructions
finding is folded into `audit()`'s `manual` bucket ("refresh from templates/agent-instructions.md,
preserving project sections") and nothing writes.

`init.py` already owns the seeding path and is the code to reuse rather than copy: `AGENT_FILES`
pairs `templates/agent-instructions.md` -> `AGENTS.md` and `templates/agent-instructions.CLAUDE.md`
-> `CLAUDE.md`, `_strip_comment` drops the leading guidance comment, and `_fill_known` fills only
the placeholders the tool can know. Note the case mismatch: `_fill_known` substitutes
`{{project_name}}` while the instructions template's heading carries `{{PROJECT_NAME}}`, so a
derivation that reuses it verbatim leaves the project name unfilled.

Seeding is bounded to a file that does not exist. Editing a file that does exist is a judgement
call (project sections must survive), so it stays a reported needs-human item.

## Acceptance Criteria

### AC1: an absent AGENTS.md is written from the template on apply

- **Given** a project with an `sdlc-studio/` workspace and no AGENTS.md
- **When** `migrate --apply` runs against it
- **Then** AGENTS.md exists, its body is the shipped template with the guidance comment stripped
  and the derivable placeholders (the project name) filled, the remaining `{{placeholders}}` are
  left visibly unfilled, and the write is reported under the deterministic section
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_migrate.py -k test_apply_seeds_a_missing_agents_md
- **Verified:** yes (2026-07-22)

### AC2: the dry run states exactly what it would write, and writes nothing

- **Given** the same project with no AGENTS.md and no CLAUDE.md
- **When** `migrate` runs without `--apply`
- **Then** the deterministic section names both files as ones it would create, and neither file
  exists on disk when the command returns
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_migrate.py -k test_dry_run_names_the_seed_and_writes_nothing
- **Verified:** yes (2026-07-22)

### AC3: an existing AGENTS.md is never overwritten

- **Given** a project whose AGENTS.md exists, carries project-specific sections, and fails one or
  more hygiene rules
- **When** `migrate --apply` runs
- **Then** the file is byte-for-byte unchanged and its drift is reported as a needs-human item
  naming the specific rules it fails
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_project_upgrade.py -k test_apply_never_rewrites_an_existing_agents_md
- **Verified:** yes (2026-07-22)

### AC4: CLAUDE.md is seeded as the thin pointer; a duplicating one is reported, not rewritten

- **Given** one project with no CLAUDE.md, and one whose CLAUDE.md restates the instructions
  instead of importing `@AGENTS.md`
- **When** `migrate --apply` runs over each
- **Then** the first gains a CLAUDE.md importing `@AGENTS.md` from
  `templates/agent-instructions.CLAUDE.md`; the second keeps its file byte-for-byte and is reported
  with the one-line pointer that would replace it
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_migrate.py -k test_claude_md_seeded_when_absent_and_reported_when_duplicating
- **Verified:** yes (2026-07-22)

## Open Questions

- [x] The marked remainder is NOT reported as a separate needs-human item. The seed leaves the
  judgement placeholders visibly unfilled in the file it writes, and the report names the file it
  created; no hygiene rule covers "Project specifics", so a follow-on finding would have nothing
  to key on. Recorded as the built behaviour, not as a ruling - a rule that reads the seeded
  placeholders back is a separate change.
- [x] Ruled by D0052: the seed lands in `project_upgrade.apply()` so `audit()` classifies it
  `auto`, which means `project upgrade --apply` seeds as well. The wider surface is intended.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story + 4 executable ACs against migrate/project_upgrade; open questions on the marked remainder and the wider surface |
| 2026-07-22 | sdlc-studio | Built: TDD, mutation-tested; open questions closed |
