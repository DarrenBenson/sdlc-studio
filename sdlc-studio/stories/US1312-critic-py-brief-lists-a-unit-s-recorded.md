# US1312: `critic.py brief` lists a unit's recorded app evidence paths, and none without failing when it has no app criterion

> **Status:** Draft
> **Depends on:** US1311
> **Risk-class:** standard
> **Delivers:** CR0738
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_app_evidence.py, changelog.d/US1312.md
> **Epic:** EP0375
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `critic.py brief` lists a unit's recorded app evidence paths, and none without failing when it has no app criterion
**So that** CR0738 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The brief lists the app evidence for the reviewer to open

- **Given** a unit whose app criterion passed and recorded two evidence files
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the brief lists both paths under one heading and tells the reviewer to open them before judging the criterion. Fails on: paths omitted, or listed without the criterion they belong to
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_app_evidence.py::BriefEvidenceTests::test_the_brief_lists_recorded_app_evidence

### AC2: No app criterion, no section; an unrun one says so

- **Given** one unit with no app criterion and one whose app criterion has no recorded run
- **When** a brief is printed for each
- **Then** the first has no evidence section and does not fail; the second says the app check has not run. Fails on: an empty heading on every brief, or a brief that fails for want of evidence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_app_evidence.py::BriefEvidenceTests::test_a_unit_without_app_evidence_gets_no_section_and_no_failure

## Notes

- Keep the addition small: briefs are counted against the context budget (RFC0062).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
