# US1059: A persona's brief carries its own live learnings, capped and ranked, and never another persona's

> **Status:** Draft
> **Delivers:** CR0632
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py, changelog.d/US1059.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1058, US1036
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, briefing review seats and builders through the shipped tools on every unit
**I want** critic.py brief, the per-seat goal-review brief and persona_resolve's build, review and consult framings to carry the briefed persona's own live learnings, capped, bounded and ranked by relevance to the unit and then by recency, from one renderer
**So that** a seat that patched one race sequence by sequence is reminded of it on its next brief, and no seat is briefed with another's learnings

## Acceptance Criteria

- **AC1:** Given qa memory holding seven approved learnings, one proposed and one past its Review-by, and product memory holding two approved, when `critic.py brief --unit US0001 --seat qa` runs, then the brief carries five qa learnings and none of product's, omits the proposed and the expired one, and says two more were withheld by the cap and one is past its horizon.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_the_review_brief_carries_its_own_seats_capped_learnings
- **AC2:** Given two approved qa learnings, an older one whose evidence cites US0005 (Affects `scripts/a.py`) and a newer one whose evidence cites US0006 (Affects `docs/x.md`), when `critic.py brief --unit US0001` runs for a unit whose Affects include `scripts/a.py`, with `personas.memory.inject_max: 1`, then the older, relevant one is carried.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_a_learning_whose_evidence_shares_the_units_files_outranks_a_newer_one
- **AC3:** Given the same memory files, when `persona_resolve.py resolve --seat qa --render build`, `resolve-consult --role qa` and `sprint.py goal-review brief --seat product` run, then the first two carry qa's learnings and the third product's, each block labelled with the render it came from, and none carries another seat's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_every_framing_carries_its_own_seats_learnings
- **AC4:** Given a qa memory file that cannot be parsed, and a project with no qa memory file, when `critic.py brief --seat qa` runs on each, then the first brief carries a line saying qa's learnings could not be read, naming the file, and the second a line saying none are recorded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_unreadable_and_absent_memory_are_told_apart
- **AC5:** Given an approved qa learning whose body is 5,000 characters, when `critic.py brief --seat qa` runs, then the learning is carried as its title and a gist of at most 200 characters naming its id, never the whole body.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_brief.py::PersonaMemoryBriefTests::test_a_long_learning_is_carried_as_a_bounded_gist

## Notes

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
