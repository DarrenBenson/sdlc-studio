# US0294: The hygiene check reports a missing instructions file as seedable rather than as an error

> **Status:** Done
> **Delivers:** CR0352
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py
> **Epic:** EP0096
> **Points:** 2

## User Story

**As a** maintainer running the upgrade path on a repo with no AGENTS.md
**I want** the hygiene check to mark the absent-file finding as mechanically seedable and name the
template that supplies it
**So that** the caller can write the file straight from the finding, rather than the finding being
read as a hand task nobody does

## Context

`validate.check_instructions` returns a flat list of `{severity, rule, message}` dicts, and
`project_upgrade.audit()` folds all of them into a single `manual` item. The absent-file case
(`no-agents`) is the only rule whose remedy is fully deterministic: every other rule is about
content already present, which only a human can rewrite without losing project sections.
Downstream callers cannot currently tell the two apart, which is why US0293 has nothing to key the
seed off.

The marker must be additive. Existing consumers read `severity`, `rule` and `message`, and the
`check_instructions` return value is asserted equal to `[]` for a clean project, so a new field
appears only on the finding that carries it.

Severity is unchanged by this story: `no-agents` stays `error` and `validate instructions` still
exits 1 on a repo with no instructions file. CR0352 asks for the finding to be actionable, not for
the gate to relax.

## Acceptance Criteria

### AC1: the absent-file finding carries a machine-readable remedy

- **Given** a root with no AGENTS.md
- **When** `check_instructions` runs
- **Then** the `no-agents` finding carries a seedable marker and names
  `templates/agent-instructions.md` as its source in a dedicated field, so a caller acts on the
  structure and never parses the prose message
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_no_agents_finding_is_marked_seedable
- **Verified:** yes (2026-07-22)

### AC2: only the absent-file case is marked seedable

- **Given** an AGENTS.md that exists but fails the content rules (no doctrine pointer, no LATEST.md
  pointer) and a CLAUDE.md that is not a thin pointer
- **When** `check_instructions` runs
- **Then** no returned finding carries the seedable marker, so a caller acting on the marker can
  never overwrite a file that exists
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_only_the_absent_file_case_is_seedable
- **Verified:** yes (2026-07-22)

### AC3: the message names the command that writes the file

- **Given** the `no-agents` finding
- **When** its message is read by an operator
- **Then** it names the command that seeds the file (`migrate --apply`) rather than describing a
  manual refresh
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_no_agents_message_names_the_seeding_command
- **Verified:** yes (2026-07-22)

### AC4: the existing rules and exit contract are untouched

- **Given** the fixtures already covered by `InstructionsTests` (a clean file, a content-drifted
  file, a CLAUDE.md that is not a pointer, an empty root)
- **When** the suite runs
- **Then** every existing rule id, severity and `validate instructions` exit code is as before, and
  a clean project still returns no findings at all
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k InstructionsTests
- **Verified:** yes (2026-07-22)

## Open Questions

- [x] Ruled by D0052: `no-agents` stays severity `error` and `validate instructions` still exits 1
  even once seeding is possible, because CI reads that exit code. The finding gains a remedy, the
  gate does not relax.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story + 4 executable ACs on check_instructions; severity left as error, recorded as an open question |
| 2026-07-22 | sdlc-studio | Built: TDD, mutation-tested; open questions closed |
