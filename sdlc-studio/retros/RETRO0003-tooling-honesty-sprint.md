<!--
Sprint retro for the tooling-honesty + loop-integrity tranche. Related:
reference-autosprint.md, CR0018.
-->
# RETRO-0003: Tooling-honesty + loop-integrity sprint

> **Date:** 2026-06-20
> **Batch:** BG0019, BG0018, CR0023, CR0022, CR0012, CR0013, CR0014, CR0017
> **Goal:** done
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- **BG0019** - integrity + audit handle the `bug` artifact class (links optional ->
  advisory; readiness by repro+fix, not AC). Cleared the RED integrity check.
- **BG0018** - reconcile reads index status by table-header **column position**, not
  a cell scan, so a title beginning with a status word is no longer misread. Systemic
  audit: only reconcile was affected.
- **CR0023** - the conformance gate is complete: a Done story now also requires
  **reconciled** (no index drift) and **critiqued** (a committed independent-critic
  APPROVE, via new `critic.py`). "Conformant" finally means the full lifecycle ran.
- **CR0022** - `autosprint plan` orders **deps-first** (topological, priority tiebreak);
  a cycle aborts named.
- **CR0012/13/14/17** - TRD/TSD doc-truth: corpus figures, deployment paths, the
  count-independent test gate, and CR0005's overstated "no timestamp".

## Blocked / deferred

- None. 8/8 green.

## What went well

- **The triage caught defects in our own new tools before any work started.** Auditing
  the backlog with `audit.py` left `integrity.py` RED on a standalone bug - so BG0019
  filed itself. Dogfooding the determinism checks is what found their bug-class gap.
- **The conformance gate proved itself on its own delivery.** US0017 (which built the
  critiqued stage) was held non-conformant by that stage until its own critic verdict
  was recorded and it was indexed. The gate works because it blocked the hand that
  built it.
- **BG0018 fixed a whole class, not an instance** - and it had bitten twice live
  (US0014, CR0023 titles). Header-positional parsing + a systemic caller audit.
- **The critic kept earning it:** REJECT-then-fix on CR0023 (reconciled too narrow -
  missing-row) and CR0022 (prose IDs in Depends-on injected phantom ordering edges).

## What was hard / what stalled

- **Backfill debt:** turning on the critiqued gate meant backfilling 11 verdicts for
  pre-existing Done stories. Honest going forward (a future Done can't skip the
  critic), but a one-time retroactive attestation.
- The `+`-at-line-start and `_emphasis_` markdownlint traps bit twice more. A
  pre-commit per-artifact lint would catch these before the gate.

## Lessons

- Treat each artifact type as its own class in the checks: bug != story != CR
  (BG0019). A required-link matrix and an AC-readiness rule are type-specific.
- A gate is only honest if it is hard to satisfy without doing the work: the
  critiqued stage is enforced by a committed artifact, not trust (CR0023).
- Read positionally, not by inference: status by column, deps by leading token -
  inference from titles/prose is where silent misreads live (BG0018, CR0022).

## Metrics

- Tokens: not separately metered · Critic rejects: 2 (CR0023, CR0022; both repaired)
  · Commits: 7 green · Tests: 254 -> 270 · New scripts: critic.py · Backfilled
  verdicts: 11.
