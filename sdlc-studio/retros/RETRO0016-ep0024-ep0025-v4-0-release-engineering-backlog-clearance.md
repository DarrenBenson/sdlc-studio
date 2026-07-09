# RETRO-0016: EP0024/EP0025 v4.0 release engineering + backlog clearance

> **Date:** 2026-07-09
> **Batch:** EP0024 (v4.0 release engineering, CR0198) + EP0025 (backlog clearance + tooling, CR0199/CR0201)
> **Goal:** prepare the v4.0.0-rc.1 release (schema v3 the default for new projects, rehearsed migration, rc checklist) and clear the open backlog, all without auto-flipping any existing project
> **Delivered:** 8/8 stories + 1 rehearsal-found bug fix (BG0070)   **Blocked:** 0

## Delivered

- US0105 - `init` seeds `schema_version: 3` for new projects; the code default stays 2 and the reader is override-only, so no existing/unpinned project flips. This repo pinned to 2.
- US0106 - `project upgrade` presents the v2->v3 migration as a directed walk; rehearsed dry-run on two real consuming projects (neutral evidence), which surfaced BG0070.
- BG0070 - `migrate_v3` batched its per-artefact `git log --follow` into one pass: >150s / did-not-complete -> 0.2-0.3s on the real ~1,700-artefact projects.
- US0107 - majors-only section added to the release-gate checklist.
- US0108 - version homed at `4.0.0-rc.1` across all homes; CHANGELOG -> `[4.0.0]` with a breaking-change inventory; dormant/freeze banners removed; `check_versions`/`validate_skill` made pre-release-aware.
- US0109 - the v4-rc-readiness checklist (each gate + a live check command).
- US0110 - deterministic `status.py backlog` census (vocab-driven terminal detection, `--format json`, `--type` filter).
- US0111 - provenance-tag lint guard widened to US-form pairs + the config-template glob; 8 leaked tags stripped.
- US0112 - closed BG0067-0070; archived 57 story + 39 cr rows into the rc release batch; `validate` accepts a v3 ULID id (`sdlc_md.is_v3_id`).

## Blocked / deferred

- None blocked. Surfaced-but-not-in-scope: **6 legacy epics (EP0001-0004, EP0008, EP0009) carry a stale `Ready` status** - discovered by US0110's new `status.py backlog` (the old grep missed them). Three fully-complete ones (EP0005/0006/0007) were closed; the rest need per-epic judgement (EP0008 has unchecked items). A small follow-up hygiene pass.

## What went well

- The adversarial critic gate paid for itself repeatedly: this sprint the **closing full-diff critic found a genuine cross-unit defect** no per-unit review could - a fresh v4 project (config schema 3, no `.version`) was shown a v2->v3 walk because `migration_walk`/`detect` read `.version` while `init` writes `.config.yaml`. Fixed with `_effective_schema` before the rc tag.
- The migration rehearsal on two REAL projects (US0106) is the "tested in anger" gate working exactly as designed: a fixture could not have shown BG0070's scale defect (per-file `git log --follow` over ~2,000 files).
- The whole v4 flip landed without auto-flipping any existing project - the override-only schema reader (US0105) plus the era-gate regression test held.

## What was hard / what stalled

- The provenance-guard widening (US0111) was harder than the CR implied: `(see CR0186)` is syntactically identical to a legitimate example `(e.g. CR0003)`, so a blanket widening false-positives on the many example ids in tree diagrams and sample output. Narrowed to the US-led slash/semicolon pair form - the real leak shape - which discriminates cleanly.
- Two test files (`test_reconcile.py` last sprint, `test_validate.py` this sprint) carry an "extra classes after a mid-file `if __name__`" layout; a naive `rfind('if __name__')` append truncated `test_validate.py` (16 methods lost) until caught by the diff stat. Always append at true EOF.
- The "backlog empty" goal met a subtlety: `Fixed` is terminal per the vocab, so the open-bug gate was already green; the readiness doc had to be corrected (US0109/US0110) to use the vocab, not intuition.

## Lessons

- A cross-unit read/write split is invisible to per-unit tests that use fixtures - US0106's test built a `.version` fixture, so it never exercised `init`'s real output. When two units share a concept (here: "the project's schema"), test the SEAM with the real producer, not a fixture. <!-- durable: promote -->
- When appending to a test file, append at true EOF; some files put classes after a mid-file `if __name__` guard, so `rfind` truncates. <!-- lessons add --global candidate -->
- A "widen the guard" request can be a false-positive trap when the target form is syntactically identical to a legitimate one; find the distinctive shape (a joined id pair) rather than blanket-matching.

## Metrics

- Units: 8/8 stories + BG0070 fix, 0 blocked · Critic rejects: 2 (BG0070 provenance tag - stripped; US0108 lockfile - folded) + 1 closing-critic cross-unit blocker (schema-source split, fixed) · Suites at close: 1455 skill + 108 tools green, gate PASS, drift 0 · CRs closed: CR0198/CR0199/CR0201 · Bugs closed: BG0067-0070 · Nothing pushed (rc tag operator-gated).
