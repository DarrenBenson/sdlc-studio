<!--
Sprint retro for EP0010. Related: reference-sprint.md (the retro lifecycle this dogfoods),
CR0125, CR0126, CR0127, CR0129, CR0130.
-->
# RETRO-0005: Skill self-improvement - token economy + learning loop

> **Date:** 2026-06-27
> **Batch:** EP0010 - CR0125, CR0126, CR0127, CR0129, CR0130 + US0047/US0048 (CI health)
> **Goal:** done
> **Delivered:** 11 stories / 11 (5 CRs; CR0128 held)   **Blocked:** 0

## Delivered

- **CR0125 - index archive (US0040, US0041).** `reconcile archive` relocates terminal index
  rows to a derived `<type>/archive/_index.md`, leaving active rows + the summary block live;
  idempotent, `--dry-run`, fail-loud on an unclassifiable status. `next_id` unions the archive
  sub-indexes so an archived id is never re-issued. Terminal-status vocab is `sdlc_md`-derived,
  not hardcoded.
- **CR0126 - agentic-wave worktree doctrine (US0045).** Commit-per-wave HEAD freshness,
  single-agent-on-main default, cherry-pick by scope narrowness, Wave-1 forward-declares shared
  types - written into `reference-agentic-lessons.md`.
- **CR0127 - pre-deploy readiness (US0046).** Env-key diff, persistent-volume assertion, remote
  heredoc discipline, crypto round-trip checklist in `reference-deploy-readiness.md`.
- **CR0129 - retro lifecycle (US0042, US0043, US0044).** The close is now a hard, fail-loud gate
  (`gate --require-retro`), plus `lessons revalidate` (close stale lessons by validity) and
  `lessons summary` (deterministic rolling `LESSONS-SUMMARY.md` read at sprint start). This retro
  is the first run of that loop.
- **CR0130 - blocker sweep (US0049, US0050).** `blocker_sweep.py` finds units whose blockers
  cleared (in-repo census + cross-repo via the PVD manifest), runs before `plan` and as an
  advisory `reconcile detect --blocker-sweep` lane; proposes `Blocked -> Ready`, never auto-moves.
- **CI health (US0047, US0048).** Coverage gate restored to green; `actions/checkout` v7 +
  `actions/setup-python` v6 adopted; Dependabot PRs #25/#26 closed as superseded.

## Blocked / deferred

- **CR0128 (test-strategy heuristics)** was held by decision at close - then unblocked and
  delivered as a follow-on (see CHANGELOG `[Unreleased]`): `best-practices/testing.md`, test-spec
  template AC stubs, and the `audit` `missing-regression-test` checker.
- Nothing blocked at delivery; the blocker sweep reports zero stale-blocked units.

## What went well

- **Every story landed as its own green unit** - TDD, executable ACs, then `transition -> Done`
  gated on the verifier - committed straight to main, CI green at the end.
- **The honest fix beat the stated symptom (US0047).** The story claimed the coverage gate fell
  below 80% from skipped suites; reproducing the CI env (shadowing `yaml`) showed the real cause
  was 8 test *failures* + 2 errors from PyYAML-absent config tests, which made `coverage run` exit
  non-zero before the threshold was ever read. Coverage was a healthy ~82%. Fixed the cause, not
  the symptom, and corrected the misdiagnosis in the story.
- **The new gates caught their own dogfood.** The full suite (not the new test) caught the
  `_row_id` name collision; the style guard caught a provenance tag the moment it landed.

## What to improve / lessons

- **L-1: a "fails on CI, passes locally" gate is an environment-gap until proven otherwise.**
  Diagnose by reproducing the missing-dependency env (shadow the dep, strip the tool), not by
  trusting the stated symptom. Promote to skill tier. [[ll0008-tools-fail-loud]]
- **L-2: a soft-dependency test must skip (guard) or its dep must be installed in CI** - a test
  that *raises* when an optional dep is absent will fail CI silently-differently from local.
- **L-3: the Verify DSL takes bare expressions** (`pytest <node>`, `shell <cmd>`) - not backticks,
  not `pytest -k`. Subagent-authored Verify lines repeatedly used the wrong form; lint them at
  authoring time (`verify_ac lint`) before the story leaves Draft.
- **L-4: a new private helper that shadows a module-level name silently breaks every existing
  caller** (the `_row_id(line)` vs `_row_id(cells, ...)` collision). Grep the module for the name
  before defining a same-named helper.
