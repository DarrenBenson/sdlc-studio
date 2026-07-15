# Unified Review - 2026-07-15 (close) - the bug-clearing sprint: four integrity fixes, a migration gap surfaced

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**All 4 bugs delivered, all approved on first independent review.** The Delivery backlog is clear.
BG0142 (reconcile agrees with check_links on a valid link), BG0144 (grooming refuses a fictional
Affects, at creation and plan), BG0145 (churn risk survives for a docs unit), BG0146 (a
recalibration can no longer relabel the falsifications that justified it). Full suite 2350 tests,
0 drift, gate PASS.

## The one thing a fresh session must carry

**This sprint surfaced a release-blocking gap: RFC0040 (P1).** The whole RFC0038 sizing + two-backlog
model is UNIVERSAL, not schema-gated - an existing consuming project upgrading to this skill version
would find `sprint plan --crs` refused (G1), childless-CR completion blocked (G2), CR creation
demanding `--size` (BG0148), and stale-Affects units ungroomed (BG0144), with no opt-in and no data
migration. It is all unreleased (freeze holds), so the migration must be built BEFORE the release,
and the release is a semver-major (5.0.0). Do not tag a release until RFC0040 lands. Already
backward-compatible: link-asymmetry/undecomposed only fire on declared links and post-intake states
(terminal CRs and link-less old artefacts are not flagged); legacy Points on a CR still reads.

## What went well

- **Independent adversarial review found no defects in any of the four fixes** - it traced each
  edge case (link resolution against live and archive indexes, the churn-fold double-count guard,
  the all-vs-some Affects logic, the sample_class reorder) and confirmed each.
- **BG0145 declined its own part (1) honestly:** the `--seed-source` CLI restriction it named was
  already removed by RFC0038, so the described symptom no longer reproduces - recorded, not faked.
- **BG0144's fixture ripple (12 files, ~140 cases) was migrated cleanly** by a subagent that left
  every deliberate-refusal test intact.

## Backlog rollup (non-terminal)

The Delivery backlog is now EMPTY of bugs. The Discovery backlog holds the forward plan, in priority
order:

- **RFC0040 (P1)** - the upgrade/migration path; must precede the post-freeze release.
- **RFC0039** - the discovery track (Issue, refine, triage, dual-track parallel roles, Three-Amigos).
- **CR0272** - command-surface cleanup + help rewrite around the process spine.
- Plus the older Discovery items: CR0254/0255/0256 (RFC0033 audit), CR0264 (filer dedup), RFCs
  0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. No
production release - and now explicitly gated on RFC0040 (the migration) before the next release,
which is a breaking, semver-major cut.

## For a fresh session

Start here, then `AGENTS.md`. The Delivery backlog is empty; the next work is a Discovery item and
must be decomposed first (refine is not yet a command). Read RFC0040 before planning any release -
the two-backlog + sizing model needs a migration and a schema/config opt-in gate before it can ship
to existing projects. Do NOT read a tokens-per-point rate from RETRO0029 or RETRO0030 - both were
delivered interactively and are UNMEASURED.
