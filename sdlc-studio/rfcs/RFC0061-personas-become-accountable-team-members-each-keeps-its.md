# RFC-0061: Personas become accountable team members: each keeps its own memory, learns from its own verdicts at the retro, and passes a persona review before it is trusted

> **Status:** Accepted
> **Forced-override:** 2026-10-09: --force waived 1 gate(s) on Accepted - RFC0061 cannot be Accepted: its status is DERIVED from its children, and 4 is/are not yet resolved: CR0631 (Proposed), CR0632 (Proposed), CR0633 (Proposed), CR0634 (Proposed). Finish or close them first
> **Decomposed-into:** CR0631, CR0632, CR0633, CR0634
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
| D1 | Where memory lives | A card section, B memory file, C owned lessons | Operator | Decide at `rfc decide` | Resolved: Option B: a committed memory file beside each card (sdlc-studio/personas/memory/<persona>.md), owned by its own tool; the card stays the reviewed identity (operator, 2026-10-09) -> CR0632 |
| D2 | Who writes a learning | the persona, briefed with its evidence; the retro facilitator; the operator | Operator | Consult the seats | Resolved: The persona itself: a context framed as that persona, briefed with its own verdict record and what followed, writes the learning in its own words (operator) -> CR0633 |
| D3 | Who approves a learning | the operator; another seat; automatic with a later review | Operator | Consult the seats | Resolved: Another seat approves each learning against its evidence; learnings are listed on the retro the operator signs, where the operator can strike any (operator) -> CR0633 |
| D4 | What evidence feeds learning | verdict outcomes, rounds to converge, operator rulings, closing-review and consuming-project findings | Engineering seat | Spike against this repo's ledger | Resolved: All four: verdict outcomes, rounds to converge, operator rulings naming the seat, and closing-review and consuming-project findings (operator) -> CR0633 |
| D5 | How memory reaches the persona | every brief (bounded, ranked) or recalled on demand | Engineering seat | Spike: measure brief size | Resolved: Every brief, bounded: the persona's top approved learnings, capped and ranked by recency and relevance, injected into its own brief (operator) -> CR0632 |
| D6 | Scope | seats only, or user personas too | Operator | Decide at `rfc decide` | Resolved: Seats first, then user personas from usage evidence such as served-goal outcomes (CR0629) and stakeholder feedback (operator) -> CR0634 |
| D7 | Persona review strength and cadence | blocking (a failing persona cannot be resolved into a brief) or advisory; on change, per release, every N sprints | Operator | Decide at `rfc decide` | Resolved: Blocking for cards, reported for memory: a new or changed card that fails the standard cannot be resolved into a brief until fixed; runs on every card change and once per release (operator) -> CR0631 |
| D8 | Forgetting | horizon and revalidation, a cap on injected learnings, how contradictions resolve | QA seat | Consult | Resolved: As project lessons: each learning carries a validity horizon and is revalidated or retired; a cap bounds what is injected; a contradicted learning is retired by the reviewing seat (operator, with D5) -> CR0632 |
| D9 | Cross-project promotion | none; or promote generalisable learnings to the shipped amigos as `lessons add --global` does | Operator | Decide at `rfc decide` | Resolved: Deliberate promotion only: a generalisable learning is promoted to the shipped amigo cards through the skill source repository, as lessons add --global promotes a lesson (operator) -> CR0634 |

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

**Outcome:** Accepted, Option B reusing Option C's mechanics, on 2026-10-09 by the operator.

Each persona keeps a committed memory file beside its card; at the retro it is scored on its own verdicts from the ledger and writes its learning in its own words; another seat approves it and the operator can strike it on the signed retro; its brief carries its own top learnings, bounded and with horizons; a persona review blocks a failing card and reports memory; seats first, user personas next; deliberate promotion only. Each of D1 to D9 is resolved above with its rationale. Recorded as ADR-012 in the TRD.

**Spawned CRs:** CR0631 (persona review, workstream 1), CR0632 (seat memory, workstream 2), CR0633 (the learning loop, workstream 3), CR0634 (user personas and promotion, workstream 4). CR0629 (a served persona's End goal at the close) feeds workstream 4.

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
| 2026-10-09 | rfc resolve (operator decision) | resolve: D1 - Option B: a committed memory file beside each card (sdlc-studio/personas/memory/<persona>.md), owned by its own tool; the card stays the reviewed identity (operator, 2026-10-09) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D2 - The persona itself: a context framed as that persona, briefed with its own verdict record and what followed, writes the learning in its own words (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D3 - Another seat approves each learning against its evidence; learnings are listed on the retro the operator signs, where the operator can strike any (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D4 - All four: verdict outcomes, rounds to converge, operator rulings naming the seat, and closing-review and consuming-project findings (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D5 - Every brief, bounded: the persona's top approved learnings, capped and ranked by recency and relevance, injected into its own brief (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D6 - Seats first, then user personas from usage evidence such as served-goal outcomes (CR0629) and stakeholder feedback (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D7 - Blocking for cards, reported for memory: a new or changed card that fails the standard cannot be resolved into a brief until fixed; runs on every card change and once per release (operator) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D8 - As project lessons: each learning carries a validity horizon and is revalidated or retired; a cap bounds what is injected; a contradicted learning is retired by the reviewing seat (operator, with D5) |
| 2026-10-09 | rfc resolve (operator decision) | resolve: D9 - Deliberate promotion only: a generalisable learning is promoted to the shipped amigo cards through the skill source repository, as lessons add --global promotes a lesson (operator) |
| 2026-10-09 | Claude Opus 5.5 | Accepted: D1-D9 resolved by the operator; CR0631-CR0634 spawned; ADR-012 |
| 2026-10-09 | transition set --force | forced RFC0061 -> Accepted, waiving 1 gate(s): RFC0061 cannot be Accepted: its status is DERIVED from its children, and 4 is/are not yet resolved: CR0631 (Proposed), CR0632 (Proposed), CR0633 (Proposed), CR0634 (Proposed). Finish or close them first |
| 2026-10-09 | Claude Opus 5.5 | Accepted with --force past the derived-terminal gate (D0362; the contradiction is BG1020) |
