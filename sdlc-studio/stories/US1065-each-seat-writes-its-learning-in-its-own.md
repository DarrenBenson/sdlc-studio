# US1065: Each seat writes its learning in its own words from a brief carrying its record, and it is recorded as proposed

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py, changelog.d/US1065.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1062, US1063, US1064, US1059
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, running the retro after a run whose seats each reviewed or built several units
**I want** `persona_memory.py learn-brief` to brief each seat, framed by its card, with its own record, its adverse items and its live learnings, and `persona_memory.py propose` to record what it wrote, verbatim, as a proposed learning carrying the evidence its record lists
**So that** the learning is in the seat's own words while its evidence comes from the ledger, so a seat cannot excuse itself with its own account

## Acceptance Criteria

- **AC1:** Given a retro whose batch qa and product reviewed, when `persona_memory.py learn-brief --persona qa --retro RETRO0002` runs, then the brief frames the qa card, carries qa's record from `retro.py seats` with each adverse item and its key and qa's live learnings, says the learning cannot change the card's Non-Negotiables or Authority, and names the file to write, and no line of product's record appears.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_the_learning_brief_carries_only_its_own_seats_record
- **AC2:** Given a file holding the qa seat's learning, when `persona_memory.py propose --persona qa --retro RETRO0002 --from-file <path>` runs, then qa's memory gains one entry with State proposed, Run the retro's run, the body the file's text verbatim and Evidence the ids `retro.py seats` lists for qa rather than ids the file names.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_a_proposal_keeps_the_seats_words_and_the_ledgers_evidence
- **AC3:** Given a seat with no record in the retro (no verdict, no unit built, no adverse item), or a second proposal while qa's first for that run is still proposed, when `persona_memory.py propose` runs, then it exits 2 and memory is unchanged, and once the first is rejected a new proposal is accepted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_propose.py::ProposeLearningTests::test_one_open_proposal_per_seat_and_run

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief embeds the whole seats report, so the seat reads another seat's record, or omits the adverse items the approver will ask about
- AC2 must fail on: evidence taken from the persona's own text (the self-flattering risk RFC0061 names), or the text folded or paraphrased
- AC3 must fail on: one open proposal per seat and run not enforced, or a seat with nothing on record proposes
- Serves: Maya Okafor #3.
- Checked at HEAD: nothing briefs a seat with its own record; `retro.py extract` (retro.py:3535) lifts Try items into the project stores, never per persona.
- D2: a context framed as that persona writes the learning. The learn-brief is that framing, printed by the shipped tool (AGENTS.md: brief with the shipped tool, never by hand); the card is framed through persona_resolve's review render.
- A seat with only later-bug items (charged while it sat the run out) may propose.
- propose copies the file's bytes into the entry body; the run is read as `retro.extract_run` reads it.
- The changelog states the loop's per-close cost, RFC0061's Cost risk: one learn-brief and one approve-brief per seat with a record, about six agent contexts for three seats.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
