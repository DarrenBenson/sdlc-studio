# US0906: The review seats push back on a check that earns nothing

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, sdlc-studio/personas/seats/qa.md, .claude/skills/sdlc-studio/templates/personas/amigos/engineering.md, .claude/skills/sdlc-studio/templates/personas/amigos/product.md, .claude/skills/sdlc-studio/templates/personas/amigos/qa.md, .claude/skills/sdlc-studio/templates/lessons-seed.jsonl, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_seats.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer whose agents plan and review her work
**I want** the engineering, QA and product seats, here and in the shipped templates, to challenge a new check that names no yield or retirement
**So that** the process earns its keep and does not become the work, in this repository and in every project that installs the skill

## Acceptance Criteria

- **AC1:** Given `persona_resolve.py resolve --seat engineering --render review` in this repository and in a greenfield project that falls back to the shipped amigo templates, then the charter pushes back on a new check, refusal, baseline or pin that names no measured yield or retired constraint, and prefers fixing the failing code path
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seats.py::RatchetWatchTests::test_engineering_pushes_back_on_an_unearned_check
  - **Verified:** yes (2026-09-24)
- **AC2:** Given the same for the qa and product seats, then QA asks whether a check has ever caught a real defect and flags a lane whose refusals caught none, and Product pushes back when a unit serves the machinery rather than a persona goal - in both sources
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seats.py::RatchetWatchTests::test_qa_and_product_watch_the_ratchet
  - **Verified:** yes (2026-09-24)
- **AC3:** Given a greenfield project with no lesson store, then `lessons.py classes` lists LC-007 and LC-008 from the bundled seed with no hits, and a plan and a review brief carry LC-008
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::SeedFallbackTests::test_the_seed_carries_the_ratchet_class
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
