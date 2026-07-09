# RV-0007: Repository review 2026-07-09: code, architecture, reliability

> **Date:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Reviewer:** Sam Eriksson (QA amigo)
> **Method:** the RV0007 prompt (`repo-review-prompt-2026-07-09.md`, successor to the CR0175
> lineage), run read-only on source at v4.0.0-rc.1 (prepared, untagged). Five parallel legs
> (architecture, code correctness, reliability and failure modes, test/CI, defensive security)
> plus a completeness pass over areas no leg claimed; every reported finding re-verified at its
> cited file:line before filing, most reproduced against scratchpad fixtures, and the Medium
> tier additionally re-verified by two adversarial verification passes (six and eight findings,
> all CONFIRMED). Remediation-only for security. Zero source files modified.

## System overview

SDLC Studio at v4.0.0-rc.1: a progressive-disclosure markdown knowledge base (SKILL.md router,
51 reference files, 39 help files, 73 templates) over a stdlib-Python layer (~45 top-level
scripts, ~16k lines, shared `lib/sdlc_md.py`), dogfooded against its own `sdlc-studio/`
workspace. Since RV0006 (v3.5.0, 2026-07-06) the project closed all 22 of that review's
findings across EP0020-EP0025, landed schema v3 (ULID identity), the v2 to v3 migration, the
context-tiering digest layer, supply-chain pins and the rc-readiness checklist. Backlog was
empty at review start; `main` is 65 commits ahead of origin under the release freeze.

The core discipline remains above category norm and most RV0006 fixes verifiably held (see
Positive observations). This round's defects concentrate in three places RV0006 could not see:
the NEW v3/v4 surface (migration, ULID identity, era-awareness), the crash/resume behaviour of
multi-step writers, and the meta-layer - the gates that guard the gates (hook enablement, CI
parity, advisory lanes, checklist completeness).

## Headline: the rc is not ready, for reasons the checklist cannot see

Nine findings block the v4.0 tag. The pattern behind them: v4's headline features were tested
on their happy paths, and the release checklist verifies the gates it lists but nothing
verifies the list. `npm run lint` fails at HEAD today because the commit gate was never
enabled in this clone and CI has been dark since the freeze; the checklist omits the eval gate
its own release-gate template mandates; and the v2 to v3 upgrade walk - v4's core promise -
corrupts a consuming project if interrupted, collides ids after a clean run, and its close
cascade cannot parse the ids it mints.

## Per-leg assessment

1. **Architecture.** CR0181/CR0182/CR0187 consolidations held; the digest tier (CR0179) is
   exemplary files-are-truth design; the import graph stays acyclic. Regressing at the edges:
   the reconcile hub is at 14 importers (11 at RV0006) with private-underscore contracts;
   config failure handling is still three regimes post-CR0180 (BG0093); `--format json` and
   exit-code conventions are drifting in the newest scripts; anchor docs carry numbers that do
   not reproduce (three different test counts coexist in same-day documents).
