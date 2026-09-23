# US0873: A verdict is written by one set of rules, and parallel writers never lose a row

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py
> **Epic:** EP0260
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator relying on review verdicts
**I want** every verdict written by one set of rules, with no row lost when reviewers run in parallel
**So that** the review record can be trusted as evidence

## Acceptance Criteria

- **AC1:** Given transition set with --verdict lgtm, when it runs, then it is refused naming the allowed verdicts and nothing is written to the ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py::VerdictVocabularyTests::test_an_unknown_verdict_word_is_refused
- **AC2:** Given transition set with --verdict APPROVE whose transition is then refused by a gate, when it runs, then no verdict row remains
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py::VerdictVocabularyTests::test_a_refused_transition_leaves_no_verdict
- **AC3:** Given 8 concurrent critic record calls for different units against one ledger, when all complete, then the ledger holds all 8 rows and still parses
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py::LedgerConcurrencyTests::test_concurrent_verdicts_are_all_kept
- **AC4:** Given 8 concurrent verify-report writes for different stories, when all complete, then all 8 entries are present
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py::LedgerConcurrencyTests::test_concurrent_verify_reports_are_all_kept

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
