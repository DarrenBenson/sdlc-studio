# US0324: artifact new and refine apply refuse an unresolvable Affects before an id is allocated, minting nothing

> **Status:** Review
> **Depends on:** US0323
> **Delivers:** CR0400
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/scripts/tests/test_artifact.py,.claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Epic:** EP0110
> **Points:** 3

## User Story

**As an** author minting a story, or a batch of them out of a request
**I want** a declared `Affects` that resolves to nothing to be refused at the moment I type it,
before an id is allocated
**So that** the wrong path is fixed while I still know what I meant, rather than surfacing days
later in a plan's collision analysis, an engagement-floor count or a reviewer's reading

## Context

Measured on RUN-01KY3MFX: of 23 stories minted through `refine apply`, five carried a wrong or
incomplete `Affects`, and the same wrong prefix was typed six times across one session. Every
occurrence entered through the two commands that do not check. The refusal must therefore be
whole - `refine` mints an epic and its stories under one rollback guard, so a bad path in the
last story of a batch has to stop the run before the first artefact exists, not undo it
afterwards.

Uses the predicate US0323 builds. This story is only what the writers do with its verdict.

## Acceptance Criteria

### AC1: artifact new refuses a wholly unresolvable Affects and allocates no id

- **Given** a scratch project and `artifact.new` called for a story whose declared `Affects`
  names only paths with nothing behind them
- **When** the command runs
- **Then** it raises, no story file is written, no `_index.md` row is added, and the id the very
  next successful mint takes is the one the refused call would have taken - so a refusal costs
  no id from the sequence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::AffectsValidatedAtMintTests::test_new_refuses_an_unresolvable_affects_and_allocates_no_id
- **Verified:** yes (2026-07-23)

### AC2: a bad path in the last story of a batch mints nothing at all

- **Given** a request being decomposed into three stories, where only the third declares an
  unresolvable `Affects`
- **When** `refine.apply` runs
- **Then** it refuses naming that story and the path, and the tree is untouched: no epic exists,
  none of the three stories exists, and the request's `Decomposed-into` is unchanged - the run
  stops before the first write rather than rolling back after two
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::AffectsValidatedAtMintTests::test_apply_refuses_the_whole_batch_before_minting_the_epic
- **Verified:** yes (2026-07-23)

### AC3: a path to a file the unit will create is still legitimate

- **Given** an `Affects` naming one existing source file and one file that does not exist yet,
  which is the ordinary case of declaring the test the unit will write
- **When** the story is minted through `artifact.new` and through `refine.apply`
- **Then** both mint it and store the field verbatim, because the check refuses only when NO
  declared path resolves - the same rule the grooming gate already applies
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::AffectsValidatedAtMintTests::test_a_partly_unresolvable_affects_still_mints
- **Verified:** yes (2026-07-23)

### AC4: the recorded grooming opt-out is honoured here too

- **Given** a project recording `sprint.breakdown: judgement`, the opt-out under which the
  planner reports instead of blocking and `check_groomed` warns instead of refusing
- **When** `artifact.new` is given a wholly unresolvable `Affects`
- **Then** it warns on stderr naming the paths and mints the unit, so one recorded decision is
  honoured at both ends and this check cannot become the one gate an opted-out project cannot
  escape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::AffectsValidatedAtMintTests::test_the_recorded_opt_out_downgrades_the_refusal_to_a_warning
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: 4 acceptance criteria authored; `Affects` extended with the two test files the criteria name |
