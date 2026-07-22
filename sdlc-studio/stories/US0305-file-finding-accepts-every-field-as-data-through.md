# US0305: file_finding accepts every field as data through a non-shell input path

> **Status:** Draft
> **Delivers:** CR0384
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0102
> **Points:** 3

## User Story

**As an** agent filing a finding mid-run, whose reproduction steps are themselves commands
**I want** to hand the whole finding to `file_finding.py` as a JSON document that no shell ever
expands
**So that** the steps are stored exactly as written instead of being executed by the shell and
silently deleted from the artefact

## Context

Every field of `file_finding.py file` arrives as a command-line argument, so the caller's shell
sees it first. Inside a double-quoted argument a backtick and a `$(` are command substitution, and
the fields most likely to hold them are `--steps` and `--fix`, whose whole content is commands.
This is not theoretical: BG0240 was filed with two reproduction commands silently removed, and
BG0242, a bug about destructive git commands, executed `git commit -a` twice against the live
repository while being filed. The damage was zero because the pre-commit gate happened to be red,
which is luck rather than safety.

The remedy is an input path that never crosses a shell: a JSON document read from a file or from
stdin, carrying the same field names the flags use. `artifact.py batch --spec` already reads a JSON
file, so the shape has a precedent in this codebase. Flags stay for short titles and enums; a
finding whose prose fields hit the hazard patterns must say so rather than store a mangled body.

## Acceptance Criteria

### AC1: A finding supplied as JSON is stored character for character

- **Given** a JSON document whose Steps field contains a backtick pair, a `$(...)` form and the
  literal text of a destructive git command
- **When** the finding is filed through the non-shell input path
- **Then** the artefact is read back from disk and its Steps section matches the supplied string
  character for character, including the backticks, the dollar-parenthesis and any trailing
  backslash
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k JsonInputFidelityTests
- **Verified:** yes (2026-07-22)

### AC2: Filing that content has no side effect on the repository

- **Given** the same filing as AC1, run inside a git working tree with staged and unstaged changes
- **When** the filing completes
- **Then** HEAD and the index are byte-identical to their state before the call, and no process was
  spawned to evaluate any field
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k JsonInputNoSideEffectTests
- **Verified:** yes (2026-07-22)

### AC3: A field arriving already mangled is reported, not stored quietly

- **Given** a prose field supplied through the flag path that contains an unbalanced backtick, a
  `$(` or a trailing backslash
- **When** the finding is filed
- **Then** the filing reports the field and the offending pattern on stderr at file time, naming
  the non-shell path as the fix, so a truncated body is visible then rather than discovered by
  whoever next reads the artefact
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k ShellHazardReportTests
- **Verified:** yes (2026-07-22)

### AC4: The non-shell path is the documented recommendation

- **Given** an agent reading `reference-scripts.md` or the tool's own `--help`
- **When** it looks for how to file a finding
- **Then** the JSON input path is named as the recommended one, with the shell hazard stated as the
  reason, rather than being an undocumented alternative to the flags
- **Verify:** grep "fields-file" .claude/skills/sdlc-studio/reference-scripts.md
- **Verified:** yes (2026-07-22)

## Open Questions

- CR0384 offers "a --fields-file taking JSON, or reading a JSON document on stdin" and does not
  choose. The ACs are written so either satisfies them; `--fields-file -` reading stdin would
  satisfy both readings, but the decision is not made here. AC4's verifier pins the documented
  name, so a different flag name needs that verifier re-pointed.
- The CR does not say whether the flag path stays available after the JSON path lands. AC3 assumes
  it does and gains a hazard report; removing the flags outright would be a larger change than the
  CR asks for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and acceptance criteria authored |
