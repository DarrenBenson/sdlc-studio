# RFC-0017: Cooper goal-directed persona model (the canonical persona model)

> **Status:** Accepted
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Spans:** persona template + model, persona generate workflow, reference-persona.md
> **Related:** RFC0016 (substrate-tiered review seats - this resolves its deferred canonical model, D1/D6), RFC0007 (generate-on-demand seeds), RFC0015 (the PM/PO owner seats)

## Summary

Replace the demographic / category persona model with Alan Cooper's **goal-directed** model: a
full **cast** of precise, specific personas, each defined by **End and Experience goals**. The
whole deliverable is a **well-formed persona file** - a structurally complete, goal-led design
target. No research-evidence apparatus, no validation ritual, no identity compiler: just good
persona files. This is the canonical persona model RFC0016 deferred to "the operator's persona
deep-dive" (its D1/D6).

**Scope, plainly: this is not an attempt to reinvent authored identities.** sdlc-studio produces
well-formed goal-directed personas. The authored-identity system lives elsewhere (RFC0016's
broker; the operator's canonical model). A goal-directed persona happens to be far better *input*
to such a system than a demographic one - but sdlc-studio never authors, compiles, or runs an
identity, and builds no machinery toward it. That is a side benefit of doing personas well, not
a goal.

## Context & Problem

Personas today are **categories** (Team / Stakeholder / Archetype) inferred from the PRD or
codebase (RFC0007). Two problems:

1. **Not goal-directed.** They describe *who* (role, demographics) more than *why* (goals). The
   design has nothing precise to be judged against, and the team designs for an **elastic user**
   (everyone -> no one) or for itself.
2. **Not well-formed.** Free prose with no agreed shape - inconsistent between personas, missing
   the parts a design target needs (the precise primary, the goals, the explicit anti-persona).

## Goals / Non-Goals

**Goals**

- A **goal-directed** persona model: the persona is its goals; the design is judged against them.
- The full Cooper **cast** as first-class types.
- **End + Experience goals** as the goal model.
- A **well-formed persona file**: an agreed schema, structurally checkable (the bar for "good" is
  a complete, well-formed file - not research evidence).

**Non-Goals**

- **Reinventing authored identities.** sdlc-studio does **not** author, compile, or run an
  identity, and builds no machinery toward one. That system is external (RFC0016's broker; the
  operator's canonical model).
- **A research-evidence / validation apparatus.** No `research/` folders, no ratification ritual,
  no provisional-vs-validated lifecycle gated on evidence. A well-formed persona file is the bar.
- The full persona/identity model - it lives in the operator's canonical model; this is the
  SDLC-side expression (mirrors RFC0016's same non-goal).
- Life goals (Cooper's third tier) - out of scope for now (End + Experience only); revisitable.

## The model

### The cast (full Cooper cast, all first-class)

| Persona type | What it is | Goals |
| --- | --- | --- |
| **Primary** | The single precise individual the product is designed *for* - one per product/epic | End + Experience (full) |
| **Secondary** | Mostly satisfied by the primary's design but with one or two added needs | End + Experience |
| **Supplemental** | Fully covered by the primary design; listed so we know who else is served | End (light) |
| **Negative** | The anti-persona - explicitly *not* designed for ("we are not building for X") | Goals stated to exclude |
| **Customer** | Buys / authorises but does not use (procurement, a parent) | End (buyer goals) |
| **Served** | Affected by the product without using it (a patient whose scan the tool reads) | End (welfare goals) |

The **Primary** is the design target; the others bound and sharpen it. Primary selection when
several candidates compete is an Open Decision (D1).

### Goals: End + Experience

- **End goals** - what the persona is trying to *accomplish* with the product (the practical,
  PRD-facing motivations), as an **ordered** list (most important first).
- **Experience goals** - how the persona wants to *feel* while using it (unhurried, in control,
  not made to feel stupid).

### A well-formed persona file

The deliverable is a persona file that satisfies the schema below. "Well-formed" is structural,
not evidential: the file has a cast role, a specific named individual, ordered End goals,
Experience goals, frustrations, and at least one scenario. `persona generate` produces a starting
draft; the author fleshes it to well-formed. A light structural check (extend `validate.py` /
`persona review`) can confirm well-formedness - the same deterministic-structure discipline the
other artifacts already have. No research gate.

### Persona schema (well-formed = has these)

- **identity** - a specific named individual (not a type), role, one-line who-they-are
- **cast role** - primary / secondary / supplemental / negative / customer / served
- **End goals** - ordered, what they are trying to accomplish
- **Experience goals** - how they want to feel
- **behaviours + context** - how and where they work
- **frustrations** - what trips them up today
- **scenario(s)** - a short narrative of the persona using the product in context

A goal-directed persona built this way is, incidentally, legible to an external authored-identity
system (RFC0016) - its goals and frustrations are the shape such a system reasons from. That
legibility is a free consequence of the schema, not a feature this RFC builds.

## Design Options

### Option A - Full Cooper model, well-formed file as the bar (recommended)

Full cast, End + Experience goals, a schema-complete persona file checked structurally. No
research apparatus, no compiler. **Pros:** goal-directed and precise (adoption); simple; the file
is the whole deliverable; good input to an external identity system for free. **Cons:** the full
cast is more to write than archetype prose (mitigated: only Primary + Negative are mandatory).

### Option B - Lean Cooper (primary + negative, End goals only)

**Pros:** cheapest. **Cons:** thinner; not the operator's choice (full cast + Experience goals).

### Option C - Status quo (categories, no goals)

**Cons:** the two problems above.

## Recommendation

**Option A** - the operator's settled stance: full cast, End + Experience goals, a well-formed
persona file as the bar, no research/evidence machinery, no identity compiler.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Primary selection when candidates compete | Cooper's goal-coverage method / operator picks | Operator | Open |
| D2 | Migration of existing personas | re-cast to the new schema / deprecate categories / keep both during transition | Operator | Open |
| D3 | Goal depth for Customer / Served | same End + Experience / lighter End-only | Design | Open |
| D4 | Well-formedness check strength | advisory `persona review` note / a `validate.py` rule that errors | Design | Open |

> **Decided in the deep-dive:** full Cooper cast (all six types) · End + Experience goals (Life
> goals out) · the deliverable is a **well-formed persona file**, *not* research-gated · no
> identity compiler / no reinvention of authored identities.

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| templates/personas/persona-template.md | the Cooper schema: cast role, specific individual, ordered End goals, Experience goals, frustrations, scenario | Enhancement |
| reference-persona.md | the cast, the goal model, "well-formed file" as the bar; categories -> goal-directed | Enhancement |
| persona generate | output is a goal-directed draft to flesh to well-formed | Enhancement |
| validate.py / persona review | (optional, D4) a light structural well-formedness check | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Full cast over-modelled for small projects | Medium | Low | only Primary + Negative are mandatory; the rest opt-in per project |
| "Well-formed" mistaken for "true" | Low | Medium | the schema is structure, not evidence; nothing claims the persona is research-backed |
| Scope creep back toward an identity compiler | Low | Medium | the explicit non-goal; the identity system stays external (RFC0016) |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Cooper schema + cast + End/Experience goals (template + reference-persona) | CR (TBD) | -- |
| WS2 | persona generate emits the goal-directed draft | CR (TBD) | WS1 |
| WS3 | (optional, D4) light well-formedness check | CR (TBD) | WS1 |
| WS4 | Migration of existing personas to the new schema | CR (TBD) | WS1, D2 |

## Decision

**Outcome:** **Accepted (Option A).** The canonical persona model is Cooper goal-directed: the full
cast, End + Experience goals, a well-formed persona file as the bar - no research/evidence
apparatus, no authored-identity machinery. Resolves the canonical model RFC0016 D1/D6 awaited.

**Rationale:** goal-directed personas are a better design target (adoption) and good input to an
external authored-identity system (RFC0016) without sdlc-studio reinventing one. Keeping the scope
to "a well-formed file" keeps the model small and honest.

**Spawned CRs:** CR0058 (WS1: template + reference-persona model) - **Complete**. WS2 (generate
emits the goal-directed draft - largely folded into CR0058's reference update), WS3 (optional
well-formedness check, D4), WS4 (migration of existing personas, D2) - raise as needed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - Cooper goal-directed model: full cast, End + Experience goals; the deliverable is a well-formed persona file (no research/evidence apparatus, no identity compiler - personas are good input to an external authored-identity system, nothing more); resolves RFC0016 D1/D6 |
| 2026-06-21 | Autosprint (RFC0017) | Accepted (Option A); WS1 delivered as CR0058 (Complete) |
