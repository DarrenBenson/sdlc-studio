# Bug Index

**Last Updated:** 2026-07-04

## Summary

| Status | Count |
| --- | --- |
| Open | 6 |
| In Progress | 0 |
| Fixed | 33 |
| Verified | 0 |
| Closed | 79 |
| Won't Fix | 0 |
| Superseded | 0 |
| **Total** | **118** |

## All Bugs

| ID | Title | Status | Severity | Created | Updated |
| --- | --- | --- | --- | --- | --- |
| [BG0053](BG0053-artifact-py-close-records-telemetry-twice-per-close.md) | artifact.py close records telemetry twice per close, inflating calibration data | Closed | High | 2026-07-06 | 2026-07-06 |
| [BG0054](BG0054-install-sh-exits-1-after-a-successful-install.md) | install.sh exits 1 after a successful install when the sweep refreshes another copy (set -e) | Closed | High | 2026-07-06 | 2026-07-06 |
| [BG0055](BG0055-ts-check-verify-report-cross-check-keys-on.md) | ts-check verify-report cross-check keys on bare AC id, flagging unrelated stories | Closed | High | 2026-07-06 | 2026-07-06 |
| [BG0056](BG0056-verify-ac-shell-execution-trust-boundary-is-prose.md) | verify_ac shell execution trust boundary is prose-only: externally ingested Verify lines reach shell=True | Closed | High | 2026-07-06 | 2026-07-06 |
| [BG0057](BG0057-verify-ac-unrecognised-verify-expressions-silently-fall-through.md) | verify_ac unrecognised Verify expressions silently fall through to shell execution | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0058](BG0058-ci-workflow-grants-default-github-token-permissions-no.md) | CI workflow grants default GITHUB_TOKEN permissions: no permissions block in lint.yml | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0059](BG0059-gate-py-only-with-an-unknown-check-name.md) | gate.py --only with an unknown check name yields a vacuous PASS | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0060](BG0060-next-id-allocate-cli-ignores-index-row-ids.md) | next_id allocate CLI ignores index-row ids and defaults remote off, diverging from allocate_number | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0061](BG0061-archive-py-hardcodes-its-own-terminal-sets-deferred.md) | archive.py hardcodes its own terminal sets: Deferred stories and CRs archived as closed | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0062](BG0062-story-done-and-parity-gates-crash-with-a.md) | story Done and parity gates crash with a PyYAML RuntimeError instead of the block message on stdlib-only machines | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0063](BG0063-github-sync-gh-wrapper-runs-network-subprocesses-with.md) | github_sync gh() wrapper runs network subprocesses with no timeout | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0064](BG0064-github-sync-pull-records-a-successful-last-pull.md) | github_sync pull records a successful last_pull even when every gh call failed | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0065](BG0065-story-done-verify-gate-passes-on-a-stale.md) | story Done verify gate passes on a stale merged report entry: edited ACs keep last week's green | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0066](BG0066-append-index-row-scans-unbounded-and-disagrees-with.md) | append_index_row scans unbounded and disagrees with reconcile on the master data table | Closed | Medium | 2026-07-06 | 2026-07-06 |
| [BG0067](BG0067-verify-ac-pytest-k-dsl-glues-path-and.md) | verify_ac pytest -k DSL glues path and marker into one argv element | Closed | Medium | 2026-07-08 | 2026-07-08 |
| [BG0068](BG0068-decisions-py-supersedes-never-flips-the-superseded-row.md) | decisions.py --supersedes never flips the superseded row's status | Closed | medium | 2026-07-08 | 2026-07-08 |
| [BG0069](BG0069-shipped-test-gate-real-wrapper-tests-assume-the.md) | Shipped test_gate real-wrapper tests assume the dev-repo path and fail from an install | Closed | low | 2026-07-08 | 2026-07-08 |
| [BG0070](BG0070-migrate-v3-build-id-map-runs-a-git.md) | migrate_v3 build_id_map runs a git log --follow per artefact, so it does not scale to a large project | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0071](BG0071-reconcile-apply-missing-row-append-crashes-keyerror-date.md) | reconcile apply missing-row append crashes KeyError 'date' on any index with a date column | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0072](BG0072-artifact-close-cannot-infer-the-type-of-any.md) | artifact close cannot infer the type of any v3 ULID id | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0073](BG0073-migrate-v3-re-run-after-an-interrupted-apply.md) | migrate_v3 re-run after an interrupted apply re-mints a different id map and silently cross-wires identities | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0074](BG0074-the-v2-v3-upgrade-walk-never-stamps-schema.md) | the v2->v3 upgrade walk never stamps schema_version: 3, so the next filing mints ids that collide with live aliases | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0075](BG0075-npm-run-lint-fails-at-head-the-pre.md) | npm run lint fails at HEAD: the pre-commit gate was never enabled in this clone and CI is dark while main is unpushed | Closed | High | 2026-07-09 | 2026-07-09 |
| [BG0076](BG0076-cr0183-concurrency-floor-is-incomplete-file-finding-and.md) | CR0183 concurrency floor is incomplete: file_finding and new_batch allocate unlocked and truth-file stamps are non-atomic (4-way id collision reproduced) | Fixed | High | 2026-07-09 | 2026-07-09 |
| [BG0077](BG0077-file-finding-is-not-era-aware-it-mints.md) | file_finding is not era-aware: it mints v2 sequential ids on schema-v3 projects | Closed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0078](BG0078-artifact-new-low-severity-consolidation-exits-1-after.md) | artifact new Low-severity consolidation exits 1 after creating the CR, and its dry-run crashes | Closed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0079](BG0079-v4-rc-readiness-checklist-omits-the-eval-gate.md) | v4 rc-readiness checklist omits the eval gate its own release-gate template mandates; evals last ran at v3.5.0 | Closed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0080](BG0080-shipped-docs-still-describe-the-superseded-regime-status.md) | shipped docs still describe the superseded regime: status/hint version tables have no schema-3 row and SECURITY.md supports only 1.x | Closed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0081](BG0081-a-reopened-after-archive-artefact-creates-permanent-drift.md) | a reopened-after-archive artefact creates permanent drift: archive rows shadow live index rows | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0082](BG0082-reconcile-index-rewriter-bleeds-a-stale-status-column.md) | reconcile index rewriter bleeds a stale Status column into following status-less tables, corrupting author-maintained cells | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0083](BG0083-verify-ac-story-discovery-executes-companions-and-any.md) | verify_ac story discovery executes companions and any us*.md file, poisoning runs and ts-check | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0084](BG0084-verify-ac-run-story-with-a-missing-path.md) | verify_ac run --story with a missing path exits 0 (false success) | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0085](BG0085-sprint-plan-origin-drift-preflight-silently-dies-for.md) | sprint plan origin-drift preflight silently dies for --order manual and empty batches; --strict cannot refuse | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0086](BG0086-v3-short-ids-carry-zero-randomness-uncoordinated-writers.md) | v3 short ids carry zero randomness: uncoordinated writers in the same ~1s window mint identical ids | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0087](BG0087-migrate-v3-id-minting-wraps-at-1024-files.md) | migrate_v3 id minting wraps at 1024 files (silent rename overwrite) and pollutes slugs of dash-named files | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0088](BG0088-format-json-suppresses-failure-exit-codes-on-reconcile.md) | --format json suppresses failure exit codes on reconcile apply and verify_ac report; reconcile fields is drift-blind in both formats | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0089](BG0089-verify-ac-run-root-mixes-roots-story-discovery.md) | verify_ac run --root mixes roots: story discovery and report are cwd-relative, verifier cwd and history are root-relative | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0090](BG0090-gate-py-fail-open-a-check-that-raises.md) | gate.py fail-open: a check that raises is recorded non-blocking and the gate prints PASS | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0091](BG0091-archive-py-is-not-idempotent-per-release-a.md) | archive.py is not idempotent per release: a crash between its two writes duplicates every archived row invisibly | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0092](BG0092-github-sync-push-exits-0-and-stamps-last.md) | github_sync push exits 0 and stamps last_push even when every gh create/edit failed | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0093](BG0093-config-failure-handling-remains-three-regime-post-cr0180.md) | config failure handling remains three-regime post-CR0180 and the decided PyYAML documentation never landed | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0094](BG0094-plan-review-resolves-stories-with-a-case-sensitive.md) | plan_review resolves stories with a case-sensitive US*.md glob: lowercase stories get a null fingerprint and an unclearable false block | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0095](BG0095-the-provenance-external-stamp-that-gates-shell-verifiers.md) | the Provenance: external stamp that gates shell verifiers has no writer anywhere on the ingest path | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0096](BG0096-ci-never-runs-gate-py-although-the-pre.md) | CI never runs gate.py although the pre-commit hook and CONTRIBUTING claim parity | Fixed | Medium | 2026-07-09 | 2026-07-09 |
| [BG0097](BG0097-the-finding-filer-emits-markdownlint-breaking-artefacts-when.md) | the finding filer emits markdownlint-breaking artefacts when prose contains underscore identifiers | Fixed | Low | 2026-07-10 | 2026-07-10 |
| [BG0098](BG0098-lint-md-s-glob-skips-dot-directories-the.md) | lint:md's glob skips dot-directories: the shipped skill payload is never markdownlint-checked | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0099](BG0099-artifact-new-batch-cannot-link-a-story-to.md) | artifact new/batch cannot link a story to a v3 ULID epic: _find_epic splits the id on the first dash | Fixed | High | 2026-07-10 | 2026-07-10 |
| [BG0100](BG0100-install-sh-sweep-overwrites-a-git-tracked-repo.md) | install.sh sweep overwrites a git-tracked repo working tree with the downloaded release (working-tree data loss) | Fixed | High | 2026-07-10 | 2026-07-10 |
| [BG0101](BG0101-reconcile-is-blind-to-epic-story-breakdown-checkbox.md) | reconcile is blind to epic Story Breakdown checkbox drift for bug/CR units | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0102](BG0102-project-upgrade-apply-stamps-schema-version-back-to.md) | project upgrade --apply stamps schema_version back to 2 on a schema-3 project | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0103](BG0103-verify-ac-lint-crashes-with-nameerror-when-story.md) | verify_ac lint crashes with NameError when --story is not passed | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0104](BG0104-legacy-verify-lines-rotted-through-renames-and-reached.md) | legacy Verify lines rotted through renames and reached the v4.0.0-rc.1 tag | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0105](BG0105-rebaseline-apply-used-a-python-3-13-only.md) | rebaseline_apply used a Python 3.13-only API; CI (3.12) red on both v4 pushes | Fixed | Medium | 2026-07-10 | 2026-07-10 |
| [BG0106](BG0106-install-downgrade-guard-ranks-a-pre-release-above.md) | install downgrade guard ranks a pre-release above its own release - rc users refused the GA upgrade | Fixed | High | 2026-07-10 | 2026-07-10 |
| [BG0107](BG0107-ci-lacks-pytest-the-audit-quiz-class-d.md) | CI lacks pytest; the audit-quiz class-D grader fails its first CI exposure | Fixed | Low | 2026-07-10 | 2026-07-10 |
| [BG0108](BG0108-artifact-py-schema-v3-skeletons-fail-their-own.md) | artifact.py schema-v3 skeletons fail their own validator (no Raised-by line) | Fixed | Medium | 2026-07-11 | 2026-07-11 |
| [BG0109](BG0109-file-finding-py-hardcodes-audit-as-the-revision.md) | file_finding.py hardcodes 'audit' as the revision-history author, ignoring --author | Fixed | Low | 2026-07-11 | 2026-07-11 |
| [BG0110](BG0110-review-lets-a-required-leg-tsd-be-self.md) | review lets a required leg (TSD) be self-downgraded to optional in prose without an explicit waiver | Fixed | -- | 2026-07-13 | 2026-07-13 |
| [BG0111](BG0111-lessons-written-by-lessons-py-are-lost-on.md) | Lessons written by lessons.py are lost on the next skill update, and project-specific lessons are dumped into the shared cross-project registry | Fixed | -- | 2026-07-13 | 2026-07-13 |
| [BG0112](BG0112-shipped-full-templates-emit-markdownlint-table-errors-md055.md) | shipped full templates emit markdownlint table errors (MD055/MD056/MD060) from the creator | Open | Low | 2026-07-13 | 2026-07-13 |
| [BG0113](BG0113-artifact-py-put-section-drops-the-template-s.md) | artifact.py _put_section drops the template's ### subsection prompts when a field is supplied | Open | Low | 2026-07-13 | 2026-07-13 |
| [BG0114](BG0114-the-documented-conformance-stage-has-no-remediation-hint.md) | the documented conformance stage has no remediation hint, and the guard meant to catch that is blind to it | Open | Medium | 2026-07-13 | 2026-07-13 |
| [BG0115](BG0115-authorship-value-accepts-a-multi-line-author-corrupting.md) | authorship_value accepts a multi-line author, corrupting the Raised-by line and the index row | Fixed | High | 2026-07-13 | 2026-07-13 |
| [BG0116](BG0116-a-consuming-project-s-first-retro-or-review.md) | a consuming project's first retro or review lands as reconcile drift (no meta index bootstrap) | Open | Low | 2026-07-13 | 2026-07-13 |
| [BG0117](BG0117-a-prose-field-can-invent-a-metadata-line.md) | a prose field can invent a metadata line in an artefact body; the low-consolidation bullet squeezes a summary onto one line | Open | Low | 2026-07-13 | 2026-07-13 |
| [BG0118](BG0118-engagement-floor-over-refuses-an-extension-less-real.md) | engagement-floor over-refuses an extension-less real file in Affects (Makefile, Dockerfile, dotfiles) | Open | Low | 2026-07-13 | 2026-07-13 |

## Archived Releases

- **v3.4.0** (BG0001-BG0052, 52 archived) -> sdlc-studio/bugs/archive/v3.4.0/bug.md
