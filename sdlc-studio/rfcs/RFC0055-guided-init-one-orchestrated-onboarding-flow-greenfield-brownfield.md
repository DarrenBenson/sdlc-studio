# RFC-0055: Guided init: one orchestrated onboarding flow (greenfield + brownfield) from zero to first sprint plan - AGENTS.md, PRD, TRD, TSD, personas, best practice baked in

> **Status:** Accepted
> **Decomposed-into:** EP0163
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

**A full guided orchestrator that always walks the whole spine, with profile tuning rigour rather than inclusion** (operator-decided 2026-07-26). `init` is one guided, resumable, draft-then-confirm flow that takes every user - greenfield or brownfield - through AGENTS.md → PRD → TRD → TSD → personas → epics/stories → a ready first `sprint plan`, and never skips an artefact. The profile (lite/standard/full) sets how deep each step goes, not whether it runs; B's resumable checklist is the always-available progress surface and escape hatch. This is a **v5-launch blocker**: the operator judges onboarding all-or-nothing for adoption, so the v5 tag waits for the full flow (both paths, every artefact). Internally it may still be built spine-first (greenfield AGENTS.md → PRD → first plan as the smallest complete slice, to de-risk abandonment early), but v5 does not launch until the whole flow is complete.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Orchestration shape | **DECIDED**: profile-gated full orchestrator (option C over A), resumable checklist (B) as fallback/progress surface |
| D2 | Greenfield vs brownfield divergence | **DECIDED**: one shared spine; `init` auto-detects the path (empty/near-empty repo = greenfield, existing source = brownfield) and asks the user to confirm. Only the PRD stage forks - greenfield `prd create` (interview), brownfield `prd generate` (read the code, and note the downstream `code verify` test-validation). TRD/TSD are generated from the PRD (brownfield also from the detected stack); personas from the PRD + risk signals. Every other stage is identical. |
| D3 | Auto-generate vs interview balance | **DECIDED**: draft-then-confirm (the tool drafts each artefact, the user edits/approves; interview only fills what cannot be inferred) |
| D4 | Mandatory vs profile-gated artefacts | **DECIDED**: ALWAYS walk everything (AGENTS.md, PRD, TRD, TSD, personas) - the profile tunes rigour/depth within a step, never skips it |
| D5 | Resumability + escape hatch | **DECIDED**: a checkpoint at `sdlc-studio/.local/onboarding.json` records each stage and its status; re-running `init` resumes from the first incomplete stage. Nothing advances without the user's confirmation (draft-then-confirm IS the checkpoint). Any stage can be run manually / skipped - recorded as `skipped` on the checklist, never silently - and `--reset` restarts the flow. The `status`/`hint` surface shows onboarding progress until the first plan is reached. |
| D6 | Relationship to RFC0019 (Accepted) + CR0077-0081 | **DECIDED**: RFC0055 ABSORBS them. The greenfield-init friction RFC0019 targets is subsumed by this orchestrator; on delivery, RFC0019 is marked Superseded-by RFC0055 and the CR0077-0081 intent is folded into the orchestrator's stages rather than built separately. |
| D7 | v5-launch blocker or fast-follow | **DECIDED**: v5-launch BLOCKER - all-or-nothing for adoption; the tag waits for the full flow |

## Delivery shape (for refine)

Decompose into one epic, spine-first so the smallest complete path (greenfield to a first plan) lands and is testable before the whole flow exists:

1. **Orchestrator skeleton + resumable checkpoint** - the `init` guided driver, the `onboarding.json` state model, greenfield/brownfield detection + confirm, the stage runner (draft-then-confirm, skip-to-manual, `--reset`).
2. **AGENTS.md stage** - write/confirm `AGENTS.md` (+ the `CLAUDE.md` import) from the tool-neutral starter.
3. **PRD stage** - the forking stage: greenfield `prd create`, brownfield `prd generate`; draft-then-confirm.
4. **TRD and TSD stages** - both generated from the PRD (+ stack for brownfield), draft-then-confirm.
5. **Personas stage** - `persona generate --team` from the PRD + risk signals, accept/edit.
6. **Decompose to first plan** - epics/stories, landing the user at a ready `sprint plan`.
7. **Progress surface** - the `status`/`hint` onboarding checklist + escape hatch.
8. **Docs + supersession** - rewrite `help/init.md` and `reference-*` for the guided flow; mark RFC0019 Superseded.

Each code story is TDD with executable ACs and a mutation-checked guard; closed through the two-role gate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
