# US0480: validate ratchets the footprint and criterion warnings against a baseline derived from the corpus

> **Status:** Draft
> **Delivers:** CR0443
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0173
> **Points:** 5

## User Story

**As a** maintainer who stopped reading validate's output
**I want** the 398 standing warnings held at a baseline so a new one fails
**So that** a defect introduced today is visible, instead of being the 399th line of a report nobody reads

## Acceptance Criteria

### AC1: a new instance fails while the baselined ones pass

- **Given** a corpus whose recorded baseline holds the current affects-undeclared, affects-unresolvable and pseudo-verify counts
- **When** a unit is added carrying one new affects-undeclared instance
- **Then** the check exits non-zero naming that unit, while every pre-existing instance passes unremarked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_a_new_instance_fails_while_the_baseline_passes

### AC2: the baseline is counted from the corpus, never read from a stored total

- **Given** a baseline recorded earlier and a corpus that has since had instances repaired
- **When** the check runs
- **Then** the expected count is recomputed from the files and the repaired instances lower the baseline, so a stale stored number cannot license a regression
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_the_baseline_is_counted_not_stored

### AC3: each warning kind ratchets separately

- **Given** a commit that repairs two pseudo-verify instances and introduces one affects-undeclared
- **When** the check runs
- **Then** it fails on the affects-undeclared kind, because a kind paid down elsewhere cannot mask a regression in another
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_each_kind_ratchets_separately

### AC4: a baseline that cannot be computed fails loud

- **Given** a run in which the corpus cannot be enumerated
- **When** the check runs
- **Then** it exits non-zero saying it could not establish a baseline, never passing on an empty count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::WarningRatchetTests::test_an_uncomputable_baseline_fails_loud

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
