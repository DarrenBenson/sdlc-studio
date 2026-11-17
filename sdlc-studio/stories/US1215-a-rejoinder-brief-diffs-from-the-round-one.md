# US1215: A rejoinder brief diffs from the round one verdict's commit and leaves out the file history

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py
> **Epic:** EP0331
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A rejoinder brief diffs from the round one verdict's commit and leaves out the file history
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A rejoinder's diff starts at the round one verdict's commit

- **Given** a unit with a REJECT recorded at one commit and a repair committed after it
- **When** `critic.py brief --unit <id> --seat qa --rejoinder` is run
- **Then** the UNIT DIFF names the round one verdict's commit as its base and holds the repair's hunks only. Fails on: a hunk that was already present at the round one commit carried again
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_rejoinders_diff_excludes_hunks_present_at_round_one

### AC2: A rejoinder leaves out the file history and keeps the round one tier

- **Given** a unit rejected at the full tier whose plain brief would now be issued at the light tier
- **When** `critic.py brief --unit <id> --seat qa --rejoinder` is run
- **Then** the brief has no FILE HISTORY section, and it keeps the quoted prior verdict with the demand to rule on each of its findings, the VERIFY COMMAND and the acceptance criteria, at the full tier. Fails on: a FILE HISTORY section in a rejoinder, or a round two briefed at a lighter tier than round one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_rejoinder_omits_file_history_and_keeps_the_round_one_tier

### AC3: With no round one commit to read, the rejoinder says so and carries the unit's own diff

- **Given** a unit whose REJECT row names no commit, and a unit whose round one commit is no longer in the history
- **When** `critic.py brief --unit <id> --seat qa --rejoinder` is run for each
- **Then** each brief carries the unit's diff from the unit's own base and one line saying the round one commit could not be read. Fails on: an empty diff printed as no change since the base, or a traceback
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_no_round_one_commit_falls_back_to_the_units_base_and_says_so

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
