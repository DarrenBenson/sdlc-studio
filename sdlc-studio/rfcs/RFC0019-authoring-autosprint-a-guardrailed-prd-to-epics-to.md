# RFC-0019: authoring autosprint - a guardrailed PRD to epics to stories loop (greenfield first-mile)

> **Status:** Draft
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new

## Summary

`autosprint` gives a guardrailed, autonomous loop for **delivery** - clarify + triage
STOP, decisions ledger, per-unit critic, stall handling, a closing reconcile + review,
a retro. But its input is always an **existing backlog of units** (`--bugs` / `--crs` /
`--stories` / `--epic` or a tranche file). On a **greenfield** start the operator has a
PRD and nothing else - no units to point the loop at. The first mile, **PRD -> epics ->
stories**, has no equivalent guided loop: only the prose `epic` / `story` workflows
(model-interpreted, no ledger/critic/STOP) or `project implement --from epics` (which
couples authoring to implementation). So an agent starting greenfield **improvises the
whole authoring orchestration by hand**.

This RFC proposes closing that gap: a guardrailed loop that drives a PRD to a
**reviewable, fully-wired backlog** of epics and Ready stories, then stops - never
implementing. It is the authoring-phase sibling of the delivery autosprint.

## Problem (evidence)

An agent observed starting a brand-new project, verbatim:

- *"artifact.py only generates minimal scaffolds without creating index files... I'll
  author the artifacts using full templates and manage the index files myself."*
- *"33 stories total across 7 epics... I'll parallelize by delegating to sub-agents -
  one per epic, each given... ID ranges... then I'll build the index myself. Sub-agents
  are costly and risk inconsistency."*
- *"I'm concerned about consistency across 7 agents handling 33 files... The filenames
  need to match the epic links exactly."*

The agent hand-built the epic cut, the 7-way fan-out, the ID ranges, the slug/filename/
link matching, the per-epic indexes, and a shared-context preamble (PRD, personas, all
decisions, the API contract, the template) baked into each agent - re-deriving, badly
and without guardrails, what a guided authoring loop should own. Its own stated worry
was **consistency**, which is exactly what a deterministic substrate plus a critic
removes.

## Design Options

- **Option A - Extend autosprint to accept a PRD as the batch source.**
  `autosprint <prd.md> --goal design` (or `--from prd`) bootstraps the backlog: decompose
  the PRD into epics, then epics into Ready stories, stopping at the `design` goal's
  existing "reviewable backlog" output. Reuses every existing guardrail (STOP, ledger,
  critic, closing review, retro) unchanged; the only new surface is "the batch can be a
  PRD, not just existing units". **Smallest, most consistent change.** Preferred.
- **Option B - A new top-level command** (e.g. `author` / `backlog`). Cleaner mental
  model for "I am creating, not delivering", but duplicates the autosprint loop scaffolding
  and risks two divergent loops. Rejected unless the loops genuinely differ.
- **Option C - Status quo + better docs.** Document the manual `epic` then `story` then
  review sequence as a recipe. Cheapest, but leaves the orchestration (consistency,
  guardrails, wiring) on the model every time - the friction this RFC exists to remove.

## Recommendation

**Option A.** The gap is narrow and precise: autosprint's batch resolver cannot take a
PRD. Teach it to, add an authoring decomposition phase ahead of the existing `design`
output, and the whole guardrail apparatus is reused rather than rebuilt. The loop should
stand on the deterministic create substrate (see Dependencies) so structural consistency
(IDs, slugs, filenames, epic links, indexes) is guaranteed by construction and the only
thing a content-authoring sub-agent owns is prose - removing the agent's stated
consistency worry.

Sketch of the proposed loop:

1. **Clarify + triage STOP.** Batch every scoping question once; present the proposed
   **epic cut** (count, titles, mapping to PRD features) and stop for approval. (Authoring
   needs the operator to bless the decomposition shape before any stories are written.)
2. **Author phase.** For each approved epic: deterministically create the epic and its
   Ready stories as fully-wired scaffolds (correct IDs, slugs, filenames matching links,
   index rows, Story-Breakdown updated) via the batch create path; delegate **content fill**
   only - Given/When/Then, `Verify:` lines, edge cases to the configured minimums.
3. **Per-epic critic.** Reuse the Three Amigos / review-seat consultation already
   described for story generation as the per-unit critic; reject -> repair. This is where
   cross-agent **content** consistency is enforced.
4. **Closing gate.** The existing mandatory reconcile + review (the `design`-goal review
   of the produced backlog) + retro. Stops at a reviewable backlog. **Never implements**
   (that is a separate, later `autosprint --goal done` or `project implement`).

## Open Decisions

A greenfield agent's reflection (2026-06-24) resolved several of these in evidence;
captured below.

