# Unified Review - 2026-07-15 (close) - command-surface audit + the two backlogs made first-class

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer:** sdlc-studio; agent; v1 (delivery critiqued independently by the Dani Okafor engineering seat)
> **Date:** 2026-07-15
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**5/5 delivered (EP0041, CR0272 slice 1) - 19 points.** `command_audit.py` enumerates every command
(SKILL Type Reference, help catalogue, scripts/), maps each to the process spine, and dispositions
keep/review from three structural signals (spine, catalogue drift, tooling health via `--check-tools`);
`--write` produces `sdlc-studio/reviews/command-audit.md`. This run recorded the real findings: 5
help-only commands to promote/retire (lessons, repo, retro, review, upgrade) and 0 broken tools across
61 scripts. And the dual-track is now visible from the first commands an operator reaches for: `hint`
names how many Discovery items await refinement/triage, and the `status` dashboard shows the
Discovery/Delivery split. Full suite 2438 tests, tools 183, 0 drift, gate PASS.

## What went well

- **The audit is a re-runnable guard, not a one-time sweep** - and it caught its own undocumented
  script on first run.
- **The independent review caught three real defects the suite missed:** the hint recomputing a
  full-repo scan twice (~1.4s -> ~0.9s once fixed), parked (Deferred/Blocked) items falsely nudged,
  and a `--write` doc certifying tooling it never checked. All fixed, re-review clean.

## Backlog rollup (non-terminal)

- **CR0272 (slice 1 done)** - the audit + backlog surfacing shipped; slice 2 (promote/retire the 5
  help-only commands + rewrite the help around the spine) is now evidenced by `command-audit.md`.
  Stays open; deliver via `refine add`.
- **RFC0039** - refine/refine-add/Issue+triage/amigo-consult all done; only CR0272 (its area e)
  remains. **RFC0040 (P1)** - only the 5.0.0 version bump remains.
- **NEW (operator report from another project):** **RFC0041** - a unified `migrate` command that
  reviews every artefact and upgrades where necessary; **BG0150** - `project upgrade` does not stamp
  the version or sweep open RFCs/CRs/epics/stories. Both filed this session for a future sprint.
- Older: CR0254/0255/0256 (RFC0033 audit), CR0264, CR0273 (velocity), RFCs 0035/0036/0037.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. The next
release is the breaking, semver-major 5.0.0 cut. This slice is additive.

## For a fresh session

Start here, then `AGENTS.md`. This repo enforces the two-backlog workflow, now visible at `hint` and
`status` (Discovery awaiting refinement/triage; the Discovery/Delivery split). `command_audit.py`
audits the command surface (`--write` refreshes `command-audit.md`). Do NOT read a tokens-per-point
rate from RETRO0029-0036 - all interactive, UNMEASURED.
