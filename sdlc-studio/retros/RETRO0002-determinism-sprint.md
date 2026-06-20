<!--
Sprint retro for the determinism-hardening tranche. Written at the close; read at
the start of the next sprint. Related: reference-autosprint.md, CR0018.
-->
# RETRO-0002: Determinism-hardening sprint

> **Date:** 2026-06-20
> **Batch:** CR0016, CR0018, CR0003, CR0021, CR0004, CR0008, CR0007
> **Goal:** done
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

- **Sprint-zero** - CR0016 (sharpened the tautological AC on CR0003-CR0009 so the
  loop can verify them) and CR0018 (retro capability already shipped; closed).
- **CR0003 / US0012** - `integrity.py`: referential-integrity check (required links
  per the matrix + dangling refs; active=error, terminal=advisory).
- **CR0021 / US0013** - `audit.py` + the new **tranche-audit** workflow step
  (weak-AC, unmet-deps, already-terminal, link-integrity), turning "operator
  notices mid-flow" into a defined gate. The operator's own insight, mid-sprint.
- **CR0004 / US0014** - `review_prep` staleness from git `%cI` commit time, datetime
  comparison, malformed-warning.
- **CR0008 / US0015** - `config.py`: config-defaults.yaml as the single source
  (status.py reads it), 12 doc YAML fences removed, drift-guard test.
- **CR0007 / US0016** - `resume.py`: `epic implement --resume` from canonical Status,
  run-state JSON.

## Blocked / deferred

- None. All 7 reached Done green. Filed **BG0018** (a reconcile parser bug surfaced
  by the closing reconcile) for a future fix.

## What went well

- **The tranche-audit step proved itself the same sprint it was built.** Run on the
  remaining batch it showed 3/3 ready (because CR0016 had sharpened the AC) and on
  the backlog it flagged CR0018 already-terminal - exactly its job.
- **The critic earned its keep, hard.** It REJECTED three of the five built units
  (audit.py AC-section scoping; config.py's missing real consumer + a relabelled
  drift hole; resume.py's too-narrow terminal set + over-matching epic id + a false
  CR AC). Every reject was a real defect or honesty gap, repaired before commit.
- **Determinism theme caught its own kind of bug:** the closing reconcile surfaced
  BG0018 (a title beginning with a status word misparsed as that status).

## What was hard / what stalled

- **AC honesty drift.** Twice the implementation quietly narrowed the CR's AC
  (config integration; resume reading the WF table). The critic caught both. Lesson:
  when deviating from an AC, amend the CR in the same unit, do not let the paperwork
  lie.
- A leading `+` at the start of a wrapped line tripped markdownlint twice in story
  Implementation notes (it reads as a list bullet).

## Lessons

- A pre-flight tranche audit belongs in the loop, not in the operator's head - now
  it is step 2. <!-- promote: durable loop-design lesson -->
- Reuse compounds: `integrity.py` (CR0003) became the audit's link-integrity lens
  the very next unit; `config.py` got a real consumer only because the critic
  insisted. Build the building block first.
- Prefer the authoritative signal over a derived view: git commit time over mtime
  (CR0004), story Status over a WF table (CR0007), config YAML over a doc table
  (CR0008). The determinism through-line.

## Metrics

- Tokens: not separately metered (continuous session) · Critic rejects: 3 (all
  repaired) · Commits: ~9 green · Tests: 200 -> 247 · New scripts: integrity, audit,
  config, resume, ledger (+loop_guard from Phase 2).
