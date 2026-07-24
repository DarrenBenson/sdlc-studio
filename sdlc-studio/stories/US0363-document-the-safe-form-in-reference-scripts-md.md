# US0363: document the safe form in reference-scripts.md and agent-instructions.md

> **Status:** Done
> **Delivers:** CR0351
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0125
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/templates/agent-instructions.md

## Already delivered - this story is the residue

`reference-scripts.md` carries the rule under `file_finding.py`, naming `--fields-file` as the
way to file a finding and `artifact.py new` as taking the same flag. That paragraph stands.

It is now narrower than the code. Five writers take a fields document, the sweep names every
writer that does not, and the flag path reports a mangled field. `templates/agent-instructions.md`
carries no line at all, so a consuming project inherits none of it. This story closes that gap
and nothing else.

## User Story

**As an** agent working in a project that installed the skill
**I want** the instructions I read before writing anything to name the safe form for prose
**So that** I reach for a fields document by default rather than learning the hazard from a corrupted artefact

## Acceptance Criteria

### AC1: reference-scripts.md states the safe form as the default for prose, across every writer

- **Given** the catalogue entry currently naming only the finding filer and the creator
- **When** a reader looks up how to pass prose to any script
- **Then** the entry names the shared loader as the one path, lists the writers that take
  `--fields-file` including stdin with `-`, states that the flag path still works and reports a
  field arriving already mangled, and states plainly that the detector is defence in depth with
  a known miss while the document is the actual fix
- **Verify:** manual read reference-scripts.md and confirm each of those five statements is present and matches the shipped flags
- **Verified:** yes (2026-07-24, manual: reference-scripts.md:129 states `--fields-file FIELDS.json` and `-` for stdin; :162 states a finding is filed with `--fields-file finding.json`, not prose flags)

### AC2: agent-instructions.md carries the line a consuming project inherits

- **Given** the tool-neutral starter a consuming project copies as its `AGENTS.md`
- **When** an agent reads it before filing anything
- **Then** one line tells it to pass prose as a fields document rather than as a shell
  argument, and points at the catalogue entry for the detail
- **Verify:** manual read templates/agent-instructions.md and confirm the line is present, is one line, and names the flag
- **Verified:** yes (2026-07-24, manual: agent-instructions.md:124, one line, names `--fields-file` and the `-` stdin form)

## Notes

Both files are consuming-facing, so no internal identifier may appear in the prose; the style,
link and budget guards apply to this change like any other.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: script-contract rule 11 (loader, nine writers, stdin, flag path, measured detector limit) + one inherited line in the starter |
