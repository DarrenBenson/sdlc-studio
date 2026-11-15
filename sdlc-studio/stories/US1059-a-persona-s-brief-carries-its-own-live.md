# US1059: A persona's brief carries its own live learnings, capped and ranked, and never another persona's

> **Status:** Done
> **Delivers:** CR0632
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_corpus_cache.py, changelog.d/US1059.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1058
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, briefing review seats and builders through the shipped tools on every unit
**I want** critic.py brief, the per-seat goal-review brief and persona_resolve's build, review and consult framings to carry the briefed persona's own live learnings, capped, bounded and ranked by relevance to the unit and then by recency, from one renderer
**So that** a seat that patched one race sequence by sequence is reminded of it on its next brief, and no seat is briefed with another's learnings

## Acceptance Criteria

- **AC1:** Given qa memory holding seven approved learnings (one with a 5,000-character body), one proposed and one past its Review-by, and product memory holding two approved, when `critic.py brief --unit US0001 --seat qa` runs, then the brief carries five qa learnings and none of product's, omits the proposed and the expired one, says two more were withheld by the cap and one is past its horizon, and carries the long learning as its id, title and a gist of at most 200 characters.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_the_review_brief_carries_its_own_seats_capped_bounded_learnings
  - **Verified:** yes (2026-11-15)
- **AC2:** Given two approved qa learnings, an older one whose evidence cites US0005 (Affects `scripts/a.py`) and a newer one citing US0006 (Affects `docs/x.md`), when `critic.py brief --unit US0001` runs for a unit whose Affects include `scripts/a.py`, with `personas.memory.inject_max: 1`, then the older, relevant one is carried.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_a_learning_whose_evidence_shares_the_units_files_outranks_a_newer_one
  - **Verified:** yes (2026-11-15)
- **AC3:** Given the same memory files, when `persona_resolve.py resolve --seat qa --render build` and `resolve-consult --role qa` run, then each carries qa's learnings in a block labelled with its render and neither carries another seat's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_every_persona_resolve_framing_carries_its_own_seats_learnings
  - **Verified:** yes (2026-11-15)
- **AC4:** Given a qa memory file that cannot be parsed, and a project with no qa memory file, when `critic.py brief --seat qa` runs on each, then the first brief says qa's learnings could not be read, naming the file, and the second says none are recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_unreadable_and_absent_memory_are_told_apart
  - **Verified:** yes (2026-11-15)

## Notes

- Run thirteen grooming (D0479):
  - AC1 must fail on: the renderer reads every memory file, applies no cap, injects proposed or expired learnings, or injects a body verbatim
  - AC2 must fail on: ranking by recency alone, or relevance read from a field no writer sets
  - AC3 must fail on: injection wired into critic.brief only, so a builder or a consult is framed without its memory
  - AC4 must fail on: an unreadable file read as no learnings
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 4 (the cause reaches the next brief); End goal 6 (cap keeps the brief small).
  - Soft dependency on US1036 broken: the goal-review `--seat` brief is dropped from AC3 (US1036 itself needs BG1002 and BG1015, both Open). The renderer is `persona_memory.digest/render`, which US1036's later work can call. sprint.py removed from Affects accordingly.
  - Five ACs merged to four (the 200-char gist folded into AC1).
  - Pinning tests added: `test_persona_resolve.py`, `test_lane_builder_brief.py`, the two critic brief tests.
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the renderer reads every memory file, applies no cap, or filters on the file alone, so proposed or expired learnings reach the brief
- AC2 must fail on: ranking by recency alone, or relevance read from a field no writer sets
- AC3 must fail on: injection wired into critic.brief only, so a builder, a consult or a goal-review seat is framed without its memory
- AC4 must fail on: an unreadable file read as no learnings, so a brief that lost them cannot be told from one that has none
- AC5 must fail on: the verbatim body injected, so one long learning outweighs the criteria the brief exists to carry
- Serves: Maya Okafor #3.
- Checked at HEAD (fixture probe): `critic.brief` (critic.py:2527) carries the project's failure classes through `_lessons_block` (:2358) and points at the card path; `persona_resolve.frame` (persona_resolve.py:261) appends the card body; neither reads a persona-scoped record.
- One renderer, `persona_memory.digest(root, key, affects)` and `render(digest)`, mirroring `lessons.phase_digest` (lessons.py:1864) and `render_phase` (:1877): capped, says how many it withheld and why, reports an unreadable store rather than dropping it. Cap `personas.memory.inject_max`, default 5 (the lessons' INJECT_MAX).
- Live, here: State approved and within its horizon. The signature story narrows it to learnings a signed close has listed and nobody struck. No approval path exists until the approve story, so nothing is live in the gap; build the approve, close-listing and signature stories in one run.
- Relevance is derived (LL0034), with no field to write: a learning is relevant to a unit when a unit its evidence cites shares an Affects path with it. A brief with no unit (consult, goal review) ranks by recency.
- Wired through US1036's `persona_resolve.review_card`, its stated hook for D5, and through `frame`, which gains a keyword-only `root=None` so the positional callers (test_amigo_consult.py:288, test_persona_resolve.py:70, :77, :218) keep working. The block sits inside the fingerprinted text, as the lessons block does.
- D5 named a brief-size spike: the story records the critic brief's size for a seat with no memory and with a full cap, in its Resolution.
- Shares persona_resolve and the goal-review brief with US1037; whichever lands second rebases.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1058 and US1036 (Draft)
- Its own note says to build it in one run with US1066, US1067 and US1068, so nothing goes live before the signature gate
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, criteria rewritten to four or fewer, notes |
