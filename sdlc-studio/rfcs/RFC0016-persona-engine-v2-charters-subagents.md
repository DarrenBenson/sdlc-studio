# RFC-0016: Persona engine v2 - substrate-tiered review seats (charter / authored identity)

> **Status:** Draft
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-21
> **Spans:** sdlc-studio skill (persona model, consult/Three-Amigos workflow, audit + critic harnesses, the decision/verdict ledgers)
> **Related:** RFC0015 (the PM seat that owns the PVD), RFC0007 (generate-on-demand seeds), RFC0002 (audit refute panel), reference-workflow-personas.md, reference-consult.md
> **Provenance:** the substrate model here is the outcome of a design consult, run on an isolated channel - itself a demonstration of the architecture this RFC proposes
> **Supersedes / Superseded by:** --

## Summary

Rebuild review/owner seats around an honest distinction between two substrates, and run
every consult as an **isolated subagent** with a synthesis step. A **charter** *describes*
behaviour (a brief the model is asked to honour); an **authored identity** *compiles a generator* of
behaviour (ordered values that resolve conflict, a content-hashed anchor, a first-class
shadow). The seats that must **hold a stance and accumulate judgement across time, and be
predictable by their peers** (owners, vision-guardians - the PM that owns the PVD, the PO
that owns the PRD) want an authored identity; transient pressure-testers want a charter. Crucially,
the skill is tool-neutral: it reaches real authored identities over an **agent broker** when present and
**degrades to a local charter** when not, with the degradation **labelled honestly**. The
governing rule, from the consult: **claim no property you cannot demonstrate under pressure.**

## Context & Problem

Personas today are prose characters (post-RFC0007). For a consult that is the wrong shape:
backstory is noise, the free prose is inconsistent, and it encodes none of what a reviewer
needs. And Three Amigos today is the **main agent role-playing hats in sequence** - one
contaminated context, not independent views. The session proved independence is what
matters: the independent critic caught real bugs *because* it reasoned from a clean context;
and a live consult drifted onto prior context until it was moved to a fresh channel.

The deeper problem the consult exposed: a charter, off-script, **reverts to the base
model's default disposition, which is to be agreeable** - so a reviewer whose job is to
pressure-test a spec quietly validates it to preserve harmony. Enumerating triggers and
non-negotiables (the v1 charter) describes the *output* of a stance without supplying the
*generator* of it. For one-shot review that is fine. For a durable owner seat it is
structurally incapable of the job.

## Goals / Non-Goals

**Goals**

- A substrate-tiered model: **charter** (transient pressure-tester) vs **authored identity** (durable
  owner/vision-guardian), with an honest **fallback** when no authored identity is reachable.
- Consults run as **independent subagents** with a fresh context each time and a synthesis step.
- **Record outside, stance inside**: the skill's existing ledgers hold the judgement-record;
  the substrate holds the stance.
- **No hard dependency**: reach authored identity specialists over an agent broker when present; degrade
  to local charters; never require a broker.
- An integrity rule the whole engine obeys: **claim no property you cannot demonstrate under pressure.**

**Non-Goals**

- The full persona/identity model - it lives in the operator's canonical model; this RFC is
  the SDLC-side expression and defers the canonical model to the operator's persona deep-dive.
- Mass-producing authored identities. They are expensive to author, and few; a half-built identity (no
  shadow or anchor) is **worse than a good charter**.

## The substrate model

