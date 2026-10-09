# RFC-0061: Personas become accountable team members: each keeps its own memory, learns from its own verdicts at the retro, and passes a persona review before it is trusted

> **Status:** Draft
> **Size:** XL
> **Date:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T07:42:25Z

## Summary

Personas are among the system's most valuable assets, and they are used as static cards. A review seat (engineering, product, QA) is rendered from its card into each brief and forgets everything when the brief ends; a user persona (Maya, Jonah, Trevor) is read at planning and then sits still. Nothing a persona gets right or wrong changes how it works next time: every learning goes to the project's lessons, never to the persona whose judgement it was.

This RFC proposes that each persona keeps its own committed memory of learnings with evidence; that the retro scores each seat's verdicts against what then happened and the persona records, in its own words, what it will do differently; that its brief carries its own learnings back to it; and that a thorough persona review holds every card and every memory to a standard of format, evidence and consistency before it is trusted, on creation, on change and on a cadence.

## Context & Problem

- **A persona repeats its own mistakes.** On 2026-10-08 the engineering seat authored BG0993 and the QA seat rejected it four times; each round found another ordering of the same race, because the author kept patching with a proxy (a reopen count) instead of modelling the concurrency. Nothing records "this seat patches races sequence by sequence" against the engineering seat, so its next brief carries no trace of it. The project lessons log records the lesson for everyone, which is to say for no one in particular.
- **Seats carry the review load; user personas mostly decorate.** Three consuming projects' agents assessed the skill on 2026-10-08 (relayed by the operator): seats caught real defects, while personas were "useful as constraints and useless as reviewers", their Persona Reference sections were copied boilerplate (CR-0623), a seat card still argued for a primary persona the project had demoted (CR-0625), and persona goals were never checked (CR-0621).
- **Nothing holds a persona to a standard.** `validate seats` checks a card's role comment, headings, a demographic denylist and provenance; `validate personas` checks well-formedness. Nothing checks that a card's content is evidenced, current, consistent with the cast, testable where it claims goals, or that it earns its place.
- **The mechanisms exist elsewhere.** The lessons system already has committed logs (LL0029), validity horizons, revalidation at the close, phase-scoped injection into briefs and promotion across projects; the verdict ledger already records which seat said what about which unit. Personas can reuse both rather than invent a parallel world.

## Goals / Non-Goals

**Goals**

- Each persona has its own memory: learnings with evidence and a validity horizon, committed beside its card, so every clone and machine reads the same.
- A persona learns from its own record. At the retro, each seat's verdicts are scored against what followed (an APPROVE on a unit later found defective, a REJECT finding later overturned, a defect found only in a later round, a closing-review or operator finding), and the persona, briefed with that evidence, writes what it will do differently in its own words.
- A persona's brief carries its own learnings back to it, bounded and ranked, beside the project lessons it already gets.
- A persona review: a defined standard (format, evidence, testable goals, consistency with the cast and with the other seats, freshness, memory hygiene) and a ceremony that applies it independently, on creation, on change and on a cadence, with an outcome a reader can see.
- User personas learn too, from usage evidence (stakeholder feedback, served-goal outcomes), not only seats.

**Non-Goals**

- No persona rewrites its own Non-Negotiables or Authority unreviewed: memory proposes, review disposes.
- No hidden or uncommitted state: a persona's memory is a reviewed artefact, never `.local`.
- No cross-project sharing by default; promotion to the skill's shipped amigos is a deliberate act, as `lessons add --global` is.
- Not a replacement for the project lessons log or the failure classes; a learning about the process stays there.

## Design Options

### Option A - Learnings on the card

A `## Learnings` section on each persona card, appended at the retro by a tool and reviewed as a card change. Simplest, and the card stays the one file. But the card grows without bound, identity and experience change in the same diff, and every learning re-opens a reviewed card.

### Option B - A memory file beside each card

`sdlc-studio/personas/memory/<persona>.md`, owned by a tool (`persona_memory.py add | list | recall | revalidate | prune`) with validity horizons like the lessons log, injected into that persona's brief by `persona_resolve` (render-phase style, bounded and ranked). The card stays the stable, reviewed identity; the memory evolves under its own lighter review. The retro proposes candidate learnings per persona from the verdict ledger and the persona writes them.

### Option C - Owned lessons

Reuse the lessons machinery: a lesson or failure class carries `owner: <persona>` and brief injection filters by owner. Least new machinery; but it mixes the project's learnings with one persona's judgement, gives a persona no identity-level standard, and makes persona review a filter rather than a ceremony.

