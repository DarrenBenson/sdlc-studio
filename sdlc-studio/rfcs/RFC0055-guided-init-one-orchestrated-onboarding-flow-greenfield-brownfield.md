# RFC-0055: Guided init: one orchestrated onboarding flow (greenfield + brownfield) from zero to first sprint plan - AGENTS.md, PRD, TRD, TSD, personas, best practice baked in

> **Status:** Draft
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Onboarding is the biggest adoption cliff. Today a new user must discover and run a SEQUENCE by hand - `init`, then `prd create` or `prd generate`, then epics, then `persona generate --team`, and separately understand AGENTS.md, the TRD and the TSD - with nothing walking them from zero to a state where they can plan their first sprint. The commands exist; the ORCHESTRATION does not. A returning v1 user, who last drove a mostly-human flow, and a brand-new user both hit the same wall: they have the pieces and no guided path through them.

This RFC proposes making `init` an **interactive onboarding orchestrator** that takes a user - greenfield OR brownfield - from an empty (or existing) repo through every artefact best practice says they need, to a first `sprint plan`, asking only what it cannot infer and baking the discipline in as it goes. The intent: replace "read the docs, then work out the order" with "answer the prompts, and you are delivering."

The flow it would drive (best-practice spine), with the two paths diverging where they must:

1. **Agent instructions** - write/confirm `AGENTS.md` (+ the `CLAUDE.md` import) from the tool-neutral starter, so every agent that touches the repo inherits the discipline.
2. **PRD** - greenfield: interview to `prd create`. Brownfield: `prd generate` reads the code and drafts the spec, then validates it against the real tests.
3. **TRD / TSD** - the technical and test-strategy docs, generated from the PRD (and, brownfield, from the stack), so the test strategy the plan later reads actually exists.
4. **Personas** - `persona generate --team` grown from the PRD, stack and risk signals; the user accepts or edits.
5. **First delivery** - decompose to epics + stories, and land the user at a ready `sprint plan`.

Checkpointed and resumable throughout: the user approves each artefact before the next, and the flow can stop and resume (it is long, and a session can end mid-way). This is design work - the divergence points, how much is auto-generated vs interviewed, which artefacts are mandatory vs profile-gated, and resumability all need deciding - hence an RFC, not a CR.

Prior art to build on, not replace: `init`, `prd create`/`prd generate`, `persona generate --team`, the tool-neutral `agent-instructions.md` starter, and **RFC0019** (greenfield init friction, Accepted) + CR0077-0081. This RFC is the ORCHESTRATOR over those.

## Impact

Every new and returning user - the exact adoption risk the v5 site and docs exist to reduce, addressed at the tool itself rather than only in prose. Done well it is a genuine usage multiplier: the discipline becomes the path of least resistance instead of a sequence to be learned. Done badly it is a long, brittle wizard that people abandon - so resumability, sensible auto-inference, and "escape to manual at any step" are load-bearing, not polish.

## Design Options

- **Option A - Full guided orchestrator (one `init` walks everything).** `init` runs the entire spine (AGENTS.md → PRD → TRD → TSD → personas → epics/stories → first plan), checkpointed and resumable, diverging greenfield/brownfield internally. Most complete; biggest build; the wizard-abandonment risk is real, so it must be resumable and skippable per step.
- **Option B - Guided but staged (`init` sets up + hands off to a resumable checklist).** `init` scaffolds AGENTS.md and detects greenfield/brownfield, then presents a **living onboarding checklist** (in `status`/`hint`) that drives the user through the remaining steps one command at a time, each with its next-action prompt. Less monolithic; the user keeps the wheel; leans on the existing `hint` spine. Risk: still feels like separate steps, less "magic".
- **Option C - Profile-driven depth.** The orchestrator asks the project's weight up front (lite / standard / full) and only walks the artefacts that profile mandates - a lite repo skips TRD/TSD and personas and lands at a plan fast; a full one does the whole spine. Layers onto A or B. Best fits "the weight it warrants," but adds a decision the user may not be ready to make on day one.

## Recommendation

Lean **C-over-A**: a full guided orchestrator (A) whose depth is profile-gated (C), with B's resumable checklist as the always-available fallback and progress surface. Decompose so the **spine ships first** (AGENTS.md → PRD → first plan, greenfield) and TRD/TSD/personas and the brownfield path land as subsequent, independently valuable slices - so value arrives before the whole wizard is built, and the abandonment risk is tested early on the smallest complete path. To be settled in the Open Decisions before refining.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Orchestration shape: full guided `init` (A), staged checklist (B), or profile-gated (C) - and the fallback | Open |
| D2 | Greenfield vs brownfield divergence: how much of the spine is shared, and where do the two paths split (PRD source, TRD/TSD generation, persona risk signals)? | Open |
| D3 | Auto-generate vs interview balance per artefact: what does the tool draft and ask the user to confirm, vs interview from scratch? Default to draft-then-confirm? | Open |
| D4 | Mandatory vs profile-gated artefacts: are TRD, TSD and personas always walked, or only on standard/full profiles (lite skips to a fast first plan)? | Open |
| D5 | Resumability + escape hatch: how is a long flow checkpointed and resumed, and how does a user drop to manual at any step without losing state? | Open |
| D6 | Relationship to RFC0019 + CR0077-0081: does this supersede, absorb, or extend them? | Open |
| D7 | Is this a v5-launch blocker (operator: "more work before launch"), or a fast-follow v5.1? Affects whether the v5 tag waits on it | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