2. **Code correctness.** Two High defects on the v3 surface: `reconcile apply` crashes on any
   dated index column (BG0071, on the skill's own shipped templates) and `artifact close`
   cannot type any ULID id (BG0072). Beneath them, a dozen verified Mediums: index-writer
   corruption classes (BG0081, BG0082), verify_ac discovery and contract gaps (BG0083, BG0084,
   BG0089), a swallowed safety pre-flight (BG0085), and JSON-mode exit suppression (BG0088).
3. **Reliability (the emphasis).** The weakest dimension again, but now with proof: an
   interrupted `migrate_v3` cross-wires identities on resume (BG0073); the upgrade walk never
   stamps `schema_version: 3`, so the next filing collides with live aliases (BG0074); v3
   short ids carry zero randomness (BG0086); CR0183's concurrency floor covers one writer of
   many - a 4-way id collision through `file_finding` was reproduced (BG0076); `archive.py`
   duplicates rows on crash-resume (BG0091); `github_sync push` lies about failure (BG0092).
   Single-writer, single-clone, uninterrupted operation is safe; every deviation from that has
   at least one live defect.
4. **Test and CI.** The unit tier is fast, green and honest (1455 + 108, no real-network
   tests, CR0185's invariant tier landed and is real). The meta-layer failed: the pre-commit
   hook was never enabled in this clone, CI is dark while `main` is unpushed, and six
   markdown-breaking commits reached `main` unchecked (BG0075); nothing detects a disabled
   gate (CR0202); CI never runs `gate.py` despite two docs claiming parity (BG0096); the
   mutation lane has warned on 100% of runs since birth (CR0203); eleven test files silently
   drop 36 classes on direct runs (CR0204).
5. **Defensive security.** Strongest leg. All RV0006 security fixes held (shell-gate technical
   control, workflow permissions, SHA pins plus dependabot, installer checksums, push secret
   scan); no committed secrets; `yaml.safe_load` only; argv-list subprocesses with timeouts;
   sanitised slugs. One Medium gap: the `Provenance: external` stamp that gates shell
   verifiers has no writer anywhere on the ingest path (BG0095) - a control with no producer.

## Findings table

All 42 findings verified; 33 artefacts filed (Lows consolidated per protocol into CR0207 and
CR0208). rc-verdict: does the finding block cutting the v4.0 tag?

| Artefact | Title (abridged) | Type | Severity | rc-verdict |
| --- | --- | --- | --- | --- |
| [BG0071](../bugs/BG0071-reconcile-apply-missing-row-append-crashes-keyerror-date.md) | reconcile apply KeyError 'date' on dated index columns | Bug | High | **blocks** |
| [BG0072](../bugs/BG0072-artifact-close-cannot-infer-the-type-of-any.md) | artifact close cannot type any v3 ULID id | Bug | High | **blocks** |
| [BG0073](../bugs/BG0073-migrate-v3-re-run-after-an-interrupted-apply.md) | interrupted migrate_v3 re-run cross-wires identities | Bug | High | **blocks** |
| [BG0074](../bugs/BG0074-the-v2-v3-upgrade-walk-never-stamps-schema.md) | upgrade walk never stamps schema_version: 3 (alias collision) | Bug | High | **blocks** |
| [BG0075](../bugs/BG0075-npm-run-lint-fails-at-head-the-pre.md) | lint fails at HEAD; commit gate never enabled; CI dark | Bug | High | **blocks** |
| [BG0076](../bugs/BG0076-cr0183-concurrency-floor-is-incomplete-file-finding-and.md) | CR0183 floor incomplete; 4-way id collision reproduced | Bug | High | post-v4 |
| [BG0077](../bugs/BG0077-file-finding-is-not-era-aware-it-mints.md) | file_finding mints v2 ids on schema-v3 projects | Bug | Medium | **blocks** |
| [BG0078](../bugs/BG0078-artifact-new-low-severity-consolidation-exits-1-after.md) | Low-consolidation exits 1 after creating the CR | Bug | Medium | **blocks** |
| [BG0079](../bugs/BG0079-v4-rc-readiness-checklist-omits-the-eval-gate.md) | rc checklist omits the mandated eval gate | Bug | Medium | **blocks** |
| [BG0080](../bugs/BG0080-shipped-docs-still-describe-the-superseded-regime-status.md) | status/hint tables lack schema-3 row; SECURITY.md 1.x-only | Bug | Medium | **blocks** |
| [BG0081](../bugs/BG0081-a-reopened-after-archive-artefact-creates-permanent-drift.md) | archive rows shadow live rows: permanent drift | Bug | Medium | post-v4 |
| [BG0082](../bugs/BG0082-reconcile-index-rewriter-bleeds-a-stale-status-column.md) | index rewriter bleeds Status into status-less tables | Bug | Medium | post-v4 |
| [BG0083](../bugs/BG0083-verify-ac-story-discovery-executes-companions-and-any.md) | verify_ac executes companions / any us*.md | Bug | Medium | post-v4 |
| [BG0084](../bugs/BG0084-verify-ac-run-story-with-a-missing-path.md) | verify_ac --story missing path exits 0 | Bug | Medium | post-v4 |
| [BG0085](../bugs/BG0085-sprint-plan-origin-drift-preflight-silently-dies-for.md) | sprint plan preflight swallowed for --order manual | Bug | Medium | post-v4 |
| [BG0086](../bugs/BG0086-v3-short-ids-carry-zero-randomness-uncoordinated-writers.md) | v3 short ids carry zero randomness | Bug | Medium | post-v4 |
| [BG0087](../bugs/BG0087-migrate-v3-id-minting-wraps-at-1024-files.md) | migrate_v3 counter wraps at 1024 (silent overwrite) | Bug | Medium | post-v4 |
| [BG0088](../bugs/BG0088-format-json-suppresses-failure-exit-codes-on-reconcile.md) | --format json suppresses failure exits | Bug | Medium | post-v4 |
| [BG0089](../bugs/BG0089-verify-ac-run-root-mixes-roots-story-discovery.md) | verify_ac --root mixes cwd and root | Bug | Medium | post-v4 |
| [BG0090](../bugs/BG0090-gate-py-fail-open-a-check-that-raises.md) | gate.py fail-open: raising check reads as PASS | Bug | Medium | post-v4 |
| [BG0091](../bugs/BG0091-archive-py-is-not-idempotent-per-release-a.md) | archive.py duplicates rows on crash-resume | Bug | Medium | post-v4 |
| [BG0092](../bugs/BG0092-github-sync-push-exits-0-and-stamps-last.md) | push exits 0 and stamps last_push on total failure | Bug | Medium | post-v4 |
| [BG0093](../bugs/BG0093-config-failure-handling-remains-three-regime-post-cr0180.md) | config handling still three regimes post-CR0180 | Bug | Medium | post-v4 |
| [BG0094](../bugs/BG0094-plan-review-resolves-stories-with-a-case-sensitive.md) | plan_review case-sensitive glob: unclearable false block | Bug | Medium | post-v4 |
| [BG0095](../bugs/BG0095-the-provenance-external-stamp-that-gates-shell-verifiers.md) | Provenance: external stamp has no writer | Bug | Medium | post-v4 |
| [BG0096](../bugs/BG0096-ci-never-runs-gate-py-although-the-pre.md) | CI never runs gate.py despite claimed parity | Bug | Medium | post-v4 |
| [CR0202](../change-requests/CR0202-detect-a-disabled-commit-gate-nothing-verifies-core.md) | detect a disabled commit gate | CR | High priority | post-v4 |
| [CR0203](../change-requests/CR0203-make-the-mutation-gate-earn-its-lane-wire.md) | mutation gate: wire a run or remove the lane | CR | Medium | post-v4 |
| [CR0204](../change-requests/CR0204-normalise-the-eleven-test-files-with-mid-file.md) | normalise mid-file `__main__` guards (36 hidden classes) | CR | Medium | post-v4 |
| [CR0205](../change-requests/CR0205-installers-replace-delete-then-copy-with-copy-then.md) | installers: copy-then-swap, not delete-then-copy | CR | Medium | post-v4 |
| [CR0206](../change-requests/CR0206-github-sync-push-adopt-an-existing-issue-by.md) | push: adopt existing issue by title (dedupe) | CR | Medium | post-v4 |
| [CR0207](../change-requests/CR0207-reliability-debt-low-themed-permissions-pagination-growth-scale.md) | reliability debt, themed (14 Low items) | CR | Low theme | post-v4 |
| [CR0208](../change-requests/CR0208-quality-and-docs-debt-low-themed-duplication-conventions.md) | quality and docs debt, themed (20 Low items) | CR | Low theme | post-v4 |

## Deduplication against the RV0006 lineage

- Nothing here refiles an RV0006 finding: all 22 (BG0053-BG0066, CR0180-CR0187) were verified
  Closed, and the fixes were spot-checked at their sites - BG0053/54/55/57/60/61/63/64(pull)/
  65/66/70 all held, as did the CR0181/0182(walker)/0185/0186/0187 deliverables.
- Three findings are "a Complete CR's scope did not hold" rather than regressions: BG0076
  (CR0183's own named scope), BG0093 (CR0180's ACs), BG0092 (the BG0064 class on the push
  side, which BG0064's fix never covered). Each is filed with fresh evidence.
- The github_sync cascade regexes matching only v2 ids was NOT filed: it falls under the
  deferred "era lens" idea already recorded in `reviews/LATEST.md`.
- BG0086 (short-id randomness) is a defect in RFC0024's delivered mechanism, cross-referenced
  there; it does not reopen the RFC.

## Positive observations (no action)

All four RV0006 security fixes held and the supply-chain work is real (SHA pins plus
dependabot, installer sha256 verification, push secret scan with public-target refusal). No
committed secrets. The digest tier is exemplary derived-state design. `next_id` allocation is
remote-aware and deletion-proof. The invariant test tier (CR0185) landed and covers the exact
RV0006 seams; the RETRO0016 schema seam got a true-producer regression test. Suites are fast
and honest (no real-network tests; git identity pinned). bash-3 portability held. The
pre-commit hook design (repo-wide, self-diagnosing) is right - only its enablement failed.
`docs/why-sdlc-studio.md` honestly publishes non-significant benchmark results. Coverage 85%
and bandit clean reproduce locally.

## Verification (read-only)

- Both suites at HEAD: **1455 skill + 108 tools, OK** (before and after filing).
- `gate.py --root .` -> PASS; `reconcile.py detect` -> **0 drift** after filing 33 artefacts;
  `validate.py` clean over the new artefacts.
- `npm run lint` -> **fails at HEAD** (BG0075, pre-existing; the six offending files predate
  this review and none are artefacts this review created).
- Every finding re-verified at its cited file:line; 14 adversarially re-verified by
  independent passes (14/14 CONFIRMED); the crash/resume and collision claims reproduced
  against scratchpad fixtures, never against this repo.

## Limitations

- `gh` failure modes verified via a stub binary and code reading; no live network calls.
- Whether release tags publish the `.sha256` sidecar the installers fetch is unverifiable
  offline; if none is published, the checksum gate is dormant by default (open question).
- Windows paths (install.ps1, the allocation-lock no-op) reviewed by read only.
- Eval scenarios were not executed (each costs real model sessions); BG0079 concerns the
  absence of a recorded run, not a graded failure.
- `npm audit` not re-run (network); LATEST.md's "0 vulnerabilities" is unrecomputed.
- Some crash windows (mid-`write_text` truncation) are argued from the syscall sequence;
  the crash-between-steps scenarios were fully reproduced.

## Top five priorities (recommended order)

1. **The rc-blocker fix pack** - BG0071/72/73/74/77/78 are all S or M effort on the v3/v4
   surface the tag ships; BG0075's lint fix plus hook enablement is an hour. None is
   architectural; together they are the difference between "v4 works" and "v4 works unless
   interrupted, retried, or run on its own defaults".
2. **BG0079 + BG0080** - run the four eval scenarios, add the eval row to the checklist, and
   make the docs stop describing the superseded regime. This is what makes the checklist's
   "GREEN" claim true rather than merely recorded.
3. **CR0202 + BG0096 + BG0090** - close the meta-layer: detect a disabled hook, put `gate.py`
   in CI, make a crashing check fail the gate. These three would have prevented or surfaced
   most of priority 1 before a review had to.
4. **BG0076 + BG0086** - finish the concurrency floor and put randomness in the short id
   before multi-agent waves become the normal operating mode; today's single-writer convention
   is the only thing standing between v3 identity and reproduced collisions.
5. **BG0081 + BG0082 + BG0091 (the index-writer cluster)** - three verified corruption classes
   in the same few functions; fix together with the CR0208 decomposition of the reconcile
   writers so the fix lands in simpler code.

## Closing rc verdict (report only - the tag is the operator's call)

**Nine findings block the v4.0 tag as prepared:** BG0071-BG0075, BG0077-BG0080. The
rc-readiness checklist reads green because it measures the gates it lists; this review found
the gaps between the gates. Every blocker is S/M effort and surgical - a focused fix pack plus
an eval run and a lint sweep would clear the set without reopening any delivered epic. The
alternative (tag now, fix in 4.0.1) ships a v4 whose headline path - migrate a real project to
v3 - can corrupt that project on interruption and collide its ids on the first filing after a
clean walk. Recommendation: fix pack first, re-run the checklist including the new eval row,
then tag.

## Console summary

- Findings: 42 verified (0 refuted) -> 33 artefacts: 26 bugs (6 High, 20 Medium) +
  7 CRs (5 Medium-tier, 2 themed Low consolidations holding 34 items).
- Artefacts raised: BG0071-BG0096, CR0202-CR0208. Roadmap RFC filed separately.
- rc verdict: 9 blockers (BG0071-BG0075, BG0077-BG0080); everything else post-v4.
- Recommended next action: sprint the nine-blocker fix pack, then re-run the rc checklist
  with the eval row added, then tag v4.0.0-rc.1.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | Sam Eriksson (QA amigo) | Full report: 26 bugs + 7 CRs filed, 14 adversarially re-verified, rc verdict recorded |