## Recommendation

**Option B, reusing C's mechanics.** A memory file per persona keeps identity (the card) and experience (the memory) apart, so each can be reviewed at its own weight; the lessons system's horizons, revalidation and phase injection are reused rather than rebuilt. Build the persona review first: it is the standard every later learning is held to, and it pays off on its own.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Where memory lives | A card section, B memory file, C owned lessons | Operator | Decide at `rfc decide` | Open |
| D2 | Who writes a learning | the persona, briefed with its evidence; the retro facilitator; the operator | Operator | Consult the seats | Open |
| D3 | Who approves a learning | the operator; another seat; automatic with a later review | Operator | Consult the seats | Open |
| D4 | What evidence feeds learning | verdict outcomes, rounds to converge, operator rulings, closing-review and consuming-project findings | Engineering seat | Spike against this repo's ledger | Open |
| D5 | How memory reaches the persona | every brief (bounded, ranked) or recalled on demand | Engineering seat | Spike: measure brief size | Open |
| D6 | Scope | seats only, or user personas too | Operator | Decide at `rfc decide` | Open |
| D7 | Persona review strength and cadence | blocking (a failing persona cannot be resolved into a brief) or advisory; on change, per release, every N sprints | Operator | Decide at `rfc decide` | Open |
| D8 | Forgetting | horizon and revalidation, a cap on injected learnings, how contradictions resolve | QA seat | Consult | Open |
| D9 | Cross-project promotion | none; or promote generalisable learnings to the shipped amigos as `lessons add --global` does | Operator | Decide at `rfc decide` | Open |

## Architecture Impact

- New: `sdlc-studio/personas/memory/`, `scripts/persona_memory.py`, a persona-review ceremony and its standard (a best-practices page and validator checks).
- Changed: `persona_resolve.py` (render a persona's learnings into its brief), `critic.py` (the verdict ledger as learning evidence; a brief carries the seat's learnings), `retro.py` (a per-persona learning step), `validate.py` (`seats`, `personas` and memory checks), the persona and seat templates, `reference-persona.md`, `reference-workflow-personas.md`, `help/persona.md`.
- Depends on verdicts being recorded as the reviewer wrote them (CR-0619) and on authorised rounds being recordable (BG1003); otherwise learning reads a transcription.

## Risks

- **Memory as noise.** Unbounded or unreviewed learnings bloat briefs and teach seats to skim. Mitigation: horizons, a cap, ranking, and review.
- **Self-flattering memory.** A persona writing its own learnings may excuse itself. Mitigation: the evidence is the ledger, not the persona's account; another seat or the operator approves.
- **Drift from the standard.** A persona that learns may stray from its role. Mitigation: Non-Negotiables and Authority are card-level and never edited by memory; the persona review checks memory against the card.
- **Cost.** A per-persona retro step and a review ceremony add work to every close. Mitigation: candidate learnings are derived mechanically; the review cadence is configurable.

## Phased Plan / Workstreams

1. **Persona review.** The standard (format, evidence, testable goals, cast consistency, freshness), validator checks, and an independent review ceremony with a visible outcome. Folds in CR-0623 and CR-0625.
2. **Seat memory.** The memory store and tool, validity horizons, and injection into the seat's own brief.
3. **The learning loop.** The retro scores each seat's verdicts from the ledger, proposes candidates, the persona writes its learning and another seat or the operator approves.
4. **User personas and promotion.** Usage evidence for user personas (with CR-0621's standing criteria), and deliberate promotion to the shipped amigos.

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** {{accepted_option | superseded | withdrawn}}

## Related Artifacts

- CR-0620, CR-0622, CR-0627 (which seats review, and each seat's own brief) and CR-0621, CR-0623, CR-0625 (persona goals and cards): this RFC frames all six; their breakdowns (G10, G11 of D0355) are input to its decision.
- CR-0619 and BG1003 (verdicts recorded as written, authorised rounds recordable): prerequisites for learning from the ledger.
- BG0966 and BG1002 (persona usage and the goal-review brief).
- RFC-0058 (stakeholder feedback shapes the work): the evidence a user persona learns from.
- The lessons system (LL0029, `lessons.py`, `retro.py extract`): the mechanics reused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Filed |
| 2026-10-09 | Claude Opus 5.5 | Written to the template from the operator's request: context, goals, three options, a recommendation, nine open decisions, impact, risks and a phased plan |