| # | Decision | Status |
| --- | --- | --- |
| D1 | Extend `autosprint` (Option A) vs a new `author` command (Option B) | **Resolved: A (extend).** The gap is only that the batch resolver can't take a PRD; extending reuses every guardrail (STOP, ledger, critic, closing gate, retro). A separate command would clone the loop and risk drift |
| D2 | How many STOPs? | **Two, confirmed.** Agent: two non-negotiable pauses - (1) approve the **epic cut** before any story is written (the highest-stakes judgement call; getting it wrong silently wastes all 33); (2) resolve the PRD's **open questions** / state the assumptions about to be baked in, before story authoring |
| D3 | Content authoring: orchestrator-inline vs per-epic sub-agent fan-out | **Fan-out wanted as an option**, over pre-wired scaffolds, "with the tool owning structure, parallelism stops being risky" |
| D4 | Reuse `--goal design` vs a distinct `--goal author` for the PRD-bootstrap case | **Resolved: reuse `design`.** The goal names the stop condition ("a reviewable backlog") - identical for both cases. The **input** (a PRD path vs a `--crs`/`--epic` query) triggers the bootstrap, not a new goal. `--goal author` would conflate input-type with stop-condition |
| D5 | Dedupe with `project implement --from epics` and `cr action` | **Resolved: shared decomposition core.** The bootstrap reuses `epic`-from-PRD + `story`-from-epic generation + `cr action`; the loop is the guardrailed wrapper stopping before implementation - the "generation half" of `--from epics`, not a parallel path |
| D8 | A `--goal plan` rung for sprint planning (operator idea, 2026-06-24) | **Open - leaning yes, as a thin rung.** See "Goal ladder" below |
| D6 | Does the loop seed the PRD, or require one? | **Require one.** PRD is the precondition; seeding is the `init`/CR0079 concern |
| D7 | Where does it stop? | **At a reviewable backlog, confirmed** - all story files at Draft, indexes built, `validate`/`reconcile` green, every epic link resolves, every story meets its minimum ACs/edge-cases. "Not one step further" - no code plan, no implementation. The closing **consistency check** "is the thing that would actually replace me as the structural coordinator" |

## Goal ladder (D8 - the `--goal plan` rung)

Today's ladder is how far the loop drives: `triage` (groom + approve) -> `design` (decompose
to a Ready backlog) -> `done` (deliver). A **`plan`** rung for *sprint planning* fits between
`triage` and `design`:

The ladder is the **operator's review workflow** - drive one rung at a time, reviewing between:

> **plan** the next autosprint -> *review* -> **breakdown** (design) to ready-to-work, with
> story-point estimates -> *review* -> **run** (done).

| `--goal` | Stops when... | Output | Operator phrase |
| --- | --- | --- | --- |
| `triage` | the groomed plan is approved | ordered worklist (readiness of the given batch) | - |
| **`plan`** *(proposed)* | a sprint-sized batch is **selected and sequenced** | a committed **sprint plan** | "plan the next autosprint" |
| `design` | units decomposed to Ready stories with AC **and story-point estimates** | a reviewable, estimated backlog | "break it down, make sure it's ready to work on" |
| `done` | every unit is delivered | the delivered increment | "run the next autosprint" |

The distinction from `triage`: triage grooms the *whole given batch* for readiness; `plan`
**selects a sprint's worth** (capacity / budget fit) and sequences it. It reuses what already
exists - `--order wsjf` + the complexity-weighted budget (CR0038) and `project plan`'s
dependency order + wave estimation - and emits a persisted sprint-plan artifact, then stops.
**`design` assigns story points** (written into each story as `**Story Points:**`), which
`reconcile fields` (CR0082) projects into the index - closing the hand-copy the field agent
hit. **Recommendation: add `plan` as a thin rung** (selection + estimation, not new
machinery); it is orthogonal to the PRD-authoring bootstrap (D1/D4) and ships as its own
work-stream. Each rung stops for operator review by default.

## Dependencies

This loop is the **orchestration**; it stands on deterministic create primitives that
should land first so structural consistency is free:

- **CR0077** - `new` creates a missing index lazily + opt-in full-template scaffolds.
- **CR0078** - batch create: reserve an ID range, write N files, wire all into epics
  atomically in one pass (the substrate for the author phase's per-epic creation).
- **CR0079** - `init` becomes executable: folder structure, indexes, agent-instructions,
  and an opt-in singleton scaffold (the step *before* this loop runs).
- **CR0080** - the project decisions log feeds the loop's **handoff context**, so the
  PRD-answers/decisions that propagate into every story are referenced once, not pasted
  per agent (the loop's D2 Pause 2 records its assumptions here).
- **CR0081** - the greenfield runbook names this loop as the step that collapses the
  `epic -> story` span once it lands.
- **CR0082** - reconcile projects the file-owned index cells (title, points, persona) so
  the loop's closing **consistency check** leaves a fully-derived index with no
  hand-copied fields (the audited residual cost of the manual fan-out).

Guardrail and consultation machinery reused (not rebuilt): RFC0001 (the loop, STOP,
ledger, stall handling, closing gate), the Three Amigos / review-seat consultation
(`reference-workflow-personas.md`), and the `design` goal's reviewable-backlog output.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
