# US0088: Auditability metric: held-back audit quizzes and audit_quiz.py grader

> **Status:** Done
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **CR:** CR-0193
> **Depends on:** US0087

## User Story

**As a** benchmark operator
**I want** a governance/traceability metric scored on outcome answerability, never artifact presence
**So that** the pipeline's auditability claim is measured fairly instead of by construction

## Acceptance Criteria

### AC1: Quizzes are held back and artifact-neutral

- **Given** each fixture's audit/quiz.json + answer_key.json
- **When** `runner.py prepare` builds a workspace
- **Then** no audit/ content is copied; no quiz question names or presupposes an sdlc-studio artifact (arm B can score 100% via README/commits/docstrings/tests)
- **Verify:** pytest tools/tests/test_bench_runner.py -k audit_reference_never_copied
- **Verified:** yes (2026-07-08)

### AC2: Class-D grading proves evidence is real

- **Given** a Class-D question citing a runnable check for requirement R, and its per-question mutant in audit/mutants/
- **When** `audit_quiz.py` grades
- **Then** the citation scores 1 only if the test exists in the workspace, passes on it, and FAILS on the mutant
- **Verify:** pytest tools/tests/test_audit_quiz.py -k class_d
- **Verified:** yes (2026-07-08)

### AC3: Class-T validation rejects fabricated citations

- **Given** an auditor-agent answer {answer, cited_path, cited_quote}
- **When** the validator runs
- **Then** a nonexistent path, a non-verbatim quote, or a fact not matching the answer key each score 0
- **Verify:** pytest tools/tests/test_audit_quiz.py -k class_t
- **Verified:** yes (2026-07-08)

### AC4: Reviewer-independence carries zero weight

- **Given** the scoring configuration
- **When** an audit score is computed
- **Then** reviewer-independence is reported descriptively alongside but contributes 0 to the score
- **Verify:** pytest tools/tests/test_audit_quiz.py -k zero_weight
- **Verified:** yes (2026-07-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0193 | Created via `new` (deterministic) |
