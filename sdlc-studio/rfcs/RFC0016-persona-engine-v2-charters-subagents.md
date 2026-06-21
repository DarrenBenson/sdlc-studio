# RFC-0016: Persona engine v2 - structured charters + isolated-subagent consults

> **Status:** Draft
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-21
> **Spans:** sdlc-studio skill (persona model, consult/Three-Amigos workflow, audit + critic harnesses)
> **Related:** RFC0015 (the PM persona that owns the PVD), RFC0007 (generate-on-demand seeds), RFC0002 (audit refute panel), reference-workflow-personas.md, reference-consult.md
> **Supersedes / Superseded by:** --

## Summary

Rebuild personas as **structured charters** rather than prose characters, and run every
persona consult as an **isolated subagent** with its own context. This gives consults
genuine independence (a reviewer that pushes back from a clean seat, not a contaminated
main thread), adds a **Product Manager** persona (owns the PVD) alongside the **Product
Owner** (owns the PRD), and - the quiet payoff - **unifies** Three Amigos, persona
consults, the audit refute-panel, and the independent critic into one review primitive.

> **Scope note.** Personas are agent-crew's reason for being; the operator has a deeper
> persona model to bring. This RFC sets the **direction and mechanism** (charter shape,
> subagent isolation, ownership tiers, the unified primitive); the **persona schema and
> depth get a dedicated design pass** (the Open Decisions below are deliberately left for it).

## Context & Problem

Personas today are prose characters (post-RFC0007, generated on demand from archetype
seeds). For a *consult* that is the wrong shape: backstory is noise in a reviewer's brief,
the free prose is inconsistent (so reviewers are not comparable), and it does not encode
what a reviewer actually needs - what they own, what they optimise for, what they reject.
And Three Amigos today is the **main agent role-playing three hats in sequence** - one
contaminated context, not three independent views. The session's evidence says
independence is what matters: the independent **critic subagent** caught real bugs all
release *because* it reasoned from a clean context.

## Goals / Non-Goals

**Goals**

- A **structured persona charter** optimised to be (a) instantiated as a subagent system
  prompt and (b) decision-relevant.
- Consults run as **independent subagents**, one per persona, with a synthesis step.
- A **Product Manager** persona (owns the PVD) and a sharpened **Product Owner** (owns the
  PRD); ownership mirrors the artifact hierarchy.
- Recognise that consults, Three Amigos, audit lenses, and the critic are **one primitive**.

**Non-Goals**

- The full persona model - left to the dedicated follow-up (agent-crew-informed).
- Removing the human-flavour entirely; a one-line disposition stays.

## Design Options

### Option A - Structured charters + subagent consults + unified primitive (recommended)

A persona is a **charter**: role + mandate, lens (standing questions), non-negotiables,
push-back triggers, authority/scope, the artifacts it reads, and its tensions with other
roles (plus a one-line disposition). The charter **is** the subagent's brief. A consult
loads the relevant charters, spawns one subagent each, collects structured verdicts, and
synthesises - the same harness as the audit refute-panel. PM/PO/Eng/QA are charters in a
declared review council. **Pros:** independent + comparable reviewers; reuses the audit +
critic machinery; partly machine-checkable. **Cons:** N subagents per consult has a token
cost.

### Option B - Keep prose personas, add subagent isolation only

Run today's prose personas as subagents without restructuring them. **Pros:** smaller
change. **Cons:** inconsistent briefs; misses the comparability + machine-checkability;
leaves the backstory noise.

### Option C - Status quo

Three Amigos as sequential hats in the main context. **Cons:** no real independence.

## Recommendation

**Option A**, built in this order: (1) the charter schema + the PM/PO ownership; (2)
consults as isolated subagents over a synthesis step; (3) refactor the audit lenses and
the critic onto the same primitive once it is proven. Keep it **proportionate** - a
single-repo project still uses a light PO consult; the PM, the product tier, and full
council panels switch on only when there is a product to coordinate (RFC0015). The charter
schema below is a **recommendation, open to the persona deep-dive**.

### Proposed charter schema (for the deep-dive to confirm/extend)

- **role + mandate** - what they own / are accountable for
- **lens** - the standing questions they bring to any artifact
- **non-negotiables** - what they will not trade
- **pushes back when** - the objection triggers
- **authority / scope** - what they approve / block / defer
- **reads** - the artifacts they consult
- **tensions** - the productive conflicts with other roles
- **disposition** - one line of human flavour

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Charter schema | the fields above **[proposed]** / the operator's agent-crew-informed model (deep-dive) | Operator | Open |
| D2 | Subagent default | always isolate **[leaning]** / scale with stakes (1 for a quick check, full council for a PVD/contract decision) | Operator | Open |
| D3 | Unify the primitive now or later | refactor audit-lenses + critic onto it now / after personas land **[leaning]** | Design | Open |
| D4 | Council declaration | a project declares its review council (which charters apply) in config | Design | Open |
| D5 | Relationship to agent-crew's persona model | align the schema with agent-crew (the persona domain) | Operator | Open |
| D6 | New seats | PM (PVD) + PO (PRD) confirmed; which others are first-class (Architect, Security, QA, ...)? | Operator | Open |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| templates/personas/persona-template.md | becomes a structured charter | Enhancement |
| reference-persona.md / persona create | generate a charter from a role seed (RFC0007 seeds -> charters) | Enhancement |
| reference-consult.md / reference-workflow-personas.md | consult = spawn-subagent-per-charter + synthesise | Enhancement |
| scripts (consult harness) | reuse the audit finder/refute orchestration for persona panels | New / Reuse |
| reference-audit.md / critic | (later) refactored onto the same primitive | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Token cost of N subagents per consult | Medium | Medium | D2 scale with stakes; cache; the value (independence) is proven |
| Over-structuring loses the human read | Low | Low | keep the one-line disposition; charter is a brief, not a form |
| Designing personas without the agent-crew model | Medium | Medium | this RFC sets mechanism only; schema/depth to the deep-dive (D1, D5) |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Charter schema + PM/PO ownership seats | CR (TBD) | D1, D6 |
| WS2 | Consult = isolated-subagent panel + synthesis | CR (TBD) | WS1, D2 |
| WS3 | `persona create` generates a charter from a role seed | CR (TBD) | WS1 |
| WS4 | (later) refactor audit lenses + critic onto the unified primitive | CR (TBD) | WS2, D3 |

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0015 | Product Vision Document | Draft | needs the PM persona this defines |
| RFC | RFC-0007 | personas generate on demand | Accepted | seeds become charters here |
| RFC | RFC-0002 | adversarial audit | Accepted | its refute-panel is the same primitive |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** TBD - direction agreed; persona schema/depth to the dedicated deep-dive
**Rationale:** TBD
**Spawned CRs:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - structured charters + isolated-subagent consults + PM/PO ownership + the unified review primitive; persona schema/depth deferred to the agent-crew-informed deep-dive |
