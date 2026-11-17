# US1243: The prompt audit of the instruction files is committed, each finding dispositioned and each kept gate named

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0700
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/change-requests/CR0700-the-agent-instruction-files-and-shipped-templates-are.md, tools/tests/test_prompt_audit_evidence.py, changelog.d/US1243.md
> **Epic:** EP0342
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The prompt audit of the instruction files is committed, each finding dispositioned and each kept gate named
**So that** CR0700 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The audit is committed with every finding fully stated

- **Given** CR0700's file, holding the prompt audit run with Opus 5.5 named as the target model over the files its Summary scopes
- **When** the audit's findings table is read
- **Then** every row states a file and line, the audited text quoted, the pattern, why it is obsolete and a confidence of high, medium or low; every file in scope has at least one row or a line saying the audit found nothing in it; and each audited file's size in characters at the audit is recorded. Fails on: a row missing a field, a scoped file the audit never mentions, or a target model other than Opus 5.5
- **Verify:** pytest tools/tests/test_prompt_audit_evidence.py::PromptAuditEvidenceTests::test_every_finding_states_file_line_text_pattern_reason_and_confidence

### AC2: Every finding is dispositioned, and a kept rule names what it guards

- **Given** the same table
- **When** each row's disposition is read
- **Then** each is `changed`, `removed` or `kept`; each kept row names the gate or the current failure it guards; and the five rules the Summary calls deliberate (no hook bypass, the worktree HOME guard, the signing rules, Affects-only staging and the builder's no-progress-message line) are each a kept row. Fails on: an undispositioned row, a kept row with no gate or failure, or a deliberate rule dispositioned as removed
- **Verify:** pytest tools/tests/test_prompt_audit_evidence.py::PromptAuditEvidenceTests::test_every_finding_is_dispositioned_and_kept_rules_name_their_gate

### AC3: Every accepted change names the story that carries it

- **Given** the rows dispositioned `changed` or `removed`
- **When** each row's carrying story is read
- **Then** each names US1244, US1245 or US1246, and the file it cites is in that story's Affects. Fails on: an accepted change no story carries, or one assigned to a story that cannot stage its file
- **Verify:** pytest tools/tests/test_prompt_audit_evidence.py::PromptAuditEvidenceTests::test_every_accepted_change_names_a_story_that_can_stage_it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
