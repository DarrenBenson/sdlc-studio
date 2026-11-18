# US1240: With review.reviewer_family set to different, a same-family verdict is refused and an unknown needs a waiver

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0698
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_setting.py, changelog.d/US1240.md
> **Epic:** EP0341
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** With review.reviewer_family set to different, a same-family verdict is refused and an unknown needs a waiver
**So that** CR0698 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The default is any and changes nothing

- **Given** a project that sets no `review.reviewer_family`, with `templates/config-defaults.yaml` and `reference-config.md` both stating the default `any`
- **When** `critic.py record` records a verdict whose reviewer ran on the builder's own model family
- **Then** the row is recorded as it is today, with no family message. Fails on: a default that behaves as `different`, or a default the reference states differently from the shipped file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_setting.py::ReviewerFamilyTests::test_the_default_is_any_and_records_a_same_family_verdict

### AC2: A same-family verdict is refused, naming both models

- **Given** `review.reviewer_family: different`, a unit whose builder's recorded model and whose reviewer's recorded model are two different ids of one family (two `claude-` models), and beside it a unit whose reviewer ran on a model of another family
- **When** `critic.py record` is run for each
- **Then** the first exits non-zero, writes no row and names the builder's model, the reviewer's model and the family they share; the second is recorded. Fails on: a refusal only when the two model ids are identical, a row written and then warned about, or the other-family verdict refused too
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_setting.py::ReviewerFamilyTests::test_a_same_family_verdict_is_refused_naming_both

### AC3: An unknown family is accepted only with a recorded waiver

- **Given** `review.reviewer_family: different` and a verdict whose reviewer model, or whose builder model, is `unknown`
- **When** `critic.py record` is run without a waiver, then again with one
- **Then** the first run refuses and names the waiver that would admit it; the second records the row, and the row carries the waiver so `critic.py show` prints it. Fails on: an unknown family read as different, or a waiver that admits the row and leaves no record of itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_setting.py::ReviewerFamilyTests::test_an_unknown_family_needs_a_recorded_waiver

### AC4: A value that is neither any nor different is refused

- **Given** `review.reviewer_family: diferent` in the project's configuration
- **When** `critic.py record` reads the setting
- **Then** it refuses, naming the key, the value and the two values allowed, and records nothing. Fails on: a misspelt value read as `any`, which turns the gate off without a word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_setting.py::ReviewerFamilyTests::test_an_unrecognised_value_is_refused_not_read_as_any

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
