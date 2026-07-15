# Unified Review - 2026-07-15 (close) - the discovery track gains a defect side: Issue + triage

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**6/6 delivered (EP0038 advancing RFC0039, EP0039 closing CR0275) - 19 points.** The Discovery
backlog gains its defect side: a new **Issue** artefact type (a raw report, sized S/M/L/XL with a
Severity, no points) and a **triage** command that decomposes an Issue DIRECTLY into the bugs that
deliver its fix - the mirror of `refine` turning a request into an epic + stories. A new
`is_discovery(type_)` predicate (RFC/CR/Issue) is what every backlog-side gate now consults, while
`is_request` stays the narrow RFC/CR set (refine's domain), so a request is refined and an Issue is
triaged, never conflated. `refine show` now also works on an already-decomposed request (CR0275).
Full suite 2404 tests, tools 183, 0 drift, gate PASS.

## What went well

- **The independent review caught a real BLOCKER the suite missed.** On schema v3, a Low-severity
  triaged bug was folded into a finding-consolidation CR, so triage mis-parented that CR as the
  Issue's child (and could delete a shared CR on rollback). Fixed with a clean
  `artifact.new(..., consolidate=False)` bypass + a defence-in-depth guard + a v3 regression test;
  the reviewer re-ran the original v3 repro and confirmed APPROVE for both v2 and v3.
- **refine's machinery paid off twice.** triage reused refine's atomic mint + rollback; the shared
  `Parent:`/`Decomposed-into:` link writers moved to `lib.sdlc_md` before triage became the second
  caller (LL0016 applied prospectively).

## Backlog rollup (non-terminal)

- **RFC0039** - Issue type + triage (EP0038) and refine (EP0035) done. REMAINING: Three-Amigos
  persona bake-in to triage/refine, and the command-surface/doc rewrite (CR0272). Stays open;
  deliver the next slice via `refine add`.
- **RFC0040 (P1)** - opt-in gate + migration both done; only the 5.0.0 version bump remains (the
  release cut, freeze-gated). Stays open.
- **CR0272** command cleanup + help rewrite, **CR0273** velocity metric (reframed); older:
  CR0254/0255/0256 (RFC0033 audit), CR0264 (filer dedup), RFCs 0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is the breaking, semver-major 5.0.0 cut. The Issue type + triage are additive and behind the
same `two_backlog.enforce` opt-in as the rest of the two-backlog workflow.

## For a fresh session

Start here, then `AGENTS.md`. This repo enforces the two-backlog workflow. A defect now enters as an
**Issue** (Discovery) and is **triaged** into bugs (Delivery); a request is **refined** into stories.
`is_discovery` (RFC/CR/Issue) is the backlog-side predicate; `is_request` (RFC/CR) is refine's. Do
NOT read a tokens-per-point rate from RETRO0029-0034 - all interactive, UNMEASURED.
