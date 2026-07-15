# Unified Review - 2026-07-15 (close) - the two-backlog finale: the gates work, and CR0271 closed by its own gate

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Triggered by:** the sprint close - review currency is a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**All 7 units delivered.** The RFC0038 finale - the two-backlog gates - is complete. CR0271 was
DECOMPOSED into EP0033 -> US0120-US0124 (14 story points, 1.75x its single-shot 8, replicating the
LL0038 under-sizing finding), delivered, and then **closed by its own G2 gate**: with every story and
EP0033 Done, `transition CR0271 -> Complete` passed the derived-status rule CR0271 itself built. The
finale closed itself.

The backlog is now genuinely dual-track: `RFC/CR` are the **Discovery backlog** (the options funnel),
`epic/story/bug` are the **Delivery backlog** (sized work), named that way by operator decision
(dual-track agile / upstream Kanban; "Delivery" does not presume a product). Five gates enforce the
split - plan refuses a request (G1), status shows both backlogs (G4), reconcile flags an
accepted-but-unrefined request as `undecomposed` (G5) and a one-sided link as `link-asymmetry` (G3),
and a request's terminal status is derived from its children (G2).

## What went well

- **Independent review caught a real bug the author had worked around.** US0120's `decomposed_ids` read
  parenthetical annotation ids as direct children; the reviewer refused the first cut, and the same
  defect had earlier been hand-worked-around (stripping the annotation off CR0271). author != reviewer
  turned a masked symptom into a root-cause fix. One rejected verdict, fixed and re-approved.
- **Every gate was validated against what it defends (LL0010):** a childless CR refused Complete, a
  one-sided link reported, a request batch refused a plan, an accepted childless request flagged
  undecomposed - each proven to FAIL, not merely to exist.
- **The `undecomposed` check keeps `reconcile detect` clean on a healthy backlog** by scoping to a
  request past intake, preserving the CI exit-0 contract.

## The one caveat a fresh session must carry

**This sprint's per-unit token cost is UNMEASURED.** It was delivered interactively, not through the
autosprint runner that measures tokens per unit, so there is no estimate-vs-actual rate for it - and
none was invented. The evidence this sprint carries is the DECOMPOSITION (14 points from a single-shot
8, 1.75x), which is about SIZING, not the rate. Do not read a tokens-per-point rate from this sprint.
The next runner-driven, decomposition-sized sprint is the real out-of-sample test.

## Backlog rollup (non-terminal)

The two-backlog view now reads honestly (13 non-terminal): 9 in Discovery, 4 in Delivery.

- **Discovery (requests to refine):** CR0254/0255/0256 (RFC0033 audit), CR0264 (filer dedup),
  **CR0272** (audit + clean up the command surface, rewrite help around the process spine - raised this
  session), and RFCs 0035/0036/0037 plus **RFC0039** (the discovery track - raised this session).
- **Delivery (bugs):** BG0142/0144/0145/0146.

## The design thread this session opened (captured, not built)

The operator sketched a coherent next phase, captured as Discovery items so nothing is lost and the
decompose discipline the gates enforce applies to it too:

- **RFC0039 - the discovery track.** Add an **Issue** as the defect-side discovery item (operator-
  confirmed Option A: an Issue triages into bugs or a story/CR; a bug stays the concrete delivery
  unit). Add **refine** (a CR/RFC -> epics/stories) and **triage** (an Issue -> bugs/stories) as
  first-class commands - the place where questions get answered. The pay-off is PARALLELISM: one person
  refines/triages the Discovery backlog ahead while another delivers the sprint, which the gates
  shipped this sprint make safe. Bake the Three-Amigos personas into refine/triage/review. Likely
  absorbs RFC0037.
- **CR0272 - command-surface cleanup + help rewrite** around the process spine (raise -> break down ->
  sprint+review; PRD/TRD/TSD/Personas as the top-level levers; reconcile/review/audit as support).

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. No production
release. The two-backlog gates are dogfooded here and ready to forward-port when the freeze lifts.

## For a fresh session

Start here, then `AGENTS.md`. The backlog is dual-track: `status backlog` shows Discovery and Delivery
separately. A request (RFC/CR) cannot be sprinted - decompose it into stories/epics first (refine is
not yet a command; do it with `artifact.py new --type epic/story` writing the `Parent:` /
`Decomposed-into:` links). Read RFC0039 before touching the discovery track, and CR0272 before touching
the command surface. Do NOT read a tokens-per-point rate from RETRO0029 - it is UNMEASURED.
