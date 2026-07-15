# Unified Review - 2026-07-15 (close) - the migrate orchestrator + the version-stamp fix

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**5/5 delivered (EP0042 + BG0150, RFC0041) - 21 points.** `migrate` is the upgrade front door: one
command that reviews every artefact and upgrades where it safely can. It orchestrates
`project_upgrade` (conventions + version) + `migrate_v3 sizing` (a container's legacy Effort/Points
-> Size) + an artefact-review sweep, and emits ONE report split into **deterministic** (auto-applied)
vs **needs a human** (each item with the exact command - refine/triage/re-size). It auto-applies only
the deterministic, reversible set and never guesses a judgement (no honest Effort->Points map).
BG0150 fixed: `project_upgrade` no longer stamps a bogus `skill_version: "unknown"` when the install
version can't be read - it warns and skips. Dogfooded on `../homelab`: 4 sizing conversions + 13
needs-human items, touching nothing in dry-run. Full suite 2445 tests, tools 183, 0 drift, gate PASS.

## What went well

- **Orchestration, not reimplementation.** `migrate` is glue over existing, tested primitives; the
  value is the aggregation and the honest deterministic-vs-needs-human split.
- **A real operator bug fixed.** BG0150 - the version logic existed and looked complete; the gap was
  one `or "unknown"` fallback silently fabricating a value.

## Backlog rollup (non-terminal)

- **RFC0041** - migrate + BG0150 done; RFC0041 reaches terminal when EP0042 + BG0150 close.
- **CR0272 slice 2** (retire/fold the 5 help-only commands + help rewrite) - evidenced by
  `command-audit.md`; deliver via `refine add`. **RFC0040 (P1)** - only the 5.0.0 version bump.
- **NEW (operator report, live):** **CR0276** - audit must warn + confirm before a large adversarial
  fan-out (a ~2.3M-token, 192-agent run launched with no heads-up). Filed for a future sprint.
- Older: CR0254/0255/0256 (RFC0033 audit), CR0264, CR0273 (velocity), RFCs 0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is the breaking, semver-major 5.0.0 cut. `migrate` and the BG0150 fix are additive.

## For a fresh session

Start here, then `AGENTS.md`. Upgrade front door: `migrate` (dry-run; `--apply` writes the
deterministic set, reports refine/triage/re-size). The two-backlog dual-track shows at `hint` and
`status`. Do NOT read a tokens-per-point rate from RETRO0029-0037 - all interactive, UNMEASURED.
