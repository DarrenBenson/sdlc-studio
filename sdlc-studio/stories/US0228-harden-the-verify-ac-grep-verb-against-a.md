# US0228: harden the verify_ac grep verb against a dash-leading pattern

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Epic:** EP0075
> **Points:** 2

## User Story

**As an** engineer writing an executable AC
**I want** the `grep` verb to treat my pattern as a pattern
**So that** an AC that starts its regex with a dash searches for what it says it searches for

## Acceptance Criteria

### AC1: A dash-leading pattern is passed as a pattern, not as flags

- **Given** a Verify line whose regex begins with `-` (`grep -Ran notes.md`)
- **When** the command is built
- **Then** the pattern is passed behind `-e` so the tool cannot read it as its own flags, and the AC searches for the text the author wrote.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.GrepDashPatternTests.test_dash_leading_pattern_is_passed_behind_dash_e
- **Verified:** yes (2026-07-18)

### AC2: A dash-leading path cannot be read as a flag either

- **Given** a Verify line whose path begins with `-`
- **When** the command is built
- **Then** the paths sit after a `--` terminator, so the search target is unambiguous.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.GrepDashPatternTests.test_paths_sit_behind_a_double_dash_terminator
- **Verified:** yes (2026-07-18)

### AC3: The hardening applies to both back-ends

- **Given** a machine with `rg` and a machine without it
- **When** each back-end command is built
- **Then** both the `rg` and the `grep -rqE` form carry `-e` and `--`, because an AC must not depend on which search tool happens to be installed.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.GrepDashPatternTests.test_both_backends_are_hardened
- **Verified:** yes (2026-07-18)

### AC4: An ordinary pattern still matches exactly as before

- **Given** the existing Verify lines across this workspace, none of which lead with a dash
- **When** they run
- **Then** they behave unchanged, so the hardening is not a silent change of search semantics.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_verify_ac.GrepDashPatternTests.test_ordinary_patterns_are_unaffected
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored; absorbs the criterion mis-seeded onto US0226 AC3, which is this story's subject |
