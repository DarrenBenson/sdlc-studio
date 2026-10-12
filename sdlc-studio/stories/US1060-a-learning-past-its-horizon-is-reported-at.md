# US1060: A learning past its horizon is reported at the close until it is revalidated or retired, and the persona review reports memory problems

> **Status:** Draft
> **Delivers:** CR0632
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_horizon.py, changelog.d/US1060.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1058, US1052
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, closing runs whose seats now carry learnings
**I want** `persona_memory.py revalidate` to extend, stamp or retire learnings, the close to name every learning past its horizon, and `persona_review.py check` to report memory problems without blocking
**So that** a learning that stopped being true leaves the briefs, and a memory nobody maintains is visible rather than silently stale

## Acceptance Criteria

- **AC1:** Given a qa learning whose Review-by has passed, when `sprint.py close` runs, then its output names the learning with its persona and horizon and the close's outcome is the same as without it, and after `persona_memory.py revalidate --persona qa --extend M-0001` the next close does not name it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_horizon.py::PersonaMemoryHorizonTests::test_an_expired_learning_is_reported_at_the_close_until_extended
- **AC2:** Given an approved qa learning, when `persona_memory.py revalidate --retire M-0001 --reviewer "Sam Eriksson (qa)" --reason ...` runs, then it exits 2 naming that a seat never retires its own learning, and with `--reviewer "Lena Marsh (product)"` the entry reads retired with the reviewer and reason and `critic.py brief --seat qa` no longer carries it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_horizon.py::PersonaMemoryHorizonTests::test_another_seat_retires_a_contradicted_learning
- **AC3:** Given a memory entry with no Evidence, an entry with no Review-by, and a memory file whose key no card or seat role declares, when `persona_review.py check` runs, then it reports memory-no-evidence, memory-unstamped and memory-orphan as reported, and `persona_resolve.py resolve --seat qa` still frames the qa card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_horizon.py::PersonaMemoryHorizonTests::test_memory_problems_are_reported_never_blocking

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the close refuses on an expired learning (D7 reports memory), or never reads memory, so the learning stays expired unnoticed
- AC2 must fail on: retire keyed on the reviewer's name rather than the seat, or a retired entry left eligible for the brief
- AC3 must fail on: memory problems made blocking, contrary to D7, or memory files skipped by the check
- Serves: Maya Okafor #2.
- Checked at HEAD: `lessons.validity_status` (lessons.py:972) and `revalidate` (:1650) do this for the project lessons log only, and the gate refuses an expired lesson; nothing reads persona memory.
- Adds one close stage, `persona-memory`, to `_CLOSE_CHAIN` (sprint.py:5668) after retro-extract. It always passes; the close-listing and served-goal stories extend it. The paths it writes are close output (CLOSE_OUTPUT_KEY).
- D8: a contradicted learning is retired by the reviewing seat, so `--retire` takes a reviewer from another seat; `--extend` and `--stamp` are mechanical, as in lessons.
- Adds the Memory hygiene rows to the standard page, which the standard story's AC1 test then holds; the rules feed `persona_review.py brief`, so the persona review reports memory as D7 asks.
- Panel cut order: this story can trail the release, its AC3 moving into the store story; no learning can expire until 90 days after the first signed close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
