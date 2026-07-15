# Unified Review - 2026-07-15 (close) - the migration pass: RFC0040 advanced via refine add

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**3/3 delivered (EP0037), advancing the P1 (RFC0040) via `refine add`.** `migrate_v3.py sizing`
brings an existing project to the sizing model - converting a cr/rfc/epic's legacy `Effort:`/`Points:`
to a `Size:` deterministically, and REPORTING what it cannot convert safely (a delivery unit's Effort
needs human re-sizing; an accepted childless request needs `refine`). The upgrade guide documents the
three-step path (migrate, refine, enforce). The review approved; its two non-blocking findings were
fixed the same sprint (point-band unified into `sdlc_md.size_for_points`; a Status-less artefact now
reports `needs_manual`). Full suite 2378 tests, 0 drift, gate PASS.

## What went well

- `refine add` did its intended job for the first time: it appended EP0037 to the already-decomposed
  RFC0040 (preserving EP0034). The finding->fix->use loop closed across three sprints.
- The migration is honest about its limits - it converts the sound mappings and flags the rest, never
  inventing an Effort->Points number the estimator would then be judged on. Dogfooded dry-run: 46
  convertible, 26 needing re-size, 0 needing refine.
- LL0016 self-caught: the point-band was duplicated, now shared.

## Backlog rollup (non-terminal)

- **RFC0040 (P1)** - opt-in gate (EP0034) AND migration + docs (EP0037) both Done. REMAINING: only
  the 5.0.0 version bump, which IS the release cut (gated by the freeze). RFC0040 stays open until then.
- **RFC0039** - refine (EP0035) + refine add (EP0036) done; REMAINING: Issue type, `triage`, personas.
- **CR0272** command cleanup, **CR0273** velocity metric, **CR0275** refine-show-on-decomposed;
  older: CR0254/0255/0256 (RFC0033 audit), CR0264 (filer dedup), RFCs 0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is the breaking, semver-major 5.0.0 cut - and with the opt-in gate, migration and upgrade
guide all shipped, RFC0040's deliverable work is DONE; only the version bump remains, at the cut.

## For a fresh session

Start here, then `AGENTS.md`. This repo enforces the two-backlog workflow. Upgrade path for a
consuming project: `migrate_v3.py sizing` -> `refine` the flagged requests -> set
`two_backlog.enforce` (see `reference-upgrade.md#two-backlog-migration`). Do NOT read a
tokens-per-point rate from RETRO0029-0033 - all interactive, UNMEASURED.
