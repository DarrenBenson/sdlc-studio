# RFC-0017: Cooper goal-directed persona model (the canonical persona model)

> **Status:** Draft
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Spans:** persona template + model, persona generate/validate workflow, reference-persona.md, reference-consult.md, and the authored-identity bridge into RFC0016
> **Related:** RFC0016 (substrate-tiered review seats - this resolves its deferred canonical model, D1/D6), RFC0007 (generate-on-demand seeds), RFC0015 (the PM/PO owner seats)

## Summary

Replace the demographic / category persona model with Alan Cooper's **goal-directed** model:
a full **cast** of precise, specific personas, each defined by **End and Experience goals**;
generation produces only **provisional** personas, which become **validated** ("real") only
when grounded in **research evidence**; and the schema is deliberately the **pre-compilation
form of an authored identity** ([[RFC0016]]), so a validated persona can later compile into
one (goals -> ordered values, frustrations -> shadow). This is the canonical persona model
RFC0016 deferred to "the operator's persona deep-dive" (its D1/D6).

Two payoffs the operator named: **adoption** (a precise, goal-led design target is more useful
than archetype prose) and a clean **on-ramp to authored identities** (a goal hierarchy is the
raw material an authored identity's value hierarchy compiles from; a demographic persona is not).

## Context & Problem

Personas today are **categories** (Team / Stakeholder / Archetype) inferred from the PRD or
codebase (RFC0007). Three problems:

1. **Not goal-directed.** They describe *who* (role, demographics) more than *why* (goals). The
   design has nothing precise to be judged against, and the team designs for an **elastic user**
   (everyone -> no one) or for itself.
2. **Cannot compile to an authored identity.** RFC0016's authored-identity tier needs an ordered
   value hierarchy and a load-bearing shadow. A demographic persona supplies neither, so the
   move to authored identities has no on-ramp.
3. **No honesty about grounding.** A generated persona reads as authoritative though it is a
   hypothesis inferred from documents - the half-truth RFC0016's integrity rule forbids
   (*claim no property you cannot demonstrate*).

## Goals / Non-Goals

**Goals**

- A **goal-directed** persona model: the persona is its goals; the design is judged against them.
- The full Cooper **cast** as first-class types.
- **End + Experience goals** as the goal model.
- A **provisional -> validated** lifecycle: generation only ever drafts *provisional*; a persona
  becomes *validated* ("real") only when **research evidence** is attached and ratified.
- The schema is the **pre-compilation form of an authored identity** ([[RFC0016]]): the field
  mapping (goals -> ordered values, frustrations -> shadow) is designed in now; the mechanical
  compile is built later.

**Non-Goals**

- The compile step itself (validated persona -> running authored identity) - the *mapping* is
  specified here; the *mechanism* lands with RFC0016's authored-identity tier.
- Mass-producing validated personas. Validation costs research; few personas earn it.
- Life goals (Cooper's third tier) - out of scope for now (End + Experience only); revisitable.

## The model

### The cast (full Cooper cast, all first-class)

| Persona type | What it is | Has goals? |
| --- | --- | --- |
| **Primary** | The single precise individual the product is designed *for* - one per product/epic; satisfying it should not satisfy others only by accident | End + Experience (full) |
| **Secondary** | Mostly satisfied by the primary's design but with one or two added needs | End + Experience |
| **Supplemental** | Fully covered by the primary design; listed so we know who else is served | End (light) |
| **Negative** | The anti-persona - explicitly *not* designed for ("we are not building for X") | Goals stated to exclude |
| **Customer** | Buys / authorises but does not use (procurement, a parent) | End (buyer goals) |
| **Served** | Affected by the product without using it (a patient whose scan the tool reads) | End (welfare goals) |

The **Primary** is the design target; the others bound and sharpen it. Primary selection (when
several candidates compete) is an Open Decision (D3).

### Goals: End + Experience

- **End goals** - what the persona is trying to *accomplish* with the product (the practical,
  PRD-facing motivations). Stated as an **ordered** list - the ordering is load-bearing: it is
  what compiles into the authored-identity value hierarchy.
- **Experience goals** - how the persona wants to *feel* while using it (unhurried, in control,
  not made to feel stupid). These give the authored-identity bridge its affective dimension.

### Lifecycle: provisional -> validated (research-required)

| State | How it is reached | What it may be used for |
| --- | --- | --- |
| **Provisional** | `persona generate` infers a hypothesis from PRD / code / docs. **Flagged** as provisional | Early design, framing, a starting hypothesis - never as settled truth |
| **Validated ("real")** | **Research evidence** (interviews, transcripts, observation) is attached and **ratified** | A real design target; eligible to compile into an authored identity |

Generation **only ever produces provisional personas.** A persona is not "real" until research
backs it - Cooper orthodoxy, and the same act as RFC0016 ratification: the research-grounding is
what buys an authored-identity anchor. (Evidence format + ratification ritual: D1/D2.)

### The authored-identity bridge (designed now, compiled later)

The schema is shaped so a **validated** persona is the pre-compilation form of an authored
identity ([[RFC0016]]):

| Cooper persona field | Compiles into (authored identity) |
| --- | --- |
| Ordered **End goals** | the **ordered value hierarchy** (what resolves conflict under pressure) |
| **Experience goals** | the affective / dispositional layer |
| **Frustrations / failure modes** | the **shadow** (RFC0016: how it fails when trying hardest to be good) |
| **Validated + ratified** state + research refs | the **human-ratified anchor** (RFC0016: anchor strength = ratification frozen in) |
| Behaviours, context, scenarios | the behavioural generator's priors |

The *mapping* is normative here; the *compile mechanism* is RFC0016's authored-identity tier
(D4). Repo-neutral throughout: "authored identity", never any product name.

## Design Options

### Option A - Full Cooper model + provisional/validated lifecycle + bridge schema (recommended)

The model above: full cast, End + Experience goals, generate-drafts-provisional /
research-validates-real, and the schema as the authored-identity pre-compilation form.
**Pros:** goal-directed and precise (adoption); honest by construction (provisional flagging =
RFC0016's integrity rule); the on-ramp to authored identities the operator wants; resolves
RFC0016 D1/D6. **Cons:** the full cast + research-required bar is heavier than archetype prose;
needs a new `persona validate` workflow and a research-evidence convention.

### Option B - Lean Cooper (primary + negative, End goals only, provisional flag only)

**Pros:** cheapest, fastest adoption. **Cons:** thin material for the authored-identity bridge;
not the operator's choice.

### Option C - Status quo (categories, no goals, no lifecycle)

**Cons:** the three problems above; no bridge.

## Recommendation

**Option A** - the operator's settled stance (full cast; End + Experience; research-required
validation; build the bridge now). Build in workstreams (below): the schema + cast + goals
first, the provisional/validated lifecycle and `persona validate` next, the bridge mapping and
migration alongside, the compile mechanism deferred to RFC0016.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Research-evidence format + where it lives | interview notes / transcript refs / observation log under `sdlc-studio/personas/<persona>/research/` | Operator | Open |
| D2 | Validation ritual + minimum evidence bar | who ratifies, how much evidence makes a persona "real" (ties RFC0016 D2) | Operator | Open |
| D3 | Primary selection when candidates compete | Cooper's goal-coverage method / operator picks | Operator | Open |
| D4 | Compile mechanism (persona -> authored identity) | defer to RFC0016 authored-identity tier / joint workstream | Design | Open |
| D5 | Migration of existing personas | re-cast as provisional / deprecate categories / keep both during transition | Operator | Open |
| D6 | Goal depth for Customer / Served | same End + Experience / lighter End-only | Design | Open |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| templates/personas/persona-template.md | full Cooper schema: cast role, ordered End goals, Experience goals, frustrations, scenarios, grounding state + research refs | Enhancement |
| reference-persona.md | the cast, the goal model, the provisional/validated lifecycle; `generate` drafts provisional only | Enhancement |
| persona generate | output is always provisional + flagged | Enhancement |
| persona validate (new) | attach research evidence -> ratify -> validated | New |
| reference-consult.md / RFC0016 | a validated, bridged persona feeds RFC0016's authored-identity tier; resolves D1/D6 | Enhancement |
| validate.py / conformance | (optional) a persona used as an owner seat must be validated, not provisional | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Research-required bar stalls adoption | Medium | Medium | provisional personas are fully usable for design; validation is required only to be "real" / to compile |
| Full cast over-modelled for small projects | Medium | Low | only Primary + Negative are mandatory; the rest are opt-in per project |
| Bridge designed without the canonical authored-identity model | Medium | Medium | mapping only here; the compile mechanism defers to RFC0016 (D4) |
| Provisional personas treated as validated in practice | Medium | High | a hard flag in the schema + (optional) conformance: an owner seat must be validated |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Cooper schema + cast + End/Experience goals (template + reference-persona) | CR (TBD) | -- |
| WS2 | Provisional/validated lifecycle + `persona validate` (research-required) | CR (TBD) | WS1, D1, D2 |
| WS3 | Authored-identity bridge mapping (schema -> RFC0016 fields) | CR (TBD) | WS1, RFC0016 |
| WS4 | Migration of existing personas to the new model | CR (TBD) | WS1, D5 |
| WS5 | (with RFC0016) compile a validated persona into an authored-identity seat | CR (TBD) | WS3, RFC0016 |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** TBD
**Rationale:** TBD
**Spawned CRs:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - Cooper goal-directed model: full cast, End + Experience goals, provisional/validated (research-required) lifecycle, authored-identity bridge designed now; resolves RFC0016 D1/D6 (the persona deep-dive) |
