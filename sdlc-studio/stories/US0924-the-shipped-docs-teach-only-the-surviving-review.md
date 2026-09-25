# US0924: The shipped docs teach only the surviving review path

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/mutation.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/story-planning.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/templates/audit-profiles/test.md, .claude/skills/sdlc-studio/templates/lessons-seed.jsonl, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-verify.md, .claude/skills/sdlc-studio/reference-decisions.md, .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/reference-schema.md, .claude/skills/sdlc-studio/reference-scripts-create.md, .claude/skills/sdlc-studio/best-practices/testing.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/help/test-spec.md, .claude/skills/sdlc-studio/help/arguments.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py, changelog.d/US0924.md, .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/reference-deploy-readiness.md, .claude/skills/sdlc-studio/reference-code.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/help/help.md, evals/scenarios/06-independence-gate.json, .claude/skills/sdlc-studio/templates/agent-instructions.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer learning the process from the skill's docs
**I want** the help, references and templates to describe one reviewer, green Verify selectors and opt-in mutation and coverage, and nothing that was deleted
**So that** an agent following the docs never reaches for a verb that exits as retired

## Acceptance Criteria

- **AC1:** Given every shipped help/, reference-*.md, best-practices/, SKILL.md and templates/ file, then none instructs a verb, flag, key or field this epic retired (the union of the deletion units' retired surfaces: `plan_review.py`, `critic.py repair`, `critic.py signoff`, `critic.py evidence`, `critic.py sprint-review`, `sprint.py review-batch`, `mutation.py register`, `verify_ac.py testplan`, `verify_ac.py depth`, `sprint.py preflight`, `--from-plan`, `--depth`, `--phase`, `review.two_role_after`, `review.mutation_evidence`, `Verification target`, `Mutation-checked`), except on a line that says it is retired. Fails on: HEAD 013a46d0, where 84 lines across 25 shipped files still name a retired surface (engineering seat's measurement), among them reference-story.md 636-654 (the `Verification target` section), reference-deploy-readiness.md 150, reference-code.md 799, templates/core/bug.md 93 and help/help.md 241, none of which the earlier Affects declared
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_no_shipped_doc_instructs_a_retired_surface
- **AC2:** Given help/mutation.md, then it documents `run`, `yield`, `window` and `prefilter`, states that mutation testing is opt-in and that no gate reads its results, and carries no section describing a ledger a gate lane reads. Fails on: HEAD, whose title calls it 'the executable mutation-check gate' (line 7) and whose 'The ledger - what the gate lane reads' section (85-172) teaches `register` and `retract`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_mutation_help_is_opt_in
- **AC3:** Given the story, story-planning, bug and Definition of Done templates, then none carries a Test Plan, mutation-evidence, verification-depth or per-unit sign-off section, no `Verification target` tier line and no `Mutation-checked` field. Fails on: removing the sections but leaving the per-criterion `Verification target` and `Mutation-checked` lines (story.md 65-103, bug.md 93), which nothing reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_docs.py::ReviewDocsTests::test_the_templates_carry_no_retired_section

## Notes

- Takes the shared prose edits from the deletion units, so no two units merge-conflict on the same doc: `reference-scripts-review.md` (from US0909, US0913, US0914, US0915, US0919 and US0923), `reference-sprint-toolchain.md` (US0911, US0918, US0923), `help/sprint.md` (US0911, US0917, US0918) and `reference-workflow-personas.md` (US0916, US0918, US0919).
- Engineering call: also takes the prose docs the original US0910 listed and neither depth half's criteria read: `reference-bug.md`, `reference-schema.md`, `reference-scripts-create.md`, `reference-test-best-practices.md`, `SKILL.md`, `help/arguments.md` and `help/verify.md`.
- `Mutation-checked` has no reader; only `test_transition.py` names it.
- `best-practices/testing.md` (143) carries a depth-tiers anchor.
- Lands after every deletion unit, because AC1's retired-surface list is the union of theirs.
- - 2026-09-25 re-measure (product seat, 013a46d0): the former AC4 (the bundled lesson seed and the QA amigo template carry no rule requiring mutant registration, a depth tier or a test-plan review) already holds at HEAD: `templates/lessons-seed.jsonl` and `templates/personas/amigos/qa.md` match none of those rules, so the criterion could not fail and is retired (LC-002). Both files stay in Affects only because AC1 scans every template. `templates/agent-instructions.md` is already fixed at HEAD (its review paragraph names `sprint sign`, not `review.two_role_after`); it stays in Affects for AC1's scan only.
- Split: the second half is US0924b (help/epic.md, help/references.md, reference-persona-generate.md). Its phrases are not in AC1's retired list, so neither unit waits on the other.
- `sprint.anchor_status_block`'s 'the two-role gate holds Done' string is code, not a doc; it is left to its own bug.
- `templates/core/bug.md` 93's 'see the regression test fail against the unfixed code' practice is kept as prose; only the `Mutation-checked` field goes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC1 takes the union of the retired surfaces and covers best-practices/; AC3 adds `Verification target` tier lines and `Mutation-checked`; Affects adds the thirteen docs the review named, the four prose docs moved from the split US0910, and the changelog fragment; the shared prose edits of the deletion units land here |
| 2026-09-25 | Claude Opus 5.5 | Affects gains evals/scenarios/06-independence-gate.json, whose EB2 still grades the depth gate US0934 deleted (US0934 review) |
| 2026-09-25 | Claude Opus 5.5 | Affects gains templates/agent-instructions.md, whose review paragraph still teaches `review.two_role_after` holding a unit at Review (US0916 review) |
| 2026-09-25 | sdlc-studio v6 planning | Product seat, Sprint 5/6 planning: Affects adds reference-story.md, reference-deploy-readiness.md, reference-code.md, templates/core/bug.md and help/help.md (engineering seat's re-measure); AC1's union adds the Sprint 5 verbs and the `Verification target`/`Mutation-checked` fields; AC4 retired as already met at HEAD; AC3 covers the bug template; points stay 5; the split's second half is US0924b |
