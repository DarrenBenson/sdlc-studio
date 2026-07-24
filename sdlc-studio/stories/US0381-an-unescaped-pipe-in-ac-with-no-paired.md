# US0381: an unescaped pipe in --ac with no paired --verify is warned or refused by name, correctly-paired output byte-identical

> **Status:** Draft
> **Delivers:** CR0381
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0139
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py

## User Story

**As an** agent scaffolding a unit with executable acceptance criteria
**I want** a criterion that swallowed its own verifier to be named at mint
**So that** I do not ship an artefact that reads as groomed but carries no check anyone can run

## Acceptance Criteria

### AC1: An --ac value containing an unescaped pipe, passed without a paired --verify, is warned by name

- **Given** a criterion written as `criterion|pytest path::Node` - the natural guess, and the shape several other tools take
- **When** `artifact.py new` is invoked with it and no `--verify` at that position
- **Then** the mint names the offending criterion by its position and says where the verifier goes, rather than writing the whole string out as prose with the command backticked into a code span
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PipeInAcTests::test_an_unescaped_pipe_without_a_paired_verify_is_warned_by_name
- **Verified:** yes (2026-07-24)

### AC2: A correctly paired --ac/--verify is untouched, so the guard adds a warning and changes no working path

- **Given** the same criterion with its verifier passed as the paired `--verify`
- **When** the artefact is minted
- **Then** nothing is warned and the `Verify:` line is written verbatim - the guard is positional, so the working path is byte-identical to what it always was
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PipeInAcTests::test_a_correctly_paired_ac_and_verify_is_byte_identical_and_silent
- **Verified:** yes (2026-07-24)

### AC3: a pipe escaped for markdown is left alone

- **Given** a criterion carrying `\|` - how a pipe is written in a table cell on purpose
- **When** the artefact is minted
- **Then** nothing is warned - a guard that fired on every pipe would be trained away, and this is the negative case that stops it flagging everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PipeInAcTests::test_an_escaped_pipe_is_left_alone
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed and delivered: positional `check_pipe_acs` guard, advisory, warned on stderr |