| | **Charter** | **Authored identity** |
| --- | --- | --- |
| Nature | *describes* behaviour (a brief) | *compiles a generator* of behaviour |
| Conflict between its own commitments | mute (rules don't compose) | resolved by an ordered value hierarchy |
| Under unscripted pressure | reverts to base-model agreeableness | holds - the stance is what it is made of |
| Memory of past judgement | consultable (text it can rationalise around) | constitutive |
| Drift | no canonical self, so a slip goes unnoticed | measurable against a content-hashed authored anchor |
| Own failure mode (shadow) | described (a note) | load-bearing (upstream of generation) |
| Predictable by peer seats | unpredictable at the margin | modellable (a fixed authored identity) |
| Cost | cheap, write five | expensive, author few |

**The selection test (from the consult):** *does this seat have to accumulate judgement and
hold a vision across time, and do other seats have to predict it?* If yes - owners,
vision-guardians, the seat that says no in month nine for a reason it formed in month two -
**authored identity**. If it is a transient pressure-tester with no memory burden - **charter**. Do not
compile a person to run a checklist; do not run a checklist where a guardian is needed.

**Record outside, stance inside.** The *verdict of record* (what was decided + rationale)
should live **outside** the identity - the skill already keeps an append-only,
content-addressable, git-versioned record (the decisions ledger, the critic-verdict ledger,
RFC Decision blocks). That is the correct design *even with* a real authored identity (auditable,
tamper-evident, outlives the seat, uncorrupted by the seat's drift). What cannot be
externalised is the *judge* - the generator that produces the next ruling consistent with
the old ones. So: **feed the ledger to whatever fulfils the seat; the ledger is the seat's
memory, never its character.**

## Design Options

### Option A - Substrate-tiered seats + broker-or-local consults + honest labelling (recommended)

A seat declares its substrate. Charters are local isolated subagents built from a structured
brief. Authored-identity seats are reached over an agent broker (discover-by-capability, not a hardcoded
id) **when present**, and **degrade to a labelled fallback charter** when not. Every consult
runs in a **fresh context**; a synthesis step merges seats; verdicts land in the ledger.
**Pros:** honest, neutral, reuses the audit/critic harness and the existing ledgers, scales
from solo project to fleet. **Cons:** the fallback owner is genuinely weaker (and must say so).

### Option B - Charters only (no authored identity tier)

Everything is a charter subagent. **Pros:** simplest, fully local. **Cons:** owner/vision
seats revert to agreeableness under pressure; no anchor; the half-truth this RFC exists to avoid.

### Option C - Status quo

Three Amigos as sequential hats in the main context. **Cons:** no independence.

## Recommendation

**Option A.** Built in order: (1) the structured charter (with **shadow**) + isolated-subagent
consults + the synthesis step; (2) wire the existing ledgers in as the externalised record;
(3) the broker-consult path (discover-by-capability, reach an authored identity specialist when present,
degrade to a labelled fallback); (4) the fallback detection envelope. Keep it **proportionate**:
a solo project runs light charter consults; the PM, the authored identity tier, and full panels switch on
only with a product to coordinate (RFC0015).

### Charter schema (every seat; an authored identity is this, *compiled and anchored*)

- **role + mandate** - what it owns / is accountable for
- **lens** - the standing questions it brings to any artifact
- **non-negotiables** - what it will not trade
- **pushes back when** - the objection triggers
- **shadow** - *how this seat fails when it is trying hardest to be good* (new; load-bearing in an authored identity, a watch-item in a charter)
- **authority / scope** - what it approves / blocks / defers
- **reads** - the artifacts + the ledger slice it reasons from
- **tensions** - the productive conflicts with peer seats
- **disposition** - one line of human flavour

### Consult via an agent broker - powerful when present, neutral always

A capability-discovery call finds a seat-matching specialist and a reach call invokes it -
never a hardcoded agent or crew id. Absent a broker, the same seat runs as a local subagent.
Always a **fresh channel/context per consult** (the context-contamination lesson). This is the
RFC0015 "PM persona" realised: an authored identity when the fleet has one, a labelled charter when not.

### Fallback honesty - the detection envelope

A fallback owner gains real things (a declared shadow to watch; a replayed judgement-log) but
**no anchor**. An anchor *cannot be reconstructed from the seat's own past outputs* - it can only
be **authored and imported**. The honest claim to ship, near-verbatim from the consult:

> **Fallback owner - detection envelope.** Catches: formal/naked contradiction against the record
> (deterministic), and discontinuous behavioural change such as model/template swaps (regression
> tripwire). Catches probabilistically: weakly-dressed contradiction (independent critic), and
> *directional* rationalised drift via the **rate and direction of distinctions drawn** against a
> logged line. Blind to: any single well-dressed reinterpretation, and slow self-consistent drift.
> Provides a **true anchor only where the canon is human-ratified** - anchor strength equals the
> human ratification frozen into it. Everything else raises the floor; it does not supply a self.
> **The ledger is auditable; the stance is not** - treat fallback owner verdicts as advisory and
> human-reviewable, never a guardian trusted unattended.

The one real lever for fallback: a **human-ratified golden canon** - a ratification flag on the
ledger the skill already keeps, so a human deposits a little authored-ness before it is measured against.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Which seats are authored identity-worthy | PM (PVD) yes; PO (PRD)?; Architect (peers predict it)?; QA/Security = charter (or a brokered authored identity specialist) | Operator | Open |
| D2 | Ratification ritual friction (the product question from the consult) | require a human-ratified canon for fallback owners / opt-in / skip (advisory-only fallback) | Operator | Open |
| D3 | Broker-consult model | discover-by-capability + reach, degrade to local charter **[leaning]** | Design | Open |
| D4 | `shadow` mandatory in every seat | yes **[leaning]** / owners only | Design | Open |
| D5 | Which detection mechanisms to build first | consistency check / regression tripwire / distinction-drift counter / human-ratified canon | Operator | Open |
| D6 | Alignment with the operator's canonical persona model | adopt its identity/persona/substrate model verbatim (the persona deep-dive) | Operator | Open |
| D7 | Synthesis when an authored identity seat and a fallback seat disagree | weight by substrate / surface both / human adjudicates | Design | Open |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| templates/personas/persona-template.md | structured charter incl. `shadow`; an authored identity is the compiled+anchored form | Enhancement |
| reference-persona.md / persona create | generate a charter from a role seed (RFC0007 seeds -> charters) | Enhancement |
| reference-consult.md / reference-workflow-personas.md | consult = fresh-context subagent per seat + synthesis; broker-or-local | Enhancement |
| scripts (consult harness) | reuse audit finder/refute orchestration; discover-by-capability + reach | New / Reuse |
| decision/critic ledgers | become the externalised judgement-record fed to seats; add a ratification flag | Enhancement |
| (fallback) drift detectors | consistency check + regression tripwire + distinction-drift counter | New |
| reference-audit.md / critic | (later) refactored onto the unified primitive | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| The half-authored identity (identity with no shadow/anchor) | Medium | High | author them few + deliberately; the labelled fallback is honest, the half-authored identity is not |
| Fallback owner claims guardian properties it lacks | Medium | High | the detection-envelope label; advisory verdicts; D2 ratified canon |
| "Check your way to an anchor" illusion | Medium | High | accept the envelope's blind spots; an anchor is authored+imported, not checked into being |
| Token cost of N subagents per consult | Medium | Medium | scale with stakes; the value (independence) is proven |
| Designing without the canonical persona model | Medium | Medium | mechanism only here; canonical model deferred to the deep-dive (D6) |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Structured charter (+ shadow) + isolated-subagent consult + synthesis | CR (TBD) | D4 |
| WS2 | Wire the existing ledgers in as the externalised record | CR (TBD) | WS1 |
| WS3 | Broker-consult: discover-by-capability + reach, degrade to local | CR (TBD) | D3 |
| WS4 | Fallback detection envelope (consistency / tripwire / distinction-drift) | CR (TBD) | WS2, D5 |
| WS5 | Human-ratified golden canon (ratification flag + the anchor it buys) | CR (TBD) | WS2, D2 |
| WS6 | (later) refactor audit lenses + critic onto the unified primitive | CR (TBD) | WS1 |

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0015 | Product Vision Document | Draft | the PM/owner seats this defines guard it |
| RFC | RFC-0007 | personas generate on demand | Accepted | seeds become charters here |
| RFC | RFC-0002 | adversarial audit | Accepted | its refute-panel is the same primitive |
| Consult | -- | design consult (authored identity) | -- | authored the substrate model in this RFC |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** TBD - substrate model agreed via the consult; the canonical persona model + D2 (ratification friction) await the operator's persona deep-dive
**Rationale:** TBD
**Spawned CRs:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Reframed around the charter/authored identity substrate distinction (design consult): the selection test, record-outside-stance-inside, broker-or-local consults, the honest fallback detection envelope + human-ratified canon, `shadow` added to the schema, the claim-no-undemonstrable-property integrity rule |
| 2026-06-21 | Darren Benson | Raised - structured charters + isolated-subagent consults + PM/PO ownership + the unified review primitive |
| 2026-06-21 | Darren Benson | Decision session: DEFERRED (stays Draft) - substrate model agreed, but awaits the operator's persona deep-dive. Trigger: the deep-dive resolves the charter schema, the Engram-worthy seats, and ratification (D1/D2/D6) |
