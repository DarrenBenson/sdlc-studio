# Bug Index

**Last Updated:** 2026-07-04

## Summary

| Status | Count |
| --- | --- |
| Open | 21 |
| In Progress | 0 |
| Fixed | 78 |
| Verified | 0 |
| Closed | 79 |
| Won't Fix | 3 |
| Superseded | 0 |
| **Total** | **181** |

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
| [BG0112](BG0112-shipped-full-templates-emit-markdownlint-table-errors-md055.md) | shipped full templates emit markdownlint table errors (MD055/MD056/MD060) from the creator | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0113](BG0113-artifact-py-put-section-drops-the-template-s.md) | artifact.py _put_section drops the template's ### subsection prompts when a field is supplied | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0114](BG0114-the-documented-conformance-stage-has-no-remediation-hint.md) | the documented conformance stage has no remediation hint, and the guard meant to catch that is blind to it | Fixed | Medium | 2026-07-13 | 2026-07-13 |
| [BG0115](BG0115-authorship-value-accepts-a-multi-line-author-corrupting.md) | authorship_value accepts a multi-line author, corrupting the Raised-by line and the index row | Fixed | High | 2026-07-13 | 2026-07-13 |
| [BG0116](BG0116-a-consuming-project-s-first-retro-or-review.md) | a consuming project's first retro or review lands as reconcile drift (no meta index bootstrap) | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0117](BG0117-a-prose-field-can-invent-a-metadata-line.md) | a prose field can invent a metadata line in an artefact body; the low-consolidation bullet squeezes a summary onto one line | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0118](BG0118-engagement-floor-over-refuses-an-extension-less-real.md) | engagement-floor over-refuses an extension-less real file in Affects (Makefile, Dockerfile, dotfiles) | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0119](BG0119-engagement-floor-uses-two-different-file-recognisers-for.md) | engagement-floor uses two different file recognisers for the declared-boolean and the file-count | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0120](BG0120-the-index-writer-emits-md060-table-errors-on.md) | the index writer emits MD060 table errors on a freshly created index | Fixed | Low | 2026-07-13 | 2026-07-13 |
| [BG0121](BG0121-the-meta-index-bootstrap-path-lacks-the-blank.md) | the meta-index bootstrap path lacks the blank-collapse and the index lint guard skips meta templates | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0122](BG0122-install-sh-no-ops-when-piped-to-bash.md) | install.sh no-ops when piped to bash (curl \| bash installs nothing) | Fixed | Critical | 2026-07-14 | 2026-07-14 |
| [BG0123](BG0123-the-retro-gate-passes-a-0-byte-file.md) | The retro gate passes a 0-byte file - it checks the filename, not the retro | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0124](BG0124-the-artefact-filer-injects-backticks-into-executable-verify.md) | The artefact filer injects backticks into executable Verify lines, producing false-green ACs | Won't Fix | Critical | 2026-07-14 | 2026-07-14 |
| [BG0125](BG0125-grep-verifier-the-documented-path-glob-example-false.md) | grep verifier: the documented path_glob example false-REDs (verb has zero test coverage) | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0126](BG0126-meta-new-allocates-retro-review-handoff-ids-without.md) | meta_new allocates retro/review/handoff ids without allocation_lock (concurrent collision) | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0127](BG0127-several-index-md-writers-bypass-atomic-write-the.md) | Several _index.md writers bypass atomic_write, the module's own torn-write guard | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0128](BG0128-grep-verifier-verb-silent-rg-grep-rqe-dialect.md) | grep verifier verb: silent rg/grep -rqE dialect swap makes a verdict environment-dependent | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0129](BG0129-review-prep-counts-personas-index-md-as-a.md) | review_prep counts personas/index.md as a persona (the underscore-index filter misses it) | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0130](BG0130-retro-py-miscounts-a-decline-whose-reason-mentions.md) | retro.py miscounts a decline whose reason mentions an artefact id as filed | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0131](BG0131-the-subagent-token-metric-does-not-track-work.md) | The subagent token metric does not track work - it cannot be used for calibration as-is | Won't Fix | High | 2026-07-14 | 2026-07-14 |
| [BG0132](BG0132-cr-acceptance-criteria-carry-verify-lines-that-nothing.md) | CR acceptance criteria carry Verify lines that nothing executes, so a false-green one is never caught | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0133](BG0133-the-accuracy-report-recomputes-the-estimate-from-live.md) | The accuracy report recomputes the estimate from live constants, so it cannot falsify the estimator | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0134](BG0134-the-engagement-floor-trailer-check-warns-after-the.md) | The engagement-floor trailer check warns after the commit has already landed, so it fails open | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0135](BG0135-reconcile-detect-is-blind-to-an-orphan-index.md) | reconcile detect is blind to an orphan index row whose artefact file is gone | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0136](BG0136-the-filer-writes-artefacts-the-planner-then-refuses.md) | The filer writes artefacts the planner then refuses: no --affects flag exists, so every filed bug is unplannable | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0137](BG0137-every-archived-index-row-link-is-wrong-depth.md) | Every archived index row link is wrong-depth: 361 dead links on GitHub | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0138](BG0138-ts0001-carries-13-broken-relative-links-where-is.md) | TS0001 carries 13 broken relative links (../../ where ../ is correct) | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0139](BG0139-the-model-router-scores-a-docs-unit-trivial.md) | The model router scores a docs unit trivial with high confidence: its dominant signal is the predictor falsified today | Won't Fix | High | 2026-07-14 | 2026-07-14 |
| [BG0140](BG0140-the-plan-time-forecast-is-written-to-gitignored.md) | The plan-time forecast is written to gitignored .local/, so BG0133 fix does not survive a clone | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0141](BG0141-retro-extract-titles-a-lesson-from-its-first.md) | retro extract titles a lesson from its first LINE, so a wrapped lesson gets a title cut mid-sentence | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0142](BG0142-reconcile-carries-the-same-archive-link-accommodation-that.md) | reconcile carries the same archive-link accommodation that check_links just shed, so a regressed row could hide there | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0143](BG0143-the-new-body-link-pass-flags-links-inside.md) | The new body-link pass flags links inside code spans and fenced blocks, so no artefact can document a broken link | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0144](BG0144-the-grooming-gate-accepts-an-affects-naming-files.md) | The grooming gate accepts an Affects naming files that do not exist, and silently sizes the unit from nothing | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0145](BG0145-telemetry-cli-rejects-the-new-rate-seed-source.md) | telemetry CLI rejects the new rate seed-source, and complexity drops derivable churn risk for a docs unit | Fixed | Low | 2026-07-14 | 2026-07-14 |
| [BG0146](BG0146-a-recalibration-relabels-past-falsifications-as-training-error.md) | A recalibration relabels past falsifications as training error, erasing the evidence that caused it | Fixed | High | 2026-07-14 | 2026-07-14 |
| [BG0147](BG0147-the-dead-complexity-signal-still-orders-the-batch.md) | The dead complexity signal still orders the batch: CR0262 removed it from the forecast and left it as the WSJF tie-breaker | Fixed | Medium | 2026-07-14 | 2026-07-14 |
| [BG0148](BG0148-the-two-creators-disagree-on-a-cr-size.md) | The two creators disagree on a CR size: file_finding writes a T-shirt Size, artifact.py has no --size flag and writes Points | Fixed | Medium | 2026-07-15 | 2026-07-15 |
| [BG0149](BG0149-artifact-py-silently-drops-points-on-a-story.md) | artifact.py silently drops --points on a story, so the canonical creator makes a story the grooming gate always rejects | Fixed | major | 2026-07-15 | 2026-07-15 |
| [BG0150](BG0150-project-upgrade-does-not-stamp-the-project-version.md) | project upgrade does not stamp the project version and skips open RFCs/CRs/epics/stories | Fixed | Medium | 2026-07-15 | 2026-07-15 |
| [BG0151](BG0151-discovery-awaiting-and-migrate-falsely-flag-old-flow.md) | discovery_awaiting and migrate falsely flag old-flow CRs as un-refined - children_of ignores the legacy Change Request / Linked Epics linking | Fixed | High | 2026-07-15 | 2026-07-15 |
| [BG0152](BG0152-per-attempt-telemetry-has-no-production-writer-neither.md) | Per-attempt telemetry has no production writer: neither the record CLI nor the transition close can produce an attempts list | Fixed | High | 2026-07-16 | 2026-07-16 |
| [BG0153](BG0153-latest-actuals-last-non-null-merge-garbles-multi.md) | latest_actuals' last-non-null merge garbles multi-record cost: a reopen-reclose second record overwrites the first cycle's tokens, and a merged flat+attempts bucket makes accuracy() and unit_cost() disagree | Fixed | High | 2026-07-16 | 2026-07-16 |
| [BG0154](BG0154-decisions-py-rewrites-the-committed-decisions-ledger-with.md) | decisions.py rewrites the committed decisions ledger with no allocation lock and no atomic write, violating both halves of the TRD's shared-file guarantee | Open | High | 2026-07-16 | 2026-07-16 |
| [BG0155](BG0155-a-corrupt-close-owed-baseline-json-silently-disarms.md) | A corrupt .close-owed-baseline.json silently disarms the entire 'un-skippable' close-down and every surface then invites re-stamping a baseline that forgives the owed debt | Open | High | 2026-07-16 | 2026-07-16 |
| [BG0156](BG0156-prd-data-architecture-places-telemetry-jsonl-in-gitignored.md) | PRD data architecture places telemetry.jsonl in gitignored .local and calls VELOCITY.md 'the one piece of measurement state deliberately committed'; committed main moved the evidence ledger to committed retros/evidence/ | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0157](BG0157-breakdown-gate-ac-in-prd-and-trd-enumerates.md) | Breakdown-gate AC in PRD and TRD enumerates size vocabularies the gate does not accept (Effort S/M/L, review-seat score) | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0158](BG0158-velocity-trusts-any-closed-run-state-sharing-one.md) | Velocity trusts any closed run-state sharing ONE unit with the retro: a carried-over unit attributes a previous run's elapsed to this sprint, even overriding an explicit --elapsed-hours | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0159](BG0159-the-advertised-pricing-config-key-is-silently-unreachable.md) | The advertised pricing config key is silently unreachable: Claude models honour only pricing.<family> (not the hinted pricing.<model>), and any dotted model id is destroyed by config.get's dot-splitting | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0160](BG0160-config-get-crashes-with-an-uncaught-parsererror-on.md) | config.get() crashes with an uncaught ParserError on a malformed .config.yaml despite BG0093's warn-and-default contract - yaml.YAMLError is missing from the catch tuple | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0161](BG0161-accepted-and-delivered-rfcs-0018-0022-and-0023.md) | Accepted-and-delivered RFCs 0018, 0022 and 0023 still list every design decision as Open, with leanings contradicting the recorded outcomes and no Decision sections | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0162](BG0162-tsd-s-per-script-test-module-gate-is.md) | TSD's per-script test-module gate is a phantom: no conformance sweep exists, and the invariant it claims to enforce is already violated by six modules | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0163](BG0163-sprint-plan-s-triage-integration-discards-the-skipped.md) | sprint plan's triage integration discards the skipped/unreadable count - a dropped backlog file is silent in the ceremony whose story title promises 'drops logged' | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0164](BG0164-an-attempts-only-telemetry-record-never-stamps-delivered.md) | An attempts-only telemetry record never stamps Delivered-by on the artefact - the escalation case loses the audit attribution the stamp exists for | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0165](BG0165-escalated-units-evade-the-mixed-model-refusal-and.md) | Escalated units evade the mixed-model refusal and pollute per-model calibration: summed multi-model attempt tokens are attributed wholly to the last attempt's model | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0166](BG0166-adr-010-s-documented-opt-out-lessons-loop.md) | ADR-010's documented opt-out lessons.loop: judgement disarms only one of the three close lanes it claims to make advisory - lessons-summary and lessons-validity block regardless | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0167](BG0167-the-eval-gate-s-an-ungraded-blocking-behaviour.md) | The eval gate's 'an ungraded blocking behaviour fails the gate' only sees scenarios someone started grading - a wholly-ungraded scenario is invisible and the run prints 'gate pass' | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0168](BG0168-prd-says-extracted-specs-are-tracked-ready-awaiting.md) | PRD says extracted specs are tracked 'Ready (awaiting test validation)' and the epic index's note says 'all epics are Ready' directly above 48 Done rows | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0169](BG0169-cr0273-marked-superseded-with-no-successor-pointer-anywhere.md) | CR0273 marked Superseded with no successor pointer anywhere in the artefact graph | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0170](BG0170-tsd-gate-lane-tables-diverge-from-gate-py.md) | TSD gate lane tables diverge from gate.py: doc-freshness and hook-enabled marked Blocking=Yes (both hard-coded advisory), and the shipped close-owed and review-legs lanes are missing entirely | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0171](BG0171-gate-py-require-close-help-text-claims-the.md) | gate.py --require-close help text claims the close-owed lane 'WARNS on every gate by default'; the plain gate never runs it | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0172](BG0172-test-specs-index-md-s-epics-without-specs.md) | test-specs/_index.md's 'Epics without specs' section is blank while 46 of 48 epics have no spec, and its Coverage/By-Test-Type tables are empty header-only shells | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0173](BG0173-refute-panel-verdicts-silently-count-failed-skeptic-votes.md) | Refute-panel verdicts silently count failed skeptic votes as refutations - an outage mid-panel mass-refutes candidates and the audit reports the wrong survivor set as complete | Open | High | 2026-07-16 | 2026-07-16 |
| [BG0174](BG0174-audit-has-no-help-file-and-no-type.md) | audit has no help file and no Type Reference row - the universal '{type} help' contract 404s for the one command with a mandatory pre-flight gate | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0175](BG0175-artifact-py-s-review-handoff-scaffold-path-drops.md) | artifact.py's review/handoff scaffold path drops --author: literal {{author}} in the revision row and no Raised-by stamp, unlike every other type | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0176](BG0176-migrate-s-needs-human-list-advises-re-sizing.md) | migrate's needs-human list advises re-sizing terminal units: 14+ Closed/Fixed legacy-Effort bugs each get 'set its Points by judgement', work nobody should do | Open | Medium | 2026-07-16 | 2026-07-16 |
| [BG0177](BG0177-rfc-decide-misreports-the-drafts-ws-counts-a.md) | rfc decide misreports the drafts: ws counts a Workstream section no RFC has (never the Decomposed-into children), and decided RFCs still read READY for decision | Fixed | Medium | 2026-07-16 | 2026-07-16 |
| [BG0178](BG0178-refine-s-seeded-ac-headings-end-in-and.md) | refine's seeded AC headings end in '...' and fail markdownlint MD026 | Open | Low | 2026-07-16 | 2026-07-16 |
| [BG0179](BG0179-handoff-generate-titles-the-artefact-from-the-goal.md) | handoff generate titles the artefact from the goal sentence verbatim and fails MD026 | Open | Low | 2026-07-17 | 2026-07-17 |
| [BG0180](BG0180-mutation-py-runs-all-mutants-and-exits-0.md) | mutation.py runs all mutants and exits 0 after a red baseline | Open | Medium | 2026-07-17 | 2026-07-17 |
| [BG0181](BG0181-retro-accuracy-reads-parenthetical-ids-in-the-batch.md) | retro accuracy reads parenthetical ids in the Batch line as rateable units | Fixed | Low | 2026-07-17 | 2026-07-17 |

## Archived Releases

- **v3.4.0** (BG0001-BG0052, 52 archived) -> sdlc-studio/bugs/archive/v3.4.0/bug.md
