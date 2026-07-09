# RETRO-0014: EP0020 + EP0021 - upgrade re-baseline, catalogue hygiene & tooling hardening

> **Date:** 2026-07-09
> **Batch:** EP0020 (US0094-US0096) + EP0021 (US0097-US0099) + BG0068 + BG0069 - 8 units
> **Closes:** CR0197, CR0200, CR0181, CR0182, CR0188; BG0068, BG0069
> **Goal:** `done` - the operator's "run the sprint" over a wide clear-the-decks batch
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- **US0094 / US0095 (CR0197)** - upgrade **re-baseline**: `project_upgrade.rebaseline()` censuses
  every non-terminal artefact against the capability delta, bucketed backfill / re-review /
  residual (empty buckets printed explicitly); `--apply` performs ONLY the mechanical backfill
  (a `route estimate` `Difficulty` stamp), idempotent, no fabricated history. A new gate attaches
  at an artefact's next transition, never retroactively. Schema v3, dormant on v2.
- **US0096 (CR0200)** - split the 643-line `reference-scripts.md` into a lean index + five grouped
  detail pages, each under budget; `doc_coverage` unions `reference-scripts*.md` so the floor still
  hard-fails a missing entry. The 643 allowlist is gone. Docs-only.
- **US0097 (CR0181)** - `github_sync`/`verify_ac` discover through the shared `sdlc_md` layer
  (lowercase-safe); `github_sync` dropped its `TYPE_DIRS` duplicate and threads `--root`; `verify_ac`
  gains a `--root` alias.
- **US0098 (CR0182)** - the two archive implementations consolidated onto one `iter_tables`-based
  `master_terminal_rows` (no hand-rolled walkers); a multi-view index can no longer double-archive.
- **US0099 (CR0188)** - origin-drift pre-flight for `sprint plan` (warn / `--strict` refuse when
  behind origin); `next_id.remote_ids` resolves origin's actual default branch, so remote-aware id
  allocation protects `master`/`develop` repos too.
- **BG0068** - `decisions.py --supersedes` flips the superseded row + fail-loud on a typo id +
  backfill (D0012/D0013). **BG0069** - `test_gate` real-wrapper tests skip visibly from an install.

## Critic loop, observed

Eight units, eight independent per-unit critics (each a separate instance, framed to refute), plus
the closing full-diff pass. **The independence gate earned its keep 8 for 8** - every unit shipped a
real defect the author's own green suite passed over, and every code unit took a REJECT -> fix ->
re-verify cycle (two took three rounds).

| Unit | Verdict path | The escape the author's own tests missed |
| --- | --- | --- |
| BG0068 | APPROVE (LOW fixed) | an over-lenient id parse: a stray-digit typo (`the 5th one`, `D00121`) silently flipped a plausible-but-wrong row instead of failing loud |
| BG0069 | REJECT -> fix -> APPROVE | the NEW locking test itself hard-asserted from an install, recreating the exact misleading FAILED the bug exists to kill |
| US0094 | REJECT -> fix -> APPROVE | the residual Verify count was file-wide, not AC-section-scoped, so a stray Verify line masked a genuinely missing AC verifier; plus a lint-blocking provenance tag |
| US0097 | REJECT -> fix -> APPROVE | `verify_ac` discovery was only half-done (the `--root` alias without the case-insensitive walk), and AC1's Verify was a false green covering only `github_sync` |
| US0099 | REJECT -> fix -> APPROVE | remote id allocation silently no-op'd on any non-`main` default branch (`next_id.remote_ids` hardcoded `origin/main`) - the exact collision CR0188 exists to prevent |
| US0095 | REJECT -> fix -> APPROVE | AC4's grep vs an uppercase doc phrase; CRLF normalised to LF on the real read path (the isolated helper preserved it, the caller did not) |
| US0098 | APPROVE (MEDIUM fixed) | the shipped multi-view regression test passed on the BUGGY pre-refactor code (its view header lacked an ID column) - it never locked the double-archive path |
| Closing full-diff | APPROVE (2 LOW fixed) | no MAJOR/MEDIUM - the cross-unit compositions held: census↔apply action only the backfill bucket (shared `_has_field`); the shared archive walker excludes the duplicated view row (2 rows not 3); the two default-branch resolvers (`next_id`, `sprint`) return the same value; the `doc_coverage` union still hard-fails a missing entry (mutation-checked). Fixed at close: the stale `doc_coverage` failure message and a defensive `next_id` subprocess timeout; the by-default `git fetch` in `sprint plan` is intentional/`--no-fetch`-overridable |

## What went well

- **Under-report / under-fire escapes, caught.** Several defects were in the dangerous direction -
  a masked missing verifier (US0094), a silently-skipped remote scan (US0099), a CRLF whole-file
  rewrite (US0095), a regression test that passed on buggy code (US0098). A confirming test would
  have shipped them; an adversarial one that tries to REFUTE found them.
- **Re-run-your-own-repro turned plausible fixes into proven ones.** US0099's non-`main` fix and
  US0098's regression fixture were each proven by the critic (or the author) running the failing
  case against the OLD code first.
- **The riskiest refactor stayed behaviour-preserving.** US0098 rewrote load-bearing archival on
  both paths; the closing/​per-unit adversarial passes confirmed multi-view, fail-loud, `--statuses`,
  idempotency and census all held, and `reconcile detect` stayed at drift 0.

## What was hard

- **A wide, two-epic clear-the-decks batch.** The operator grew the sprint twice (all open bugs, then
  three EP0018 debt CRs). Eight units across two themes is a long run; sequencing them as independent
  W1 units (disjoint files) with a per-unit critic each, committing green one at a time, kept the tree
  clean and the critic diffs isolated.
- **Executable-AC Verify-line mechanics.** Three units hit a red AC not from a code defect but from a
  brittle Verify line (a `grep -E` the DSL cannot parse, a recursive `verify_ac` self-invocation, a
  full-suite `tail -1 | grep OK`). The lesson: an AC's Verify must be a clean DSL form or a targeted
  test, never a shell pipe with flags/quoting the runner will mangle.

## Lessons

- **A fix is a change and earns its own adversarial pass** - BG0069's regression was introduced by
  the fix for the same bug; only re-running the repro from an install exposed it.
- **A regression test must fail on the buggy code** - US0098's shipped fixture passed on the
  pre-refactor code, so it proved correctness but never locked the regression. Prove the lock by
  running the new test against the reverted source.
- **Deterministic proxies must not answer a judgement question too generously** - US0094's file-wide
  Verify count and US0099's hardcoded `origin/main` both quietly widened/narrowed a check; surface
  the fact and narrow the proxy.
- **Write the AC Verify as a clean DSL verb or a named test** - never a shell pipe the runner mangles.

## Metrics

- Delivered 8/8; 0 blocked. 9 adversarial reviews (8 per-unit + closing), every unit with a real
  finding, 0 shipped unaddressed. 5 of 6 code stories + both bugs took a REJECT->fix cycle.
- 1413 script tests pass (was 1312 at EP0014 close; +new rebaseline/archive/decisions/sprint/
  github_sync/verify_ac tests). Gate PASS; reconcile drift 0 throughout; per-unit conformance 7/7
  on all six stories.
- Story index now 45 terminal rows (> 30 advisory) - archive deferred to the v4.0 cut (no release
  label to archive under mid-freeze). `reference-scripts.md` budget debt cleared (the catalogue
  split was itself a sprint unit).
