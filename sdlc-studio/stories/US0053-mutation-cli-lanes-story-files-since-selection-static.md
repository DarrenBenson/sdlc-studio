# US0053: Mutation CLI lanes: story/files/since selection, static assertion pre-filter, cost ceiling

> **Status:** Ready
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Epic:** EP0011
> **Persona:** Dani (Engineering amigo)
> **Story Points:** 3
> **Depends on:** US0051, US0052

## User Story

**As an** operator or autonomous loop
**I want** the gate runnable over a story's changed surface, an explicit file set, or the files changed since a git ref, with a declared cost ceiling and a static pre-filter
**So that** cost stays proportional to the changed surface and truncation is reported, never silent

## Design (settles RFC-0022 D4 and D6 within the accepted direction)

- **Surface selection (D4):** `--files a.py b.py` (explicit), `--story USxxxx` (the story's
  parent CR/epic `Affects` resolved to existing files; the story's non-manual Verify commands
  are the test set), `--since REF` (`git diff --name-only REF` - the release-gate default).
- **Cost ceiling (D6):** `--max-mutations N` (default from `quality.mutation_max`, fallback 25);
  enumeration past the ceiling is dropped AND counted in the report's `truncated` -
  truncated coverage reads as un-checked, never as covered.
- **Static pre-filter (the D lane):** `mutation.py prefilter --tests <paths>` lists test files
  with no recognisable assertion (assert/expect/self.assert) - the cheap ordering signal for
  which tests to mutate first; advisory output only.

## Acceptance Criteria

### AC1: explicit file lane and since-ref lane select the declared surface

- **Given** a repo with changed and unchanged files
- **When** run with --files and with --since
- **Then** only the named/changed files are enumerated as targets
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::LaneTests::test_files_and_since_select_surface

### AC2: the cost ceiling truncates loudly

- **Given** more enumerable mutations than the ceiling
- **When** the run completes
- **Then** exactly N are applied and the report's truncated count carries the remainder
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::LaneTests::test_ceiling_truncates_loudly

### AC3: the pre-filter flags assertion-free tests

- **Given** one test file with assertions and one without
- **When** prefilter runs
- **Then** only the assertion-free file is listed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::LaneTests::test_prefilter_flags_assertion_free

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
| 2026-07-04 | claude | Authored at design: D4 + D6 settled per accepted RFC-0022; points + ACs + Verify lines |
