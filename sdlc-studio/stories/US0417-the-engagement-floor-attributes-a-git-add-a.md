# US0417: the engagement floor attributes a git add -A commit to every unit it touched, not only those named

> **Status:** Review
> **Delivers:** CR0416
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As an** author committing one unit while the next is already being written
**I want** a commit that sweeps in another unit's files to say so
**So that** one unit is not credited with another's work, and the swept-in unit does not read as undelivered

## Acceptance Criteria

### AC1: a commit whose files belong to an unnamed unit is reported

- **Given** a commit staging a modification to a file belonging to a unit its subject and `Refs:` trailers never name
- **When** the commit-msg gate runs
- **Then** it names that unit and gives the `Refs:` line to paste, so the attribution is stated rather than guessed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::UnnamedUnitAttributionTests::test_a_file_owned_by_an_unnamed_unit_is_reported
- **Verified:** yes (2026-07-24)

### AC2: a warning, not a refusal, where ownership is ambiguous

- **Given** a file claimed by several units, or by none
- **When** the gate runs
- **Then** nothing is reported and nothing is refused - shared and unowned files are the ordinary case, and a gate that blocked on them would be disabled within a week
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::UnnamedUnitAttributionTests::test_a_shared_or_unowned_file_does_not_refuse
- **Verified:** yes (2026-07-24)

### AC3: the advisory never becomes a refusal, even under the strict flag the hook uses

- **Given** a reported mis-attribution and the hook's own `--strict` invocation
- **When** the commit-msg check runs
- **Then** it prints the note and exits 0 - ownership is read from a declaration, and only the multi-id rule may refuse a commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::UnnamedUnitAttributionTests::test_the_cli_reports_the_note_and_still_exits_zero
- **Verified:** yes (2026-07-24)

### AC4: the same behaviour holds through the bash hook, not only the library

- **Given** the gate invoked the way git invokes it
- **When** a commit stages an unnamed unit's file
- **Then** the note reaches the author's terminal and the commit still lands
- **Verify:** pytest tools/tests/test_commit_msg_hook.py::UnnamedUnitAttributionTests::test_a_file_owned_by_an_unnamed_unit_is_reported
- **Verified:** yes (2026-07-24)

## Detail

**The historical mis-attribution, recorded rather than corrected (CR0416 AC3).** Commit
`6ae0c80e` - subject `fix(BG0276): the ungroomed count sees the legacy scaffold, not only the new
marker` - also carries BG0268's delivery: its source change, its test class and its changelog
fragment. A background commit for BG0276 ran a `git add -A` while BG0268 was being written beside
it. History is not rewritten; this note is the record, and it is written where a reader of either
unit meets it. The new lane, run against that commit, reports `named-file BG0268` - the case it
was built for, on the evidence that produced it.

**Two ownership signals, not one, because they are not equally strong.**

- `named-file` - the path CARRIES the id (a unit's artefact, its changelog fragment). Nothing is
  inferred and it does not weaken as the backlog grows. This is what catches `6ae0c80e`.
- `declared-affects` - the file is declared by exactly ONE judged unit. On this repo's mature
  backlog `sprint.py` has 157 declared owners, so this signal is deliberately quiet: of 320
  declared paths only 137 have a single owner. That is a measured limitation, not a claim.

**Measured noise, and the three restrictions that bought it down.** Over the last 200 commits of
this repo: the naive check fires on **92**; reading MODIFICATIONS only (a newly minted artefact is
a filing, not an attribution) takes it to **67**; treating an id reachable within two links of a
named one as named (a `feat(CR0371)` commit touching the stories that deliver CR0371 is the
decomposition working, not a mis-attribution) and skipping messages that name no judged unit at
all takes it to **27**. Each of those three has its own negative-control test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed and delivered as `unnamed_unit_attribution`, advisory at the commit-msg gate |
