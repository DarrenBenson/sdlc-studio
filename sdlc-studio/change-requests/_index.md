# Change Request Index

**Last Updated:** 2026-07-04

## Summary

| Status | Count |
| --- | --- |
| Proposed | 7 |
| Approved | 0 |
| In Progress | 0 |
| Complete | 132 |
| Rejected | 0 |
| Deferred | 0 |
| Superseded | 1 |
| Blocked | 0 |
| **Total** | **140** |

## All Changes

| ID | Title | Status | Priority | Type | Date | Linked Epics |
| --- | --- | --- | --- | --- | --- | --- |
| [CR-0001](CR0001-doc-accuracy-fixes.md) | Documentation accuracy - command-vs-script scope and metadata convention | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0002](CR0002-add-deterministic-duplicate-id-collision-detector.md) | Add deterministic duplicate-ID / collision detector; census scripts silently collapse colliding IDs | Complete | High | Improvement | 2026-06-20 | -- |
| [CR-0003](CR0003-add-referential-integrity-check-for-required-epic.md) | Add referential-integrity check for required Epic/Story link fields and dangling ID references | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0004](CR0004-review-prep-staleness-uses-filesystem-mtime-and-ra.md) | review_prep staleness uses filesystem mtime and raw-string timestamp comparison, breaking determinism across clones and timestamp formats | Complete | High | Improvement | 2026-06-20 | EP0005 |
| [CR-0005](CR0005-verify-ac-py-writes-no-report-in-dry-run-and-overw.md) | verify_ac.py writes no report in dry-run and overwrites a single report with no run history | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0006](CR0006-add-a-graded-llm-judge-verifier-verb-to-verify-ac.md) | Add a graded/LLM-judge verifier verb to verify_ac DSL for AI-output and qualitative ACs | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0007](CR0007-add-epic-implement-resume-that-reads-the-workflow.md) | Add epic implement --resume that reads the workflow execution table and restarts at the first non-Done story | Complete | High | Improvement | 2026-06-20 | EP0007 |
| [CR-0008](CR0008-collapse-three-way-config-defaults-duplication-and.md) | Collapse three-way config-defaults duplication and make one source authoritative that scripts actually read | Complete | Medium | Improvement | 2026-06-20 | EP0008 |
| [CR-0009](CR0009-make-best-practices-guides-sliceable-and-load-once.md) | Make best-practices guides sliceable and load-once; a TypeScript code plan misses the DOM guidance it delegates to javascript.md | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0010](CR0010-prd-performance-nfr-cites-non-existent-scripts-tes.md) | PRD Performance NFR cites non-existent 'scripts/tests timings' evidence | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0011](CR0011-prd-plan-file-lifecycle-location-omits-its-backing.md) | PRD Plan-file lifecycle Location omits its backing script scripts/plan.py | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0012](CR0012-trd-adr-001-corpus-counts-contradict-the-component.md) | TRD ADR-001 corpus counts contradict the Component Overview table and reality | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0013](CR0013-trd-deployment-topology-lists-six-targets-but-hide.md) | TRD deployment topology lists six targets but hides that codex and agents share one directory | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0014](CR0014-tsd-and-ep0008-hard-code-181-as-a-gate-ac-criterio.md) | TSD and EP0008 hard-code '181' as a gate/AC criterion, coupling them to a count that changes every release | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0015](CR0015-tsd-claims-a-workspace-write-confinement-test-that.md) | TSD claims a workspace write-confinement test that does not exist | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0016](CR0016-all-eight-audit-filed-crs-carry-an-identical-place.md) | All eight audit-filed CRs carry an identical placeholder AC that asserts nothing about the change | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0017](CR0017-cr0005-evidence-is-partly-false-it-claims-verify-a.md) | CR0005 evidence is partly false: it claims verify_ac writes the report 'with no timestamp', but write_report emits generated_at | Complete | Low | Improvement | 2026-06-20 | -- |
| [CR-0018](CR0018-sprint-retro-lessons-folder.md) | Sprint retro and committed lessons-learned folder | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0019](CR0019-progressive-disclosure-archived-indexes.md) | Progressive-disclosure indexes with release archival | Superseded | High | Improvement | 2026-06-20 | -- |
| [CR-0020](CR0020-autosprint-phase2-guardrails-ledger.md) | Autosprint Phase 2 - deterministic guardrails, decisions ledger, autonomous wiring | Complete | High | Feature | 2026-06-20 | EP0007 |
| [CR-0021](CR0021-autosprint-tranche-audit-step.md) | Autosprint tranche-audit step (pre-flight grooming) | Complete | High | Feature | 2026-06-20 | EP0007 |
| [CR-0022](CR0022-autosprint-deps-first-ordering.md) | Dependency-first ordering in autosprint plan | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0023](CR0023-complete-conformance-gate.md) | Complete the conformance gate - reconciled, reviewed, and a recorded critic verdict | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0024](CR0024-rfc-decide-decision-session.md) | `rfc decide` - the multi-RFC decision session | Complete | High | Feature | 2026-06-20 | EP0006 |
| [CR-0025](CR0025-checks-emit-remediation-guidance.md) | deterministic checks emit remediation guidance, not just findings | Complete | High | Feature | 2026-06-20 | EP0005 |
| [CR-0026](CR0026-reconcile-apply-subcommand.md) | reconcile `apply` - mechanical index fixes behind --dry-run | Complete | High | Feature | 2026-06-20 | EP0005 |
| [CR-0027](CR0027-per-project-status-vocab-and-conformance-cutoff.md) | per-project status vocab + conformance adoption cutoff | Complete | High | Feature | 2026-06-20 | EP0005/EP0008 |
| [CR-0028](CR0028-complexity-computation.md) | complexity computation (RFC0009 WS1) | Complete | High | Feature | 2026-06-20 | EP0008 |
| [CR-0029](CR0029-code-plan-complexity-estimation.md) | code plan complexity estimation + refactor-first (RFC0009 WS2) | Complete | High | Feature | 2026-06-20 | EP0008 |
| [CR-0030](CR0030-decompose-apply-type.md) | decompose apply_type (refactor-first on RFC0009's own signal) | Complete | Medium | Improvement | 2026-06-20 | EP0005 |
| [CR-0031](CR0031-validate-no-ac-adoption-cutoff.md) | validate no-ac honours the conformance adoption cutoff | Complete | Medium | Improvement | 2026-06-20 | EP0005 |
| [CR-0032](CR0032-repo-map-honest-lexical-ranker.md) | redocument repo_map as a lexical relevance ranker (RFC0004) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0033](CR0033-consolidate-test-reference-clique.md) | consolidate the test-reference clique (RFC0008) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0034](CR0034-personas-generate-on-demand.md) | personas generate on demand from seeds (RFC0007) | Complete | Medium | Improvement | 2026-06-20 | -- |
| [CR-0035](CR0035-deterministic-finding-filer.md) | deterministic Bug/CR/RFC finding filer (RFC0002 WS3) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0036](CR0036-reference-audit-methodology.md) | reference-audit.md methodology + project lens packs (RFC0002 WS1) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0037](CR0037-audit-harness-templates.md) | portable audit prompt-harness templates (RFC0002 WS2) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0038](CR0038-autosprint-wsjf-complexity.md) | autosprint --order wsjf + complexity-weighted budget (RFC0009 WS3) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0039](CR0039-audit-skill-profile-pack.md) | package the skill-profile lens pack (RFC0002 WS5) | Complete | Low | Feature | 2026-06-20 | -- |
| [CR-0040](CR0040-project-constitution-gate.md) | optional project constitution + machine-checkable principle gate (RFC0005) | Complete | Medium | Feature | 2026-06-20 | -- |
| [CR-0041](CR0041-progressive-disclosure-indexes.md) | progressive-disclosure indexes with release archival (RFC0012) | Complete | High | Feature | 2026-06-20 | -- |
| [CR-0042](CR0042-transition-helper.md) | deterministic status-transition helper | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0043](CR0043-complexity-churn-test-risk.md) | churn-weighted composite + complexity-driven test risk (RFC0009 WS4) | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0044](CR0044-skill-version-check-self-update.md) | skill version check + consent `skill-update` | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0045](CR0045-deterministic-artifact-write-cascade.md) | deterministic artifact create + cross-link cascade | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0046](CR0046-portable-ci-quality-gate.md) | portable quality-gate entrypoint for CI (ecosystem-neutral) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0047](CR0047-pvd-template-and-manifest.md) | PVD template + product manifest (RFC0015 WS1) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0048](CR0048-read-only-pvd-projection-drift-check.md) | read-only PVD projection + drift check (RFC0015 WS2) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0049](CR0049-product-reconcile-feature-map-traceability.md) | product reconcile - cross-repo feature-map traceability (RFC0015 WS3) | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0050](CR0050-telemetry-record-and-schema.md) | telemetry record + .local/telemetry.jsonl schema (RFC0014 WS1) | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0051](CR0051-telemetry-loop-capture.md) | loop writes a telemetry record per unit close (RFC0014 WS2) | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0052](CR0052-asset-provenance-stamp-misuse-check-remake.md) | asset provenance stamp + misuse check + remake migration | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0053](CR0053-autosprint-dod-includes-documentation-deterministic-doc-coverage-gate.md) | autosprint DoD includes documentation + deterministic doc-coverage gate | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0054](CR0054-review-and-reframe-all-help-text-around-getting.md) | review and reframe all help text around getting-started and autosprint | Complete | High | Improvement | 2026-06-21 | -- |
| [CR-0055](CR0055-gate-gains-a-duplicate-id-check-optional-provenance.md) | gate gains a duplicate-id check + optional provenance registration | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0056](CR0056-conformance-and-validate-flag-unresolved-placeholder-content.md) | conformance and validate flag unresolved placeholder content | Complete | Medium | Improvement | 2026-06-21 | -- |
| [CR-0057](CR0057-unify-the-two-artifact-create-paths-and-share.md) | unify the two artifact create paths and share index helpers | Complete | Medium | Improvement | 2026-06-21 | -- |
| [CR-0058](CR0058-cooper-goal-directed-persona-template-and-reference-persona.md) | Cooper goal-directed persona template and reference-persona model RFC0017 WS1 | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0059](CR0059-persona-well-formedness-check-cast-role-aware-advisory.md) | Persona well-formedness check cast-role-aware advisory RFC0017 WS3 | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0060](CR0060-review-seat-charters-and-isolated-subagent-consults-rfc0016.md) | Review-seat charters and isolated-subagent consults RFC0016 lean | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0061](CR0061-stakes-scaled-autosprint-review-depth-token-trim.md) | Stakes-scaled autosprint review depth token trim | Complete | Medium | Improvement | 2026-06-21 | -- |
| [CR-0062](CR0062-project-upgrade-migrate-a-consuming-project-to-current.md) | project upgrade migrate a consuming project to current conventions offered by skill-update | Complete | High | Feature | 2026-06-21 | -- |
| [CR-0063](CR0063-disclosure-check-progressive-disclosure-and-claude-code-best.md) | disclosure check progressive disclosure and claude code best practice advisory | Complete | Medium | Feature | 2026-06-21 | -- |
| [CR-0064](CR0064-drive-disclosure-backlog-to-zero-fix-real-gaps.md) | drive disclosure backlog to zero fix real gaps and refine the check | Complete | Medium | Improvement | 2026-06-21 | -- |
| [CR-0065](CR0065-product-owner-owns-prd-and-product-manager-owns.md) | Product Owner owns PRD and Product Manager owns PVD as review seats with requirements-met sign-off | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0066](CR0066-deploy-contract-and-config-yaml-deploy-schema-rfc0013.md) | deploy contract and .config.yaml deploy schema (RFC0013 WS1) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0067](CR0067-deploy-workflow-gate-to-operator-triggered-deploy-to.md) | deploy workflow gate to operator-triggered deploy to verify tier to surface rollback (RFC0013 WS2) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0068](CR0068-record-deploy-outcome-into-the-artifact-graph-rfc0013.md) | record deploy outcome into the artifact graph (RFC0013 WS3) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0069](CR0069-harden-shared-table-parser-edge-cases-plus-regression.md) | harden shared table-parser edge cases plus regression battery (review WS B1a) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0070](CR0070-test-density-backfill-for-repo-map-github-sync.md) | test-density backfill for repo_map github_sync lessons (review WS B1b) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0071](CR0071-project-upgrade-determinism-hygiene-sorted-globs-and-injectable.md) | project_upgrade determinism hygiene sorted globs and injectable date (review WS B1) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0072](CR0072-contributing-dev-bootstrap-plus-architecture-pointer-review-ws.md) | CONTRIBUTING dev bootstrap plus architecture pointer (review WS B3b) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0073](CR0073-doc-freshness-advisory-gate-check-latest-claims-vs.md) | doc-freshness advisory gate check LATEST claims vs reality (review WS B4) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0074](CR0074-navigation-entry-points-persona-quality-gates-and-progressive.md) | navigation entry points persona quality-gates and progressive-loading rows (review WS B2bc) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0075](CR0075-consolidate-the-reference-test-doc-set-with-routing.md) | consolidate the reference-test doc set with routing maps (review WS B2a) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0076](CR0076-ci-coverage-gate-plus-python-security-scan-bandit.md) | CI coverage gate plus python security scan bandit (review WS B3c) | Complete | Medium | Feature | 2026-06-22 | -- |
| [CR-0077](CR0077-greenfield-new-lazy-index-creation-plus-full-template.md) | greenfield new - lazy index creation plus full-template scaffolds | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0078](CR0078-batch-artifact-creation-reserve-an-id-range-and.md) | batch artifact creation - reserve an ID range and wire many stories in one pass | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0079](CR0079-init-scaffold-seed-singleton-docs-and-index-files.md) | init becomes executable - create the folder structure, indexes, and singleton docs | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0080](CR0080-first-class-project-decisions-log-a-canonical-home.md) | first-class project decisions log - a canonical home for resolved decisions and open questions | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0081](CR0081-greenfield-runbook-the-canonical-command-order-from-init.md) | greenfield runbook - the canonical path from init through the autosprint handoff | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0082](CR0082-reconcile-projects-file-owned-index-fields-title-points.md) | reconcile projects file-owned index fields (title, points, persona) not just status and counts | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0083](CR0083-agent-instructions-enforce-the-deterministic-tooling-discipline-never.md) | agent-instructions enforce the deterministic-tooling discipline (never hand-roll IDs or indexes) | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0084](CR0084-transition-to-done-consults-the-ac-verify-report.md) | transition to Done consults the AC-verify report - definition-of-done safety net on the hand-driven path | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0085](CR0085-authored-verify-lines-must-use-the-verifier-dsl.md) | enforce the test-spec as the AC-to-test bridge at epic scope (runner-targeted Verify lines as a sub-fix) | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0086](CR0086-authoring-lint-a-story-s-acceptance-criteria-must.md) | authoring lint - a story's acceptance criteria must be satisfiable within its own epic | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0087](CR0087-rename-autosprint-to-sprint-keep-autosprint-as-a.md) | rename autosprint to sprint, keep autosprint as a deprecated alias | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0088](CR0088-sprint-batch-resolver-accepts-a-prd-input-for.md) | sprint batch resolver accepts a PRD input for the authoring bootstrap | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0089](CR0089-authoring-decomposition-phase-prd-to-epics-to-stories.md) | authoring decomposition phase PRD to epics to stories via shared core | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0090](CR0090-the-two-authoring-stops-epic-cut-and-open.md) | the two authoring STOPs epic cut and open questions plus autonomy ceiling | Complete | High | Feature | 2026-06-24 | -- |
| [CR-0091](CR0091-goal-plan-rung-select-sequence-estimate-to-a.md) | goal plan rung select sequence estimate to a sprint plan artifact | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0092](CR0092-goal-design-assigns-story-points-projected-into-the.md) | goal design assigns story points projected into the index | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0093](CR0093-authoring-closing-consistency-pass-ac-scope-ts-check.md) | authoring closing consistency pass ac-scope ts-check reconcile integrity | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0094](CR0094-the-sprint-loop-runs-reconcile-before-plan-surfacing.md) | the sprint loop runs reconcile before plan, surfacing drift before selection | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0095](CR0095-done-requires-verified-config-toggle-plus-a-status.md) | done-requires-verified config toggle plus a status unverified-manual lane | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0096](CR0096-hard-epic-scope-test-spec-requirement-wired-into.md) | hard epic-scope test-spec requirement wired into epic implement | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0097](CR0097-persona-index-projection-in-reconcile-fields-via-a.md) | persona index projection in reconcile fields via a canonical persona field | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0098](CR0098-plan-and-audit-flag-ready-units-whose-verifiers.md) | plan and audit flag Ready units whose verifiers already pass as already-satisfied | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0099](CR0099-goal-plan-consults-the-review-seats-for-wsjf.md) | goal plan consults the review seats for WSJF inputs and defaults to WSJF order | Complete | Medium | Feature | 2026-06-24 | -- |
| [CR-0100](CR0100-re-anchor-the-story-completion-cascade-on-the.md) | Re-anchor the Story Completion Cascade on the deterministic close (artifact.py close / transition.py) | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0101](CR0101-reconcile-per-command-help-help-reconcile-md-must.md) | reconcile per-command help (help/reconcile.md) must point at the deterministic scripts/reconcile.py | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0102](CR0102-no-artifacts-suppress-enforce-behaviour-is-restated-verbatim.md) | --no-artifacts suppress/enforce behaviour is restated verbatim across epic, story, and outputs references | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0103](CR0103-best-practices-code-check-omit-sota-linters-shellcheck.md) | best-practices + code check omit SOTA linters (ShellCheck/shfmt, Ruff/mypy) and teach bare set -e | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0104](CR0104-surface-v3-0-capabilities-in-the-always-loaded.md) | Surface v3.0 capabilities in the always-loaded router + help catalogue (decisions, goal ladder, init-first, batch) | Complete | High | Improvement | 2026-06-24 | -- |
| [CR-0105](CR0105-extend-deterministic-id-allocation-to-the-meta-artifacts.md) | Extend deterministic id-allocation to the meta-artifacts (review/retro/persona/lessons) | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0106](CR0106-sprint-plan-should-scope-a-story-batch-by.md) | sprint plan should scope a story batch by epic, not only by status | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0107](CR0107-sprint-plan-should-emit-dependency-waves-not-just.md) | sprint plan should emit dependency waves, not just a flat order | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0108](CR0108-lead-every-command-help-file-with-a-natural.md) | Lead every command help file with a natural-language 'You can just ask' block + enforce it | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0109](CR0109-tranche-audit-sprint-breakdown-should-run-verify-ac.md) | Tranche audit (sprint breakdown) should run verify_ac lint + ac_scope, not leave them hand-found | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0110](CR0110-author-the-test-spec-ac-coverage-matrix-at.md) | Author the test-spec AC Coverage Matrix at --goal design (shift the AC-to-test bridge left) | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0111](CR0111-verify-ac-batch-mode-run-the-test-runner.md) | verify_ac batch mode - run the test runner once, not a cold start per AC | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0112](CR0112-strip-internal-provenance-tags-cr-bg-rfc-from.md) | Strip internal provenance tags (CR/BG/RFC) from consuming-facing docs + shipped code | Complete | Medium | Improvement | 2026-06-24 | -- |
| [CR-0113](CR0113-ac-scope-cross-epic-ac-false-positives-on.md) | ac_scope / cross-epic-ac false-positives on shared domain vocabulary (cry-wolf in the audit) | Complete | High | Improvement | 2026-06-25 | -- |
| [CR-0114](CR0114-establish-inter-story-depends-on-at-design-so.md) | Establish inter-story Depends on at design so sprint-plan waves are real, not flat | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0115](CR0115-scaffold-the-test-spec-ac-coverage-matrix-from.md) | Scaffold the test-spec AC Coverage Matrix from an epic stories ACs at design time | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0116](CR0116-frame-the-implementation-sub-agent-as-the-engineering.md) | Frame the implementation sub-agent as the Engineering persona/seat, not a generic agent | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0117](CR0117-mechanically-enforce-author-reviewer-independence-gate-not-an.md) | Mechanically enforce author != reviewer (independence gate), not an honour-system convention | Complete | High | Improvement | 2026-06-25 | -- |
| [CR-0118](CR0118-enriched-amigo-template-instantiate-the-three-default-amigos.md) | Enriched amigo template + instantiate the three default amigos (Cooper depth + seat discipline) | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0119](CR0119-project-upgrade-installs-the-v3-1-amigo-defaults.md) | project upgrade installs the v3.1 amigo defaults into consuming projects | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0120](CR0120-project-upgrade-enriches-existing-review-seats-in-place.md) | project upgrade enriches existing review seats in place instead of installing a parallel amigo set | Complete | High | Improvement | 2026-06-25 | -- |
| [CR-0121](CR0121-gate-points-at-the-conformance-adopt-after-remedy.md) | gate points at the conformance adopt_after remedy instead of burying it in a docstring | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0122](CR0122-reconcile-apply-signposts-fix-order-and-emits-expected.md) | reconcile apply signposts fix-order and emits expected filenames for new index rows | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0123](CR0123-disambiguate-the-three-upgrade-surfaces-skill-update-project.md) | disambiguate the three upgrade surfaces skill-update project-upgrade and schema upgrade | Complete | Low | Improvement | 2026-06-25 | -- |
| [CR-0124](CR0124-migrate-consult-to-the-declared-role-resolver-so.md) | migrate consult to the declared-role resolver so authored seats are honoured there too | Complete | Medium | Improvement | 2026-06-25 | -- |
| [CR-0125](CR0125-index-archive-relocate-terminal-rows-to-a-derived.md) | index archive: relocate terminal rows to a derived sub-index | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0126](CR0126-harden-agentic-wave-worktree-doctrine-commit-per-wave.md) | harden agentic-wave worktree doctrine: commit-per-wave, cherry-pick order, forward-scaffold | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0127](CR0127-pre-deploy-readiness-gate-env-key-diff-persistent.md) | pre-deploy readiness gate: env-key diff, persistent-volume assertion, remote heredoc, crypto round-trip | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0128](CR0128-test-strategy-heuristics-production-state-integration-tests-regression.md) | test-strategy heuristics: production-state integration tests, regression-per-bug, contract rejects-old-shape | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0129](CR0129-sprint-retro-lifecycle-hard-close-gate-lessons-re.md) | sprint retro lifecycle: hard close gate, lessons re-validation, rolling summary of learnings | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0130](CR0130-blocker-sweep-detect-now-unblocked-units-cross-project.md) | blocker sweep: detect now-unblocked units (cross-project via PVD), pre-plan + reconcile lane | Complete | Medium | Improvement | 2026-06-27 | -- |
| [CR-0131](CR0131-assertion-integrity-discipline-mutation-check-gate-templates-reference.md) | assertion-integrity discipline: mutation-check gate + templates + reference | Complete | High | Improvement | 2026-07-04 | -- |
| [CR-0132](CR0132-reconcile-status-vocabulary-must-be-project-configurable-drift.md) | reconcile findings must self-diagnose (name the out-of-vocab status + suggest the actionable fix) | Proposed | High | Improvement | 2026-07-04 | -- |
| [CR-0133](CR0133-surface-a-canonical-non-interactive-artefact-create-path.md) | surface the deterministic toolbox so an agent reaches for the right script (map tasks to scripts, not just prose) | Proposed | High | Improvement | 2026-07-04 | -- |
| [CR-0134](CR0134-executable-mutation-check-test-quality-gate-enforce-assertion.md) | executable mutation-check / test-quality gate (enforce assertion integrity, not just document it) | Proposed | High | Feature | 2026-07-04 | -- |
| [CR-0135](CR0135-house-style-linter-british-english-no-em-dashes.md) | extend the style guard with British-spelling detection (em-dash + jargon already enforced) | Proposed | Low | Improvement | 2026-07-04 | -- |
| [CR-0136](CR0136-enforce-verification-depth-tiers-on-transition-fixed-needs.md) | enforce verification-depth tiers on transition (Fixed needs functional+, Close needs soak) | Proposed | Medium | Improvement | 2026-07-04 | -- |
| [CR-0137](CR0137-pre-commit-hook-runs-the-gate-and-explains.md) | pre-commit hook runs the gate and explains every failure in detail (make enforcement un-skippable) | Complete | High | Feature | 2026-07-04 | -- |
| [CR-0138](CR0138-mixed-batch-sprint-tranches-bugs-plus-crs-first-class.md) | make a mixed bugs + CRs tranche a first-class sprint batch | Proposed | Medium | Improvement | 2026-07-04 | -- |
| [CR-0139](CR0139-deterministic-check-messages-name-numbers-and-remedy.md) | deterministic-check findings should name the exact mismatch and the sanctioned remedy | Proposed | Low | Improvement | 2026-07-04 | -- |
| [CR-0140](CR0140-move-repo-only-tools-checker-tests-out-of.md) | move repo-only tools/ checker tests out of the shipped skill payload (payload hygiene) | Complete | Medium | Improvement | 2026-07-04 | -- |
