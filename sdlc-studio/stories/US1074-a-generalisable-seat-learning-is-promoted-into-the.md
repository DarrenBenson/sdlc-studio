# US1074: A generalisable seat learning is promoted into the skill source's shipped amigo card, and refused into an installed copy

> **Status:** Draft
> **Delivers:** CR0634
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_promote.py, changelog.d/US1074.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1068, US1002
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, starting a new project on the shipped default seats
**I want** a generalisable seat learning from a project like mine to reach the shipped amigo card's Learned section through `persona_memory.py promote`, written into the skill source checkout as `lessons add --global` writes a lesson, and refused into an installed copy
**So that** my next project's default seats start with what earlier projects' seats learned, by a deliberate, committed change and never by a write the next skill update deletes

## Acceptance Criteria

- **AC1:** Given a live qa learning and a fixture skill source checkout (install.sh and tools/validate_skill.py present, `templates/personas/amigos/qa.md` tracked), when `persona_memory.py promote --id M-0001 --source-dir <checkout>` runs, then the checkout's qa card gains the learning under `## Learned` with the origin 'a consuming project', `git status` in the checkout shows the card modified, and the memory entry reads promoted with the path and date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_promote.py::PromoteLearningTests::test_promotion_writes_the_source_checkouts_amigo_card
- **AC2:** Given no `--source-dir` and no `skill_source_repo`, so the destination is the running skill and that is an installed copy without the source markers, when `persona_memory.py promote` runs, then it exits non-zero with the remedies `lessons add --global` prints and no card or memory file changes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_promote.py::PromoteLearningTests::test_promotion_into_an_installed_copy_is_refused
- **AC3:** Given a learning whose text carries a word on the checkout's neutrality blocklist, and a live learning of a project-declared sre seat, when `persona_memory.py promote` runs on each, then the first is refused through the checkout's `check_neutrality.py --stdin` naming the Learned text, the second naming the shipped roles, and nothing is written.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_promote.py::PromoteLearningTests::test_an_unneutral_or_unshipped_role_learning_is_refused

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the origin defaulted to the working directory's name (BG1016's leak), or the memory entry left unmarked so one learning is promoted twice
- AC2 must fail on: the write made into the installed copy, which the next skill update replaces wholesale
- AC3 must fail on: the neutrality check left to file_finding alone, or an sre learning written to a card the skill does not ship
- Serves: Maya Okafor #1 (ship through a disciplined lifecycle).
- D9: deliberate promotion only, never automatic.
- Checked at HEAD: `lessons add --global` resolves and refuses its destination (`resolve_global_dir` lessons.py:339, `untracked_reason` :287, `is_skill_source_checkout` :317) for the lessons registry only; nothing writes into an amigo card.
- `untracked_reason` and `is_skill_source_checkout` take the file they guard (the amigo card instead of `_index.md`), so both promotions share one rule (LL0016).
- Only live learnings (approved, listed by a signed close, not struck) of the shipped roles (engineering, qa, product) are promotable. The neutrality call follows US1002's `--stdin` contract; the neutral default origin is what BG1016 asks of lessons.
- The promoted card is then owed a persona review in the skill repository, which the owed-review story names. First to shed if the release must shrink.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
