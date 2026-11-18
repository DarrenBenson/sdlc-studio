# US1241: The review brief names the harness and model to dispatch the reviewer to when the family setting is on

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0698
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_dispatch.py, changelog.d/US1241.md
> **Epic:** EP0341
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The review brief names the harness and model to dispatch the reviewer to when the family setting is on
**So that** CR0698 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: With the setting on, the brief names where to dispatch the reviewer

- **Given** `review.reviewer_family: different` and a unit whose builder's recorded model is known
- **When** `critic.py brief --unit <id> --seat qa` is printed
- **Then** the brief's dispatch line names one harness `lanes.BINARIES` knows and a model of a family other than the builder's, in the form `sprint lane run --harness` takes, and `reference-review.md` describes that line. Fails on: a line naming the builder's own family, or a harness the headless lane cannot run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_dispatch.py::ReviewerFamilyDispatchTests::test_the_brief_names_a_harness_and_model_of_another_family

### AC2: With the setting off, the brief carries no dispatch line

- **Given** the same unit with `review.reviewer_family` unset, and again set to `any`
- **When** `critic.py brief` is printed for each
- **Then** neither brief carries a dispatch line, and both have the text and fingerprint they have with the key absent. Fails on: a dispatch line, or a changed fingerprint, in a project that never opted in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_dispatch.py::ReviewerFamilyDispatchTests::test_no_dispatch_line_when_the_setting_is_any

### AC3: Where no other family can be named, the brief says so

- **Given** `review.reviewer_family: different` and a unit whose builder's model is `unknown`
- **When** `critic.py brief` is printed
- **Then** the brief says no reviewer of a different family can be named and why, and names no harness or model. Fails on: a harness and model named on a guess, which `record` would then refuse
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reviewer_family_dispatch.py::ReviewerFamilyDispatchTests::test_an_unknown_builder_family_names_no_dispatch

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
