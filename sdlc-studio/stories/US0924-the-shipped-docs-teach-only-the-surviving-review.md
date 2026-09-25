# US0924: The shipped docs teach only the surviving review path

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/story-planning.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/templates/audit-profiles/test.md, .claude/skills/sdlc-studio/templates/lessons-seed.jsonl, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-decisions.md, .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/best-practices/testing.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/help/test-spec.md, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py, changelog.d/US0924.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer learning the process from the skill's docs
**I want** the help, references and templates to describe one reviewer, green Verify selectors and opt-in mutation and coverage, and nothing that was deleted
**So that** an agent following the docs never reaches for a verb that exits as retired

## Acceptance Criteria

- **AC1:** Given every shipped help/, reference-*.md, best-practices/, SKILL.md and templates/ file, then none instructs a verb, flag or key this epic retired (the union of the deletion units' retired surfaces, for example `plan_review.py`, `critic.py repair`, `critic.py signoff`, `mutation.py register`, `verify_ac.py testplan`, `verify_ac.py depth`, `sprint.py preflight`, `--from-plan`, `--depth`, `review.two_role_after`, `review.mutation_evidence`), except on a line that says it is retired. Fails on: HEAD, where 158 lines across 30 shipped files name a retired surface
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_no_shipped_doc_instructs_a_retired_surface
- **AC2:** Given help/mutation.md, then it documents `run`, `yield`, `window` and `prefilter` and states that mutation testing is opt-in and that no gate reads its results
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_mutation_help_is_opt_in
- **AC3:** Given the story, story-planning and Definition of Done templates, then none carries a Test Plan, mutation-evidence, verification-depth or per-unit sign-off section, no `Verification target` tier line and no `Mutation-checked` field. Fails on: removing the sections but leaving the per-criterion `Verification target` and `Mutation-checked` lines, which nothing reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_templates_carry_no_retired_section
- **AC4:** Given the bundled lesson seed and the QA amigo template, then neither carries a rule requiring mutant registration, a depth tier or a test-plan review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_seed_and_qa_template_carry_no_retired_rule

## Notes

- Takes the shared prose edits from the deletion units, so no two units merge-conflict on the same doc: `reference-scripts-review.md` (from US0909, US0913, US0914, US0915, US0919 and US0923), `reference-sprint-toolchain.md` (US0911, US0918, US0923), `help/sprint.md` (US0911, US0917, US0918) and `reference-workflow-personas.md` (US0916, US0918, US0919).
- Engineering call: also takes the prose docs the original US0910 listed and neither depth half's criteria read: `reference-bug.md`, `reference-schema.md`, `reference-scripts-create.md`, `reference-test-best-practices.md`, `SKILL.md`, `help/arguments.md` and `help/verify.md`.
- `Mutation-checked` has no reader; only `test_transition.py` names it.
- `best-practices/testing.md` (143) carries a depth-tiers anchor.
- Lands after every deletion unit, because AC1's retired-surface list is the union of theirs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC1 takes the union of the retired surfaces and covers best-practices/; AC3 adds `Verification target` tier lines and `Mutation-checked`; Affects adds the thirteen docs the review named, the four prose docs moved from the split US0910, and the changelog fragment; the shared prose edits of the deletion units land here |
