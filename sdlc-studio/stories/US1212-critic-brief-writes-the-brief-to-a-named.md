# US1212: Critic brief writes the brief to a named path and prints one line, and the dispatch says to read it whole

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_out.py
> **Epic:** EP0331
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Critic brief writes the brief to a named path and prints one line, and the dispatch says to read it whole
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: With an output path the brief is written there and one line is printed

- **Given** a unit ready for review
- **When** `critic.py brief --unit <id> --seat qa --out <path>` is run
- **Then** the brief is written to the path, and standard output is exactly one line naming the path, the brief's token count, its tier and its fingerprint; that fingerprint is the one `critic.py record --brief` accepts for the unit. Fails on: the brief also printed to standard output, or a fingerprint that differs from the written file's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_out.py::BriefOutTests::test_out_writes_the_brief_and_prints_one_line

### AC2: Without the flag nothing changes, and an unwritable path is refused

- **Given** the same unit
- **When** `critic.py brief` is run without `--out`, and then with `--out` naming a path under a directory that does not exist
- **Then** the first prints the whole brief to standard output as it does today; the second exits non-zero naming the path, writes no file and prints no fingerprint line. Fails on: a missing directory answered with exit 0, or the plain form's output changing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_out.py::BriefOutTests::test_no_flag_prints_the_brief_and_an_unwritable_path_is_refused

### AC3: The shipped dispatch says to read the brief whole in one call

- **Given** reference-review.md and the review dispatch in reference-agent-prompt-template.md
- **When** each is read
- **Then** both name `critic.py brief --out` and tell the reviewer to read the written brief whole in one call. Fails on: a dispatch that tells the reviewer to read the brief in line ranges, or that names no output path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_out.py::BriefOutTests::test_the_dispatch_says_to_read_the_brief_whole

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
