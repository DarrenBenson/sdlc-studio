# US1202: The critic brief prints the author's recorded mutants and their replay, labelled as the author's

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0673
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, tools/check_budgets.py, changelog.d/US1202.md
> **Epic:** EP0327
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The critic brief prints the author's recorded mutants and their replay, labelled as the author's
**So that** CR0673 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The brief prints the author's mutants and their replay, labelled as the author's

- **Given** a unit whose recorded self-check carries a list of three mutants from the runner
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the brief carries a section labelled as the author's recorded mutants, listing each mutant with its recorded verdict and the verdict the runner's replay gives it now. Fails on: a brief that names only the counts, or prints the recorded verdict in place of a replay it never ran
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefAuthorMutantsTests::test_the_brief_lists_the_authors_mutants_with_their_replay
- **Verified:** yes (2026-11-19)

### AC2: A replay that disagrees with the record is marked

- **Given** the same unit after a change that makes one mutant recorded as killed survive
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** that mutant's line shows recorded killed and replayed survived and is marked as a disagreement, while the other two lines agree. Fails on: a stale kill passed on to the reviewer as current
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefAuthorMutantsTests::test_a_replay_that_disagrees_with_the_record_is_marked
- **Verified:** yes (2026-11-19)

### AC3: The author's replayed mutants are not the reviewer's own pass

- **Given** a full-tier brief for the unit, a brief for a unit whose self-check recorded no mutant list, and `reference-review.md`
- **When** each is read
- **Then** the full-tier brief says the replayed list is the author's and does not count as the reviewer's own mutation pass, and still carries the practice to mutate the author's tests; the second brief says no mutant list was recorded and is issued as before; `reference-review.md` states the same rule. Fails on: a brief that lets a replay of the author's mutants stand in for the reviewer's own, or one refused for want of a mutant list
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefAuthorMutantsTests::test_the_replay_is_never_counted_as_the_reviewers_own_pass
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
