# US0924: The shipped docs teach only the surviving review path

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/story-planning.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/templates/audit-profiles/test.md, .claude/skills/sdlc-studio/templates/lessons-seed.jsonl, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer learning the process from the skill's docs
**I want** the help, references and templates to describe one reviewer, green Verify selectors and opt-in mutation and coverage, and nothing that was deleted
**So that** an agent following the docs never reaches for a verb that exits as retired

## Acceptance Criteria

- **AC1:** Given every shipped help/, reference-*.md, SKILL.md and templates/ file, then none instructs a verb, flag or key this epic retired (for example `critic.py repair`, `mutation.py register`, `verify_ac.py testplan`, `--from-plan`, `review.two_role_after`), except on a line that says it is retired
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_no_shipped_doc_instructs_a_retired_surface
- **AC2:** Given help/mutation.md, then it documents `run`, `yield`, `window` and `prefilter` and states that mutation testing is opt-in and that no gate reads its results
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_mutation_help_is_opt_in
- **AC3:** Given the story, story-planning and Definition of Done templates, then none carries a Test Plan, mutation-evidence, verification-depth or per-unit sign-off section
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_templates_carry_no_retired_section
- **AC4:** Given the bundled lesson seed and the QA amigo template, then neither carries a rule requiring mutant registration, a depth tier or a test-plan review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_seed_and_qa_template_carry_no_retired_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
