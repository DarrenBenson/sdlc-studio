# US0325: The refusal names the closest unique basename match where one exists, rather than sending the caller to look

> **Status:** Draft
> **Delivers:** CR0400
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py
> **Epic:** EP0110
> **Points:** 2

## User Story

**As an** author whose `Affects` has just been refused for a wrong directory prefix
**I want** the refusal to name the one file that carries the basename I typed
**So that** I correct the path from the message instead of going to look for what the tool
could already see

## Context

The failure this addresses is a typing hazard, not a knowledge gap: the same wrong prefix was
typed six times in one session by an author who knew the rule. A refusal that only says "this
path resolves to nothing" sends that author back to search; the basename is almost always
right and the directory almost always wrong, so the tool holds the answer at the moment it
refuses.

The suggestion is help, never a correction: nothing is rewritten on the author's behalf, and a
guess is never presented as an answer.

## Acceptance Criteria

### AC1: a unique basename match is named as the correction

- **Given** a declared path whose directory is wrong and whose basename is carried by exactly
  one file in the repository
- **When** the mint is refused
- **Then** the message names that one real path alongside the value that was rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::ClosestMatchTests::test_the_refusal_names_a_unique_basename_match

### AC2: an ambiguous basename lists its candidates and chooses none

- **Given** a declared path whose basename is carried by several files, such as one that exists
  under both the skill tree and a test directory
- **When** the mint is refused
- **Then** the message lists the candidates it found and states that it cannot choose between
  them, rather than presenting the first as the answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::ClosestMatchTests::test_an_ambiguous_basename_lists_candidates_without_choosing

### AC3: no match offers no suggestion

- **Given** a declared path whose basename matches no file in the repository
- **When** the mint is refused
- **Then** the message still names the unresolvable path and says plainly that no candidate was
  found, so the author is never sent to a file the tool invented
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::ClosestMatchTests::test_no_basename_match_offers_no_suggestion

### AC4: every writer's refusal carries the suggestion

- **Given** the same wrong-directory path given to `file_finding.file`, `artifact.new` and
  `refine.apply`
- **When** each refuses
- **Then** each message carries the same named candidate, because the suggestion is built where
  the predicate lives rather than at one caller
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::ClosestMatchTests::test_all_three_refusals_carry_the_same_suggestion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: 4 acceptance criteria authored; `Affects` extended with the predicate's home and the test file the criteria name |
