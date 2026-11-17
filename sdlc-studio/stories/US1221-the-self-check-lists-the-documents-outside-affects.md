# US1221: The self-check lists the documents outside Affects that name what the diff changed and needs a ruling on each

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0682
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py
> **Epic:** EP0333
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The self-check lists the documents outside Affects that name what the diff changed and needs a ruling on each
**So that** CR0682 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The self-check lists the documents outside Affects that name what changed

- **Given** a fixture of BG1236: a unit whose diff removes a long flag from a script, and a line of reference-sprint.md outside its Affects that still names that flag
- **When** `critic.py brief` prints the author self-check steps for the unit
- **Then** the steps list that reference page with the line that names the flag, under the documents that name what changed; a help page naming the changed script's basename is listed the same way. Fails on: steps that list no document outside Affects
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::DocsNamingTheChangeTests::test_a_stale_reference_line_outside_affects_is_listed

### AC2: Each listed document needs a ruling before the self-check records

- **Given** the same unit, with two documents listed
- **When** `critic.py self-check record` is given a claims file ruling one of them, and then one ruling both
- **Then** the first is refused naming the document with no ruling and writes nothing; the second is recorded. Fails on: a self-check recorded while a listed document is unruled
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::DocsNamingTheChangeTests::test_a_listed_document_with_no_ruling_refuses_the_record

### AC3: Documents inside Affects, and a diff that changes no script or flag, list nothing

- **Given** a unit whose Affects holds the reference page that names its flag, and a unit whose diff changes prose only
- **When** `critic.py brief` prints the steps and `critic.py self-check record` is run for each
- **Then** neither lists a document outside Affects and neither record asks for a document ruling. Fails on: a document the unit already changes listed again, or every reference page listed for a unit that changed no script
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::DocsNamingTheChangeTests::test_nothing_is_listed_for_affects_docs_or_a_prose_only_diff

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
