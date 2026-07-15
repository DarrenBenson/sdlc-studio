# Unified Review - 2026-07-15 (close) - the Three Amigos, baked into refine and triage

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**6/6 delivered (EP0040, advancing RFC0039) - 20 points.** The Three-Amigos consult, dormant since
the seats/amigos convergence, is now wired into the decomposition ceremonies. `refine` and `triage`
resolve their `--question` items to the actual named seat cards (the project's own, else the shipped
defaults Dani Okafor / Lena Marsh / Sam Eriksson), framed with each seat's review render -
**engineering-led** for refine, **QA-led** for triage - and record the consult on the request/Issue
(a `> **Consulted:**` line + an `## Amigo Consult` section) as an audit trail. `--skip-personas` is
byte-equivalent; a broken project seat fails the ceremony before anything is minted. Shared
`persona_resolve` library (`consult`/`amigo_panel`/`seat_name`/`record_consult`) + a `panel` CLI.
Full suite 2422 tests, tools 183, 0 drift, gate PASS.

## What went well

- **Wiring, not building.** `resolve_consult`/`frame` existed and were correct but callerless; the
  sprint gave them a reason to run, so it was small precisely because the primitive was sound.
- **The independent review found a real correctness bug the suite missed.** Dani Okafor (author !=
  reviewer, and the very seat this feature resolves) built a multi-line question that injected a
  fake `##` heading into the audit section and broke its idempotency; also flagged ~15KB of unused
  framing in every JSON result. Both fixed (collapse questions to one line; `consult()` returns a
  lean panel), re-review APPROVE.

## Backlog rollup (non-terminal)

- **RFC0039** - refine (EP0035), refine add (EP0036), Issue+triage (EP0038), and the amigo consult
  (EP0040) all done. REMAINING: the command-surface / doc rewrite (CR0272, area e). Stays open.
- **RFC0040 (P1)** - deliverable work done; only the 5.0.0 version bump remains (the release cut,
  freeze-gated). Stays open.
- **CR0272** command cleanup + help rewrite, **CR0273** velocity metric; older: CR0254/0255/0256
  (RFC0033 audit), CR0264 (filer dedup), RFCs 0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is the breaking, semver-major 5.0.0 cut. The amigo consult is additive and behind the same
`two_backlog.enforce` opt-in path as the ceremonies it enriches; `--skip-personas` is the escape
hatch for a project with no seats that wants the generic path.

## For a fresh session

Start here, then `AGENTS.md`. This repo enforces the two-backlog workflow. A defect enters as an
**Issue** (Discovery), is **triaged** into bugs; a request is **refined** into stories. Both
ceremonies now run the **Three-Amigos consult** on `--question` - resolved to named seats, recorded
on the artefact. Do NOT read a tokens-per-point rate from RETRO0029-0035 - all interactive,
UNMEASURED.
