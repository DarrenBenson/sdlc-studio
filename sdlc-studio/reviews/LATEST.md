# Unified Review - 2026-07-15 (close) - the v5 spine: opt-in gate + refine, and two bugs the reviewer caught

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**All 7 stories delivered across two epics.** EP0034 (the schema-v4/config opt-in gate) makes the
whole two-backlog + sizing model enforce-on-request, default OFF, so an existing project can upgrade
without its CR workflow breaking - the precondition RFC0040 named for a safe release. EP0035 (the
`refine` command) turns the hand-decomposition (CR0271 -> EP0033) into a command, and doubles as the
migration tool. Full suite 2367 tests, 0 drift, gate PASS.

## The one thing a fresh session must carry

**The independence gate caught TWO real bugs this sprint, both invisible to the author.** In Epic A,
`new_batch` never threaded the target root, so a batch create read enforcement from the CWD, not
`--root`. In Epic B, `refine` was not atomic: a bad story title left an orphan epic on disk that
reconcile could not see in the unenforced projects refine migrates - while the CLI printed "refused".
Both fixed and re-approved. Keep running author != reviewer on every delivery; it is the discipline
that pays.

## What went well

- The opt-in gate is default-off via `project_override` (own file only), so no defaults-merge can
  flip it on globally - existing projects stay on their old flow until they opt in.
- `refine` validates ALL input up front (refinable + points + every title + the request's Status
  line) and rolls back on a residual IO error, so a bad breakdown mints nothing.
- The happy path is clean: refine produces symmetric `Parent:`/`Decomposed-into:` links, a matching
  `Derived Point Total`, and a request moved to its working status; reconcile stays 0-drift.

## Backlog rollup (non-terminal)

The Discovery backlog holds the forward plan; each item now has its first slice DELIVERED or is
untouched:

- **RFC0040 (P1)** - opt-in gate delivered (EP0034); REMAINING: the migration pass (Effort->Points/
  Size, old childless CRs), the docs, and the 5.0.0 bump. Still gates the release.
- **RFC0039** - refine delivered (EP0035); REMAINING: the Issue type, `triage`, deeper persona
  integration.
- **CR0272** - command-surface cleanup + help rewrite (untouched).
- Older: CR0254/0255/0256 (RFC0033 audit), CR0264, RFCs 0035/0036/0037.

Note: `refine` refuses re-refining an already-decomposed request, so RFC0039/RFC0040's next slices
need a `refine --add` mode or manual wiring (RETRO0031 action).

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is a breaking, semver-major (5.0.0) cut and is gated on RFC0040's remaining work (migration +
docs). The opt-in gate shipped this sprint is what makes that release safe.

## For a fresh session

Start here, then `AGENTS.md`. This repo has `two_backlog.enforce: true`, so its gates are on; a bare
project defaults off. Use `refine show`/`refine apply` to decompose a request (no more hand-wiring).
Read RFC0040 before planning a release. Do NOT read a tokens-per-point rate from RETRO0029/0030/0031 -
all three were delivered interactively and are UNMEASURED.
