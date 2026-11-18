# US1239: Each recorded verdict states the reviewer's model and harness, or unknown where the store gives neither

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0698
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_reviewer_model.py, changelog.d/US1239.md
> **Epic:** EP0341
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Each recorded verdict states the reviewer's model and harness, or unknown where the store gives neither
**So that** CR0698 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A bound row names the reviewing agent's model and harness

- **Given** a Claude Code session store in which the briefed reviewer agent wrote the unit's verdict file, its transcript naming the model that answered, and a main thread that ran on a different model
- **When** `critic.py record --from-verdict` binds the row
- **Then** the row's `Source` cell carries, after the writer tokens, the harness and the model id that agent's own transcript names, and `critic.py show` prints both. Fails on: a row naming the main thread's model, or a model from configuration, in place of the reviewing agent's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_reviewer_model.py::ReviewerModelTests::test_a_bound_row_names_the_reviewing_agents_model_and_harness

### AC2: A store that gives neither records unknown, and still records

- **Given** a verdict file recorded under a harness whose session store is not read for provenance, and separately a Claude Code transcript whose records name no model
- **When** `critic.py record --from-verdict` binds each row
- **Then** each row is written, exit 0, and states the reviewer's model as `unknown` (and the harness as `unknown` where none was chosen), with the reason on the line `record` prints. Fails on: a guessed model written where none was read, a blank in place of `unknown`, or `record` refusing the verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_reviewer_model.py::ReviewerModelTests::test_a_store_giving_no_model_records_unknown

### AC3: A row recorded before the tokens existed reads as unknown and keeps its identity

- **Given** a delivery ledger holding rows recorded before this unit, some with a `Source` of `-` and some with writer tokens only
- **When** the reviewer's model is read back from each row through the one reader `critic.py` exposes for it
- **Then** each reads as model `unknown` without error, and `row_identity` of every such row is what it was before the change. Fails on: an older row raising or being rewritten, or a row identity a signed run record froze moving
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_reviewer_model.py::ReviewerModelTests::test_an_older_row_reads_unknown_and_its_identity_holds

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
