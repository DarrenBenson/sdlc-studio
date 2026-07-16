# Unified Review - 2026-07-16 (close) - backlog triage as a ceremony inside plan (RFC0037 -> EP0047)

> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer of record:** Darren Benson (operator) - signed off explicitly; adversarial pass by the Dani Okafor engineering seat (subagent)
> **Date:** 2026-07-16
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**5/5 delivered (20 points).** RFC0037 built and Accepted (by derivation), ABSORBING CR0264 (now
Superseded). Backlog triage becomes a ceremony inside `plan`: `backlog_triage.py` runs deterministic
coherence lenses - **duplicate/subsumed** (shared `Affects` + wording similarity), **oversized**
(>8pts blocks), **stale** (old, undepended), **orphaned-dependency** (dep terminal/absent) - surfaced
from one shared primitive as a **filing-time** warning (US0169), a **plan** pass (US0170), and a
**status/hint** advisory (US0171). Full suite 2522, 0 drift, style clean.

## The review model this sprint (and the friction it surfaced)

The independent review ran as the **Dani Okafor** engineering-seat subagent: an adversarial pass with
a fresh context that did not write the code. It went **two rounds of REQUEST-CHANGES before APPROVE**
and earned every one - see below. The **recorded sign-off**, however, could not be the subagent's: the
author spawns and controls it, so recording its own APPROVE is self-review by automation (the harness
self-approval guard correctly refused). The operator signed off as **reviewer of record** and the
verdicts were recorded on their say-so. The distinction - adversarial reviewer (finds issues) vs
reviewer of record (an independent principal who signs off) - is being raised as its own RFC.

## What the independent review caught (two rounds)

- **Round 1:** a shared-library robustness bug - `iter_artifact_files` caught only `OSError`, so ONE
  non-UTF-8 artefact crashed EVERY scanner in the codebase. Plus orphaned-dep false positives on live
  non-triage-type deps, a future/prose date defeating staleness, no drop accounting, and a pointed
  container escaping the oversized lens.
- **Round 2:** the first fix landed one layer too high - the crash relocated into
  `reconcile.file_census` (past the write -> a partial write + index drift, on the filer AND the
  pre-commit drift gate). Fixed at the true root: a shared `read_text_safe` through the census and the
  dozen other artefact-body reads, with an END-TO-END regression test driving the real filer path.
- **Round 3: APPROVE**, all six findings independently re-verified end-to-end.

## Backlog rollup (non-terminal)

- **RFC0043** (DoR/DoD) - Accepted-pending, XL, decompose next (Sprint 3 territory). **RFC0035**
  (sprint report - needs per-attempt telemetry), **CR0273** (velocity), **RFC0036** (rolling policy),
  **RFC0039** close-out (its epics all Done). Release-gated (5.0.0, after the freeze): RFC0040,
  CR0254/0255/0256, CR0272 retire/promote half. NEW to raise: the reviewer-role RFC.

## Production state

v4.1.0 released. Freeze holds until ~2026-07-21. All work on `main` under `[Unreleased]`. Additive.

## For a fresh session

Start here, then `AGENTS.md`. `plan` now runs a backlog-triage pass; `backlog_triage.py check` gives
the detail; `status` carries a triage advisory. A non-UTF-8 artefact is now NAMED, never crashes a
scanner. Review model: an amigo/seat subagent does the adversarial pass, an independent principal
signs off.
