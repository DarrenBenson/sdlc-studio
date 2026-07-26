# US0378: a no-subcommand status prints the pillars and exits 0, explicit subcommands unchanged

> **Status:** Done
> **Delivers:** CR0375
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0136
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py

## User Story

**As an** agent or operator making first contact with a project
**I want** a bare `status.py` to answer the question it obviously asks
**So that** the session does not open with an argparse usage error and a retry

## Acceptance Criteria

### AC1: a bare call prints the pillars dashboard and exits 0

- **Given** a project workspace
- **When** `status.py --root <dir>` runs with no subcommand
- **Then** the output is byte-identical to `status.py pillars --root <dir>` and the exit code is 0
  - a default printing something merely similar would be a second dashboard to keep in step
  with the first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BareInvocationTests::test_no_subcommand_prints_the_pillars_and_exits_zero
- **Verified:** yes (2026-07-24)

### AC2: the default is supplied without a second top-level `--format`

- **Given** `--format` is per-subcommand family-wide, pinned by the CLI-grammar conformance test
- **When** the bare call runs
- **Then** `format` defaults to text from a namespace default and no top-level `--format` flag is
  declared - a top-level copy would be overwritten by the subparser's own default on
  `status.py --format json pillars`, printing text after json was asked for. Known cost: the bare
  call cannot ask for json; `status.py pillars --format json` does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BareInvocationTests::test_the_bare_call_defaults_to_text_without_a_top_level_format_flag
- **Verified:** yes (2026-07-24)

### AC3: explicit subcommands and their flags behave unchanged

- **Given** the existing verbs and their flags
- **When** each is invoked explicitly, including a verb-specific flag and `--root` after the verb
- **Then** every one behaves exactly as before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BareInvocationTests::test_explicit_subcommands_are_unchanged
- **Verified:** yes (2026-07-24)

### AC4: an unknown verb is still a usage error

- **Given** a mistyped verb
- **When** `status.py pillrs` runs
- **Then** it exits non-zero with an invalid-choice error - a typo silently printing the
  dashboard and exiting 0 would be worse than the error this story removes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BareInvocationTests::test_an_unknown_verb_is_still_a_usage_error
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
